#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
from socket import gethostname
import Image
import ImageDraw
import ImageFont

disp = Adafruit_SSD1306.SSD1306_128_64(rst=24)
disp.begin()
disp.clear()
disp.display()

width = disp.width
height = disp.height
image = Image.new('1', (width, height))
draw = ImageDraw.Draw(image)

font = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 20)
draw.text((0, 0), "Hostname:\n%s" % gethostname(),  font=font, fill=255)

disp.image(image)
disp.display()
