#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib.tio import tio
from serial import serial_for_url
from logzero import logger
import socket


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
        self._serial = serial_for_url(self._devpath, do_not_open=True)

    def open(self):
        self._serial.baudrate = self._config.baudrate
        self._serial.timeout = self._config.read_timeout
        #self._serial.writeTimeout = self._config.write_timeout
        logger.info("Open '%s' with baudrate %d", self._devpath,
                    self._config.baudrate)
        self._serial.open()

    def close(self):
        if self._serial is not None:
            self._serial.close()
            self._serial = None
            logger.info("Close '%s'", self._devpath)

    def read(self, readsize):
        return self._serial.read(readsize)

    def write(self, data):
        return self._serial.write(data)
