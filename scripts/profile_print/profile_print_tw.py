#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# MentionEject + favEject
#  2013 Akkiesoft / Eject-Command-Users-Group
# Inspire From:
#   http://peter-hoffmann.com/2012/simple-twitter-streaming-api-access-with-python-and-oauth.html

from escpos import printer
import RPi.GPIO as GPIO
import json
import tweepy

from print_receipt import print_receipt

consumer_key    = ""
consumer_secret = ""
access_key      = ""
access_secret   = ""

class CustomStreamListener(tweepy.StreamListener):
    def on_data(self, data):
        jdata = json.loads(data)
        # MentionEject
        try:
          name = jdata['user']['name']
          sn   = jdata['user']['screen_name']
          url  = jdata['user']['url']
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

# GPIO init
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.output(17, 0)

Printer = printer.Usb(0x08a6,0x0041)

# Twitter
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)
#me = api.me()

# printer,sns ok.
GPIO.output(17, 1)

# start twitter stream
stream = tweepy.streaming.Stream(auth, CustomStreamListener())
try:
  stream.userstream()
except(KeyboardInterrupt):
  print("exit.")
finally:
  GPIO.output(17, 0)
  GPIO.cleanup()
