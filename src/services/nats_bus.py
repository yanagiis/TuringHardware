#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers
from logzero import logger
import json


class NatsBus(object):
    def __init__(self, host, port):
        self._nats_client = NATS()
        self._url = "nats://%s:%d" % (host, port)

    async def start(self):
        retry_times = 0
        while True:
            try:
                logger.info("Try to connect to nats server '%s', %d times",
                            self._url, retry_times)
                await self._nats_client.connect(servers=[self._url])
                break
            except ErrNoServers:
                retry_times += 1
                logger.error("Cannot connect to nats server '%s'", self._url)
        logger.info("Connect to nats server '%s' successfully", self._url)

    async def req(self, path, payload):
        if not self._nats_client.is_connected:
            return None
        return await self._nats_client.request(
            path, json.dumps(payload).encode('utf-8'))

    async def reg_rep(self, path, callback):
        return await self.reg_sub(path, callback)

    async def pub(self, path, payload):
        if not self._nats_client.is_connected:
            return False
        await self._nats_client.publish(path,
                                        json.dumps(payload).encode('utf-8'))
        return True

    async def reg_sub(self, path, callback):
        if not self._nats_client.is_connected:
            return False
        await self._nats_client.subscribe(path, cb=callback)
        return True
