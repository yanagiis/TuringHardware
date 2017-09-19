#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from logzero import logger
from hardware.error import HardwareError
from hardware.sensor import Sensor


class RTD(object):
    RTD_PT100 = 0x0
    RTD_PT1000 = 0x1


class MAX31865Config(object):
    def __init__(self):
        self.wire = MAX31865.WIRE_2
        self.mode = MAX31865.MODE_AUTOMATIC


class MAX31865(Sensor):

    WIRE_2 = 0
    WIRE_3 = 1
    WIRE_4 = 0

    MODE_ONESHOT = 0
    MODE_AUTOMATIC = 1

    ADDR_WRITE_MASK = 0x80

    ADDR_CR = 0x0
    ADDR_RTDH = 0x1
    ADDR_RTDL = 0x2
    ADDR_HFTH = 0x3
    ADDR_HFTL = 0x4
    ADDR_LFTH = 0x5
    ADDR_LFTL = 0x6
    ADDR_FAULT = 0x7

    R_REF = 400.0  # reference ohm
    RTD_0 = 100.0  # PT100 probe has 100 ohm at 0 degree C

    # Callendar-Van Dusen equation:
    # R(T) = R0(1 + aT + bT2 + c(T - 100)T3)
    # where:
    #     T = temperature (C)
    #     R(T) = resistance at T
    #     R0 = resistance at T = 0C
    #     IEC 751 specifies α = 0.00385055 and the following
    #     Callendar-Van Dusen coefficient values:
    #         a = 3.90830 x 10^-3
    #         b = -5.77500 x 10^-7
    #         c = -4.18301 x 10^-12 for -200C < T < 0C, 0 for 0C < T < +850C

    # Linearizing Temperature Data
    # For a temperature range of -100C to +100C, a good
    # approximation of temperature can be made by simply
    # using the RTD data as shown below:
    # Temperature (C) ≈ (ADC code/32) – 256

    CV_A = 3.9083E-3
    CV_B = -5.775E-7
    CV_C = 0

    def __init__(self, spidev, config):
        """
        Args:
            spidev (SPI): max31865 communication interface
            config (MAX31865Config): max31865 configuration
        """
        self._spi = spidev
        self._config = config
        self._is_connected = False

    def connect(self):
        """
        Returns:
            bool: True if connect success, otherwise return False
        """

        if self.is_connected():
            return True

        logger.info("Connect to max31865")
        self._spi.open()
        self.wire = self._config.wire
        self.mode = self._config.mode

        if self.wire != self._config.wire:
            logger.error("max31865 set wire failed")
            self._spi.close()
            return False
        if self.mode != self._config.mode:
            logger.error("max31865 set mode failed")
            self._spi.close()
            return False

        self._enable()
        self._is_connected = True
        return True

    def disconnect(self):
        logger.info("Disconnect max31865")
        if self.is_connected():
            self._disable()
            self._spi.close()
        self._is_connected = False

    def is_connected(self):
        return self._is_connected

    def read_measure_temp_c(self):
        if not self.is_connected():
            logger.error("max31865 is not connected")
            raise HardwareError('max31865', 'is not connected')

        [rtd_msb, rtd_lsb] = self._read_reg(MAX31865.ADDR_RTDH, 2)
        if rtd_lsb & 0x1 != 0:
            logger.error("MAX31865 get fault")
            raise HardwareError('max31865', 'sensor return fault')

        rtd_adc_code = ((rtd_msb << 8) | rtd_lsb) >> 1

        if rtd_adc_code == 0:
            logger.error("max31865 get zero value")
            raise HardwareError('max31865', 'get zero value')

        return (rtd_adc_code / 32) - 256

    def _enable(self):
        [cr_value] = self._read_reg(MAX31865.ADDR_CR, 1)
        cr_value = (cr_value & 0x7f) | (1 << 7)
        self._write_reg(MAX31865.ADDR_CR, [cr_value])

    def _disable(self):
        [cr_value] = self._read_reg(MAX31865.ADDR_CR, 1)
        cr_value = (cr_value & 0x7f)
        self._write_reg(MAX31865.ADDR_CR, [cr_value])

    @property
    def mode(self):
        [cr_value] = self._read_reg(MAX31865.ADDR_CR, 1)
        return (cr_value & 0x40) >> 6

    @mode.setter
    def mode(self, mode):
        [cr_value] = self._read_reg(MAX31865.ADDR_CR, 1)
        cr_value = (cr_value & 0xbf) | (mode << 6)
        self._write_reg(MAX31865.ADDR_CR, [cr_value])

    @property
    def wire(self):
        [cr_value] = self._read_reg(MAX31865.ADDR_CR, 1)
        return (cr_value & 0x10) >> 4

    @wire.setter
    def wire(self, wire):
        [cr_value] = self._read_reg(MAX31865.ADDR_CR, 1)
        cr_value = (cr_value & 0xef) | (wire << 4)
        self._write_reg(MAX31865.ADDR_CR, [cr_value])

    def _read_reg(self, addr, size):
        return self._spi.transfer([addr], size)

    def _write_reg(self, addr, data):
        self._spi.transfer([addr | MAX31865.ADDR_WRITE_MASK] + data, 0)
