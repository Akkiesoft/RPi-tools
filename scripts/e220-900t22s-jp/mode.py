#!/usr/bin/env python3

# USAGE:
# get mode: python3 mode.py
# set mode: python3 mode.py <0-3>

import RPi.GPIO as GPIO
from sys import argv,exit

M0_pin = 5
M1_pin = 6

modes = ((0, 0), (1, 0), (0, 1), (1, 1))
mode_names = ("NORMAL", "WOR_SEND", "WOR_RECEIVE", "CONFIG")

def show_current_mode():
    pin_state = (GPIO.input(M0_pin), GPIO.input(M1_pin))
    if pin_state in modes:
        i = modes.index(pin_state)
        print("Current mode: %s (%s)" % (i,mode_names[i]))

def main():
    # Configuring GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(M0_pin, GPIO.OUT)
    GPIO.setup(M1_pin, GPIO.OUT)

    argv_len = len(argv)
    if argv_len == 1:
        show_current_mode()
        exit(0)
    elif argv_len == 2:
        mode = int(argv[1])
    else:
        print("Invalid parameter")
        exit(1)

    if 0 <= mode and mode <= 3:
        GPIO.output(M0_pin, modes[mode][0])
        GPIO.output(M1_pin, modes[mode][1])
        print("Set mode to: %s (%s)" % (mode,mode_names[mode]))
    else:
        print("Invalid mode")
        exit(1)

if __name__ == "__main__":
    main()