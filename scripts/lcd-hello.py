#!/usr/bin/env python3
# coding: utf-8

import RPi.GPIO as GPIO
import smbus
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

class LCD():
    def __init__(self, addr = 0x3e, contrast = 0x5e, light_pin = False):
        self.addr      = addr
        self.contrast  = contrast
        self.light_pin = light_pin
        self.bus       = smbus.SMBus(1)

        if self.light_pin:
            GPIO.setup(self.light_pin,GPIO.OUT)

    def reset(self):
        self.bus.write_block_data(self.addr, 0, [0x38, 0x39, 0x14, 0x78, self.contrast, 0x6c])
        sleep(0.25)
        self.bus.write_block_data(self.addr, 0, [0x0c, 0x01, 0x06])
        sleep(0.25)

    def clear(self):
        self.bus.write_block_data(self.addr, 0, [1])

    def set_cursor(self, x, y):
        self.bus.write_byte_data(self.addr, 0, 128 + 64 * y + x)

    def print(self, string):
        s = string.encode('shift_jis')
        for x in s:
            self.bus.write_byte_data(self.addr, 0x40, x)

    def light(self, value):
        if self.light_pin:
            GPIO.output(self.light_pin, value)

if __name__ == '__main__':
    # For Switch Science i2c miniLCD
    #  https://www.switch-science.com/catalog/1405/
    #  contrast = 0x5d
    #  no light_pin
    # lcd = LCD(contrast = 0x5d)

    # For Strawberry Linux SB1602BW (default)
    #  https://strawberry-linux.com/catalog/items?code=27021
    #  contrast = 0x5e
    #  light_pin = 7
    lcd = LCD(light_pin = 4)

    lcd.reset()
    lcd.clear()

    lcd.set_cursor(0, 0)
    lcd.print("Hello!")
    lcd.set_cursor(2, 1)
    lcd.print("World!")

    i = 0
    try:
        while True:
            i = 1 - i
            lcd.light(i)
            sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        lcd.clear()
        GPIO.cleanup()