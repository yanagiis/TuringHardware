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
        self._bus.reg_rep('tank.water', self.rep_water_command)
        while True:
            self.pub_water_status()
            await asyncio.sleep(float(self._interval) / 1000)

    async def pub_water_status(self):
        if not self._sensor.is_connected() and not self._sensor.connect():
            await self._bus.pub('tank.water', {
                "status": "error",
                "message": "Cannot connect to sensor"
            })
            return

        is_water_full = self._sensor.is_water_full()
        if is_water_full != self._is_water_full:
            self._is_water_full = is_water_full
            await self._bus.pub('tank.water', self._get_status())

    async def rep_water_command(self, data):
        if not self._sensor.is_connected() and not self._sensor.connect():
            return {"status": "error", "message": "Cannot connect to sensor"}

        cmd = data['command']
        if cmd == 'get':
            return self._get_status()
        return {"status": "error", "message": "Unknown command '%s'" % cmd}

    def _get_status(self):
        return {"status": "ok", "water": self._is_water_full}
