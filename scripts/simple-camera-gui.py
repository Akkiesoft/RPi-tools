#!/usr/bin/python3

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget
from picamera2 import Picamera2
from picamera2.previews.qt import QGlPicamera2
import time

size_x = 480
size_y = 800
cam_main = {"size": (480, 800)}
cam_raw = {"size": (1640, 1232)}
capturing = False

class QWidgetWithKey(QWidget):
    def __init__(self):
        super().__init__()
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_T:
            print("key pressed!")
            take_picture()
        event.accept()

def take_picture():
    global capturing
    if not capturing:
        print("capturing...")
        capturing = True
        cfg = picam2.create_still_configuration(
            main=cam_main, raw=cam_raw)
        now = time.strftime('%Y%m%d-%H%M%S', time.localtime())
        path = "%s.jpg" % now
        picam2.switch_mode_and_capture_file(
            cfg, path, signal_function=qpicamera2.signal_done)

def capture_done(job):
    global capturing
    picam2.wait(job)
    print("captured!")
    capturing = False

app = QApplication([])

picam2 = Picamera2()
cam_conf = picam2.create_preview_configuration(
    main=cam_main, raw=cam_raw)
picam2.configure(cam_conf)
qpicamera2 = QGlPicamera2(
    picam2, width=size_x, height=size_y, keep_ar=False)
qpicamera2.done_signal.connect(capture_done)

layout_v = QVBoxLayout()
layout_v.setContentsMargins(0,0,0,0)
layout_v.addWidget(qpicamera2)
# window = QWidget()
window = QWidgetWithKey()
window.setLayout(layout_v)

picam2.start()
window.setWindowTitle("simple camera")
window.resize(size_x, size_y)
# window.show()
window.showFullScreen()
app.exec()
