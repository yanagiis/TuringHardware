#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib.tio import tio

from periphery import GPIO as sysGPIO, GPIOError
import RPi.GPIO as rGPIO

HARDWARE = gethardware()
if HARDWARE == 'BCM2709':
    rGPIO.setmode(rGPIO.BCM)


def gethardware():
    # Extract serial from cpuinfo file
    hardware = ""
    with open('/proc/cpuinfo', 'r') as f:
        try:
            for line in f:
                if line[0:6] == 'Hardware':
                    hardware = line[10:26]
        except:
            hardware = "ERROR"

    return hardware


class GPIO(object):
    @staticmethod
    def getpin(pin, direction):
        if HARDWARE == 'BCM2709':
            return _RPiGPIO(pin, direction)
        else:
            return _SysfsGPIO(pin, direction)


class _RPiGPIO(object):
    def __init__(self, pin, direction):
        self._pin = pin
        self._dir = direction

        if self._dir == "out":
            rGPIO.setup(pin, rGPIO.OUT)
        else:
            rGPIO.setup(pin, rGPIO.IN)

    def __del__(self):
        rGPIO.setup(self._pin, rGPIO.IN)

    def read(self):
        return rGPIO.input(self._pin)

    def write(self, value):
        output = rGPIO.LOW
        if value is True:
            output = rGPIO.HIGH
        else:
            output = rGPIO.LOW

        return rGPIO.output(self._pin, output)


class _SysfsGPIO(object):
    def __init__(self, pin, direction):
        self._pin = pin
        self._dir = direction
        self._gpio = sysGPIO(self._pin, direction)

    def __del__(self):
        sysGPIO(self._pin, "in")
        self._gpio = None

    def read(self):
        return self._gpio.read()

    def write(self, value):
        return self._gpio.write(value)
