#!/usr/bin/env python

import datetime
import time
import json
import socket
import urllib2
from microdotphat import write_string, scroll, scroll_vertical, scroll_to, clear, show

print("Press Ctrl+C to exit.")

base="JPY"
exchanges="USD,GBP"

while True:
    rate = ""
    try:
      r = urllib2.urlopen(
        'https://api.exchangeratesapi.io/latest?base='
        + base
        + '&symbols='
        + exchanges
      )
      rate = json.loads(r.read())
      r.close()
    except urllib2.URLError:
      write_string("Can not get JSON. Retry 30 seconds later.      ")
      for x in range(600):
        scroll()
        show()
        time.sleep(0.05)
      scroll_to()
      continue

    for line, r in enumerate(rate["rates"]):
      write_string(r + rate["base"], offset_y=line*2*7, kerning=False)
      write_string('{0:.2f}'.format(1/rate["rates"][r]), offset_y=(line*2+1)*7, kerning=False)
    show()
    for y in range(8):
      time.sleep(5)
      for x in range(7):
        scroll_vertical()
        show()
        time.sleep(0.05)
