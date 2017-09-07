#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from logzero import logger
from hardware.error import HardwareError


class MAX31856Config(object):
    def __init__(self):
        self.tc_type = MAX31856.K_TYPE
        self.sample_avg = MAX31856.SAMPLE_AVG_1


class MAX31856(object):

    B_TYPE = 0x0
    E_TYPE = 0x1
    J_TYPE = 0x2
    K_TYPE = 0x3
    N_TYPE = 0x4
    R_TYPE = 0x5
    S_TYPE = 0x6
    T_TYPE = 0x7

    MODE_MANUAL = 0
    MODE_AUTOMATIC = 1

    SAMPLE_AVG_1 = 0x0
    SAMPLE_AVG_2 = 0x1
    SAMPLE_AVG_4 = 0x2
    SAMPLE_AVG_8 = 0x3
    SAMPLE_AVG_16 = 0x4

    ADDR_WRITE_MASK = 0x80

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

    def __init__(self, spidev, config):
        """
        Args:
            spidev (SPI): max31856 communication interface
            config (MAX31856Config): max31856 configuration
        """
        self._spi = spidev
        self._config = config

    def connect(self):
        """ Connect to max31856
        Try to connect max31856 and check the function is worked or not.

        Returns:
            bool: True if connect success, otherwise return False
        """
        logger.info("Connect to max31856")
        self._spi.open()
        self.tc_type = self._config.tc_type
        self.sample_avg = self._config.sample_avg

        # Check out this sensor is work or not
        if self.tc_type != self._config.tc_type:
            logger.error("max31856 set tc type failed")
            self._spi.close()
            return False
        if self.sample_avg != self._config.sample_avg:
            logger.error("max31856 set sample average failed")
            self._spi.close()
            return False

    def disconnect(self):
        logger.info("Disconnect max31856")
        self._spi.close()

    def read_measure_temp_c(self):
        [temp0, temp1, temp2, fault] = self._read_reg(MAX31856.ADDR_LTCBH, 4)

        if fault != 0:
            logger.error("MAX31856 get fault: %02x", fault)
            raise HardwareError('max31856', 'error code: %02d' % fault)

        tempc = ((temp0 << 16) | (temp1 << 8) | temp2) >> 5
        if temp0 & 0x80 != 0:
            tempc -= 0x80000

        return tempc * MAX31856.RESOLUTION_TC

    def read_coldjunction_temp_c(self):
        [temp0, temp1] = self._read_reg(MAX31856.ADDR_CJTH, 2)
        tempc = ((temp0 << 8) | temp1) >> 2
        if temp0 & 0x80 != 0:
            tempc -= 0x4000

        return tempc * MAX31856.RESOLUTION_CJ

    @property
    def tc_type(self):
        cr1 = self._read_reg(MAX31856.ADDR_CR1, 1)
        return cr1 & 0x7

    @tc_type.setter
    def tc_type(self, tc_type):
        """
        Args:
            tc_type: (TC.TYPE)
        """
        if not MAX31856.B_TYPE <= tc_type <= MAX31856.T_TYPE:
            raise ValueError("arg 'value' should be TC TYPE")
        [cr1] = self._read_reg(MAX31856.ADDR_CR1, 1)
        cr1 = (cr1 & 0xf0) | tc_type
        self._write_reg(MAX31856.ADDR_CR1, [cr1])

    @property
    def sample_avg(self):
        avg = self._read_reg(MAX31856.ADDR_CR1, 1)
        return avg >> 4

    @sample_avg.setter
    def sample_avg(self, sample):
        [avg] = self._read_reg(MAX31856.ADDR_CR1, 1)
        avg = (avg & 0x0f) | sample
        self._write_reg(MAX31856.ADDR_CR1, [avg])

    @property
    def mode(self):
        [cr0] = self._read_reg(MAX31856.ADDR_CR0, 1)
        return cr0 >> 7

    @mode.setter
    def mode(self, mode):
        [cr0] = self._read_reg(MAX31856.ADDR_CR0, 1)
        cr0 = (cr0 & 0x7f) | (mode << 7)
        self._write_reg(MAX31856.ADDR_CR0, [cr0])

    def _read_reg(self, addr, size):
        return self._spi.transfer([addr], size)

    def _write_reg(self, addr, data):
        self._spi.transfer([addr | MAX31856.ADDR_WRITE_MASK] + data, 0)
