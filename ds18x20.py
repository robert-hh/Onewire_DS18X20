#
# small class for reading the DS18x20 temperature sensor using
# the onewire module
#
"""
DS18x20 temperature sensor driver for MicroPython.

This driver uses the OneWire driver to control DS18S20 and DS18B20
temperature sensors.  It supports multiple devices on the same 1-wire bus.

The following example assumes the data of your DS18x20 is connected to P10

import time
from machine import Pin
from ds18x20 import DS18X20
from onewire import OneWire

ow = OneWire(Pin('P10'))
temp = DS18X20(ow)

while True:
    temp.start_conversion()
    time.sleep(1)
    print(temp.read_temp_async())
    time.sleep(1)

"""


class DS18X20(object):
    def __init__(self, onewire):
        self.ow = onewire
        self.roms = [rom for rom in self.ow.scan() if rom[0] == 0x10 or rom[0] == 0x28]
        try:
            1/1
            self.fp = True
        except TypeError:
            self.fp = False # floatingpoint not supported

    def isbusy(self):
        """
        Checks wether one of the DS18x20 devices on the bus is busy
        performing a temperature convertion
        """
        return not self.ow.read_bit()

    def start_conversion(self, rom=None):
        """
        Start the temp conversion on one DS18x20 device.
        Pass the 8-byte bytes object with the ROM of the specific device you want to read.
        """
        assert rom is not None, "ROM address missing or empty"
        ow = self.ow
        ow.reset()
        ow.select_rom(rom)
        ow.write_byte(0x44)  # Convert Temp

    def read_temp_async(self, rom):
        """
        Read the temperature of one DS18x20 device if the convertion is complete,
        otherwise return None.
        """
        if self.isbusy():
            return None

        assert rom is not None, "ROM address missing or empty"

        ow = self.ow
        ow.reset()
        ow.select_rom(rom)
        ow.write_byte(0xbe)  # Read scratch
        data = ow.read_bytes(9)
        if ow.crc8(data) == 0:
            return self.convert_temp(rom[0], data)
        else:
            return None

    def convert_temp(self, rom0, data):
        """
        Convert the raw temperature data into degrees celsius and return as a fixed point with 2 decimal places.
        """
        temp_lsb = data[0]
        temp_msb = data[1]
        if rom0 == 0x10:
            if temp_msb != 0:
                # convert negative number
                temp_read = temp_lsb >> 1 | 0x80  # truncate bit 0 by shifting, fill high bit with 1.
                temp_read = -((~temp_read + 1) & 0xff) # now convert from two's complement
            else:
                temp_read = temp_lsb >> 1  # truncate bit 0 by shifting
            count_remain = data[6]
            count_per_c = data[7]
            if self.fp:
                return temp_read - 25 + (count_per_c - count_remain) / count_per_c
            else:
                return 100 * temp_read - 25 + (count_per_c - count_remain) // count_per_c
        elif rom0 == 0x28:
            temp = None
            if self.fp:
                temp = (temp_msb << 8 | temp_lsb) / 16
            else:
                temp = (temp_msb << 8 | temp_lsb) * 100 // 16
            if (temp_msb & 0xf8) == 0xf8: # for negative temperature
                temp -= 0x1000
            return temp
        else:
            assert False
