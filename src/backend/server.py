# -*- coding: utf-8 -*-

import asyncio
from aiohttp import web
from aiohttp_index import IndexMiddleware
from backend import barista
from backend import cookbook
from backend import machine
from backend.cookbook_manager import CookbookManager

from services.output_temp_service import OutputTempClient
from services.tank_temp_service import TankTempClient
from services.tank_water_service import TankWaterClient
from services.refill_service import RefillClient
from services.heater import HeaterClient
from services.barista.barista import BaristaClient


async def start_backend(config, bus):

    username = config['username']
    password = config['password']
    host = config['host']
    port = config['port']
    database = config['database']

    url = "mongodb://%s:%s@%s:%d/%s" % (username, password, host, port,
                                        database)
    cookbook_mgr = CookbookManager(url)
    await cookbook_mgr.connect()

    app = web.Application(middlewares=[IndexMiddleware()])
    app['cookbook_mgr'] = cookbook_mgr

    app['output_temp_client'] = OutputTempClient(bus)
    app['tank_temp_client'] = TankTempClient(bus)
    app['tank_water_client'] = TankWaterClient(bus)
    app['refill_client'] = RefillClient(bus)
    app['heater_client'] = HeaterClient(bus)
    app['barista_client'] = BaristaClient(bus)

    app.router.add_route('*', '/api/barista/{id}/brew', barista.BrewView)
    app.router.add_route('*', '/api/barista/jog', barista.JogView)
    app.router.add_route('*', '/api/cookbooks/{id}', cookbook.CookbookView)
    app.router.add_route('*', '/api/cookbooks', cookbook.CookbooksView)
    app.router.add_route('*', '/api/machine', machine.MachineView)
    app.router.add_route('*', '/api/machine/tank/temperature',
                         machine.TankTemperatureView)

    app.router.add_static(
        '/', path=str('backend/build'), name='build', show_index=True)

    loop = asyncio.get_event_loop()
    await loop.create_server(app.make_handler(), '0.0.0.0', 3001)
