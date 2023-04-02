import board
import busio
import digitalio
import adafruit_ssd1306
import uhat_porter_pico_type_s as board_bcm
import time

show_rssi = True

#i2c = busio.I2C(board_bcm.BCM3, board_bcm.BCM2)
uart = busio.UART(board_bcm.BCM14, board_bcm.BCM15, baudrate=9600)

"""
display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
display.rotate(180)
display.fill(0)
display.show()
"""

# Init M0,M1 pin to NORMAL mode
m = [[board_bcm.BCM27, False], [board_bcm.BCM22, False]]
for i in m:
    mm = digitalio.DigitalInOut(i[0])
    mm.direction = digitalio.Direction.OUTPUT
    mm.value = i[1]

payload = bytes()
while True:
    now = time.localtime()
    now_str = "{:02}:{:02}:{:02}".format(now.tm_hour, now.tm_min, now.tm_sec)
    payload = now_str.encode()
    uart.write(payload)
    uart.flush()
    time.sleep(3)