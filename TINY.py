#!/usr/bin/env python
#encoding: utf-8
 
        
'''Te module it allows you to Read and Write
of TINY RTC break-board 
'''
        
import time   
from datetime import datetime
import glob
import os
import smbus

msg_ram_1='addr RAM (0-63) out of range. Used REF is :'			

class RTC():

# attributi 'PRIVATE'	
	__REG_SECONDS = 0x00
	__REG_MINUTES = 0x01
	__REG_HOURS = 0x02
	__REG_DAY = 0x03
	__REG_DATE = 0x04
	__REG_MONTH = 0x05
	__REG_YEAR = 0x06
	__REG_CONTROL = 0x07
	__REG_RAM = 0x08
	__MAX_RAM=0x3F
# funzioni 'PRIVATE'	
	def __init__(self, twi=1, addr=0x68):
		self._bus = smbus.SMBus(twi)
		self._addr = addr

	def __decToBcd(self,A):
		return ( (A-A%10)/10*16 + A%10 )
		
	def __bcdToDec(self,B):
		return ( (B-B%16)/16*10 + B%16 )   

	def __write(self, register, data):
		self._bus.write_byte_data(self._addr, register, data)

	def __read(self, data):
		return self._bus.read_byte_data(self._addr, data)

	def __read_day(self):
		return self.__bcdToDec(self.__read(self.__REG_DAY))
		
	def __read_date(self):
		return self.__bcdToDec(self.__read(self.__REG_DATE))
		
	def __read_month(self):
		return self.__bcdToDec(self.__read(self.__REG_MONTH))

	def __read_year(self):
		return self.__bcdToDec(self.__read(self.__REG_YEAR))
		
	def __write_all(self, seconds=None, minutes=None, hours=None, day=None, date=None, month=None, year=None, save_as_24h=True):
			"""Direct write un-none value.  Range: seconds [0,59], minutes [0,59], 
			hours [0,23],day [0,7], date [1-31], month [1-12], year [0-99].
			"""
			if seconds is not None:
				if seconds < 0 or seconds > 59:
					raise ValueError('Seconds is out of range [0,59].')
				self.__write(self.__REG_SECONDS, self.__decToBcd(seconds))

			if minutes is not None:
				if minutes < 0 or minutes > 59:
					raise ValueError('Minutes is out of range [0,59].')
				self.__write(self.__REG_MINUTES, self.__decToBcd(minutes))

			if hours is not None:
				if hours < 0 or hours > 23:
					raise ValueError('Hours is out of range [0,23].')
				if save_as_24h:
					self.__write(self.__REG_HOURS, (self.__decToBcd(hours) ))
				else:
					if hours == 0:
						h = __decToBcd(12) | 0x32
					elif hours <= 12:
						h = __decToBcd(hours)
					else:
						h = __decToBcd(hours - 12) | 0x32
					self.__write(self.__REG_HOURS, h)
        
			if year is not None:
				if year < 0 or year > 99:
					raise ValueError('Years is out of range [0,99].')
				self.__write(self.__REG_YEAR, self.__decToBcd(year))
			
			if month is not None:
				if month < 1 or month > 12:
					raise ValueError('Month is out of range [1,12].')
				self.__write(self.__REG_MONTH, self.__decToBcd(month))
			
			if date is not None:
				if date < 1 or date > 31:
					raise ValueError('Date is out of range [1,31].')
				self.__write(self.__REG_DATE, self.__decToBcd(date))
			
			if day is not None:
				if day < 1 or day > 7:
					raise ValueError('Day is out of range [1,7].')
				self.__write(self.__REG_DAY, self.__decToBcd(day))
            
# funzioni 'PUBBLIC'		
	def getSec(self):
		'''Return Seconds in RTC'''
		return  self.__bcdToDec(self.__read(self.__REG_SECONDS))
		
	def getMin(self):
		'''Return Minuts in RTC'''
		return self.__bcdToDec(self.__read(self.__REG_MINUTES))

	def getHour(self):
		''' Return hours in format 24h'''
		d = self.__read(self.__REG_HOURS)
		if d & 0x40:#x1xx xxxx  modo 24 ore
			return self.__bcdToDec(d & 0x3F)
		else: # modo AM PM
			h = self.__bcdToDec(d & 0x1F)
			if (d & 0x20) :# xx1x xxxx   ore PM
				h += 12  # Converte 12h to 24h
			elif h == 12: # sono le 12   AM
				h = 0
			return h
		
	def read_tupleDate(self):
			"""Return a tuple (year, month, date, day, hours, minutes,
			seconds).
			"""
			return (self.__read_year(), self.__read_month(), self.__read_date(),
			self.__read_day(), self.getHour(), self.getMin(),
			self.getSec())
			
	def read_strDate(self):
			"""Return a string  'DD-MM-YYYY HH-MM-SS'.
			"""
			return '%02d-%02d-%02d %02d:%02d:%02d' % (self.__read_date(),
			self.__read_month(), 2000 + self.__read_year(),  self.getHour(),
			self.getMin(), self.getSec())
			
	def read_objDate(self, century=21, tzinfo=None):
	        """Return datetime.datetime object.
	        """
	        return datetime((century - 1) * 100 + self.__read_year(),
	        self.__read_month(),  self.__read_date(), self.getHour(),
	        self.getMin(), self.getSec(), 0, tzinfo=tzinfo)
	        
	def write_datetime(self, dt):
			"""Receives dt = datetime.datetime object.
			and writes it in RTC
			"""
			self.__write_all(dt.second, dt.minute, dt.hour,
			dt.isoweekday(), dt.day, dt.month, dt.year % 100)
		
	def write_now(self):
			"""Updates the date RTC reading it
			by SoC clock
			"""
			self.write_datetime(datetime.now())

        def rtc_work(self):
		if (self.__read(0x00) & 0b10000000)==1:
			return False
		else: return True	

