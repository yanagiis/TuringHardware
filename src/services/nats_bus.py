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

    def cb_wrap(self, callback):
        async def wrap(msg):
            response = await callback(json.loads(msg.data.decode()))
            if response is not None:
                await self._nats_client.publish(
                    msg.reply, json.dumps(response).encode('utf-8'))

        return wrap

    async def _disconnected_cb(self):
        logger.info("Disconnected from nats server")

    async def _reconnected_cb(self):
        logger.info("Reconnected to nats server")

    async def _error_cb(self, e):
        logger.info("Nats connection error: %s", e)

    async def start(self):
        try:
            logger.info("Try to connect to nats server '%s'", self._url)
            await self._nats_client.connect(
                servers=[self._url],
                max_reconnect_attempts=-1,
                disconnected_cb=self._disconnected_cb,
                reconnected_cb=self._reconnected_cb,
                error_cb=self._error_cb)
            logger.info("Connect to nats server successfully")
        except ErrNoServers:
            pass

    async def req(self, path, payload, timeout=1):
        if not self._nats_client.is_connected:
            return None
        response = await self._nats_client.timed_request(
            path + '.rep', json.dumps(payload).encode('utf-8'), timeout)
        return json.loads(response.data.decode())

    async def reg_rep(self, path, callback):
        if not self._nats_client.is_connected:
            return False
        await self._nats_client.subscribe(
            path + '.rep', cb=self.cb_wrap(callback))
        return True

    async def pub(self, path, payload):
        if not self._nats_client.is_connected:
            return False
        await self._nats_client.publish(path + '.pub',
                                        json.dumps(payload).encode('utf-8'))
        return True

    async def reg_sub(self, path, callback):
        if not self._nats_client.is_connected:
            return False
        await self._nats_client.subscribe(
            path + '.pub', cb=self.cb_wrap(callback))
        return True
