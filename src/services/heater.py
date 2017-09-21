#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from logzero import logger


class Heater(object):
    def __init__(self, pwm, pid, scan_interval_ms, bus):
        self._pwm = pwm
        self._pid = pid
        self._interval_ms = scan_interval_ms
        self._pwm_task = None
        self._recv_task = None
        self._bus = bus
        self._target_temp = 0

    async def start(self):
        self._pwm.open()
        self._pwm_task = asyncio.get_event_loop().create_task(
            self._pwm.start())
        await self._bus.reg_rep('tank.heater', self.command_callback)

        logger.info("start heating water")
        while True:
            response = await self._bus.req('tank.temperature',
                                           {'command': 'get'})
            if response['status'] == 'ok':
                temp = response['temperature']
                dutycycle = self._pid.compute(temp, self._target_temp,
                                              float(self._interval_ms) / 1000)
                self._pwm.dutycycle = dutycycle
            else:
                logger.warning(
                    'tank.temperature got a error, set heater dutycycle to 0')
                self._pwm.dutycycle = 0

            await asyncio.sleep(float(self._interval_ms) / 1000)

    async def stop(self):
        self._pwm_task.cancel()
        self._recv_task.cancel()
        self._pwm.close()
        logger.info("stop heating water")

    async def command_callback(self, data):
        cmd = data['command']
        if cmd == 'get':
            return {
                "status": "ok",
                "duty_cycle": self._pwm.duty_cycle,
                "frequency": self._pwm.frequency
            }
        return {"status": "error", "message": "unknown command"}
