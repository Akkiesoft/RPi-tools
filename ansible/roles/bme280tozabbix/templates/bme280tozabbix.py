#!/usr/bin/env python3

# sudo apt install -y python-pip python-smbus
# sudo pip install rpi.bme280 py-zabbix

import smbus2
import bme280
from zabbix_utils import ItemValue, Sender

address = 0x76
bus = smbus2.SMBus(1)
bme280.load_calibration_params(bus, address)
data = bme280.sample(bus, address)

#print(data.temperature)
#print(data.humidity)
#print(data.pressure)

params = [
  ItemValue("{{ zabbix_hostname }}", "verandah_temperature", round(data.temperature, 2)),
  ItemValue("{{ zabbix_hostname }}", "verandah_humidity", round(data.humidity, 2)),
  ItemValue("{{ zabbix_hostname }}", "verandah_pressure", round(data.pressure, 2))
]
result = Sender(use_config=True).send(params)
