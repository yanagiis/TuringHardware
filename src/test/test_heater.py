#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from contextlib import suppress

from test.mock.pwm import MockPWM
from test.mock.bus import MockBus
from test.mock.pid import MockPID
import pytest
from services.heater import Heater


@pytest.mark.asyncio
async def test_heater_start():
    async def _req_cb(path, timeout):
        assert False

    async def _pub_cb(path, timeout):
        assert False

    async def _reg_rep_cb(path, callback):
        assert path == 'tank.heater'

    async def _reg_sub_cb(path, callback):
        assert False

    bus = MockBus()
    bus.req_cb = _req_cb
    bus.pub_cb = _pub_cb
    bus.reg_rep_cb = _reg_rep_cb
    bus.reg_sub_cb = _reg_sub_cb

    pwm = MockPWM()
    pid = MockPID()
    heater = Heater(pwm, pid, 1000, bus)

    loop = asyncio.get_event_loop()
    task = loop.create_task(heater.start())

    await asyncio.sleep(0.5)
    assert pwm._open is True
    assert pwm._start is True
    task.cancel()


@pytest.mark.asyncio
async def test_heater_command():
    async def _req_cb(path, timeout):
        assert False

    async def _pub_cb(path, timeout):
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

    pid = MockPID()
    heater = Heater(pwm, pid, 1000, bus)

    response = await heater.command_callback({'command': 'get'})
    assert response['status'] == 'ok'
    assert response['duty_cycle'] == 50
    assert response['frequency'] == 51

    response = await heater.command_callback({'command': 'put', 'temperature': 80})
    assert response['status'] == 'ok'
