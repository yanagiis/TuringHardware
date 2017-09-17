#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from logzero import logger
from hardware.error import HardwareError


class TankTempService(object):
    def __init__(self, sensor, scan_interval_ms, bus):
        """
        Args:
            sensor: temperature sensor, can be max31856 and max31865
            scan_interval_ms (int): scan interval in milisecond
        """
        self._sensor = sensor
        self._interval = scan_interval_ms
        self._error_count = 0
        self._tempc = None
        self._tempc_available = False
        self._bus = bus

    async def start(self):
        self._sensor.connect()
        while True:
            try:
                tempc = self._sensor.read_measure_temp_c()
                self._tempc_available = True
                self._bus.pub('tank.temperature',
                              {"status": "ok",
                               "temperature": tempc})
            except HardwareError as error:
                self._tempc_available = False
                self._error_count += 1
                self._sensor.disconnect()
                asyncio.sleep(0.1)
                self._bus.pub('tank.temperature', {
                    "status":
                    "error",
                    "message":
                    "output sensor '%s' got error: '%s'" % (error.name,
                                                            error.message)
                })
            await asyncio.sleep(float(self._interval) / 1000)

        self._sensor.disconnect()
