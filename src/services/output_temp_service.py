#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from logzero import logger
from hardware.error import HardwareError


class OutputTempService(object):
    def __init__(self, sensor, scan_interval_ms, bus):
        """
        Args:
            sensor: temperature sensor, can be max31856 and max31865
            scan_interval_ms (int): scan interval in milisecond
        """
        self._sensor = sensor
        self._bus = bus
        self._interval = scan_interval_ms
        self._error_count = 0
        self._tempc = None

    async def start(self):
        self._sensor.connect()
        while True:
            try:
                tempc = self._sensor.read_measure_temp_c()
                self._tempc = tempc
                await self._bus.pub('output.temperature', {
                    "status": "ok",
                    "temperature": tempc,
                    "error_count": self._error_count
                })
            except HardwareError as error:
                self._error_count += 1
                self._sensor.disconnect()
                await asyncio.sleep(0.1)
                self._sensor.connect()
                await self._bus.pub('output.temperature', {
                    "status":
                    "error",
                    "message":
                    "output sensor '%s' got error: '%s'" % (error.name,
                                                            error.message)
                })
            await asyncio.sleep(float(self._interval) / 1000)

        self._sensor.disconnect()
