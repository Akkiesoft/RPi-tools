#!/usr/bin/env python

import datetime
import time
import python_forex_quotes
from microdotphat import write_string, scroll, scroll_vertical, scroll_to, clear, show

# https://1forge.com/
# pip install python_forex_quotes
apikey=""
client = python_forex_quotes.ForexDataClient(apikey)

print("Press Ctrl+C to exit.")

while True:
  try:
    rate = client.getQuotes(['USDJPY', 'GBPJPY'])
  except:
    write_string("Can not get exchange. Retry 30 seconds later.      ")
    for x in range(600):
      scroll()
      show()
      time.sleep(0.05)
  for line, text in enumerate(rate):
    write_string(text["symbol"], offset_y=line*2*7, kerning=False)
    write_string(str(text["price"])[0:6], offset_y=(line*2+1)*7, kerning=False)
  show()
  for y in range(8):
    time.sleep(5)
    for x in range(7):
      scroll_vertical()
      show()
      time.sleep(0.05)

