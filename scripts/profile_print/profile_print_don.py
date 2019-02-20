#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# MentionEject + favEject
#  2013 Akkiesoft / Eject-Command-Users-Group
# Inspire From:
#   http://peter-hoffmann.com/2012/simple-twitter-streaming-api-access-with-python-and-oauth.html

from escpos import printer
import RPi.GPIO as GPIO
from mastodon import Mastodon, StreamListener

from print_receipt import print_receipt

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
try:
  mstdn.stream_user(MaStreamListener(), run_async=False)
except(KeyboardInterrupt):
  print("exit.")
finally:
  GPIO.output(17, 0)
  GPIO.cleanup()
