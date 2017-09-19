# -*- coding: utf-8 -*-

from hardware.pwm import PWM


class MockPWM(PWM):
    def __init__(self):
        self.dutycycle = 0
        self.freq = 0
        self._start = False
        self._open = True

    def open(self):
        self._open = True

    def close(self):
        self._open = False

    async def start(self):
        self._start = True
