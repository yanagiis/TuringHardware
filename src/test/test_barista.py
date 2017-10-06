# -*- coding: utf-8 -*-

import asyncio
from services.barista import barista
from test.mock.bus import MockBus
from test.mock.pid import MockPID
import pytest


class MovingDev(object):
    def __init__(self):
        self.sent_commands = []

    def connect(self, retry_times):
        return True

    def send(self, command):
        self.sent_commands.append(command)

    def recv(self):
        return "ok"


class ExtruderDev(object):
    def __init__(self):
        self.sent_commands = []

    def connect(self, retry_times):
        return True

    def send(self, command):
        self.sent_commands.append(command)

    def recv(self):
        return "ok"


@pytest.mark.asyncio
async def test_barista_start():
    async def _req_cb(path, timeout):
        assert False

    async def _pub_cb(path, timeout):
        assert False

    async def _reg_rep_cb(path, callback):
        assert path == 'barista'

    async def _reg_sub_cb(path, callback):
        assert False

    bus = MockBus()
    bus.req_cb = _req_cb
    bus.pub_cb = _pub_cb
    bus.reg_rep_cb = _reg_rep_cb
    bus.reg_sub_cb = _reg_sub_cb

    pid = MockPID()
    pos = barista.WasteWaterPosition(x=0, y=0, z=0)
    b = barista.Barista(MovingDev(), ExtruderDev(), pid, pos, 5000, bus)

    loop = asyncio.get_event_loop()
    task = loop.create_task(b.start())
    response = await b.command_callback({'command': 'get'})
    assert response['status'] == 'ok'

    task.cancel()


@pytest.mark.asyncio
async def test_barista_brew():
    async def _req_cb(path, data, timeout):
        if path == 'tank.refill':
            return {'status': 'ok'}
        if path == 'output.temperature':
            return {'status': 'ok', 'temperature': 50}

    async def _pub_cb(path, timeout):
        assert False

    async def _reg_rep_cb(path, callback):
        assert path == 'barista'

    async def _reg_sub_cb(path, callback):
        assert False

    bus = MockBus()
    bus.req_cb = _req_cb
    bus.pub_cb = _pub_cb
    bus.reg_rep_cb = _reg_rep_cb
    bus.reg_sub_cb = _reg_sub_cb

    pid = MockPID()
    moving = MovingDev()
    extruder = ExtruderDev()
    pos = barista.WasteWaterPosition(x=70, y=50, z=180)
    b = barista.Barista(moving, extruder, pid, pos, 5000, bus)

    await b.brew([{'type': 'command', 'name': 'home'}])
    assert len(moving.sent_commands) == 1
    assert moving.sent_commands[0] == 'G28'

    await b.brew([{'type': 'command', 'name': 'calibration'}])
    assert moving.sent_commands[0] == 'G28'
    assert moving.sent_commands[1] == 'G1 X70.00000 Y50.00000 Z180.00000 F5000.00000'
