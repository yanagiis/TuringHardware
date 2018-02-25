#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class PID(object):
    def __init__(self, pid_p, pid_i, pid_d, lower, upper):
        """
        Args:
            pid_p, pid_i, pid_d (float): PID parameters
            lower (float): lower bound of output value
            upper (float): upper bound of output value
        """
        self.upper = upper
        self.lower = lower

        self._pid_p = None
        self._pid_i = None
        self._pid_d = None

        self._iterm = None
        self._last_measure = None

        self.turing(pid_p, pid_i, pid_d)
        self.reset()

    def compute(self, measure, setpoint, diff_time):
        """
        Args:
            measure (float): the actual value
            setpoint (float): the target value
            diff_time (float): elapsed time
        Return:
            float:
        """

        if self._last_measure is None:
            self._last_measure = measure

        error = setpoint - measure

        self._iterm += self._pid_i * error * diff_time
        self._iterm = self._limit_value(self._iterm)

        dinput = measure - self._last_measure
        if diff_time != 0:
            output = self._pid_p * error + self._iterm - (self._pid_d *
                                                          (dinput / diff_time))
        else:
            output = self._pid_p * error
        output = self._limit_value(output)

        self._last_measure = measure
        return output

    def reset(self):
        self._iterm = 0
        self._last_measure = None

    def _limit_value(self, value):
        if value > self.upper:
            return self.upper
        elif value < self.lower:
            return self.lower
        return value

    def turing(self, pid_p, pid_i, pid_d):
        self._pid_p = pid_p
        self._pid_i = pid_i
        self._pid_d = pid_d
