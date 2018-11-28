#!/usr/bin/env python
# coding: UTF-8

from io import BytesIO
import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# ディスプレイの初期化
disp = Adafruit_SSD1306.SSD1306_128_64(rst=None)
disp.begin()
disp.clear()
disp.display()
width = disp.width
height = disp.height

# PILのイメージを作成
image = Image.new('1', (width, height))

# PILイメージに描画
draw = ImageDraw.Draw(image)
fpath = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font = ImageFont.truetype(fpath, 12)
draw.text((0,0), "Hello, World!", font=font, fill=255)
draw.line((80,0,128,40), fill=255)
draw.line((80,40,128,0), fill=255)
draw.rectangle((38,40,112,58), outline=0, fill=255)
draw.text((40,40), "Hello, World!", font=font, fill=0)

# 描画結果を有機ELディスプレイに送って表示
disp.image(image)
disp.display()
