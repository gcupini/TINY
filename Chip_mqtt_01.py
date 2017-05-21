#!/usr/bin/python
# -*- coding: utf-8 -*-
'''mqtt pubblica da SiOC [C.H.I.P] su broker  [iot.eclipse.org]
   Pin LCD-D2  OneWire [C.H.I.P] due sensori DS18B20 Interno ed Esterno
   TOPIC:
   Temp/interna  -> pubbl/sott la temperatura del sensore interno 
   Temp/esterna  -> pubbl/sott la temperatura del sensore esterno
   Temp/data	 -> pubbl/sott la data e ora della misura
   Temp/bassa    -> pubbl/sott la temperatura Interna MINIMA di allarme
   Temp/alta     -> pubbl/sott la temperatura interna MASSIMA di allarme
   Temp/run	 -> pubbl/sott lo Stato del programma ON | OFF
   Led/bassa 0|1 -> pubbl/sott Stato di allarme Bassa Temperatura
   Led/alta  0|1 -> pubbl/sott Stato di allarme Alte Temperatura
   Cmd/alt    1  -> pubbl/sott il comando di alt (Stop all'esecuzione)
   Cmd/Read   1  -> pubbl/sott il comando di Rileggere le temperature

   HW compatibile:
   RaspberryPI, raspberryPiZero, C.H.I.P	
   due sensori DS18B20		[prot. 1-wire]

   Il programma mostra in Locale su LCD 4x20
   Data, Temperature e Stati di allarme
  '''
# moduli pubblici di python   
import paho.mqtt.client as pubb
import time
import os
from datetime import datetime

# MODULI PRIVATI in corso di perfezionamento
# Modulo TEMP  per gestione  DS18B20
from TINY_1 import TEMP
# Modulo base per gestine LCD 
import Lcd

# Define GPIO (CHIP Computer) to LCD mapping
LCD_RS  	= "CSID0"
LCD_E   	= "CSID1"
LCD_Back 	= "CSID3"
LCD_D4  	= "CSID4"
LCD_D5  	= "CSID5"
LCD_D6  	= "CSID6"
LCD_D7  	= "CSID7"

# global var
dir_prog="/home/chip/Documents/"	# directory del file e del prog
nome_file=dir_prog+'mqtt.txt'		# file di memorizzazione stato

halt = False			# var che interrompe il loop infinito
Test = False			# porre a True per mostrare messaggi a video

led_basso_att = 0		# valori di avvio stato led
led_alto_att  = 0		# valori di avvio stato led
temp_data_att ="00-00-0000  00:00:00"	# valori di avvio data

# global var la cui modifica ha influenza su SWITCH (topic led/#) e Management
temp_int=0
temp_int_att=0
temp_est=0
temp_est_att=0
reg_min=0
reg_min_att=0
reg_max=0
reg_max_att=0

rileggi=False	# variabile logica che consente all'attuatore
		# il client SWITCH la rilettura dei dati sensori

# indirizzo del broker mqtt remoto
Broker='iot.eclipse.org'

# pointer al client mqtt
mqttc= pubb.Client()
	
def init_mqtt():
	''' attiva connessione al Broker'''
	mqttc.connect(Broker)
	mqttc.loop_start()

#def init_GPIO():
#	''' attiva il GPIO di CHIP (o Raspberry)'''
#	GPIO.setmode(GPIO.BOARD)
#	GPIO.setwarnings(False)

def Mostra_lcd(temp_data_att,temp_int_att,temp_est_att,led_basso_att,led_alto_att,reg_min_att,reg_max_att):
	'''mostra i dati misurati su LCD'''
	riga_uno=temp_data_att
	riga_due="Tint:"+str(temp_int_att)+" Test:"+str(temp_est_att)
	riga_tre="Min:"+str(reg_min_att)+ "  Max:"+str(reg_max_att)
	riga_qua="Nessun Allarme"
	if (led_basso_att=='1'): riga_qua="Allarme BASSA!"
	if (led_alto_att=='1'): riga_qua="Allarme ALTA!"
	Lcd.lcd_string(riga_uno,1,1)
        Lcd.lcd_string(riga_due,2,2)
        Lcd.lcd_string(riga_tre,3,2)
        Lcd.lcd_string(riga_qua,4,2)

