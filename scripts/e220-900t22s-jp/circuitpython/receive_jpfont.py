import board
import busio
import digitalio
import adafruit_ssd1306
import uhat_porter_pico_type_p as board_bcm
import time

import displayio
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font

show_rssi = True

i2c = busio.I2C(board_bcm.BCM3, board_bcm.BCM2)
uart = busio.UART(board_bcm.BCM14, board_bcm.BCM15, baudrate=9600)

display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
display.rotate(180)
display.fill(0)
display.show()

font_file = "/misaki_gothic.bdf"
font = bitmap_font.load_font(font_file)

# Init M0,M1 pin to NORMAL mode
m = [[board_bcm.BCM27, False], [board_bcm.BCM22, False]]
for i in m:
    mm = digitalio.DigitalInOut(i[0])
    mm.direction = digitalio.Direction.OUTPUT
    mm.value = i[1]

splash = displayio.Group()
txt_now = label.Label(font, text="", color=0xFFFFFF)
txt_now.x = 0
txt_now.y = 0
splash.append(txt_now)
txt_rsv = label.Label(font, text="", color=0xFFFFFF)
txt_rsv.x = 0
txt_rsv.y = 10
splash.append(txt_rsv)
txt_dat = label.Label(font, text="", color=0xFFFFFF)
txt_dat.x = 0
txt_dat.y = 20
splash.append(txt_dat)
txt_rssi = label.Label(font, text="", color=0xFFFFFF)
txt_rssi.x = 0
txt_rssi.y = 30
splash.append(txt_rssi)
display.show(splash)

payload = bytes()
while True:
    now = time.localtime()
    now_str = "{:02}:{:02}:{:02}".format(now.tm_hour, now.tm_min, now.tm_sec)
    display.fill_rect(0, 0, 127, 8, 0)
    txt_now.text = "NOW: %s" % now_str
    if uart.in_waiting:
        payload = payload + uart.read(uart.in_waiting)
    else:
        if len(payload) < 1:
            time.sleep(0.01)
            continue
        txt_rsv.text = "RECEIVED: %s" % now_str
        data = payload.split(b'\n')[0].decode('utf-8')
        txt_dat.text = 'DATA: %s' % data
        if show_rssi:
            rssi = int(payload[-1]) - 256
            txt_rssi.text = f"RSSI: {rssi} dBm"
        payload = bytes()