# Funzioni di accesso alla RAM libera
	def write_ram(self, reg=__REG_RAM, data=0):
		'''Write a byte in RTC Ram register at address reg
		'''
		if (reg>=self.__REG_RAM  and reg <=self.__MAX_RAM): 
			self.__write(reg, data)
		else:
			raise ValueError(msg_ram_1+str(reg))
			
	def read_ram_n(self,reg=__REG_RAM,n=1):
		''' Return n bytes at address reg '''
		L=[]
		if (reg>=self.__REG_RAM  and reg+n-1<=self.__MAX_RAM): 
			for i in range(reg,reg+n):
				L.append(self.__read(i))
		else:	
			raise ValueError(msg_ram_1+str(reg)+' To '+str(reg+n-1))

		return L
		
	def read_ram(self,reg=__REG_RAM):
		'''Return a byte at address reg'''
		if (reg>=self.__REG_RAM  and reg <=self.__MAX_RAM): 
			return self.__read(reg)
		else:
			raise ValueError(msg_ram_1+str(reg))
			
# ======    Classe TEMP =====================

''' Testato su CHIP e Raspberry. Lavora su Sensori
OneWire sia montati sy Tiny RTC che autonomi.
Consente attacco/distacco di sensori in parallelo
anche durante il funzionamento '''


class TEMP:
	# funzioni 'PRIVATE'	

	def __temp_raw(self, mio_file):
		''' legge una linea di testo dal file '/sys/../28-xxxxxxx/w1_slave
		che contiene 2 linee di testo con i valori dei registri del sensore
		che saranno usati per leggere lo stato e la temperatura
		'''
		f=open(mio_file, 'r')
		lines=f.readlines()
		f.close()
		return lines

	def __get_enabled(self):
		''' Ricostruisce la lista dei sensori attivi '''
		i=0
		self._dev_file=[]
		while True:
			try:
				dev_folder=glob.glob(self._base_path+'28*')[i]
				mio_file=dev_folder+self._base_file
				if (self.__temp_raw(mio_file)[0].strip()[-3:]=='YES'):
					self._dev_file.append(mio_file)
				i=i+1
				time.sleep(1)
			except: 
				IndexError('ERR in get_enabled Func.')
				break
				
		
	def __init__(self, base_path='/sys/bus/w1/devices/', base_file='/w1_slave', Low_alarm=-20, Hi_alarm=125):
		self._base_path=base_path
		self._base_file=base_file
		self._lo=Low_alarm
		self._hi=Hi_alarm
		self._alarm=0
		self._dev_file=[]
		self.__get_enabled()

