# -*- coding: utf-8 -*-

import time
import asyncio
from services.barista.point import Point
from services.barista.point_translator import point_to_gcode
from services.barista.point_translator import point_to_hcode
from services.refill_service import RefillClient
from services.output_temp_service import OutputTempClient
from services.tank_temp_service import TankTempClient


class WasteWaterPosition(Point):
    def __init__(self, x, y, z):
        super(WasteWaterPosition, self).__init__()
        self.x = x
        self.y = y
        self.z = z


class Barista(object):
    def __init__(self, moving_dev, extruder_dev, mix_pid_dev,
                 waste_water_position, default_moving_speed, bus):
        self._commands = {
            "wait": self._create_wait,
            "calibration": self._create_calibration,
            "waste_water": self._create_waste_water,
            "mix": self._create_mix,
            "home": self._create_home
        }

        self._moving_dev = moving_dev
        self._extruder_dev = extruder_dev
        self._mix_pid_dev = mix_pid_dev
        self._waste_water_position = waste_water_position
        self._default_moving_speed = 5000
        self._bus = bus
        self._refill = RefillClient(bus)
        self._output_temp = OutputTempClient(bus)
        self._tank_temp = TankTempClient(bus)

        self._high_temperature = None
        self._low_temperature = None
        self._accumulated_water = 0
        self._percentage = 0

        self._stop = False
        self._stop_event = asyncio.Event()
        self._queue = asyncio.Queue(maxsize=1)

        self._position = Point.create_point(x=0, y=0, z=0)

    def _create_wait(self, param):
        _time = param['time']

        async def implement(self):
            nonlocal _time
            while not self._stop and _time > 0:
                asyncio.sleep(1)
                _time -= 1
            return True

        return implement

    def _create_calibration(self, _):
        async def implement(self):
            # move
            await self._move_to_waste_water_position()

            # e1
            points = [Point.create_point(e1=3, t=1)] * 100
            self._handle_point(points)
            asyncio.sleep(1)
            self._high_temperature = self._get_temperature()
            if self._high_temperature is None:
                return False

            # e2
            points = [Point.create_point(e2=3, t=1)] * 100
            self._handle_point(points)
            asyncio.sleep(1)
            self._low_temperature = self._get_temperature()
            if self._low_temperature is None:
                return False
            return True

        return implement

    def _create_waste_water(self, _):
        async def implement(self):
            await self._move_to_waste_water_position()
            points = [Point.create_point(e1=3, e2=3, t=1)] * 10
            self._handle_point(points)
            return True

        return implement

    def _create_mix(self, param):
        target_temperature = param['t']

        async def implement(self):
            await self._move_to_waste_water_position()
            points = [Point.create_point(e=5, t=1)] * 2
            while True:
                self._handle_point(points)
                current_temperature = self._get_temperature()
                if abs(current_temperature - target_temperature) < 0.5:
                    break
            return True

        return implement

    def _create_home(self, _):
        async def implement(self):
            self._moving_dev.send('G28')
            self._set_position(x=0, y=0, z=0)
            return True

        return implement

    def _create_handle_points(self, point_params):
        async def implement(self):
            nonlocal point_params
            points = []
            for point_param in point_params:
                points.append(Point.create_point(*point_param))
            await self._handle_point(points)
            return True

        return implement

    async def _handle_point(self, points):
        previous_time = time.time()
        self._accumulated_water = 30
        self._percentage = 0

        for point in points:
            if point.e is not None:
                if self._accumulated_water >= 30:
                    temperature = self._get_temperature()
                    percentage = self._mix_pid_dev(temperature, point.t,
                                                   time.time() - previous_time)
                    self._accumulated_water = 0
                point.e1 = point.e * percentage
                point.e2 = point.e - point.e1
            gcode = point_to_gcode(point)
            hcode = point_to_hcode(point)

            if gcode is not None:
                self._moving_dev.send(gcode)
            if hcode is not None:
                self._extruder_dev.send(gcode)

            if gcode is not None:
                while self._moving_dev.recv() != 'ok':
                    await asyncio.sleep(0.1)
            if hcode is not None:
                while self._extruder_dev.recv() != 'ok':
                    await asyncio.sleep(0.1)

    async def start(self):
        await self._bus.reg_rep('barista', self.command_callback)

        # HOME, Set Unit to Millimeters,
        # Set to Absolute Positioning, Set extruder to relative mode
        for cmd in ['G28', 'G21', 'G90', 'M83']:
            self._moving_dev.send(cmd)

        while True:
            point_params = await self._queue.get()
            await self._stop_tank()

            commands = []
            for param in point_params:
                if param['command'] and param['name'] in self._commands:
                    commands += self._commands[param['name']]
                else:
                    commands += self._create_handle_points(param['points'])

            for command in commands:
                await command()

            await self._start_tank()

    async def command_callback(self, data):
        cmd = data['command']
        if cmd == 'get':
            return self._status()
        elif cmd == 'brew':
            points = data['points']
            try:
                self._queue.put_nowait(points)
                return {'status': 'ok'}
            except asyncio.QueueFull:
                return {'status': 'error', 'message': 'barista is busy'}


    async def _status(self):
        return {'status': 'ok'}

    async def _move_to_waste_water_position(self):
        points = [
            Point.create_move_point(
                x=self._waste_water_position.x,
                y=self._waste_water_position.y,
                z=self._waste_water_position.z,
                f=self._default_moving_speed)
        ]
        await self._handle_point(points)

    async def _set_position(self, x=None, y=None, z=None):
        if x is not None:
            self._position.x = x
        if y is not None:
            self._position.y = y
        if z is not None:
            self._position.z = z
