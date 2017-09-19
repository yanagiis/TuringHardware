#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import asyncio
from test.mock.pwm import MockPWM
from test.mock.bus import MockBus
from services.heater import Heater


def test_heater_start():
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
    heater = Heater(pwm, bus)
    asyncio.get_event_loop().run_until_complete(heater.start())

    assert pwm._open is True
    assert pwm._start is True


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

    heater = Heater(pwm, bus)

    response = await heater.command_callback({'command': 'get'})
    assert response['status'] == 'ok'
    assert response['duty_cycle'] == 50
    assert response['frequency'] == 51

    response = await heater.command_callback({'command': 'put'})
    assert response['status'] == 'error'
