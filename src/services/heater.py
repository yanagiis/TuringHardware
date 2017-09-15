#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from logzero import logger


class Heater(object):
    def __init__(self, pwm, bus):
        self._pwm = pwm
        self._pwm_task = None
        self._recv_task = None
        self._bus = bus

    async def start(self):
        self._pwm.open()
        self._pwm_task = asyncio.get_event_loop().create_task(
            self._pwm.start())
        self._bus.reg_rep('tank.heater', self.heater_callback)
        logger.info("start heating water")

    async def stop(self):
        self._pwm_task.cancel()
        self._recv_task.cancel()
        self._pwm.close()
        logger.info("stop heating water")

    async def heater_callback(self, msg):
        cmd = msg.data.decode()
        if cmd == 'get':
            self._bus.pub(msg.reply, {
                "status": "ok",
                "duty_cycle": self._pwm.duty_cycle,
                "frequency": self._pwm.frequency
            })
        else:
            self._bus.pub(msg.reply,
                          {"status": "error",
                           "message": "unknown command"})
