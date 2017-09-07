#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from periphery import GPIO


class WaterDetector(object):
    """ water detector driver
    """

    def __init__(self, gpio_pin):
        self._gpio_pin = gpio_pin
        self._gpio = None

    def connect(self):
        self._gpio = GPIO(self._gpio_pin, "in")

    def disconnect(self):
        self._gpio = None

    def is_water_full(self):
        """
        Returns:
            bool: return True if detect water full, otherwise return False
        """
        return self._gpio.read()
