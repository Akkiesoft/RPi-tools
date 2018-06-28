#!/bin/sh

HAT=`cat /proc/device-tree/hat/product`

if [ "$HAT" = "Unicorn HAT" ]; then
	python /home/pi/unicornpaint.py &
fi

if [ "$HAT" = "Unicorn HAT HD" ]; then
	python /home/pi/unicornpainthd.py &
fi
