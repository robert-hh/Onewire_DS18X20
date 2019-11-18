# DS18x20 temperature sensor driver for MicroPython.
#
# Convenience adapter class for reading a single
# DS18X20 temperature sensor attached to the 1-Wire bus.
# MIT license; Copyright (c) 2019 Andreas Motl
#
from ds18x20 import DS18X20


class DS18X20Single(DS18X20):
    def __init__(self, onewire):
        super().__init__(onewire)
        self.roms = self.scan()
        assert len(self.roms) == 1, "Not (only) one sensor on the bus"

    def convert_temp(self):
        return super().convert_temp(self.roms[0])

    def read_temp(self):
        return super().read_temp(self.roms[0])