# Funzioni 'PUBBLIC'	
	def set_alarm(self, lo, hi,disp):
		''' setta gli estremi di temperatura di allarme 
		Riceve: lo, hi estremi allarme, disp il 
		dispositivo a cui si riferiscono
		Return: void '''
		if lo<=hi:
			self._lo=lo
			self._hi=hi

	def get_alarm_val(self,disp):
		''' legge gli estremi di temperatura di allarme fissati 
		Riceve: disp il	dispositivo a cui si riferiscono
		Return: List dei due valori '''
		return [self._lo, self._hi]

	def get_alarm_state(self):
		''' Return: state<0, =0, >0 
		ES. se lo<temp<hi return 0
		    se temp<lo return valore negativo gradi in meo di lo
		    se temp>hi return volore positivo gradi in piÃ¹ di hi '''
		return self._alarm		 

			

	def exist_disp(self):
		'''Verifica se ci sono dispositivi connessi al bus One Wire 
		testato per C.H.I.P. and RaspberryPi
		Return: True or False
		'''
		if self._dev_file==[]:
			return False
		else:
			return True
			
	
	def get_disp(self):
		''' verifica i dispositivi conneessi al BUS OneWire
		testata per C.H.I.P. and RaspberryPi
		Return: Lista dei dispositivi connessi
		'''
		return self._dev_file
	
			
	def read_temp(self,disp,test=True):
		''' Legge ela temperatura del dispositivo 
		Riceive: disp=dispositivo che restituisce la temperatura
		test se=True ri-verifica la lista dei sipositivi ancora connessi 
		dall'avvio. Consente di inserire togliere dispÃositivi
		durante l'esecuzione. Se=False usa i dipositivi registrati 
		all'avvio da errore se dispositivi rimossi in esecuzione. 
        	Return: la Temperatura misurate in Celsius
        	'''
		if test: self.__get_enabled()
		Temp=0.0
		#self._alarm=0
		lines1=self.__temp_raw(disp)
		lines2=self.__temp_raw(disp)
		temp_out=lines2[1].find('t=')
		if temp_out != -1:
			temp_string=lines2[1].strip()[temp_out+2:]
			temp_c = float(temp_string)/1000.0
			Temp=temp_c
			if temp_c>=self._lo and temp_c<=self._hi:
				self._alarm=0
			elif temp_c<self._lo:
				self._alarm=temp_c-self._lo
			else:	self._alarm=temp_c-self._hi
				
		return Temp

# ========= Classe EPROM ==============================
msg_EPROM_1='addr EPROM (0-4095) out of range. Used REF is :'	

class EPROM():
# attributi 'PRIVATE' indirizzi di EEPROM AT24C32 di TINY	
	__MIN_ADDR = 0x0000
	__MAX_ADDR = 0x0FFF
# funzioni 'PRIVATE'	
	def __init__(self, twi=1, addr=0x50):
		self._bus = smbus.SMBus(twi)
		self._addr = addr

	def __get_addr(self,reg):
		up_byte=(reg & 0b1111111100000000)>>8
		lo_byte=(reg & 0b0000000011111111)
		return up_byte, lo_byte


	def get_byte(self,reg):
		''' Legge in Byte di posizione reg della EEPROM 
		Param:  reg=0 .. 4095 indirizzo su cui leggere
		Return: il byte in EEPROM di posizione reg '''
		if (reg>=self.__MIN_ADDR  and reg<=self.__MAX_ADDR):
			tu=self.__get_addr(reg)
	 		self._bus.write_i2c_block_data(self._addr, tu[0],[tu[1]])
			return self._bus.read_byte(self._addr)
		else:
			raise ValueError(msg_EPROM_1+str(reg))


        def set_byte(self,reg,val):
		''' Scrive il byte val alla posizione reg della EEPROM 
		Param: reg=0..4095 e val=0..255 un byte numerico
		Return: True or False se la scrittura Ã¨ andata in porto'''
                if (reg>=self.__MIN_ADDR  and reg<=self.__MAX_ADDR):
                        tu=self.__get_addr(reg)
                        self._bus.write_i2c_block_data(self._addr, tu[0],[tu[1],val])
			time.sleep(0.1)
			return True
                else:
			raise ValueError(msg_EPROM_1+str(reg))
			return False
		
        def get_str(self,reg,dim):
		''' Legge una stringa di dimensione dim a partire dal registo reg
		Param: reg=0..4095 registro da cui inizia, dim= num caratteri da leggere
		Return: La stringa di dimensione dim '''
		Ris=""
                if (reg>=self.__MIN_ADDR  and (reg+dim-1)<=self.__MAX_ADDR):
                       	tu=self.__get_addr(reg)
                        self._bus.write_i2c_block_data(self._addr, tu[0],[tu[1]])
			for i in range(dim):
				Ris=Ris+chr(self._bus.read_byte(self._addr))
		else:
			raise ValueError(msg_EPROM_1+str(reg)+' To '+str(reg+dim-1))
		return Ris

        def set_str(self, reg, val):
		''' Scrive la stringa val a partire dal registro reg
		Param: reg=0..4095 registro di inizio val= stringa da scrivere
		Return: True or False se la scrittura Ã¨ andata in porto'''
		l=0
		L_car=[]
                if type(val)==str:
                        l=len(val)
			for i in val: 
				L_car.append(ord(i))
                else:
                        raise TypeError('Err must be a String. is :'+str(type(val)))
			return False

             	if (reg>=self.__MIN_ADDR  and (reg+l-1)<=self.__MAX_ADDR):
                        tu=self.__get_addr(reg)
			L_car.insert(0,tu[1])
			print L_car 
			self._bus.write_i2c_block_data(self._addr, tu[0], L_car)
			time.sleep(0.1)
			return True
                else:
			raise ValueError(msg_EPROM_1+str(reg)+' To '+str(reg+l-1))
			return False

