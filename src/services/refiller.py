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
        return True if self._pwm_task is not None else False

    async def refiller_callback(self, msg, data):
        cmd = data['command']
        if cmd == 'get':
            await self._bus.pub(msg.reply, self._status())
            return
        elif cmd == 'start':
            await self._start_pwm()
            await self._bus.pub(msg.reply, self._status())
            return
        elif cmd == 'stop':
            await self._stop_pwm()
            await self._bus.pub(msg.reply, self._status())
            return

        await self._bus.pub(msg.reply, {
            "success": False,
            "message": "Unknown command '%s'" % cmd
        })

    def _status(self):
        return {"success": True, "stop": self._is_pwm_stop()}
