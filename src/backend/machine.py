# -*- coding: utf-8 -*-

from aiohttp import web
from backend import response


class MachineView(web.View):
    async def get(self):
        output_temp_client = self.request.app['output_temp_client']
        tank_temp_client = self.request.app['tank_temp_client']
        tank_water_client = self.request.app['tank_water_client']
        refill_client = self.request.app['refill_client']
        heater_client = self.request.app['heater_client']

        output_temp = await output_temp_client.get_temperature()
        tank_temp = await tank_temp_client.get_temperature()
        water_level = await tank_water_client.get_water_level()
        refill_status = await refill_client.get()
        heater_status = await heater_client.get_status()

        return await response.response(200, "Get machine status successfully",
                                       {
                                           "output_temperature": output_temp,
                                           "tank_temperature": tank_temp,
                                           "water_level": water_level,
                                           "refill_status": refill_status,
                                           "heater_status": heater_status
                                       })


class TankTemperatureView(web.View):
    async def put(self):
        payload = await self.request.json()
        temperature = payload['temperature']
        heater_client = self.request.app['heater_client']
        await heater_client.set_temperature(temperature)

        return await response.response(200,
                                       'get tank temperature successfully',
                                       {"tank_temperature": temperature})
