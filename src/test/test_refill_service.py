#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from test.mock.pwm import MockPWM
from test.mock.bus import MockBus
import pytest
from services.refill_service import RefillService


@pytest.mark.asyncio
async def test_refiller_start():
    async def _req_cb(path, data, timeout):
        assert path == 'tank.water'
        assert data['command'] == 'get'
        return {'status': 'ok', 'water': True}

    async def _pub_cb(path, timeout):
        assert False

    async def _reg_rep_cb(path, callback):
        assert path == 'tank.refill'

    async def _reg_sub_cb(path, callback):
        assert False

    bus = MockBus()
    bus.req_cb = _req_cb
    bus.pub_cb = _pub_cb
    bus.reg_rep_cb = _reg_rep_cb
    bus.reg_sub_cb = _reg_sub_cb

    pwm = MockPWM()
    refiller = RefillService(pwm, 1000, bus)

    loop = asyncio.get_event_loop()
    task = loop.create_task(refiller.start())

    await asyncio.sleep(0.5)
    task.cancel()


@pytest.mark.asyncio
async def test_refiller_command():
    async def _req_cb(path, data, timeout):
        assert False

    async def _pub_cb(path, data):
        assert False

    async def _reg_rep_cb(path, callback):
        assert False

    async def _reg_sub_cb(path, callback):
        assert False

    bus = MockBus()
    bus.req_cb = _req_cb
    bus.pub_cb = _pub_cb
    bus.reg_rep_cb = _reg_rep_cb
    bus.reg_sub_cb = _reg_sub_cb

    pwm = MockPWM()
    pwm.duty_cycle = 50
    pwm.frequency = 51

    service = RefillService(pwm, 1000, bus)

    response = await service.command_callback({'command': 'get'})
    assert response['status'] == 'ok'
    assert response['stop'] is True

    response = await service.command_callback({'command': 'put'})
    assert response['status'] == 'error'

    response = await service.command_callback({'command': 'start'})
    assert response['status'] == 'ok'
    assert pwm._open is True
