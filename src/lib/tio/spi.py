#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib.tio import tio
from spidev import SpiDev
from logzero import logger


class SPIConfig(object):
    """
    SPI configuration

    Attributes:
        speed (int): SPI max speed in HZ
        mode (int): SPI CPOL and CPHA setting
    """

    MODE_CPOL = 0x2
    MODE_CPHA = 0x1

    def __init__(self):
        self.speed = 1000000
        self.mode = SPIConfig.MODE_CPOL | SPIConfig.MODE_CPHA


class SPI(tio.IO):
    """ SPI interface (abstract)
    """

    def open(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def transfer(self, writedata, readsize):
        """
        Args:
            writedata (bytes): data to write
            readsize (int): size of read data after writing
        """
        raise NotImplementedError


class HWSPI(SPI):
    """ Hardware SPI
    """

    def __init__(self, device, ce, config):
        """
        Args:
            device (int): the number of SPI device
            ce (int): the number of chip select of SPI device
            config (SPIConfig):
        """
        self._device = device
        self._ce = ce
        self._spi = SpiDev()

    def open(self):
        logger.info("Open SPI(%d,%d)", self._device, self._ce)
        self._spi.open()

    def close(self):
        logger.info("Close SPI(%d,%d)", self._device, self._ce)
        self._spi.close()

    def transfer(self, writedata, readsize):
        buf = self._spi.xfer(writedata + [0] * readsize)
        return buf[len(writedata):]
