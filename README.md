# TINY
python modules to manage the board TINY RTC

TINY.py is a python module to handle all of TINY RTC devices.

In particular, it manages via I2C:

-> RTC Chip DS1307
-> The EPROM chip AT24C32

Via OneWire:
-> If present the temperature sensor DS18B20
-> also it runs DS18B20 sensors without TINY RTC
