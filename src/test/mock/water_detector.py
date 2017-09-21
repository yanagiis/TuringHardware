# -*- coding: utf-8 -*-


class MockWaterDetector(object):
    def __init__(self):
        self._is_water_full = False
        self._is_connected = False

    def connect(self):
        self._is_connected = True
        return True

    def disconnect(self):
        self._is_connected = False
        return True

    def is_water_full(self):
        return self._is_water_full

    def is_connected(self):
        return self._is_connected
