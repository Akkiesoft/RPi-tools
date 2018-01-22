#!/usr/bin/env python
# -*- coding: utf-8 -*-

# MentionEject + favEject
#  2013 Akkiesoft / Eject-Command-Users-Group
# Inspire From:
#   http://peter-hoffmann.com/2012/simple-twitter-streaming-api-access-with-python-and-oauth.html

import os
import sys
import json
import urllib.request
from PIL import Image
from escpos import printer
import RPi.GPIO as GPIO
import tweepy
from mastodon import Mastodon, StreamListener
import threading

# Mastodon thread
class mstdn_thread(threading.Thread):
  def __init__(self, mstdn, stream):
    super(mstdn_thread, self).__init__()
    self.mstdn = mstdn
    self.stream = stream

  def run(self):
    self.mstdn.stream_user(self.stream, async=False)


def get_icon(url, file_orig, file_resize):
  urllib.request.urlretrieve(url, file_orig)
  icon = Image.open(file_orig)
  icon_w, icon_h = icon.size
  #icon_w = 200 if 200 < icon_w else icon_w
  #icon_h = 200 if 200 < icon_h else icon_h
  icon_w = 200
  icon_h = 200
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


def print_receipt(name, sn, icon, status):
  if (-1 < status.find(u"debug")):
      GPIO.output(17, 0)
      Printer.set(align="left", text_type="NORMAL",width=1,height=1)
      Printer.text("twitter: ok\n")
      GPIO.output(17, 1)
  if (-1 < status.find(u"ニャーン")):
      Printer.set(align="left", text_type="NORMAL",width=1,height=1)
      Printer._raw(jptext("@" + sn + "\n" + status + "\n\n"))
  if (-1 < status.find(u"うすいほん")):
      Printer.set(align="center", text_type="B",width=1,height=3)
      Printer._raw(jptext(u"Ejectコマンドユーザー会\n同人誌をPDFで頒布中！！\n"))
      Printer.set(align="center", text_type="NORMAL",width=1,height=1)
      Printer.text("https://eject.booth.pm/\n\n")
      Printer.image("/home/pi/ejectboothpm2.png", False, True, 'bitImageColumn')
      Printer.text("\n\n")
  if (-1 < status.find(u"ちらし")):
      GPIO.output(17, 0)
      Printer.set(align="center", text_type="NORMAL",width=1,height=2)
      Printer.text("Japanese Raspberry Pi\n Users Group\n")
      Printer.set(align="left", text_type="NORMAL",width=1,height=1)
      Printer.text("URL: http://raspi.jp/\n\n")
      Printer.set(align="center", text_type="NORMAL",width=1,height=2)
      Printer._raw(jptext(u"Ejectコマンドユーザー会\n"))
      Printer.set(align="left", text_type="NORMAL",width=1,height=1)
      Printer.text("URL: http://eject.kokuda.org/\n\n")
      Printer.set(align="center", text_type="NORMAL",width=1,height=2)
      Printer.text("@Akkiesoft Github\n")
      Printer.set(align="center", text_type="NORMAL",width=1,height=1)
      Printer.text("http://github.com/Akkiesoft/\n\n")
      Printer.set(align="left", text_type="NORMAL",width=1,height=1)
      Printer._raw(jptext(u"☆RPi-toolsリポジトリ:\n    便利なAnsible Playbook\n    展示物と同じスクリプトなど\n\n☆Eject-Command-Users-Group\n  リポジトリ\n    Ejectっぽいスクリプトとか\n\n\n\n"))
      GPIO.output(17, 1)
  if (-1 < status.find(u"なふだ")):
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

# Twitter Streaming API
class CustomStreamListener(tweepy.StreamListener):
  def on_data(self, data):
    jdata = json.loads(data)
    # MentionEject
    try:
      name = jdata['user']['name']
      sn   = jdata['user']['screen_name']
      icon = jdata['user']['profile_image_url'].replace("_normal.", ".")
      print_receipt(name, sn, icon, jdata['text'])
    except KeyError:
        pass

  def on_error(self, status_code):
    print >> sys.stderr, 'Encountered error with status code:', status_code
    return True # Don't kill the stream

  def on_timeout(self):
    print >> sys.stderr, 'Timeout...'
    return True # Don't kill the stream

# Mastodon Streaming API
class MaStreamListener(StreamListener):
  def on_notification(self, status):
    try:
      domain = status['status']['url'].split('/')[2]
      name = "@" + domain + "\n\n" + status['status']['account']['display_name']
      sn   = status['status']['account']['username']
      icon = status['status']['account']['avatar_static']
      print_receipt(name, sn, icon, status['status']['content'])
    except KeyError:
        pass

# GPIO init
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.output(17, 0)

# Connect to printer
Printer = printer.Usb(0x08a6,0x0041)

# Twitter
consumer_key    = ""
consumer_secret = ""
access_key      = ""
access_secret   = ""

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)


# Mastodon
mstdn = Mastodon(
    client_id     = '',
    client_secret = '',
    access_token  = '',
    api_base_url  = ''
)

# printer,sns ok.
GPIO.output(17, 1)

# start mastodon stream
m_thread = mstdn_thread(mstdn, MaStreamListener())
m_thread.start()

# start twitter stream
stream = tweepy.streaming.Stream(auth, CustomStreamListener())
try:
  stream.userstream()
except(KeyboardInterrupt):
  print("exit.")
finally:
  # かわいそうに、Mastodonではこの処理がない（手抜き）
  GPIO.output(17, 0)
  GPIO.cleanup()
