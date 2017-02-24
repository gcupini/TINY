from TINY import EPROM
import time

ds=EPROM()
# scrive un byte
ds.set_byte(4090,99)
# Scrive una Stringa in EPROM
ds.set_str(4091,'Pippa')
# legge un Byet
print ds.get_byte(4090)
# legge stringa
print ds.get_str(4091,5)
