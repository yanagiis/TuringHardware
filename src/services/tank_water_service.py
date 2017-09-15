#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from logzero import logger


class TankWaterService(object):
    def __init__(self, sensor, scan_interval_ms, bus):
        """
        Args:
            sensor (water detector):
            scan_interval_ms (int): scan interval in milisecond
        """
        self._sensor = sensor
        self._is_water_full = None
        self._interval = scan_interval_ms
        self._bus = bus

    async def start(self):
        self._sensor.connect()

        while True:
            try:
                is_water_full = self._sensor.is_water_full()
                if is_water_full != self._is_water_full:
                    self._is_water_full = is_water_full
                    await self._bus.pub('tank.water',
                                        {"water": self._is_water_full})
                await asyncio.sleep(float(self._interval) / 1000)
            except asyncio.CancelledError:
                logger.info("Tank water service shutdown")

        self._sensor.disconnect()
