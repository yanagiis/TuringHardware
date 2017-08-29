#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib.tio import tio
from periphery import GPIO
import asyncio


class PWM(tio.IO):
    """ PWM interface
    Attributes:
        dutycycle (float): 0 - 1 (0% - 100%)
        frequency (int): hz
    """

    def open(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError


class PWMConfig(object):
    def __init__(self):
        self.dutycycle = 0
        self.frequency = 0


class SWPWM(PWM):
    """ Software PWM
    """

    def __init__(self, gpio_pin, config, loop):
        """
        Args:
            gpio_pin (int): gpio pin number this PWM used
            config (PWMConfig): configuration for pwm
            loop (asyncio.loop):
        """
        self._gpio_pin = gpio_pin
        self._loop = loop
        self._dutycycle = config.dutycycle
        self._freq = config.frequency
        self._stop = 0
        self._gpio = None

    def open(self):
        self._gpio = GPIO(self._gpio_pin, "out")

    def close(self):
        self._gpio = GPIO(self._gpio_pin, "in")

    @property
    def dutycycle(self):
        """
        dutycycle (float): 0 - 1 (0% - 100%)
        """
        return self._dutycycle

    @dutycycle.setter
    def dutycycle(self, dutycycle):
        if not 0 < dutycycle < 1:
            raise ValueError("Duty cycle should be ranged in 0 and 1")
        self._dutycycle = dutycycle

    @property
    def frequency(self):
        """
        frequency (int): hz
        """
        return self._freq

    @frequency.setter
    def frequency(self, freq):
        self._freq = freq

    async def start(self):
        while not self._stop:
            on_time = self._dutycycle / self._freq
            off_time = (1 - self._dutycycle) / self._freq
            if on_time > 0:
                self._gpio.write(True)
                await asyncio.sleep(on_time)
            if off_time > 0:
                self._gpio.write(False)
                await asyncio.sleep(off_time)
            if on_time == 0 and off_time == 0:
                break

    def stop(self):
        self._stop = True
