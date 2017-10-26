#!/usr/bin/env python
# -*- coding: utf-8 -*-

# MentionEject + favEject
#  2013 Akkiesoft / Eject-Command-Users-Group
# Inspire From:
#   http://peter-hoffmann.com/2012/simple-twitter-streaming-api-access-with-python-and-oauth.html
# Thanks:
#   https://github.com/SIGCOWW/saty (printing Japanese)

import os
import sys
import json
import tweepy
import urllib.request
from PIL import Image
from escpos import printer

consumer_key    = ""
consumer_secret = ""
access_key      = ""
access_secret   = ""

def get_icon(url, file_orig, file_resize):
  urllib.request.urlretrieve(url, file_orig)
  icon = Image.open(file_orig)
  icon_w, icon_h = icon.size
  icon_w = 200 if 200 < icon_w else icon_w
  icon_h = 200 if 200 < icon_h else icon_h
  icon.resize((icon_w,icon_h)).save(file_resize)

def jptext(str):
  # 文字列を1文字ずつ読んで、マルチバイト文字をESCPOSで使える
  # エスケープコードなしのJIS文字に変換する
  output = []
  jpmode = 0
  jpstart = b'\x1c\x26'
  jpend   = b'\x1c\x2e'
  for c in str:
    c_jis = c.encode('iso2022_jp', 'ignore')
    # single byte code
    if len(c_jis) == 1:
      if jpmode:
        # end japanese mode
        jpmode = 0
        output.append(jpend)
      output.append(c_jis)
      continue
    # start japanese mode
    if not jpmode:
      jpmode = 1
      output.append(jpstart)
    # add multibytes character without escape code.
    output.append(c_jis[3:-3])
  # end japanese mode
  if jpmode:
    output.append(jpend)
  return b''.join(output)

class CustomStreamListener(tweepy.StreamListener):
    def on_data(self, data):
        jdata = json.loads(data)

        # MentionEject
        try:
          name = jdata['user']['name']
          sn   = jdata['user']['screen_name']
          url  = jdata['user']['url']
          icon = jdata['user']['profile_image_url'].replace("_normal.", ".")
          if (-1 < jdata['text'].find(u"なふだ")):
              GPIO.output(17, 0)
              get_icon(icon, "/tmp/icon_orig", "/tmp/icon_resize.png")
              Printer.set(align="center", text_type="BU",width=3,height=3)
              Printer.text("@" + sn + "\n")
              Printer.set(align="center", text_type="NORMAL",width=1,height=1)
              Printer._raw(jptext(name + "\n\n\n"))
              Printer.image("/tmp/icon_resize.png", False, True, 'bitImageColumn')
              Printer.set(align="center", text_type="normal",height=1)
              Printer.text("\n\n\n\n")
              GPIO.output(17, 1)
        except KeyError:
            pass

    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return True # Don't kill the stream

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True # Don't kill the stream

Printer = printer.Usb(0x08a6,0x0041)

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)
#me = api.me()

stream = tweepy.streaming.Stream(auth, CustomStreamListener())
try:
  stream.userstream()
except(KeyboardInterrupt):
  print("exit.")
