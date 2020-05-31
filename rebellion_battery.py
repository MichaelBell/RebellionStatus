#!/usr/bin/env python

import time
import requests

def get_status_string():
  r = requests.get("http://localhost:8080/status")
  if r.status_code == 200:
    data = r.json()
    if 'Voltage' in data and 'Current' in data and 'Charge' in data:
      return "%.1fA %.1fV %.1f%%" % (data['Current'], data['Voltage'], data['Charge'])
  return ""

if __name__ == '__main__':
  print "Rebel battery monitor test"
  while True:
    print "'%s'" % get_status_string()
    time.sleep(1)

