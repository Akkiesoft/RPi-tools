#!/usr/bin/env python
import skywriter
import signal
from mcpi.minecraft import Minecraft

mc = Minecraft.create()
touch = 0

@skywriter.move()
def move(x, y, z):
  global touch
  mx = x * 256 - 128.5
  my = y * 256 - 128.5
  mz = 36
#  mz = z * 40
  if touch:
    mc.camera.setPos(my, mz, mx)

@skywriter.touch()
def touch(position):
  global touch
  if touch:
    touch = 0
    mc.postToChat("set camera mode to normal")
    mc.camera.setNormal()
  else:
    touch = 1
    mc.postToChat("set camera mode to fixed")
    mc.camera.setFixed()

signal.pause()
