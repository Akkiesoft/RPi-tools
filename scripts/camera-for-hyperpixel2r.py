#!/usr/bin/python3

# Camera app for hyperpixel2r

# Based on this script:
# https://github.com/raspberrypi/picamera2/blob/main/apps/app_capture2.py

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QLabel
from picamera2 import Picamera2
from picamera2.previews.qt import QGlPicamera2
import time

init_error = False
capturing = False

class QWidgetWithKey(QWidget):
    def __init__(self):
        super().__init__()
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_T:
            if init_error:
                sys.exit()
            take_picture()
        event.accept()

def take_picture():
    global capturing
    if not capturing:
        print("capturing...")
        capturing = True
        cfg = picam2.create_still_configuration(main={"size": (1024, 768)})
        now = time.strftime('%Y%m%d-%H%M%S', time.localtime())
        path = "/var/www/html/camera/%s.jpg" % now
        picam2.switch_mode_and_capture_file(cfg, path, signal_function=qpicamera2.signal_done)

def capture_done(job):
    global capturing
    picam2.wait(job)
    print("captured!")
    capturing = False

app = QApplication([])

layout_v = QVBoxLayout()
layout_v.setContentsMargins(0, 0, 0, 0)

window = QWidgetWithKey()
window.setLayout(layout_v)
window.showFullScreen()

try:
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"size": (480, 480)}))
    qpicamera2 = QGlPicamera2(picam2, width=480, height=480, keep_ar=False)
    qpicamera2.done_signal.connect(capture_done)
    layout_v.addWidget(qpicamera2)
    picam2.start()
except:
    layout_v.setContentsMargins(20, 0, 0, 0)
    msg = "Failed to initialize the camera.\nPrease make sure the camera is installed correctly.\n\nPress the shutter button to exit."
    msg_label = QLabel(msg)
    layout_v.addWidget(msg_label)
    init_error = True

app.exec()
