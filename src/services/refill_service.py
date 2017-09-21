#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from logzero import logger


class RefillService(object):
    def __init__(self, pwm, scan_interval_ms, bus):
        super(RefillService, self).__init__()
        self._pwm = pwm
        self._pwm_task = None
        self._bus = bus
        self._force_stop = False
        self._interval_ms = scan_interval_ms

    async def start(self):
        await self._bus.reg_rep('tank.refill', self.command_callback)
        while True:
            if self._force_stop is False:
                response = await self._bus.req('tank.water',
                                               {'command': 'get'})
                if response['status'] != 'ok' or response['water'] is True:
                    await self._stop_pwm()
                else:
                    await self._start_pwm()
            else:
                await self._stop_pwm()
            await asyncio.sleep(float(self._interval_ms)/1000)

    async def stop(self):
        await self._stop_pwm()

    async def _start_pwm(self):
        if not self._is_pwm_stop():
            return

        self._pwm.open()
        self._pwm_task = asyncio.get_event_loop().create_task(
            self._pwm.start())
        logger.info("start refill water")

    async def _stop_pwm(self):
        if self._is_pwm_stop():
            return

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

    async def command_callback(self, data):
        cmd = data['command']
        if cmd == 'get':
            return self._status()
        elif cmd == 'start':
            self._force_stop = False
            return {'status': 'ok'}
        elif cmd == 'stop':
            self._force_stop = True
            return {'status': 'ok'}

        return {"status": "error", "message": "Unknown command '%s'" % cmd}

    def _status(self):
        return {"status": "ok", "stop": self._is_pwm_stop()}
