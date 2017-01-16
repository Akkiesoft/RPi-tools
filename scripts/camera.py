import blinkt
import paramiko
import picamera
import time
import socket

##########################
# Config

host = "{{ host }}"
port = {{ port }}
user = "{{ user }}"
key  = "{{ private_key_path }}"
photo_file = "{{ photo_file }}"
count_file = "{{ count_file }}"
remote_path = "{{ remote_path }}"
remote_count_path = "{{ remote_count_path }}"

##########################

blinkt.set_brightness(0.04)

def update_status(x, s):
  if s == 0:
    blinkt.set_pixel(x,0,0,0)
  elif s == 1:
    blinkt.set_pixel(x,0,8,8)
  elif s == 2:
    blinkt.set_pixel(x,0,8,0)
  elif s == 3:
    blinkt.set_pixel(x,8,0,0)
  blinkt.show()

def count(c):
  blinkt.set_pixel(7-c,0,0,0)
  if 0 < c :
    blinkt.set_pixel(8-c,0,8,0)
    blinkt.show()
    time.sleep(1)
  blinkt.show()

def get_count():
  for l in open(count_file, 'r'):
    count = int(l)
    break
  return count

def put_count(count):
  f = open(count_file, 'w')
  f.write(str(count))
  f.close

# Init camera
try:
  camera = picamera.PiCamera()
  camera.resolution = (640, 480)
  update_status(0, 1)
except picamera.exc.PiCameraMMALError:
  update_status(0, 3)
  time.sleep(5)
  exit(1)

# Main loop
while True:
  try:
    # clear sleep status
    update_status(2, 0)

    # Connect to remote server
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, user, key_filename = key)
    sftp = ssh.open_sftp()
    update_status(1, 1)

    # Count down (5sec)
    for i in range(0,6):
      count(5-i)

    # Take Picture
    camera.capture(photo_file, quality = 90)

    # Upload
    cnt = get_count()
    remote_file = remote_path + "/" + str(cnt) + ".jpg"
    sftp.put(count_file, remote_count_path)
    sftp.put(photo_file, remote_file)
    sftp.close()
    ssh.close()
    put_count(cnt + 1)
    update_status(1, 0)

    # Sleep (10sec)
    update_status(2, 2)
    time.sleep(10)

  except socket.gaierror:
    # SSH error
    update_status(1, 3)
    sleep(30)

  except KeyboardInterrupt:
    blinkt.clear()
    blinkt.show()
    sftp.close()
    ssh.close()
    exit(0)
