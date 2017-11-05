#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from concurrent import futures
import asyncio
from logzero import logger
from services.tank_temp_service import TankTempClient


class Heater(object):
    def __init__(self, pwm, pid, scan_interval_ms, bus):
        self._pwm = pwm
        self._pid = pid
        self._interval_ms = scan_interval_ms
        self._pwm_task = None
        self._bus = bus
        self._target_temp = 0
        self._stop = False
        self._stop_event = asyncio.Event()
        self._tank_temp_client = TankTempClient(bus)

    async def start(self):
        self._stop = False
        self._pwm.open()
        self._pwm_task = asyncio.get_event_loop().create_task(
            self._pwm.start())
        await self._bus.reg_rep('tank.heater', self.command_callback)

        logger.info("start heating water")
        while not self._stop:
            temperature = await self._tank_temp_client.get_temperature()
            if temperature is None:
                logger.warn('Cannot get temperature, stop heat')
                self._pwm.dutycycle = 0
            else:
                dutycycle = self._pid.compute(temperature, self._target_temp,
                                              float(self._interval_ms) / 1000)
                self._pwm.dutycycle = dutycycle
            await asyncio.sleep(float(self._interval_ms) / 1000)

        self._pwm.stop()
        self._pwm.close()
        self._pwm_task = None
        self._stop_event.set()

    async def stop(self):
        self._stop = True
        await self._stop_event.wait()
        logger.info("stop heating water")

    async def command_callback(self, data):
        cmd = data['command']
        if cmd == 'get':
            return {
                "status": "ok",
                "target_temperature": self._target_temp,
                "duty_cycle": self._pwm.duty_cycle,
                "frequency": self._pwm.frequency
            }
        if cmd == 'put':
            self._target_temp = data['temperature']
            return {"status": "ok", "target_temperature": self._target_temp}
        return {"status": "error", "message": "unknown command"}


class HeaterClient(object):
    def __init__(self, bus):
        self._bus = bus

    async def get(self):
        try:
            response = await self._bus.req('tank.heater', {'command': 'get'})
            if response is None:
                logger.warn("Get 'tank.heater' timeout")
                return None
            if response['status'] != 'ok':
                logger.warn("Cannot get 'tank.heater' status: %s",
                            response['message'])
                return None
            return response
        except futures.TimeoutError:
            logger.warn("Cannot get 'tank.heater' status: request timeout")
            return None

    async def set_temperature(self, temperature):
        try:
            response = await self._bus.req('tank.heater', {'command': 'put'})
            if response is None:
                logger.warn("Update 'tank.heater' timeout")
                return None
            if response['status'] != 'ok':
                logger.warn("Cannot put 'tank.heater' status: %s",
                            response['message'])
                return None
            return response
        except futures.TimeoutError:
            logger.warn("Cannot put 'tank.heater' status: request timeout")
            return None
