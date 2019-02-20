#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
from PIL import Image

def get_icon(url, file_orig, file_resize):
  urllib.request.urlretrieve(url, file_orig)
  icon = Image.open(file_orig)
  icon_w, icon_h = icon.size
  #icon_w = 200 if 200 < icon_w else icon_w
  #icon_h = 200 if 200 < icon_h else icon_h
  icon_w = 200
  icon_h = 200
  icon.resize((icon_w,icon_h)).save(file_resize)
