#!/usr/bin/env python

from microdotphat import set_pixel, write_string, scroll_vertical, scroll_to, clear, show
import time

def write_nishi(offset_x=0, offset_y=0):
    nishi = [0x7D, 0x4F, 0x45, 0x4F, 0x7D]
    write_customchar(nishi, offset_x=offset_x, offset_y=offset_y)

def write_kokudaland(offset_x=0, offset_y=0):
    font = [[
        0x00, 0x62, 0x42, 0x42, 0x46],[ # ko
        0x00, 0x18, 0x24, 0x42, 0x00],[ # ku
        0x44, 0x3E, 0x54, 0x56, 0x55],[ # da
        0x00, 0x4A, 0x4A, 0x2A, 0x1A],[ # la
        0x00, 0x44, 0x44, 0x20, 0x1E],[ # n
        0x00, 0x7E, 0x08, 0x12, 0x11]   # d
    ]
    for (i, char) in enumerate(font):
        write_customchar(char, offset_x=i*8+offset_x, offset_y=offset_y)

def write_customchar(char, offset_x=0, offset_y=0):
    for x in range(5):
        for y in range(7):
            p = (char[x] & (1 << y)) > 0
            set_pixel(offset_x + x, offset_y + y, p)


write_kokudaland()
write_nishi(offset_y=7)
write_string("g-17a", offset_x=8, offset_y = 7, kerning=False)
show()

while True:
    time.sleep(5)
    for i in range(7):
        scroll_vertical()
        show()
        time.sleep(0.05)
