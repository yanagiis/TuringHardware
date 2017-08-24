#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from logzero import logger


class TC(object):
    B_TYPE = 0x0
    E_TYPE = 0x1
    J_TYPE = 0x2
    K_TYPE = 0x3
    N_TYPE = 0x4
    R_TYPE = 0x5
    S_TYPE = 0x6
    T_TYPE = 0x7


class TCSensorError(Exception):
    def __init__(self, msg):
        self.message = msg


class MAX31856(object):

    ADDR_CR0 = 0x0
    ADDR_CR1 = 0x1
    ADDR_MASK = 0x2
    ADDR_CJHF = 0x3
    ADDR_CJLF = 0x4
    ADDR_LTHFTH = 0x5
    ADDR_LTHFTL = 0x6
    ADDR_LTLFTH = 0x7
    ADDR_LTLFTL = 0x8
    ADDR_CJTO = 0x9
    ADDR_CJTH = 0xA
    ADDR_CJTL = 0xB
    ADDR_LTCBH = 0xC
    ADDR_LTCBM = 0xD
    ADDR_LTCBL = 0xE
    ADDR_SR = 0xF

    RESOLUTION_TC = 0.0078125
    RESOLUTION_CJ = 0.015625

    def __init__(self, spidev):
        """
        Args:
            spidev (SPI): max31856 communication interface
        """
        self._spi = spidev
        self._tc_type = None

    def connect(self):
        self._spi.open()

    def disconnect(self):
        self._spi.close()

    def readMeasureTempC(self):
        [temp0, temp1, temp2, fault] = self._read_reg(MAX31856.ADDR_LTCBH, 4)

        if fault != 0:
            logger.error("MAX31856 get fault: %02x", fault)
            raise TCSensorError("MAX31856 get fault: %02x" % fault)

        tempc = ((temp0 << 16) | (temp1 << 8) | temp2) >> 5
        if temp0 & 0x80 != 0:
            tempc -= 0x80000

        return tempc * MAX31856.RESOLUTION_TC

    def readColdJunctionTempC(self):
        [temp0, temp1] = self._read_reg(MAX31856.ADDR_CJTH, 2)
        tempc = ((temp0 << 8) | temp1) >> 2
        if temp0 & 0x80 != 0:
            tempc -= 0x4000

        return tempc * MAX31856.RESOLUTION_CJ

    @tc_type.getter
    def tc_type(self):
        cr1 = self._read_reg(MAX31856.ADDR_CR1, 1)
        return cr1 & 0x7

    @tc_type.setter
    def tc_type(self, tc_type):
        """
        Args:
            tc_type: (TC.TYPE)
        """
        if not TC.B_TYPE <= tc_type <= TC.T_TYPE:
            raise ValueError("arg 'value' should be TC TYPE")
        [cr1] = self._read_reg(MAX31856.ADDR_CR1, 1)
        cr1 = (cr1 & 0xf0) | tc_type
        self._write_reg(MAX31856.ADDR_CR1, [cr1])

    @sample_avg.getter
    def sample_avg(self):
        avg = self._read_reg(MAX31856.ADDR_CR1, 1)
        return avg >> 4

    @sample_avg.setter
    def sample_avg(self, sample):
        [avg] = self._read_reg(MAX31856.ADDR_CR1, 1)
        avg = (avg & 0x0f) | sample
        self._write_reg(MAX31856.ADDR_CR1, [avg])

    def _read_reg(self, addr, size):
        return self._spi.transfer([addr], size)

    def _write_reg(self, addr, data):
        self._spi.transfer([addr] + data, 0)
