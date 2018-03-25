#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import threading
import time
import RPi.GPIO as rGPIO

from lib.tio import tio
from hardware.gpio import GPIO
from hardware.hardware import HARDWARE


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

    async def start(self):
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

    def __init__(self, gpio_pin, config):
        """
        Args:
            gpio_pin (int): gpio pin number this PWM used
            config (PWMConfig): configuration for pwm
        """
        self._gpio_pin = gpio_pin
        self._dutycycle = config.dutycycle
        self._freq = config.frequency
        self._stop = False
        self._gpio = None
        self._stop_event = asyncio.Event()

    def open(self):
        self._gpio = GPIO.getpin(self._gpio_pin, "out")

    def close(self):
        self._gpio = None

    @property
    def dutycycle(self):
        """
        dutycycle (float): 0 - 1 (0% - 100%)
        """
        return self._dutycycle

    @dutycycle.setter
    def dutycycle(self, dutycycle):
        if not 0 <= dutycycle <= 1:
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
        self._stop = False
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
                await asyncio.sleep(1)
        self._stop_event.set()

    async def stop(self):
        self._stop = True
        await self._stop_event.wait()


class HWPWM(PWM):
    """ Hardware PWM
    """

    def __init__(self, gpio_pin, config):
        """
        Args:
            gpio_pin (int): gpio pin number this PWM used
            config (PWMConfig): configuration for pwm
        """
        self._gpio_pin = gpio_pin
        self._dutycycle = config.dutycycle
        self._freq = config.frequency
        self._gpio = None

    def open(self):
        rGPIO.setup(self._gpio_pin, rGPIO.OUT)
        self._gpio = rGPIO.PWM(self._gpio_pin, self._freq)

    def close(self):
        self._gpio = None

    @property
    def dutycycle(self):
        """
        dutycycle (float): 0 - 1 (0% - 100%)
        """
        return self._dutycycle

    @dutycycle.setter
    def dutycycle(self, dutycycle):
        if not 0 <= dutycycle <= 1:
            raise ValueError("Duty cycle should be ranged in 0 and 1")
        self._dutycycle = dutycycle
        self._gpio.ChangeDutyCycle(dutycycle * 100)

    @property
    def frequency(self):
        """
        frequency (int): hz
        """
        return self._freq

    @frequency.setter
    def frequency(self, freq):
        self._gpio.ChangeFrequency(freq)

    async def start(self):
        self._gpio.start(self._dutycycle * 100)

    async def stop(self):
        self._gpio.stop()
