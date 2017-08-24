#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from logzero import logger


class RTD(object):
    RTD_PT100 = 0x0
    RTD_PT1000 = 0x1


class RTDSensorError(Exception):
    def __init__(self, msg):
        self.message = msg


class MAX31865(object):

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

    def __init__(self, spidev):
        """
        Args:
            spidev (SPI): max31865 communication interface
        """
        self._spi = spidev

    def connect(self):
        self._spi.open()

    def disconnect(self):
        self._spi.close()

    def readMeasureTempC(self):
        [rtd_msb, rtd_lsb] = self._read_reg(MAX31865.ADDR_RTDH, 2)
        if rtd_lsb & 0x1 != 0:
            raise RTDSensorError("MAX31865 get fault")

        rtd_adc_code = ((rtd_msb << 8) | rtd_lsb) >> 1
        return (rtd_adc_code / 32) - 256

    def _read_reg(self, addr, size):
        return self._spi.transfer([addr], size)

    def _write_reg(self, addr, data):
        self._spi.transfer([addr] + data, 0)
