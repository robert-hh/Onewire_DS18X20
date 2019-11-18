# Micropython driver for onewire and the DS18x20 sensor

This two classes support the DS18x20 sensor and the onewire protocol
used by this sensor on Pycom devices. Similar classes exists for the Micropython.org 
version of MicroPython, which make use of the built-in onewire driver.

## Class Onewire

ow = Onewire(Pin_object)

Pin_object must be an output caspable pin. It will be configured by driver.

## Methods

### reset([required=False])

Resets the bus. If the parameter required is True, AssertError is raised if no
device on the bus responds

### value = readbit()
### value = readbyte()
### buffer = readbytes(count)
### readinto(buffer)

Read data form the bus, either a single bit, or a byte, or a sequence of bytes.
readbytes expects the numer of bytes to be read. These will be returned.
Readinto expects a buffer to be supplied, and len(buffer) bytes will be read.

### writebit(bit [, powerpin=None])
### writebyte(byte [, powerpin=Nobe])
### writebytes(buffer)

Write data to the bus. powerpin, if supplied, must be a Pin object. This pin will
be set if the bit is tranferred resp. the last bit of a byte is transferred.
writebytes send all bytes in the buffer.

### select_rom(rom)

Send the message to select a specific device based on the rom number. This number
will be obtained by scan(). The selected device will respond to further read and write
calls.

### devices = scan()

Return the list of rom numbers of all devices on the onwire bus.

### _search_rom()

Internal function. Search devices on the bus and obtain the rom number.  

-------
## Class DS18X20

sensor = DS18X20(onewire)

onewire must be an instance of the Onewire class.

## Methods

### devices = scan()

Return the list of DS18x2x devices on the bus. Only devices with rom type 
0x10, 0x22 and 0x22 are selected.

### mode = powermode([pin_object=None])

Test the powermode on the bus. If the bus has strong power, 1 is returned. In case of
paraisitic power, 0 is returned. pin_object must be a pin object, which is output mode 
capable. It will be use to switch between soft and strong pullup for parasitic power.
To enable string pull-up, the pin will be set to 1 (high). The power has then to be 
supplied by an external circuit. In case of just a few active devices on the devices, 
a small signal schottky diode (e.g. 1N5817) between the pin_object and 
the data bus is sufficient.

### convert_temp([rom=None])

Start temperture conversion. If rom is supplied, only this device will start conversion.
Otherwise, all devices on the bus will be started.

### data = read_scratch(rom)

Read the scratchpad memory of the addressed device. 9 bytes of data will be returned

### write_scratch(rom, data)

Write to the scratchpad of the addressed devices. data shall be three bytes. 
The first two bytes are the high and low alarm temperature. 
The third by is the configuration. See the DS18B20 data sheet for details.

### read_temp(rom)

Get the temperature reading of the addressed device as degree Celsuis.
In case of an CRC error, None is returned.

### res = resolution(rom [, bits])

Get or set the resolution of a sensor. If the paramter bits is specified,
the resolution is set to that value. Valid values are 9 though 12.
If bits is not specified, the actual resolution is returned. The value set is not 
permanent. After a power cycle it is reset to 12. The conversion time depends on the
resoltion. The figures are: 

|bits|Conversion time (ms)|
|:---:|:---:|
|9|94|
|10|188|
|11|375|
|12|750|  

### deg_f = fahrenheit(celsius)
### deg_k = kelvin(celsius)
### deg_r = rankine(celsius)

Three fuctions converting the celsius value returned by read_temp() into other scales.
the rankine scale is surely the least important. 
  
-------
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
  
  The same example using parasitic power and setting the resolution of the first device: 

```
import time
from machine import Pin
from ds18x20 import DS18X20
from onewire import OneWire

#DS18B20 data line connected to pin P10
ow = OneWire(Pin('P10'))
temp = DS18X20(ow)
pm = temp.powermode(Pin('P11'))
print("Powermode = ", pm)
roms = temp.scan()

temp.resolution(roms[0], 9)
print("Resolution", temp.resolution(roms[0]))

temp.convert_temp()
while True:
    time.sleep(1)
    for rom in roms:
        print(temp.read_temp(rom), end=" ")
    print()
    temp.convert_temp()
```
