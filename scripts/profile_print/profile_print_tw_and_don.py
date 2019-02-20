#!/usr/bin/env python
# -*- coding: utf-8 -*-

# MentionEject + favEject
#  2013 Akkiesoft / Eject-Command-Users-Group
# Inspire From:
#   http://peter-hoffmann.com/2012/simple-twitter-streaming-api-access-with-python-and-oauth.html

import json
from escpos import printer
import RPi.GPIO as GPIO
import tweepy
from mastodon import Mastodon, StreamListener
import threading

from print_receipt import print_receipt

# Mastodon thread
class mstdn_thread(threading.Thread):
  def __init__(self, mstdn, stream):
    super(mstdn_thread, self).__init__()
    self.mstdn = mstdn
    self.stream = stream

  def run(self):
    self.mstdn.stream_user(self.stream, async=False)

# Twitter Streaming API
class CustomStreamListener(tweepy.StreamListener):
  def on_data(self, data):
    jdata = json.loads(data)
    # MentionEject
    try:
      name = jdata['user']['name']
      sn   = jdata['user']['screen_name']
      icon = jdata['user']['profile_image_url'].replace("_normal.", ".")
      GPIO.output(17, 0)
      print_receipt(Printer, name, sn, icon, jdata['text'])
      GPIO.output(17, 1)
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
      GPIO.output(17, 0)
      print_receipt(Printer, name, sn, icon, status['status']['content'])
      GPIO.output(17, 1)
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
