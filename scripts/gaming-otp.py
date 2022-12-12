#!/usr/bin/env python3

# Show OTP using Pimoroni Unicorn HAT Mini( https://shop.pimoroni.com/products/unicorn-hat-mini )
#
# Based on:
# * https://github.com/pimoroni/unicornhatmini-python/blob/master/examples/text.py
# * https://github.com/pimoroni/unicornhatmini-python/blob/master/examples/button-splash.py
#
# Required libraries (run following command):
# $ pip3 install gpiozero unicornhatmini pyotp
#
# 2020 Akkiesoft ( Mastodon: @Akkiesoft@social.mikutter.hachune.net )

import time
import sys

import pyotp
import datetime

from colorsys import hsv_to_rgb
from PIL import Image, ImageDraw, ImageFont
from unicornhatmini import UnicornHATMini
from gpiozero import Button

otp = 0
image = 0
offset_x = 0

# SECRETS for OTP
button_map = {5: "",
              6: "",
              16: "",
              24: ""}

# init buttons
button_a = Button(5)
button_b = Button(6)
button_x = Button(16)
button_y = Button(24)

# init Unicorn HAT Mini
unicornhatmini = UnicornHATMini()
unicornhatmini.set_rotation(0)
unicornhatmini.set_brightness(0.03)
display_width, display_height = unicornhatmini.get_shape()
# font
font = ImageFont.truetype("/home/pi/Minecraftia-Regular.ttf", 8)

def pressed(button):
    global image, otp

    print(f"Button {button.pin.number} pressed!")
    if button_map[button.pin.number] == "":
        # OTP is not set
        print("OTP is not set.")
        return
    if otp:
        print("Please wait to finish to drawing current OTP.")
        return

    totp = pyotp.TOTP(button_map[button.pin.number])
    time_remaining = int("{:.0f}".format(totp.interval - datetime.datetime.now().timestamp() % totp.interval))
    if time_remaining < 5:
        # 期限切れが5秒以内なら次を待つ
        unicornhatmini.set_pixel(0, 0, 255, 0, 0)
        unicornhatmini.show()
        print("OTP expire soon. So waiting the next OTP({:d} sec)".format(time_remaining + 1))
        time.sleep(time_remaining + 1)
        unicornhatmini.set_pixel(0, 0, 0, 0, 0)
        unicornhatmini.show()
    # OTPの取得
    otp = totp.now()
    # 描画データの用意
    text_width, text_height = font.getsize(otp)
    image = Image.new('P', (text_width + display_width * 2, display_height), 0)
    draw = ImageDraw.Draw(image)
    draw.text((display_width, -2), otp, font=font, fill=255)

try:
    button_a.when_pressed = pressed
    button_b.when_pressed = pressed
    button_x.when_pressed = pressed
    button_y.when_pressed = pressed

    while True:
        if otp:
            for y in range(display_height):
                for x in range(display_width):
                    hue = (time.time() / 10.0) + (x / float(display_width * 2))
                    r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, 1.0, 1.0)]
                    if image.getpixel((x + offset_x, y)) == 255:
                        unicornhatmini.set_pixel(x, y, r, g, b)
                    else:
                        unicornhatmini.set_pixel(x, y, 0, 0, 0)
            unicornhatmini.show()
            offset_x += 1
            if offset_x + display_width > image.size[0]:
                offset_x = 0
                otp = 0
            time.sleep(0.1)
        else:
            time.sleep(1)
except KeyboardInterrupt:
    button_a.close()
    button_b.close()
    button_x.close()
    button_y.close()
