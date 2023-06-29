# DS18x20 temperature sensor driver for MicroPython.
#
# Convenience adapter class for reading a single
# DS18X20 temperature sensor attached to the 1-Wire bus.
# MIT license; Copyright (c) 2019 Andreas Motl
#
from ds18x20 import DS18X20

class DS18X20Single(DS18X20):
    def __init__(self, onewire, scan=True):
        super().__init__(onewire)
        if scan:
            roms = self.scan()
            if len(roms) == 0:
                raise AssertionError('No sensor on the bus')
            elif len(roms) > 1:
                raise AssertionError('More than one sensor on the bus')
            self.rom = roms[0]
        else:
            self.rom = None

    def convert_temp(self):
        return super().convert_temp(self.rom)

    def read_temp(self):
        return super().read_temp(self.rom)
