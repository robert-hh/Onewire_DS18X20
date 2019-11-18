# DS18x20 temperature sensor driver for MicroPython.
# MIT license; Copyright (c) 2018 Robert Hammelrath
#
# Convenience adapter class for reading a single
# DS18X20 temperature sensor attached to the 1-Wire bus.
#
from ds18x20 import DS18X20


class DS18X20Single(DS18X20):

    def convert_temp(self, rom=None):
        if rom is None and len(self.roms) == 1:
            rom = self.roms[0]
        return super().convert_temp(rom)

    def read_temp(self, rom=None):
        if rom is None and len(self.roms) == 1:
            rom = self.roms[0]
        return super().read_temp(rom)
