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

    async def pub_tank_temperature(self):
        if not self._sensor.is_connected() and not self._sensor.connect():
            await self._bus.pub('tank.temperature', {
                "status": "error",
                "message": "Cannot connect to sensor"
            })
            return

        try:
            tempc = self._sensor.read_measure_temp_c()
            self._tempc_available = True
            await self._bus.pub('tank.temperature',
                                {"status": "ok",
                                 "temperature": tempc})
        except HardwareError as error:
            self._tempc_available = False
            self._error_count += 1
            self._sensor.disconnect()
            await self._bus.pub('tank.temperature', {
                "status":
                "error",
                "message":
                "output sensor '%s' got error: '%s'" % (error.name,
                                                        error.message)
            })

    async def start(self):
        while True:
            self.pub_tank_temperature()
            await asyncio.sleep(float(self._interval) / 1000)
