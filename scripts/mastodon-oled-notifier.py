#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Mastodon OLED Notifer.

import json
import re
import requests
import textwrap
import threading
import time
from io import BytesIO
import Adafruit_SSD1306
from pytz import timezone
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from mastodon import Mastodon, StreamListener

# init display
disp = Adafruit_SSD1306.SSD1306_128_64(rst=None)
disp.begin()
disp.clear()
disp.display()
width = disp.width
height = disp.height

# load font
font = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 11)

TAG_RE = re.compile(r'<[^>]+>')
def remove_tags(text):
    return TAG_RE.sub('', text)

def get_icon(url):
  response = requests.get(url)
  icon = Image.open(BytesIO(response.content))
  return icon.resize((32, 32)).convert("1")

# Mastodon Streaming API
status_id = 0
class MaStreamListener(StreamListener):
  def on_notification(self, status):
    global status_id, width, height
    try:
      status_id = status['id']
      icon = status['account']['avatar_static']
      domain = status['account']['url'].split('/')[2]
      name = status['account']['display_name']
      toot = remove_tags(status['status']['content'])
      text = name + "\n"
      if status['type'] == 'mention':
        text += "mentioned\n"
      if status['type'] == 'reblog':
        text += "boosted\n"
      if status['type'] == 'favourite':
        text += "favorited"
      if status['type'] == 'follow':
        text += "followed you\n"
    except KeyError:
        pass
    image = Image.new('1', (width, height))
    draw = ImageDraw.Draw(image)
    image.paste(get_icon(icon))
    draw.text((35, 0), text, font=font, fill=255)
    offset = 35
    # 全角半角の判定がないので雑
    for line in textwrap.wrap(toot, width=11):
      draw.text((0, offset), line, font=font, fill=255)
      offset += font.getsize(line)[1]
    disp.image(image)
    disp.display()
    thread = threading.Thread(target=clear_display, args=(status_id,))
    thread.start()

def clear_display(i):
  global status_id
  time.sleep(10)
  if i == status_id:
    disp.clear()
    disp.display()

# Mastodonのアカウント情報、自分でappつくって適当にいれてね
mstdn = Mastodon(
    client_id     = '',
    client_secret = '',
    access_token  = '',
    api_base_url  = 'https://social.mikutter.hachune.net'
)

# Start mastodon stream
try:
  mstdn.stream_user(MaStreamListener(), run_async=False)
except(KeyboardInterrupt):
  print("exit.")
