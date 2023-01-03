import board
import busio
import digitalio
import adafruit_ssd1306
import uhat_porter_pico_type_p as board_bcm
import time

show_rssi = True

i2c = busio.I2C(board_bcm.BCM3, board_bcm.BCM2)
uart = busio.UART(board_bcm.BCM14, board_bcm.BCM15, baudrate=9600)

display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
display.rotate(180)
display.fill(0)
display.show()

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
    if uart.in_waiting:
        payload = payload + uart.read(uart.in_waiting)
    else:
        if len(payload) < 1:
            continue
        display.fill_rect(0, 0, 127, 30, 0)
        display.text('DATA: %s'%payload, 0, 0, 1)
        if show_rssi:
            rssi = int(payload[-1]) - 256
            display.text(f"RSSI: {rssi} dBm", 0, 10, 1)
        display.text("RECEIVED: %s"%now_str, 0, 20, 1)
        payload = bytes()
    display.fill_rect(0, 30, 127, 8, 0)
    display.text("NOW: %s"%now_str, 0, 30, 1)
    display.show()