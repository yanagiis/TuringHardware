# -*- coding: utf-8 -*-

from aiohttp import web
import json
import jsonschema
from jsonschema import validate
from backend import response
from backend.process_translator import process_to_points
from logzero import logger


class BrewView(web.View):
    async def post(self):
        cookbook_id = self.request.match_info.get('id', None)
        if cookbook_id is None:
            return await response.response(404, 'Missing cookbook id', None)
        cookbook_mgr = self.request.app['cookbook_mgr']
        cookbook = await cookbook_mgr.get_cookbook(cookbook_id)

        points_array = []
        for process in cookbook['processes']:
            points = process_to_points(process)
            if points is None:
                logger.error("Cannot translate process")
                logger.error("%s", json.dumps(process))
                return await response.response(500, 'Cookbook translate error',
                                               None)
            points_array += points

        barista_client = self.request.app['barista_client']
        await barista_client.brew([point.toDict() for point in points_array])

        return await response.response(200, 'Brew successfully', None)


class JogView(web.View):
    schema = {
        "type": "object",
        "properties": {
            "x": {
                "type": "number"
            },
            "y": {
                "type": "number"
            },
            "z": {
                "type": "number"
            },
            "f": {
                "type": "number"
            },
            "e": {
                "type": "number"
            },
            "e0": {
                "type": "number"
            },
            "e1": {
                "type": "number"
            },
            "t": {
                "type": "number"
            },
            "time": {
                "type": "number"
            }
        }
    }

    async def post(self):
        return await web.json_response(
            200, 'Send the jog command to the printer successfully', None)
