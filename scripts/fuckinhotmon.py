#!/usr/bin/env python

import sys
import signal
import subprocess
import time
import datetime
import math
import ConfigParser
import Adafruit_Nokia_LCD as LCD
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# Check argv
if len(sys.argv) > 1:
  conf_file = sys.argv[1]
else:
  print('USAGE: %s <config file>' % sys.argv[0])
  sys.exit(1)

zbx = {}
# Read config file
try:
  conf = ConfigParser.ConfigParser()
  conf.read(conf_file)

  # ds18b20
  ds18b20 = conf.get('sensor', 'ds18b20')
  # threshold
  threshold_hot = conf.getint('sensor', 'threshold_hot')
  threshold_cold = conf.getint('sensor', 'threshold_cold')

  # theme
  font_path = conf.get('theme', 'font_path')
  font_size = conf.getint('theme', 'font_size')
  pic_normal = conf.get('theme', 'normal')
  pic_fuckinhot = conf.get('theme', 'fuckinhot')
  pic_samui = conf.get('theme', 'samui')

  # zabbix
  zbx['enabled'] = conf.getboolean('zabbix', 'enabled')
except Exception as e:
  print("Could not read config file.: %s" % e)
  sys.exit(1)

# exit if caught the SIGTERM
def sigterm_handler(signal_number, stack_frame):
    disp.clear()
    disp.display()
    sys.exit(0)   
signal.signal(signal.SIGTERM, sigterm_handler)

# functions to get temp from ds18b20
def read_temp_raw():
  catdata = subprocess.Popen(['cat',ds18b20], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out,err = catdata.communicate()
  out_decode = out.decode('utf-8')
  lines = out_decode.split('\n')
  return lines

def read_temp():
  lines = read_temp_raw()
  while lines[0].strip()[-3:] != 'YES':
    time.sleep(0.2)
    lines = read_temp_raw()
  equals_pos = lines[1].find('t=')
  if equals_pos < 0:
    return 99.99
  temp_string = lines[1][equals_pos+2:]
  temp = float(temp_string) / 1000.0
  return round(temp, 2)


# dummy
zbx_temp = 25
room_temp = 25

# connect to zabbix server
if zbx['enabled']:
  import socket
  import urllib2
  from zabbix.api import ZabbixAPI
  timeout = 10
  socket.setdefaulttimeout(timeout)
  try:
    z = ZabbixAPI(url=zbx['url'], user=zbx['user'], password=zbx['pass'])
  except urllib2.URLError:
    zbx['enabled'] = False


# make sure zabbix or ds18b20 is enabled
if not zbx['enabled'] and ds18b20 == "":
  print("Please enable zabbix or ds18b20.")
  sys.exit(1)


# load theme
fuckinhot = Image.open(pic_fuckinhot).convert('1')
samui = Image.open(pic_samui).convert('1')
normal = Image.open(pic_normal).convert('1')
font = ImageFont.truetype(font_path, font_size)

# init lcd
# RPi software SPI:
SCLK = 17
DIN = 18
DC = 27
RST = 23
CS = 22
disp = LCD.PCD8544(DC, RST, SCLK, DIN, CS)
disp.begin(contrast=60)


# loop
while True:
  try:
    # zabbix temp
    if zbx['enabled']:
      t = z.item.get(itemids=(zbx['itemid']))
      zbx_temp = round(float(t[0]["lastvalue"]), 2)

    # room temp
    if ds18b20:
      room_temp = read_temp()

    if zbx_temp >= threshold_hot or room_temp >= threshold_hot:
      lcd = fuckinhot
    elif zbx_temp < threshold_cold or room_temp < threshold_cold:
      lcd = samui
    else:
      lcd = normal
    draw = ImageDraw.Draw(lcd)

    if zbx['enabled']:
      draw.rectangle((48,0,84,8), outline=255, fill=255)
      draw.text((48,0), '%05s' % (zbx_temp) + '  C', font=font)

    if ds18b20:
      draw.rectangle((48,9,84,17), outline=255, fill=255)
      draw.text((48,8), '%5s' % (room_temp) + ' C', font=font)

    d = datetime.datetime.today()
    draw.rectangle((0,0,24,8), outline=255, fill=255)
    draw.text((0,0), '%02d:%02d' % (d.hour, d.minute), font=font)

    disp.image(lcd)
    disp.display()
    time.sleep(10.0)

  except KeyboardInterrupt:
    disp.clear()
    disp.display()
    sys.exit(0)
