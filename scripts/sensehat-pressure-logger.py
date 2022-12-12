#!/usr/bin/python3

from sense_hat import SenseHat
import datetime
import argparse

d = datetime.datetime.now()
today = "{0:%Y-%m-%d}".format(d)
now = "{0:%H:%M:%S}".format(d)

def get_pressure(path):
    sense = SenseHat()
    pressure = sense.get_pressure()
    pressure = round(pressure, 1)

    f = open('%s/%s.csv' % (path, today), 'a')
    f.write("%s,%s,%s\n" % (today, now, pressure))
    f.close()

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Output the pressure with formatted by CSV append mode.')
  parser.add_argument('--path', type=str, nargs=1, default='.',
                    help='where is save to the CSV file.')
  args = parser.parse_args()
  get_pressure(args.path[0])

