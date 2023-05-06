#!/usr/bin/env python3
# coding: utf-8

import os
from time import localtime
import urllib.request
import json
from PIL import Image, ImageDraw, ImageFont
from inky import InkyPHAT

path = os.path.dirname(__file__)
fontpath = '/usr/share/fonts/truetype'

# Kanagawa
area_code = "140000"
# East
area_sub_code = "140010"
# Yokohama-shi
area_city_code = "46106"

# 天気コードをアイコンに変えるためのやつ
# 0: 晴れ
# 1: 曇り
# 2: 雨
# 3: 雪
weather_codes = {100: 0, 101: 0, 102: 2, 103: 2, 104: 3, 105: 3, 106: 2, 107: 2, 108: 2, 110: 0, 111: 0, 112: 2, 113: 2, 114: 2, 115: 3, 116: 3, 117: 3, 118: 2, 119: 2, 120: 2, 121: 2, 122: 2, 123: 0, 124: 0, 125: 2, 126: 2, 127: 2, 128: 2, 130: 0, 131: 0, 132: 0, 140: 2, 160: 3, 170: 3, 181: 3, 200: 1, 201: 1, 202: 2, 203: 2, 204: 3, 205: 3, 206: 2, 207: 2, 208: 2, 209: 1, 210: 1, 211: 1, 212: 2, 213: 2, 214: 2, 215: 3, 216: 3, 217: 3, 218: 2, 219: 2, 220: 2, 221: 2, 222: 2, 223: 1, 224: 2, 225: 2, 226: 2, 228: 3, 229: 3, 230: 3, 231: 1, 240: 2, 250: 3, 260: 3, 270: 3, 281: 3, 300: 2, 301: 2, 302: 2, 303: 3, 304: 2, 306: 2, 308: 2, 309: 3, 311: 2, 313: 2, 314: 3, 315: 3, 316: 2, 317: 2, 320: 2, 321: 2, 322: 3, 323: 2, 324: 2, 325: 2, 326: 3, 327: 3, 328: 2, 329: 2, 340: 3, 350: 2, 361: 3, 371: 3, 400: 3, 401: 3, 402: 3, 403: 3, 405: 3, 406: 3, 407: 3, 409: 3, 411: 3, 413: 3, 414: 3, 420: 3, 421: 3, 422: 3, 423: 3, 425: 3, 426: 3, 427: 3, 450: 3}

# 天気アイコン
statuses = ['sunny', 'cloudy', 'rain', 'snow']

# 夜の回は明日の天気を出したい
if 20 <= localtime().tm_hour:
  title = "あしたのてんき"
  day = 1
else:
  title = "きょうのてんき"
  day = 0

# APIから天気情報をもらってくる
url = "https://www.jma.go.jp/bosai/forecast/data/forecast/%s.json" % area_code
#print(url)
req = urllib.request.Request(url)
with urllib.request.urlopen(req) as res:
  body = res.read()
json = json.loads(body)

# ループ
for i in json:
  for j in i['timeSeries']:
    # 出力順序は変わらないと信じてるけど信じてないので必要なさそうな回はパス
    if 4 < len(j['timeDefines']):
      continue
    # 使えそうな回はareasでループ
    for area in j["areas"]:
      # 今日明日の天気が含まれる回。発表元と発表時刻はここで見ることにする
      if area['area']['code'] == area_sub_code:
        if "weatherCodes" in area:
          data_from = "%s発表" % i['publishingOffice']
          forecast_date = i['reportDatetime'].replace('T', ' ').replace('-','/').split(':00+')[0]
          weather_code = weather_codes[int(area["weatherCodes"][day])]
          status = statuses[weather_code]
      # 今日明日の気温が含まれる回
      if area['area']['code'] == area_city_code:
        if "temps" in area:
          # 夜は1セットしかないので固定でOK
          min = "-" if area["temps"][0] == area["temps"][1] else area["temps"][0]
          temp_max = u"%s℃" % (area["temps"][1])
          temp_min = u"%s℃" % (min)

# -------------------------
#  Draw to Inky pHAT
# -------------------------

display = InkyPHAT('red')
display.set_border(display.BLACK)
img = Image.open(os.path.join(path, "tenki-base.png"))
status_img = Image.open(os.path.join(path, "%s.png" % status))
img.paste(status_img, box=(0, 26))
draw = ImageDraw.Draw(img)

font = ImageFont.truetype(os.path.join(fontpath, "x14y24pxHeadUpDaisy.ttf"), 24)
draw.text((4, -3), title, 2, font=font)
draw.text((3, -4), title, 0, font=font)
draw.text((10, 75), temp_max, 2, font=font)
draw.text((10, 75), "   /%s" % temp_min, 0, font=font)

font2 = ImageFont.truetype(os.path.join(fontpath, "vlgothic/VL-Gothic-Regular.ttf"), 12)
draw.text((105, -3), data_from, 0, font=font2)

font3 = ImageFont.truetype(os.path.join(fontpath, "x8y12pxTheStrongGamer.ttf"), 12)
draw.text((105, 8), forecast_date, 0, font=font3)

display.set_image(img)
display.show()

with open(os.path.join(path, 'tenki.txt'), 'w') as f:
  print(status, file=f)
  print(temp_max, file=f)
  print(temp_min, file=f)
