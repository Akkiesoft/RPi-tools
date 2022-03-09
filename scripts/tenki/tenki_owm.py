#!/usr/bin/env python
# coding: utf-8

from PIL import Image
import inkyphat
import pyowm
import os
import datetime
from pytz import timezone

path = '/home/pi/tenki/'

#inkyphat.set_colour('red')
inkyphat.set_border(inkyphat.BLACK)
inkyphat.set_image(Image.open(path+"tenki-base.png"))

jst = timezone('Asia/Tokyo')
now = datetime.datetime.now(jst)
tomorrow = now + datetime.timedelta(days = 1)

owm = pyowm.OWM('')
fc = owm.daily_forecast("Machida,JP", limit=2)
forecasts = fc.get_forecast().get_weathers()
title = u"きょうのてんき"
for forecast in forecasts:
  forcast_date = forecast.get_reference_time(timeformat='date').astimezone(jst)
  # 夜の回は明日の天気を出したい
  if (now.hour >= 22):
    title = u"あしたのてんき"
    if (tomorrow.day != forcast_date.day):
      continue
  forcast_date_str = str(forcast_date).split(' ')[0].replace('-','/')
  status = forecast.get_status()
  temp = forecast.get_temperature(unit='celsius')
  temp_max = u"%s℃" % (int(round(temp['max'])))
  temp_min = u"   /%s℃" % (int(round(temp['min'])))
  break

status_img = Image.open(path+status+".png")
inkyphat.paste(status_img, box=(0,26))

font = inkyphat.ImageFont.truetype(path+"x14y24pxHeadUpDaisy.ttf", 24)
inkyphat.text((4, -3), title, 2, font=font)
inkyphat.text((3, -4), title, 0, font=font)
inkyphat.text((10, 75), temp_max, 2, font=font)
inkyphat.text((10, 75), temp_min, 0, font=font)

font2 = inkyphat.ImageFont.truetype(path+"x8y12pxTheStrongGamer.ttf", 12)
inkyphat.text((110, 8), forcast_date_str, 0, font=font2)

inkyphat.show()

