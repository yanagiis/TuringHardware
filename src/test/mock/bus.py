# -*- coding: utf-8 -*-


class MockBus(object):
    def __init__(self):
        self.req_cb = None
        self.pub_cb = None
        self.reg_rep_cb = None
        self.reg_sub_cb = None

    async def start(self):
        raise NotImplementedError()

    async def req(self, path, timeout):
        await self.req_cb(path, timeout)

    async def reg_rep(self, path, callback):
        await self.reg_rep_cb(path, callback)

    async def pub(self, path, payload):
        await self.pub_cb(path, payload)

    async def reg_sub(self, path, callback):
        await self.reg_sub_cb(path, callback)
