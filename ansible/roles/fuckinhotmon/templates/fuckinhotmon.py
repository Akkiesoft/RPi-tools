#!/usr/bin/env python

import time
import datetime
import math
import subprocess
import Adafruit_GPIO as GPIO
import Adafruit_Nokia_LCD as LCD
import Adafruit_GPIO.SPI as SPI
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# Path
path="/home/pi"
# Pictures
pic_normal = path+"/shachikuchan.png"
pic_fuckinhot = path+"/hot.png"
pic_samui = path+"/samui.png"

# threshold
threshold_hot = {{ threshold.hot }}
threshold_cold = {{ threshold.cold }}

{% if use_zabbix %}
# Zabbix Parameters
from zabbix.api import ZabbixAPI
zbxurl    = "{{ zabbix_url }}"
zbxuser   = "{{ zabbix_user }}"
zbxpass   = "{{ zabbix_pass }}"
zbxitemid = {{ zabbix_item_id }}
z = ZabbixAPI(url=zbxurl, user=zbxuser, password=zbxpass)
{% endif %}

{% if use_ds18b20 %}
ds18b20 = "/sys/bus/w1/devices/{{ ds18b20_id }}/w1_slave"
{% endif %}

# RPi software SPI:
SCLK = 17
DIN = 18
DC = 27
RST = 23
CS = 22
disp = LCD.PCD8544(DC, RST, SCLK, DIN, CS)
disp.begin(contrast=60)
disp.clear()

fuckinhot = Image.new('1', (LCD.LCDWIDTH, LCD.LCDHEIGHT))
draw = ImageDraw.Draw(fuckinhot)

# http://www.dafont.com/minecraftia.font
font = ImageFont.truetype(path+'/Minecraftia-Regular.ttf', 8)

{% if ds18b20_override_gpio %}
# Power
gpio=GPIO.get_platform_gpio()
gpio.setup({{ ds18b20_gpio_vcc }}, GPIO.OUT)
gpio.set_high({{ ds18b20_gpio_vcc }})
{% endif %}

# Data
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
	if equals_pos != -1:
		temp_string = lines[1][equals_pos+2:]
		temp = float(temp_string) / 1000.0
		return round(temp, 2)

# loop
while True:
	t = []
{% if use_zabbix %}
	temp = z.item.get(itemids=(zbxitemid))
	t.append(round(float(temp[0]["lastvalue"]), 2))
{% endif %}
{% if use_ds18b20 %}
	t.append(read_temp())
{% endif %}

	fuckinhot = Image.open(pic_normal).convert('1')
	for i in t:
		if i >= threshold_hot:
			fuckinhot = Image.open(pic_fuckinhot).convert('1')
		if i < threshold_cold:
			fuckinhot = Image.open(pic_samui).convert('1')
	draw = ImageDraw.Draw(fuckinhot)

	y = 0
	for i in t:
		draw.rectangle((50,y+1,84,y+8), outline=255, fill=255)
		draw.text((50,y), '%05s' % (i) + 'C', font=font)
		y += 8

	d = datetime.datetime.today()
	draw.rectangle((0,0,24,8), outline=255, fill=255)
	draw.text((0,0), '%02d:%02d' % (d.hour, d.minute), font=font)

	disp.image(fuckinhot)
	disp.display()
	time.sleep(10.0)
