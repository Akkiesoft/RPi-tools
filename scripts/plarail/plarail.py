#!/usr/bin/env python3
# coding: utf-8

# RPi Plarail
# Copyright (C) 2019-2023 Akkiesoft
# MIT License
# https://akkiesoft.hatenablog.jp/entry/20190220/1550669689

# The web streaming code for the camera was taken from:
#   https://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming
# The original code is licensed under the BSD License.

import os
import io
import RPi.GPIO as GPIO
import time
import copy
import socketserver
import threading
from http import server
import logging

B_MIN_SPEED = 12
P_MIN_SPEED = 18
USE_CAMERA = 1
RUNDIR = os.path.dirname(os.path.abspath(__file__))

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = threading.Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class PlarailCommand():
    def __init__(self, forward, backward, freq = 320):
        self.cmd = 0
        self.speed = 0
        self.direction = 0
        self.forward = forward
        self.backward = backward

        GPIO.setmode(GPIO.BCM)
        GPIO.setup((self.forward, self.backward), GPIO.OUT)
        self.pwm_forward  = GPIO.PWM(self.forward, freq)
        self.pwm_backward = GPIO.PWM(self.backward, freq)
        self.pwm = self.pwm_forward

    def set_direction(self, direction):
        self.set_cmd("/EB")
        time.sleep(0.2)
        self.pwm.stop()
        self.set_speed(0)
        self.pwm = self.pwm_backward if direction else self.pwm_forward

    def set_cmd(self, cmd):
        self.cmd = cmd

    def set_speed(self, speed):
        #print(speed)
        self.speed = speed
        if self.speed:
            self.pwm.ChangeDutyCycle(plarail.speed)
            changePowerFreq(self.pwm, self.speed)
        else:
            self.pwm.stop()
            self.pwm.ChangeFrequency(320)

def changePowerFreq(pwm, s):
    if 25 < s and s < 33:
        pwm.ChangeFrequency(690)
    elif 32 < s and s < 43:
        pwm.ChangeFrequency(1090)
    elif 42 < s and s < 51:
        pwm.ChangeFrequency(690)
    else:
        # if s < 26 or 50 < s:
        pwm.ChangeFrequency(320)

def brake(cmd, duty):
    if plarail.cmd == cmd:
        return
    if plarail.speed == 0:
        return
    plarail.set_cmd(cmd)
    time.sleep(0.2)
    plarail.pwm.ChangeFrequency(1090)
    while B_MIN_SPEED < plarail.speed:
        if cmd != plarail.cmd:
            logging.info("[Plarail] command has been changed.")
            break
        plarail.set_speed(plarail.speed - duty)
        if plarail.speed < B_MIN_SPEED:
            break
        time.sleep(0.2)
    if plarail.speed <= B_MIN_SPEED:
        plarail.set_speed(0)
        logging.info("[Plarail] stopped.")

def power(cmd, duty):
    if plarail.cmd == cmd:
        return
    plarail.set_cmd(cmd)
    time.sleep(0.2)
    if plarail.speed == 0:
        #print("zero start")
        plarail.set_speed(P_MIN_SPEED)
        plarail.pwm.start(plarail.speed)
    if plarail.speed < duty:
        #print("speedup.")
        while plarail.speed < duty:
            if cmd != plarail.cmd:
              logging.info("[Plarail] command has been changed.")
              break
            plarail.set_speed(plarail.speed + 1)
            time.sleep(0.1)
    else:
        #print("slowdown.")
        while duty < plarail.speed:
            if cmd != plarail.cmd:
              logging.info("[Plarail] command has been changed.")
              break
            plarail.set_speed(plarail.speed - 1)
            time.sleep(0.1)

class Handler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        logging.info("[Plarail] access: " + self.path)
        code = 200
        body = b"ok"
        if self.path == "/":
            body = bytes(html, 'UTF-8')
        elif self.path == "/FW":
            plarail.set_direction(0)
        elif self.path == "/BK":
            plarail.set_direction(1)
        elif self.path == "/EB":
            plarail.set_cmd(self.path)
            time.sleep(0.2)
            plarail.set_speed(0)
        elif self.path == "/B4":
            t = threading.Thread(target=brake, args=([self.path, 4]))
            t.start()
        elif self.path == "/B3":
            t = threading.Thread(target=brake, args=([self.path, 3]))
            t.start()
        elif self.path == "/B2":
            t = threading.Thread(target=brake, args=([self.path, 2]))
            t.start()
        elif self.path == "/B1":
            t = threading.Thread(target=brake, args=([self.path, 1]))
            t.start()
        elif self.path == "/P1":
            t = threading.Thread(target=power, args=([self.path, 35]))
            t.start()
        elif self.path == "/P2":
            t = threading.Thread(target=power, args=([self.path, 43]))
            t.start()
        elif self.path == "/P3":
            t = threading.Thread(target=power, args=([self.path, 48]))
            t.start()
        elif self.path == "/P4":
            t = threading.Thread(target=power, args=([self.path, 55]))
            t.start()
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            code = 404
            body = b"invalid request"
        self.send_response(code)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Content-length', len(body))
        self.end_headers()
        self.wfile.write(body)

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


with open(RUNDIR + "/mascon.html", 'r') as f:
    html = f.read()

plarail = PlarailCommand(forward=24, backward=23)
position = 5

if USE_CAMERA:
    import picamera
    camera = picamera.PiCamera(resolution='320x240', framerate=24)
    output = StreamingOutput()
    #Uncomment the next line to change your Pi's Camera rotation (in degrees)
    camera.rotation = 90
    #camera.rotation = 180
    camera.start_recording(output, format='mjpeg')

try:
    address = ('', 8000)
    server = StreamingServer(address, Handler)
    server.serve_forever()
finally:
    if USE_CAMERA:
        camera.stop_recording()
    GPIO.cleanup()
