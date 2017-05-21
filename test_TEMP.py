#!/usr/bin/env python
#encoding: utf-8

from TINY import TEMP
import time

ds=TEMP()
# There are DS18B20 devices connected?
print  ds.exist_disp()
# show device code connected
print ds.get_disp()
print
# show tempture for any devices
for i in ds.get_disp():
	print "device: %s" %i
	print ds.read_temp(i)