def Misura():
	''' esegue le misure di temperatura sui due sensori. 
	return: due misure '''
	Sensore_interno=tempture._dev_file[0]
	Sensore_esterno=tempture._dev_file[1]
	TI=tempture.read_temp(Sensore_interno)
	TE=tempture.read_temp(Sensore_esterno)
	TI= format(TI,"0.1f")
	TE= format(TE,"0.1f")
	return TI, TE
 
def leggi_data_att():
	''' legge data e ora da rete '''
	temp_data_att= datetime.now().strftime("%d-%m-%Y  %H:%M:%S")
	return temp_data_att
	
def test_alarm(inte):
	''' verifica se la Temperatura interna e in allarme
	return: True|False '''
	alarm = False
	global led_basso_att
	global led_alto_att
	global reg_min_att
	global reg_max_att
	led_alto_att='0'
	led_basso_att='0'
	if (inte<reg_min_att): 
		led_basso_att='1'
		alarm=True
	if (inte>reg_max_att): 
		led_alto_att='1'
		alarm=True
	return alarm
	
def mostra_cambi(K=1):
	''' pubblica cambi temperature e stato limiti 
	stampa enche per controlli K=0 solo in avvio'''
	global temp_data_att
	global temp_int
	global temp_est
	global temp_int_att
	global temp_est_att
	global reg_min
	global reg_max
	global reg_min_att
	global reg_max_att
	global led_basso_att
	global led_alto_att
	if (K==1):	temp_data_att=leggi_data_att()
	test_alarm(float(temp_int_att))
	mqttc.publish('Temp/data',temp_data_att)
	mqttc.publish('Temp/interna',temp_int_att)
	mqttc.publish('Temp/esterna',temp_est_att)
	mqttc.publish('Led/bassa',led_basso_att,1)
	mqttc.publish('Led/alta',led_alto_att)
	mqttc.publish('Temp/min',reg_min_att)
	mqttc.publish('Temp/max',reg_max_att)
	mqttc.publish('Temp/run',"ON")
	time.sleep(0.2)
	# mostra su LCD
  	Lcd.lcd_init(LCD_RS,LCD_E,LCD_D4,LCD_D5,LCD_D6,LCD_D7,LCD_Back)
  	Lcd.lcd_backlight(True)
	Lcd.lcd_clear()
	Mostra_lcd(temp_data_att,temp_int_att,temp_est_att,led_basso_att,led_alto_att,reg_min_att,reg_max_att)
	# fine LCD
	if (Test): print
	if (K==0):  # interviene solo dopo la lettura iniziale del file di stato
        	temp_int=temp_int_att
        	temp_est=temp_est_att
        	reg_min=reg_min_att
        	reg_max=reg_max_att
        	if (Test): print

def on_connect(client,userdata,flags, rc):
	''' sottoscrive i topic '''
	if rc==0 : 
		if (Test): print "Connected"
	else : 
		if (Test) : print "Connection Error",str(rc)
	client.subscribe("Temp/+")
	client.subscribe("Led/+")
	client.subscribe("Cmd/+")

def on_message(client, userdata,msg):
	''' stampa e gestisce i Topic in arrivo '''
	global temp_int_att
	global temp_est_att
	global reg_min_att
	global reg_max_att
	global temp_int
	global temp_est
	global reg_min
	global reg_max
	global temp_data_att
	global halt
	global rileggi
	M=msg.topic
	D=msg.payload
	# stampa Topic payload per controllo
	if (Test): print(msg.topic+" "+D)
	# gestisce i diversi valori dei Topic		
	if M=='Cmd/alt': 		halt=int(D)
	if M=='Temp/esterna':		temp_est_att=float(D)
	if M=='Temp/interna': 		temp_int_att=float(D)
	if M=='Temp/data':     		temp_data_att=D
	if M=='Temp/min':         	reg_min_att=float(D)
	if M=='Temp/max':          	reg_max_att=float(D)
	if M=='Cmd/read':		rileggi=bool(D)

def cambiato():
	''' determina se sono cambiate le Temperature 
	o gli allarmi. return: True|False'''
	global temp_int
	global temp_est
	global temp_int_att
	global temp_est_att
	global reg_min
	global reg_max
	global reg_min_att
	global reg_max_att
	Cambio=False
	Cambio=(float(temp_int_att)>float(temp_int)+0.2) or (float(temp_int_att)<float(temp_int)-0.2)
	Cambio=Cambio or (float(temp_est_att)>float(temp_est)+0.2) or (float(temp_est_att)<float(temp_est)-0.2)
	Cambio=Cambio or (not (reg_min_att == reg_min)) or (not(reg_max_att == reg_max))
	return  Cambio

