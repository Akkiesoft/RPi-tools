#!/usr/bin/env python3
from sense_hat import SenseHat
import time
import pyowm

owm = pyowm.OWM('{{ your_api_key }}')
mgr = owm.weather_manager()
SH = SenseHat()

map = {
	#1~20
	'Sapporo-shi':[(6,0),(6,1)],
	'Kushiro':[(7,0),(7,1)],
	'Aomori-ken':[(7,3)],
	'Akita-ken':[(6,3)],
	'Miyagi-ken':[(7,4)],
	'Fukushima-ken':[(7,5)],
	'Tochigi-ken':[(7,6)],
	'Chiba-ken':[(7,7)],
	'Tokyo':[(6,6)],
	'Niigata-ken':[(6,4)],
	'Nagano-ken':[(6,5)],
	'Fukui-ken':[(5,4)],
	'Shizuoka-ken':[(5,6),(5,7)],
	'Aichi-ken':[(5,5)],
	'Kyoto':[(4,4)],
	'Osaka-shi':[(4,5)],
	'Okayama-ken':[(3,4),(3,5)],
	'Shimane-ken':[(3,4)],
	'Tottori-ken':[(2,4)],
	'Hiroshima-ken':[(2,5)],
	#21-27
	'Yamaguchi-ken':[(1,4)],
	'Tokushima-ken':[(3,7)],
	'Kochi-shi':[(2,7)],
	'Fukuoka-ken':[(0,5)],
	'Kumamoto-ken':[(0,6)],
	'Kagoshima-ken':[(0,7)],
	'Okinawa-ken':[(0,1),(1,0)],
}

def get_wether(owm, i):
  weather = mgr.weather_at_place(i + ',JP')
  w = weather.weather.status
  if w == "Clear": return (64,48,0)
  if w == "Clouds": return (48,48,48)
  if w == "Rain" or w == "Mist": return (0,0,64)
  if w == "Snow": return (0,64,64)
  return (0,64,0)

for i in map:
  for x,y in map[i]:
    r,g,b = (0,64,0)
    SH.set_pixel(x,y,r,g,b)
time.sleep(3)

for i in map:
  for x,y in map[i]:
    r,g,b = (0,96,0)
    SH.set_pixel(x,y,r,g,b)
  weather_status = get_wether(owm, i)
  for x,y in map[i]:
    r,g,b = weather_status
    SH.set_pixel(x,y,r,g,b)
