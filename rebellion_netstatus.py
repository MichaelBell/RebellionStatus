#!/usr/bin/env python

import time
import re
import requests
from easysnmp import snmp_get

conn_type_map = {
  'LTE': '4G',
  'DC-HSPA+': '4G',
  'WCDMA': '3G',
  'HSPA+': '3G',
}

class NetStatus:
  def __init__(self):
    self.operator = ""
    self.signal_strength = -1
    self.conn_type = ""
    self.data_remaining = ""
    self.last_snmp_time = 0
    self.last_data_time = 0

  def read_snmp(self):
    if self.last_snmp_time + 2 < time.time():
      self.last_snmp_time = time.time()
      print "Reading SNMP"
      try:
        self.operator = snmp_get('.1.3.6.1.4.1.99999.2.5.0', hostname='192.168.1.1', community='private', version=2).value
        dbm = snmp_get('.1.3.6.1.4.1.99999.2.4.0', hostname='192.168.1.1', community='private', version=2).value
        self.conn_type = snmp_get('.1.3.6.1.4.1.99999.2.8.0', hostname='192.168.1.1', community='private', version=2).value
      except easysnmp.exceptions.EasySNMPError:
        self.operator = 'unknown'
        self.conn_type = 'unknown'
        self.signal_strength = -1
      try:
        dbm = int(dbm)
        if dbm > -52: self.signal_strength = 5
        elif dbm > -67: self.signal_strength = 4
        elif dbm > -82: self.signal_strength = 3
        elif dbm > -97: self.signal_strength = 2
        elif dbm > -112: self.signal_strength = 1
        else: self.signal_strength = 0
      except ValueError:
        self.signal_strength = -1

      if self.conn_type in conn_type_map: self.conn_type = conn_type_map[self.conn_type]

  def get_operator(self):
    self.read_snmp()
    return self.operator

  def get_signal_strength(self):
    self.read_snmp()
    return self.signal_strength

  def get_conn_type(self):
    self.read_snmp()
    return self.conn_type

  def read_data_remaining(self):
    if self.last_data_time + 600 < time.time():
      print "Reading data"
      if self.get_operator() == 'EE':
        try:
          r = requests.get('http://add-on.ee.co.uk/')
          if r.status_code == 200:
            self.last_data_time = time.time()
            m = re.search('>([0-9.]+)GB', r.text)
            self.data_remaining = float(m.group(1))
          else:
            self.data_remaining = -1
        except requests.exceptions.RequestException:
          self.data_remaining = -1
      else:
        self.last_data_time = time.time()
        self.data_remaining = -1

  def get_data_remaining(self):
    self.read_data_remaining()
    return self.data_remaining

  def get_net_summary_string(self):
    return "%s, %s: %d bars\nData left: %d\nxx" % (self.get_operator(), self.get_conn_type(), self.get_signal_strength(), self.get_data_remaining())

if __name__ == '__main__':
  print "Rebel status test"
  status = NetStatus()
  while True:
    print status.get_net_summary_string()
    time.sleep(5)

