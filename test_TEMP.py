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
for i in ds.get_disp():
	print "device: %s" %i
	ds.set_alarm(21,23,i)
	print ds.get_alarm_val(i)
	print ds.read_temp(i)
	Al=ds.get_alarm_state()
	if Al>0: print "Alarm hot temperature %4.2f *C" %Al
	elif Al==0: print "temperature OK"
	else: print "Alarm low temperature %4.2f *C" %Al

