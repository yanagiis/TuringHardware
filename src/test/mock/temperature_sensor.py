# -*- coding: utf-8 -*-


class MockTemperatureSensor(object):
    def __init__(self):
        self._is_connected = False
        self.temp = 0

    def connect(self):
        self._is_connected = True
        return True

    def disconnect(self):
        self._is_connected = False
        return True

    def is_connected(self):
        return self._is_connected

    def read_measure_temp_c(self):
        return self.temp
