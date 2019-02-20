#!/usr/bin/env python3
# coding: utf-8

# camera web streaming:
# https://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming

import os
import io
import picamera
import RPi.GPIO as GPIO
import time
import copy
import socketserver
import threading
from http import server
import logging

GPIO.setmode(GPIO.BCM)
chan_list = [24,23]
GPIO.setup(chan_list, GPIO.OUT)

freq=220
pwm = GPIO.PWM(24, freq)

B_MIN_SPEED = 12
P_MIN_SPEED = 18

RUNDIR = os.path.dirname(os.path.abspath(__file__))

f = open(RUNDIR + "/mascon.html", 'r')
html = f.read()
f.close()

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

def brake(mycmd, duty):
  global cmd, pwmstat, pwm
  cmd = mycmd
  time.sleep(0.1)
  pwm.ChangeFrequency(1090)
  while B_MIN_SPEED < pwmstat:
    # print(pwmstat, duty)
    if mycmd != cmd:
      logging.info("[Plarail] command has been changed.")
      break
    pwmstat = pwmstat - duty
    if pwmstat < B_MIN_SPEED:
      break
    pwm.ChangeDutyCycle(pwmstat)
    time.sleep(0.2)
  if pwmstat <= B_MIN_SPEED:
    pwm.stop()
    pwmstat = 0
    logging.info("[Plarail] stopped.")

def power(mycmd, duty):
  global cmd, pwmstat, pwm
  cmd = mycmd
  time.sleep(0.15)
  # print(pwmstat, duty)
  if pwmstat == 0:
    pwmstat = P_MIN_SPEED
    pwm.start(pwmstat)
    pwm.ChangeFrequency(320)
  if pwmstat < duty:
    # print("speedup.")
    while pwmstat < duty:
      if mycmd != cmd:
        logging.info("[Plarail] command has been changed.")
        break
      pwmstat = pwmstat + 1
      pwm.ChangeDutyCycle(pwmstat)
      changePowerFreq(pwm, pwmstat)
      # print(pwmstat)
      time.sleep(0.1)
  else:
    # print("slowdown.")
    while duty < pwmstat:
      if mycmd != cmd:
        logging.info("[Plarail] command has been changed.")
        break
      pwmstat = pwmstat - 1
      pwm.ChangeDutyCycle(pwmstat)
      changePowerFreq(pwm, pwmstat)
      # print(pwmstat)
      time.sleep(0.1)

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

# global
cmd = ""
pwmstat = 0

class Handler(server.BaseHTTPRequestHandler):
  def do_GET(self):
    global pwmstat, html
    logging.info("[Plarail] access: " + self.path)
    code = 200
    body = b"ok"
    if self.path == "/":
      body = bytes(html, 'UTF-8')
    elif self.path == "/EB":
      pwm.stop()
      pwmstat = 0
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

with picamera.PiCamera(resolution='320x240', framerate=24) as camera:
  output = StreamingOutput()
  #Uncomment the next line to change your Pi's Camera rotation (in degrees)
  #camera.rotation = 90
  camera.rotation = 180
  camera.start_recording(output, format='mjpeg')
  try:
    address = ('', 8000)
    server = StreamingServer(address, Handler)
    server.serve_forever()
  finally:
    camera.stop_recording()
    GPIO.cleanup()
