#!/usr/bin/env python

import datetime
import time
import json
import socket
import urllib2
from microdotphat import write_string, scroll, scroll_vertical, scroll_to, clear, show

print("Press Ctrl+C to exit.")

# Reference:
#   http://qiita.com/masato/items/6f81bdc89f81a7b6cc3a (Japanese)
#   https://github.com/yql/yql-tables/blob/master/yahoo/finance/yahoo.finance.xchange.xml

exchanges="USDJPY,GBPJPY"

while True:
    rate = ""
    try:
      r = urllib2.urlopen(
        'https://query.yahooapis.com/v1/public/yql?'
        + 'q=select%20*%20from%20yahoo.finance.xchange%20where%20pair%20in%20(%22'
        + exchanges
        + '%22)&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys'
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

    for line, text in enumerate(rate["query"]["results"]["rate"]):
      write_string(text["id"], offset_y=line*2*7, kerning=False)
      write_string(text["Rate"][0:6], offset_y=(line*2+1)*7, kerning=False)
    show()
    for y in range(8):
      time.sleep(5)
      for x in range(7):
        scroll_vertical()
        show()
        time.sleep(0.05)
