import time
from machine import Pin
from ds18x20 import DS18X20
from onewire import OneWire

#DS18B20 data line connected to pin P10
ow = OneWire(Pin('P10'))
power = Pin('P11', Pin.OUT, value=0)
temp = DS18X20(ow)
print("Powermode = ", temp.powermode(power))
roms = temp.scan()

temp.convert_temp()
while True:
    time.sleep(1)
    for rom in roms:
        print(temp.read_temp(rom), end=" ")
    print()
    temp.convert_temp()

