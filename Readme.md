# Micropython driver for onewire and the DS18x20 sensor

This two classes support the DS18x20 sensor and the onewire protocol
used by this sensor on Pycom devices. Similar classes exists for the Micropython.org 
version of MicroPython, which make use of the built-in onewire driver.

## Class Onewire

## Methods

## Class DS18X20

## Methods


## Example

Copy `ds18x20.py` and `onewire.py` to the board, and the file `ds18x20_example.py`.
Connect the data line of the sensor to P10, GND to GND and Vcc of the sensor to the 3.3V
output of your device. You need also to attach a pull-up resistor of 4.7kOhm between the
data line and Vcc of the sensor. The internal pull-up of the ES32 may not be strong enough.

Then you may start that example with:

`import ds18x20_example`

The code of the example reads as:
``` python
import time
from machine import Pin
from ds18x20_new import DS18X20
from onewire_new import OneWire

#DS18B20 data line connected to pin P10
ow = OneWire(Pin('P10'))
temp = DS18X20(ow)
roms = temp.scan()

temp.convert_temp()
while True:
    time.sleep(1)
    for rom in roms:
        print(temp.read_temp(rom), end=" ")
    print()
    temp.convert_temp()
```
