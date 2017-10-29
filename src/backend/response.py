# -*- coding: utf-8 -*-

from aiohttp import web
from bson.json_util import dumps


async def response(status, message, payload):
    data = {}
    if status is not None:
        data['status'] = status
    if message is not None:
        data['message'] = message
    if payload is not None:
        data['payload'] = payload
    return web.Response(text=dumps(data), status=status)