def leggi_stato():
	''' legge lo stato memorizzato su file'''
	global temp_int_att
	global temp_est_att
	global reg_min_att
	global reg_max_att
	global temp_data_att
	global led_basso_att
	global led_alto_att
	mio_file=open(nome_file,"r")
	reg_min_att=float(mio_file.readline())
	reg_max_att=float( mio_file.readline())
	temp_int_att=float( mio_file.readline())
	temp_est_att=float( mio_file.readline())
	led_basso_att=( mio_file.readline())
	led_basso_att=int(led_basso_att)	
	led_alto_att=( mio_file.readline())
	led_alt_att=int(led_alto_att)
	temp_data_att=str(mio_file.readline())[0:20]
	mio_file.close()
	
def salva_stato():
	''' salva su file  lo stato attuale'''
	global temp_int_att
	global temp_est_att
	global reg_min_att
	global reg_max_att
	global temp_data_att
	global led_basso_att
	global led_alto_att
	mio_file=open(nome_file,"w")
	mio_file.write(str(reg_min_att)+"\n")
	mio_file.write(str(reg_max_att)+"\n")
	mio_file.write(str(temp_int_att)+"\n")
	mio_file.write(str(temp_est_att)+"\n")
	mio_file.write(str(led_basso_att)+"\n")
	mio_file.write(str(led_alto_att)+"\n")
	mio_file.write(str(temp_data_att)+"\n")
	mio_file.close()

def Avvio_LCD():
  	  # Initialise display
  	  Lcd.lcd_init(LCD_RS,LCD_E,LCD_D4,LCD_D5,LCD_D6,LCD_D7,LCD_Back)
  	  # Accensione backlight
  	  Lcd.lcd_backlight(True)
  	  time.sleep(0.5)
          # Send some centred test
          Lcd.lcd_string("--------------------",1,2)
          Lcd.lcd_string("C.H.I.P. computer",2,2)
          Lcd.lcd_string("Works",3,2)
          Lcd.lcd_string("--------------------",4,2)
	  time.sleep(5)

def main():
	global temp_int
	global temp_est
	global temp_int_att
	global temp_est_att
	global reg_min
	global reg_max
	global reg_min_att
	global reg_max_att
	global halt
	global rileggi
	# acquisisce stato iniziale
	leggi_stato()
	mostra_cambi(0)
	while(not halt): 
		''' testa eventuali cambi di Temp o di Estremi di Allarme'''
		temp_int_att,temp_est_att=Misura()
		OK_Change=cambiato()
		if rileggi:
			OK_Change=True
			rileggi=False
		if (OK_Change): 
			# mostra i dati
			mostra_cambi(1)
			temp_int=temp_int_att
			temp_est=temp_est_att
			reg_min=reg_min_att
			reg_max=reg_max_att
		else: pass
		# rilegge i sensori ogni x secondi
		time.sleep(2)
	# salva stato su file se Topic Cmd/alt '1'
	salva_stato()

if __name__ == '__main__':
	try:
	  tempture=TEMP()
	  os.system('clear')	  
	  if (Test): print "... tentativo di avvio ..."
	  init_mqtt()	  
	  mqttc.on_connect=on_connect
	  mqttc.on_message=on_message
	  # inizializza LCD
	  Avvio_LCD()
	  main()
	except KeyboardInterrupt:
          # salva stato su file in calso di Ctrl C
	  salva_stato()
  	  pass
	finally:
	  # spegne gli Switch di allarme 
	  mqttc.publish("Led/bassa",0)
	  mqttc.publish("Led/alta",0)
	  mqttc.publish("Temp/run","OFF")
	  # chiude LCD
	  Lcd.lcd_clear()
	  Lcd.lcd_string("Programma interrotto",2,2)
	  Lcd.lcd_string("Goodbye!",3,2)
	  time.sleep(1)
	  Lcd.lcd_stop()
	  # disconnetti mqtt
	  mqttc.disconnect()
	  os.system('clear')
	  print "Programma interrotto\nGoodbye!"
