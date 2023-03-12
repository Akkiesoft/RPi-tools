#!/usr/bin/env python3
# coding: utf-8

# IC balance checker for Python / 2023 @Akkiesoft
#   MIT License
#   Original: https://github.com/Akkiesoft/RPi-tools/blob/master/scripts/lcd-icreader.rb
#   references:
#     http://hito.music.coocan.jp/pasori/libpafe.html
#     http://iccard.jennychan.at-ninja.jp/format/
#     https://thinkami.hatenablog.com/entry/2015/06/16/212600
#     https://qiita.com/Imagawayaki/items/23844281cf53156a196f

from __future__ import print_function
from ctypes import *
from time import sleep
import RPi.GPIO as GPIO
import smbus

class LCD():
    def __init__(self, addr = 0x3e, contrast = 0x5e, light_pin = False, beep_pin = False):
        self.addr      = addr
        self.contrast  = contrast
        self.light_pin = light_pin
        self.beep_pin  = beep_pin
        self.bus       = smbus.SMBus(1)
        if self.light_pin:
            GPIO.setup(self.light_pin,GPIO.OUT)
        if self.beep_pin:
            GPIO.setup(self.beep_pin, GPIO.OUT)

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

    def beep(self):
        if self.beep_pin:
            GPIO.output(self.beep_pin, 1)
            sleep(0.1)
            GPIO.output(self.beep_pin, 0)
            sleep(0.025)
            GPIO.output(self.beep_pin, 1)
            sleep(0.1)
            GPIO.output(self.beep_pin, 0)

FELICA_POLLING_ANY = 0xffff
FELICA_POLLING_EDY = 0xfe00
int_array16 = c_uint8 * 16
class felica_block_info(Structure):
    _fields_ = [
        ("service", c_uint16),
        ("mode",    c_uint8 ),
        ("block",   c_uint16)
    ]

card_list = {
      3: { 'name': 'Suica',  'balance_code': 0x008B },
  32990: { 'name': 'Iruca',  'balance_code': 0x008B },
  33007: { 'name': 'Ica',    'balance_code': 0x898F },
  34194: { 'name': 'PASPY',  'balance_code': 0x008B },
  34398: { 'name': 'SAPICA', 'balance_code': 0x008B, 'point_code': 0xBA4B },
  36801: { 'name': 'Okica',  'balance_code': 0x028F },
   1223: { 'name': 'nanaco', 'balance_code': 0x5597, 'point_code': 0x560B },
   4860: { 'name': 'WAON',   'balance_code': 0x6817, 'point_code': 0x684B },
  33134: { 'name': 'WAON',   'balance_code': 0x6817, 'point_code': 0x684B },
  65024: { 'name': 'WAON',   'balance_code': 0x6817, 'point_code': 0x684B },
  32898: { 'name': 'Edy',    'balance_code': 0x1317 },
}

def get_card_type(felica):
    # (Ruby版のコードを読みつつもわからんので)雰囲気でやっている
    data = c_uint16()
    n = c_int(sizeof(data))
    r = libpafe.felica_request_system(felica, byref(n), byref(data))
    if r:
        return None
    return data.value

def read_block(felica, code, block = 0, dump = False):
    data = int_array16()
    info = felica_block_info(c_uint16(code), c_uint8(0), c_uint16(block))
    libpafe.felica_read(felica, byref(c_int(1)), byref(info), byref(data))
    if dump:
        for c,i in enumerate(data):
            print(c, hex(i))
    return data

def read_traffic_balance(felica):
    point = None
    data = read_block(felica, card['balance_code'])
    balance = data[13] << 16 | data[12] << 8 | data[11]
    if 'point_code' in card:
        data = read_block(felica, card['point_code'])
        if card['name'] == 'SAPICA':
            point = data[2] | data[1] | data[0]
    return (balance, point)

def read_okica(felica):
    data = read_block(felica, card['balance_code'])
    balance = data[11] << 8 | data[10]
    return balance

def read_ica(felica):
    data = read_block(felica, card['balance_code'])
    balance = data[13] << 8 | data[14]
    return balance

def read_nanaco():
    felica2 = libpafe.felica_polling(pasori, FELICA_POLLING_EDY, 0, 0)
    data = read_block(felica2, card['balance_code'])
    balance = data[3] << 24 | data[2] << 16 | data[1] << 8 | data[0]
    data = read_block(felica2, card['balance_code'], block=1)
    point = (data[0] << 16 | data[1] << 8 | data[2]) + (data[5] << 16 | data[6] << 8 | data[7])
    return (balance, point)

def read_waon():
    felica2 = libpafe.felica_polling(pasori, FELICA_POLLING_EDY, 0, 0)
    data = read_block(felica2, card['balance_code'])
    balance = data[1] << 8 | data[0]
    data = read_block(felica2, card['point_code'])
    point = data[0] << 16 | data[1] << 8 | data[2]
    return (balance, point)

def read_edy():
    felica2 = libpafe.felica_polling(pasori, FELICA_POLLING_EDY, 0, 0)
    data = read_block(felica2, card['balance_code'])
    balance = data[3] << 24 | data[2] << 16 | data[1] << 8 | data[0]
    return balance

def read_card(felica, card):
    balance = None
    point = None
    if card['balance_code'] == 0x008B:
        balance,point = read_traffic_balance(felica)
    if card['balance_code'] == 0x028F:
        balance = read_okica(felica)
    if card['balance_code'] == 0x898F:
        balance = read_ica(felica)
    if card['balance_code'] == 0x5597:
        balance,point = read_nanaco()
    if card['balance_code'] == 0x6817:
        balance,point = read_waon()
    if card['balance_code'] == 0x1317:
        balance = read_edy()
    return (balance, point)

def lcd_ready(lcd):
    lcd.light(0)
    lcd.clear()
    lcd.print("Please touch IC.")

if __name__ == '__main__':
    libpafe = cdll.LoadLibrary("/usr/local/lib/libpafe.so")
    libpafe.pasori_open.restype = c_void_p
    libpafe.felica_polling.restype = c_void_p

    pasori = libpafe.pasori_open()
    libpafe.pasori_init(pasori)

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    lcd = LCD(light_pin = 4, beep_pin = 26)
    lcd.reset()
    lcd_ready(lcd)

    try:
        while True:
            # ポーリング
            felica = libpafe.felica_polling(pasori, FELICA_POLLING_ANY, 0, 0)
            if not felica:
                sleep(1)
                continue
            # カードの種類の特定
            card_type = get_card_type(felica)
            if card_type is None:
                sleep(1)
                continue
            card = card_list[card_type] if card_type in card_list else { 'name': 'unknown', 'balance_code': 0 }
            # 残高とポイント読み出し
            balance,point = read_card(felica, card)
            # 結果の表示
            lcd.light(1)
            lcd.clear()
            lcd.print("%s ｻﾞﾝﾀﾞｶ" % card['name'])
            lcd.set_cursor(0, 1)
            if not balance is None:
                lcd.print("¥%s" % balance)
            if point:
                lcd.print("/%spts" % point)
            lcd.beep()
            # 次へ
            sleep(5)
            lcd_ready(lcd)
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()