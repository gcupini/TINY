#!/usr/bin/env python
#encoding: utf-8

from TINY import RTC
#import time
from datetime import datetime
import os

def main():
	print "-------- RTC Function ----------"
	ds = RTC() 
	#SETTAGGIO ORA, in TINY RTC
	if not ds.rtc_work():
		ds.write_now()	# Legge time da Micro e lo regisra su RTC
		''' Se desiderate fissarlo a piacere:
		Time=datetime(aaa,mm,gg,hh,mm,ss)
		ds.write_datetime(Time)
		'''
	else :
		pass

	# Funzioni di lettura Calendario RTC 
	print "Ore: %i:%i:%i " %(ds.getHour(),ds.getMin(),ds.getSec())
	print "tupla : ",ds.read_tupleDate()
	print "string: ",ds.read_strDate()
	print "Obj   : ",ds.read_objDate()
	
	# ******* SCRIVE/LEGGE IN RAM libera di RTC *********

	print "-------- RAM function ----------"
	reg=0x3B
	# scrive dati in RAM RTC a partire da reg	
	# reg 0x3B -> dec addr = 59, 60 , 61 ,62 ,63  (64 non esiste in ram)
	# Scriveràn ei reg i numeri 99, 98, 97 ,96 ,95
	for i in range (99,94,-1):
		ds.write_ram(reg,i)
		reg=reg+1
	
	# MOSTRA BYTES DI RAM RTC
	reg=0x3B
	for i in range (1,6):
		print "Reg Addr: 0x%X dec:%i val: %i" %(reg,reg,ds.read_ram(reg))
		reg=reg+1	
	# Stampa n byte
	print ds.read_ram_n(0x3B,5)

if __name__ == '__main__':
        try:
          main()
        except KeyboardInterrupt:
          os.system('clear')
          pass
        except ValueError,a:
	  print a
	except IndexError,i:
	  print i
        finally:
          print "Goodbye!\n\n"
