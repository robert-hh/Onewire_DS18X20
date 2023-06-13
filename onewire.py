#!/usr/bin/env python3
#
# The crc8 implementation is a Python port of the C code published here:
# http://lentz.com.au/blog/tag/crc-table-generator
# As far as suitable, the copyrigth notice and the disclaimer of the link apply
#
"""
OneWire library for MicroPython
"""

import time
import machine

class OneWire:
    CMD_SEARCHROM = 0xf0
    CMD_READROM = 0x33
    CMD_MATCHROM = 0x55
    CMD_SKIPROM = 0xcc
    PULLUP_ON = 1

    def __init__(self, pin):
        self.pin = pin
        self.pin.init(pin.OPEN_DRAIN, pin.PULL_UP)
        self.disable_irq = machine.disable_irq
        self.enable_irq = machine.enable_irq
        self.crctab1 = (b"\x00\x5E\xBC\xE2\x61\x3F\xDD\x83"
                        b"\xC2\x9C\x7E\x20\xA3\xFD\x1F\x41")
        self.crctab2 = (b"\x00\x9D\x23\xBE\x46\xDB\x65\xF8"
                        b"\x8C\x11\xAF\x32\xCA\x57\xE9\x74")


    def reset(self, required=False):
        """
        Perform the onewire reset function.
        Returns True if a device asserted a presence pulse, False otherwise.
        """
        sleep_us = time.sleep_us
        pin = self.pin

        pin(0)
        sleep_us(480)
        i = self.disable_irq()
        pin(1)
        sleep_us(60)
        status = not pin()
        self.enable_irq(i)
        sleep_us(420)
        assert status is True or required is False, "Onewire device missing"
        return status

    def readbit(self):
        sleep_us = time.sleep_us
        pin = self.pin

        pin(1) # half of the devices don't match CRC without this line
        i = self.disable_irq()
        pin(0)
        # skip sleep_us(1) here, results in a 2 us pulse.
        pin(1)
        sleep_us(5) # 8 us delay in total
        value = pin()
        self.enable_irq(i)
        sleep_us(40)
        return value

    def readbyte(self):
        value = 0
        for i in range(8):
            value |= self.readbit() << i
        return value

    def readbytes(self, count):
        buf = bytearray(count)
        for i in range(count):
            buf[i] = self.readbyte()
        return buf

    def readinto(self, buf):
        for i in range(len(buf)):
            buf[i] = self.readbyte()

    def writebit(self, value, powerpin=None):
        sleep_us = time.sleep_us
        pin = self.pin

        i = self.disable_irq()
        pin(0)
        # sleep_us(1) # dropped for shorter pulses
        pin(value)
        sleep_us(60)
        if powerpin:
            pin(1)
            powerpin(PULLUP_ON)
        else:
            pin(1)
        self.enable_irq(i)

    def writebyte(self, value, powerpin=None):
        for i in range(7):
            self.writebit(value & 1)
            value >>= 1
        self.writebit(value & 1, powerpin)

    def write(self, buf):
        for b in buf:
            self.writebyte(b)

    def select_rom(self, rom):
        """
        Select a specific device to talk to. Pass in rom as a bytearray (8 bytes).
        """
        self.reset()
        self.writebyte(CMD_MATCHROM)
        self.write(rom)

    def crc8(self, data):
        """
        Compute CRC, based on tables
        """
        crc = 0
        for i in range(len(data)):
           crc ^= data[i] ## just re-using crc as intermediate
           crc = (self.crctab1[crc & 0x0f] ^
                  self.crctab2[(crc >> 4) & 0x0f])
        return crc

    def scan(self):
        """
        Return a list of ROMs for all attached devices.
        Each ROM is returned as a bytes object of 8 bytes.
        """
        devices = []
        diff = 65
        rom = False
        for i in range(0xff):
            rom, diff = self._search_rom(rom, diff)
            if rom:
                devices += [rom]
            if diff == 0:
                break
        return devices

    def _search_rom(self, l_rom, diff):
        if not self.reset():
            return None, 0
        self.writebyte(CMD_SEARCHROM)
        if not l_rom:
            l_rom = bytearray(8)
        rom = bytearray(8)
        next_diff = 0
        i = 64
        for byte in range(8):
            r_b = 0
            for bit in range(8):
                b = self.readbit()
                if self.readbit():
                    if b: # there are no devices or there is an error on the bus
                        return None, 0
                else:
                    if not b: # collision, two devices with different bit meaning
                        if diff > i or ((l_rom[byte] & (1 << bit)) and diff != i):
                            b = 1
                            next_diff = i
                self.writebit(b)
                if b:
                    r_b |= 1 << bit
                i -= 1
            rom[byte] = r_b
        return rom, next_diff

