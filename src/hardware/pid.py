#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class PID(object):
    def __init__(self, kp, ki, kd, upper, lower):
        """
        Args:
            kp, ki, kd (float): PID parameters
            upper (float): upper bound of output value
            lower (float): lower bound of output value
        """
        self._upper = upper
        self._lower = lower

        self._kp = None
        self._ki = None
        self._kd = None

        self._iterm = None
        self._last_measure = None

        self.turing(kp, ki, kd)
        self.reset()

    def compute(self, measure, setpoint, diff_time):
        if self._last_measure is None:
            self._last_measure = measure

        error = setpoint - measure

        self._iterm += self._ki * error * diff_time
        self._iterm = self._limit_value(self._iterm)

        dinput = measure - self._last_measure
        output = self._kp * error + self._iterm - (
            self._kd * dinput / diff_time)
        output = self._limit_value(output)

        self._last_measure = measure

    def reset(self):
        self._iterm = 0
        self._last_measure = None

    def _limit_value(self, value):
        if value > self._upper:
            return self._upper
        elif value < self._lower:
            return self._lower
        return value

    def turing(self, kp, ki, kd):
        self._kp = kp
        self._ki = ki
        self._kd = kd
