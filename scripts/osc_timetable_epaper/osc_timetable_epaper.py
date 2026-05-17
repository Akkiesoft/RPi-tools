#!/usr/bin/env python3
# coding: utf-8
# SPDX-FileCopyrightText: 2026 Akkiesoft a.k.a. Akira Ouchi <akkiesoft@marokun.net>
# SPDX-License-Identifier: MIT

"""
OSCのタイムテーブルをPimoroni Inky pHATに表示するデモ
"""

import os
from time import localtime
import urllib.request
import json
from PIL import Image, ImageDraw, ImageFont
from unicodedata import east_asian_width
from mojimoji import zen_to_han

# 電子ペーパーではなくpng画像に出力する時はTrueにする
png_mode = True

# OSCのタイムテーブルのURL
# Q: このOSCのタイムテーブルのJSONって使っていいんですか？
# A: いいよ（私がこれのために作ったため）
osc = "osc2026-nagoya"
day = "1"
url = "https://event.ospn.jp/%s/session/timetable.json?day=%s" % (osc, day)

# フォントの設定（縦12pxのフォントを想定）
# x12y12pxMaruMinya: https://hicchicc.github.io/00ff/
font = ImageFont.truetype("x12y12pxMaruMinya.ttf", 12)

# JSONを取得
req = urllib.request.Request(url)
with urllib.request.urlopen(req) as res:
  body = res.read()
data = json.loads(body)

now = localtime()
hour = now.tm_hour

# 雑に補正
if hour < 10 or 17 < hour:
    hour = 10

# Based on: https://note.nkmk.me/python-unicodedata-east-asian-width-count/
def get_east_asian_width_count(text):
    count = 0
    for c in text:
        if east_asian_width(c) in 'FWA':
            count += 12
        else:
            count += 6
    return count

if not png_mode:
    #  Draw to Inky pHAT
    from inky.auto import auto
    display = auto()
    display.set_border(display.BLACK)
    image_mode = "P"
else:
    image_mode = "RGB"
    class InkyPallet():
        def __init__(self):
            self.BLACK  = (  0,   0,   0)
            self.RED    = (255,   0,   0)
            self.YELLOW = (255, 255,   0)
            self.WHITE  = (255, 255, 255)
    display = InkyPallet()

img = Image.new(image_mode, (250, 122), display.WHITE)
draw = ImageDraw.Draw(img)

draw.rectangle([(0, 0), (250, 12)], display.BLACK)
draw.text((2, 0), "%s %s日目 %s時のセミナー" % (data['site_name'], day, hour), display.WHITE, font=font)

y = 15
for t in data['timetable']:
    timeframe = int(t['start'].split(':')[0])
    if timeframe != hour:
        continue
    output = ""
    for s in t['sessions']:
        # OSC名古屋向けハードコーディング
        room = zen_to_han("%s" % s['room']).replace('展示会場内 ', '')[0:-4]
        room_length = get_east_asian_width_count(room)
        floor = s['room'][-3:-1]
        floor_length = get_east_asian_width_count(floor)

        line = y + 12
        # フロア
        draw.rectangle([(0, y), (floor_length, line)], display.RED)
        # 部屋
        draw.rectangle([(floor_length, y), (floor_length + room_length, line)], display.YELLOW)
        # 下線
        draw.line([(0, line + 1), (250, line + 1)], display.BLACK, width=1)
        # 文字
        draw.text((0, y), floor, display.WHITE, font=font)
        draw.text((floor_length + 1, y), room, display.BLACK, font=font)
        if (not s['room_empty']):
            draw.text((floor_length + room_length + 1, y), zen_to_han("%s" % s['title']), display.BLACK, font=font)
        # 次の行へ
        y += 14
    break

if png_mode:
    img.save("result.png")
else:
    display.set_image(img)
    display.show()
