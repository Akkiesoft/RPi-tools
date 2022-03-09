#!/usr/bin/env python3
# coding: utf-8

from datetime import datetime, timezone, timedelta
from requests_oauthlib import OAuth1Session
from PIL import Image
import inkyphat

path = '/home/pi/tenki/'
fontpath = '/usr/share/fonts/truetype/'
location = 'Yokohama-shi,JP'

# https://developer.yahoo.com/weather/
CONSUMER_KEY = ''
CONSUMER_SECRET = ''


# -------------------------
#  Get weather from Yahoo!
# -------------------------

y = OAuth1Session(CONSUMER_KEY, client_secret=CONSUMER_SECRET)
baseurl = "https://weather-ydn-yql.media.yahoo.com/forecastrss"
q = {
  'location': location,
  'u': 'c',
  'format': 'json'
}
r = y.get(baseurl, params = q)
data = r.json()

# 夜の回は明日の天気を出したい
now = datetime.now()
if (now.hour >= 22):
  title = u"あしたのてんき"
  w = data['forecasts'][1]
else:
  title = u"きょうのてんき"
  w = data['forecasts'][0]

temp_max = u"%s℃" % (w['high'])
temp_min = u"   /%s℃" % (w['low'])
JST = timezone(timedelta(hours=+9), 'JST')
d = datetime.fromtimestamp(w['date'], JST)
forcast_date_str = d.strftime("%Y/%m/%d")

# https://developer.yahoo.com/weather/documentation.html#codes
# 多すぎて全部書けないのでざっくりまとめる
weather_code = int(w['code'])
if weather_code in [31, 32, 33, 34]:
  status = 'sunny'
if weather_code in [25]:
  # cold (TBD)
  status = 'sunny'
if weather_code in [36]:
  # hot (TBD)
  status = 'sunny'
if weather_code in [19, 21, 26, 27, 28, 29, 30, 44]:
  status = 'cloudy'
if weather_code in [6, 10, 35, 8, 9, 10, 11, 12, 20, 22, 40, 47, 3, 4, 37, 38, 39, 45]:
  status = 'rain'
if weather_code in [5, 7, 13, 14, 15, 16, 18, 41, 42, 43, 46, 17, 35]:
  status = 'snow'
#if weather_code in [0, 1, 2, 23, 24]:
#  status = 'wind'


# -------------------------
#  Draw to Inky pHAT
# -------------------------

# Comment out only V1
# inkyphat.set_colour('red') 
inkyphat.set_border(inkyphat.BLACK)
inkyphat.set_image(Image.open(path + "tenki-base.png"))
status_img = Image.open(path + status + ".png")
inkyphat.paste(status_img, box=(0, 26))

font = inkyphat.ImageFont.truetype(fontpath + "x14y24pxHeadUpDaisy.ttf", 24)
inkyphat.text((4, -3), title, 2, font=font)
inkyphat.text((3, -4), title, 0, font=font)
inkyphat.text((10, 75), temp_max, 2, font=font)
inkyphat.text((10, 75), temp_min, 0, font=font)

font2 = inkyphat.ImageFont.truetype(fontpath + "x8y12pxTheStrongGamer.ttf", 12)
inkyphat.text((110, -3), location.split(',')[0], 0, font=font2)
inkyphat.text((110, 8), forcast_date_str, 0, font=font2)

inkyphat.show()
