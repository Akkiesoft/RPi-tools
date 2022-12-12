#!/usr/bin/python3

from sense_hat import SenseHat
import math
import time

sense = SenseHat()
sense.clear()

ox = 0
oy = 0

while True:
  raw = sense.accel_raw
  px = int(math.floor(raw['x'] * 20 + 4))
  py = int(math.floor(raw['y'] * 20 + 4))
  print(px,py)
  if px < 0 or 7 < px or py < 0 or 7 < py:
    sense.clear(128, 0, 0)
    time.sleep(3)
    sense.clear()
    continue
  sense.set_pixel(ox, oy, 0, 0, 0)
  sense.set_pixel(px, py, 0, 255, 255)
  ox = px
  oy = py
  #time.sleep(0.1)
