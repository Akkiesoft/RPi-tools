# The script that showing PNG image for waveshare 2.13 Inch e-Paper module. 

import time
import spidev as SPI
import EPD_driver
import datetime
from PIL import Image

xDot = 122
yDot = 250
DELAYTIME = 4

bus = 0
device = 0

# PNG image must be palette mode. Image size is 250x122.
# Palette  0: white, 1: black
image = Image.open("image.png")
size = image.size

data = []
for x in range(size[0]):
    for by in range(size[1] / 8 + 1):
        block = 0
        for y in range(8):
           block = block << 1
           try:
               pixel = 1 - image.getpixel((x, by * 8 + y))
               block = block | pixel
           except:
               pass
        data.append(int(block))

disp = EPD_driver.EPD_driver(spi=SPI.SpiDev(bus, device))
disp.Dis_Clear_full()
disp.Dis_full_pic(data)