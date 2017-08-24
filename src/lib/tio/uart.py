#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib.tio import tio
from serial import Serial


class UARTConfig(object):
    """ UART configuration

    Attributes:
        baudrate (int): UART baudrate. e.g. 9600, 57600, 115200, default is 115200.
        rtscts (bool): Hardware flow control, default is False
        dsrdts (bool): Hardware flow control, default is False
        read_timeout (int): max read time in second, default is 1
        write_timeout (int): max write time in second, default is 1
    """

    def __init__(self):
        self.baudrate = 115200
        self.rtscts = False
        self.dsrdtr = False
        self.read_timeout = 1
        self.write_timeout = 1


class UART(tio.IO, tio.Reader, tio.Writer):
    """ UART interface
    """
    def __init__(self, devpath, uart_config):
        """
        Args:
            devpath (string): UART device path. e.g. /dev/ttyUSB0
            uart_config (UARTConfig):
        """
        self._devpath = devpath
        self._config = uart_config
        self._serial = None

    def open(self):
        if self._serial is None:
            self._serial = Serial(
                self._devpath,
                self._config.baudrate,
                timeout=self._config.read_timeout,
                writeTimeout=self._config.write_timeout)

    def close(self):
        if self._serial is not None:
            self._serial.close()
            self._serial = None

    def read(self, readsize):
        return self._serial.read(readsize)

    def write(self, data):
        return self._serial.write(data)
