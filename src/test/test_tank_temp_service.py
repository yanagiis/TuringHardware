#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import asyncio
from test.mock.pwm import MockPWM
from test.mock.bus import MockBus
from test.mock.temperature_sensor import MockTemperatureSensor
from services.tank_temp_service import TankTempService


@pytest.mark.asyncio
async def test_tank_temp_service_pub():
    async def _req_cb(path, timeout):
        assert False

    async def _pub_cb(path, data):
        assert path == 'tank.temperature'
        assert data['status'] == 'ok'
        assert data['temperature'] == 100

    async def _reg_rep_cb(path, callback):
        assert False

    async def _reg_sub_cb(path, callback):
        assert False

    bus = MockBus()
    bus.req_cb = _req_cb
    bus.pub_cb = _pub_cb
    bus.reg_rep_cb = _reg_rep_cb
    bus.reg_sub_cb = _reg_sub_cb

    sensor = MockTemperatureSensor()
    sensor.temp = 100
    service = TankTempService(sensor, 1000, bus)
    await service.pub_tank_temperature()
    assert sensor.is_connected() is True
