#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from logzero import logger


class Refiller(object):
    def __init__(self, pwm, bus):
        super(Refiller, self).__init__()
        self._pwm = pwm
        self._pwm_task = None
        self._bus = bus

    async def start(self):
        await self._bus.reg_rep('tank.refiller', self.refiller_callback)

    async def stop(self):
        await self._stop_pwm()

    async def _start_pwm(self):
        self._pwm.open()
        self._pwm_task = asyncio.get_event_loop().create_task(
            self._pwm.start())
        logger.info("start refill water")

    async def _stop_pwm(self):
        self._pwm.stop()
        self._pwm.close()
        self._pwm_task.cancel()
        try:
            await self._pwm_task
        except asyncio.CancelledError:
            logger.info("stop refill water")
        self._pwm_task = None

    def _is_pwm_stop(self):
        return False if self._pwm_task is not None else True

    async def refiller_callback(self, data):
        cmd = data['command']
        if cmd == 'get':
            return self._status()
        elif cmd == 'start':
            await self._start_pwm()
            return self._status()
        elif cmd == 'stop':
            await self._stop_pwm()
            return self._status()

        return {"status": "error", "message": "Unknown command '%s'" % cmd}

    def _status(self):
        return {"status": "ok", "stop": self._is_pwm_stop()}
