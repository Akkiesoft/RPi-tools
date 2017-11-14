#!/usr/bin/env python
# -*- coding: utf-8 -*-

from inputs import get_gamepad
import unicornhat as uh

uh.brightness(0.3)

palette = [
        [  0,  0,  0],
        [255,255,255],
        [255,  0,  0],
        [255,255,  0],
        [  0,255,  0],
        [  0,255,255],
        [  0,  0,255],
        [255,  0,255]
]
cx = 0
cy = 0
curpal = 1

uhmap = [0] * 64

def update_cursor(oldx, x, oldy, y):
    oldpos = uhmap[oldy * 8 + oldx]
    col = palette[oldpos]
    uh.set_pixel(oldx, oldy, col[0], col[1], col[2])
    curcol = palette[curpal]
    uh.set_pixel(x, y, curcol[0], curcol[1], curcol[2])
    uh.show()

update_cursor(0,0,0,0)

while 1:
  events = get_gamepad()
  for event in events:
    # キーと十字キー以外はパス
    if event.ev_type != 'Key' and event.ev_type != 'Absolute': continue

    if event.code == 'ABS_X' and event.state == 0:
        # print "Pressed left"
        old_cx = cx
        cx = cx - 1
        if cx < 0 : cx = 0
        update_cursor(old_cx, cx, cy, cy)
    if event.code == 'ABS_X' and event.state == 255:
        # print "Pressed right"
        old_cx = cx
        cx = cx + 1
        if cx > 7 : cx = 7
        update_cursor(old_cx, cx, cy, cy)
    if event.code == 'ABS_Y' and event.state == 0:
        # print "Pressed up"
        old_cy = cy
        cy = cy - 1
        if cy < 0 : cy = 0
        update_cursor(cx, cx, old_cy, cy)
    if event.code == 'ABS_Y' and event.state == 255:
        # print "Pressed down"
        old_cy = cy
        cy = cy + 1
        if cy > 7 : cy = 7
        update_cursor(cx, cx, old_cy, cy)
    if event.code == 'BTN_BASE3' and event.state == 1:
        # print "Pressed select"
        curpal = curpal + 1
        if curpal >= len(palette):
            curpal = 1
        update_cursor(cx, cx, cy, cy)
    if event.code == 'BTN_BASE4' and event.state == 1:
        # print "Pressed start"
        uhmap = [0] * 64
        cx = 0
        cy = 0
        curpal = 1
        uh.clear()
        update_cursor(0,0,0,0)
    if event.code == 'BTN_TOP2' and event.state == 1:
        print "Pressed L"
    if event.code == 'BTN_PINKIE' and event.state == 1:
        print "Pressed R"
    if event.code == 'BTN_THUMB' and event.state == 1:
        # print "Pressed A"
        uhmap[cy * 8 + cx] = curpal
        curcol = palette[curpal]
        uh.set_pixel(cx, cy, curcol[0], curcol[1], curcol[2])
        uh.show()
    if event.code == 'BTN_THUMB2' and event.state == 1:
        # print "Pressed B"
        uhmap[cy * 8 + cx] = 0
        uh.set_pixel(cx, cy, 0, 0, 0)
        uh.show()
    if event.code == 'BTN_TOP' and event.state == 1:
        print "Pressed Y"
    if event.code == 'BTN_TRIGGER' and event.state == 1:
        print "Pressed X"
    # print(event.ev_type, event.code, event.state)
