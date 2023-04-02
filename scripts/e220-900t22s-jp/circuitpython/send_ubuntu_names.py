import board
import busio
import digitalio
import uhat_porter_pico_type_p as board_bcm
import time
import random

target_address = 0
target_channel = 0
send_strings = [
    "Warty Warthog",
    "Hoary Hedgehog",
    "Breezy Badger",
    "Dapper Drake",
    "Edgy Eft",
    "Feisty Fawn",
    "Gutsy Gibbon",
    "Hardy Heron",
    "Intrepid Ibex",
    "Jaunty Jackalope",
    "Karmic Koala",
    "Lucid Lynx",
    "Maverick Meerkat",
    "Natty Narwhal",
    "Oneiric Ocelot",
    "Precise Pangolin",
    "Quantal Quetzal",
    "Raring Ringtail",
    "Saucy Salamander",
    "Trusty Tahr",
    "Utopic Unicorn",
    "Vivid Vervet",
    "Wily Werewolf",
    "Xenial Xerus",
    "Yakkety Yak",
    "Zesty Zapus",
    "Artful Aardvark",
    "Bionic Beaver",
    "Cosmic Cuttlefish",
    "Disco Dingo",
    "Eoan Ermine",
    "Focal Fossa",
    "Groovy Gorilla",
    "Hirsute Hippo",
    "Impish Indri",
    "Jammy Jellyfish",
    "Kinetic Kudu",
    "⁠Lunar Lobster"
]

uart = busio.UART(board_bcm.BCM14, board_bcm.BCM15, baudrate=9600)

"""
# for oled
import adafruit_ssd1306
i2c = busio.I2C(board_bcm.BCM3, board_bcm.BCM2)
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

led = digitalio.DigitalInOut(board.GP25)
led.direction = digitalio.Direction.OUTPUT

btn = digitalio.DigitalInOut(board_bcm.BCM17)
btn.switch_to_input(pull=digitalio.Pull.UP)

t_addr_H = target_address >> 8
t_addr_L = target_address & 0xFF
addr_ch = bytes([t_addr_H, t_addr_L, target_channel])

while True:
    if not btn.value:
        now = time.localtime()
        now_str = "{:02}:{:02}:{:02}".format(now.tm_hour, now.tm_min, now.tm_sec)
        a = random.choice(send_strings)
        payload = addr_ch + a + "\n".encode()
        led.value = 1
        uart.write(payload)
        print("SENDED: %s (%s)" % (a, now_str))
        led.value = 0
        time.sleep(0.5)
