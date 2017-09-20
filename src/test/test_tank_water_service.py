#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import asyncio
from test.mock.pwm import MockPWM
from test.mock.bus import MockBus
from test.mock.water_detector import MockWaterDetector
from services.tank_water_service import TankWaterService


@pytest.mark.asyncio
async def test_tank_water_service_pub():
    async def _req_cb(path, timeout):
        assert False

    async def _pub_cb(path, data):
        assert path == 'tank.water'
        assert data['status'] == 'ok'
        assert data['water'] is True

    async def _reg_rep_cb(path, callback):
        assert False

    async def _reg_sub_cb(path, callback):
        assert False

    bus = MockBus()
    bus.req_cb = _req_cb
    bus.pub_cb = _pub_cb
    bus.reg_rep_cb = _reg_rep_cb
    bus.reg_sub_cb = _reg_sub_cb

    sensor = MockWaterDetector()
    sensor._is_water_full = True

    service = TankWaterService(sensor, 1000, bus)
    await service.pub_water_status()
    assert sensor.is_connected() is True


@pytest.mark.asyncio
async def test_tank_water_service_command():
    async def _req_cb(path, timeout):
        assert False

    async def _pub_cb(path, data):
        assert path == 'tank.water'
        assert data['status'] == 'ok'
        assert data['water'] is True

    async def _reg_rep_cb(path, callback):
        assert False

    async def _reg_sub_cb(path, callback):
        assert False

    bus = MockBus()
    bus.req_cb = _req_cb
    bus.pub_cb = _pub_cb
    bus.reg_rep_cb = _reg_rep_cb
    bus.reg_sub_cb = _reg_sub_cb

    sensor = MockWaterDetector()
    sensor._is_water_full = True

    service = TankWaterService(sensor, 1000, bus)
    await service.pub_water_status()
    response = await service.rep_water_command({'command': 'get'})
    assert sensor.is_connected() is True
    assert response['status'] == 'ok'
    assert response['water'] is True
