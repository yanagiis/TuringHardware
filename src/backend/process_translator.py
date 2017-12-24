# -*- coding: utf-8 -*-

import math
from time import sleep
from services.barista.point import Point
from services.barista import command

POINT_INTERVAL = 2


def process_to_points(process):
    """
    Attributes:
        process:
    Return:
        Array(Points) or None
    """
    if process['name'] in _mapping:
        return _mapping[process['name']](process)
    return None


def _spiral_to_points(process):

    coordinates_x = process['coordinates']['x']
    coordinates_y = process['coordinates']['y']
    z_from = process['z']['from']
    z_to = process['z']['to']
    time = process['time']
    water = process['water']
    temperature = process['temperature']
    radius_from = process['radius']['from']
    radius_to = process['radius']['to']
    cylinder = process['cylinder']

    rotate_theta = cylinder * 360
    acceleration = (radius_to - radius_from) / rotate_theta

    current_theta = 0
    points = []
    radius = radius_from
    while current_theta < rotate_theta:
        theta = (360 * POINT_INTERVAL) / (2 * math.pi * radius)
        radius += (acceleration * theta)
        current_theta += theta

        point = Point.create_point(x=radius, y=0)
        _rotate_point(point, current_theta)
        points.append(point)

    # translate z
    z = z_from
    z_step = (z_to - z_from) / len(points)
    for point in points:
        point.z = z
        z += z_step

    # feedrate
    path_len = (len(points) - 1) * POINT_INTERVAL
    feedrate = path_len / (time / 60)
    point_water = water / len(points)
    for point in points:
        _translate_point(point, coordinates_x, coordinates_y)
        point.t = temperature
        point.f = feedrate
        point.e = point_water

    move_point = Point.create_move_point(radius_from, 0, z_from, 5000)
    points.insert(0, move_point)

    return points


def _fixedpoint_to_points(process):
    coordinates_x = process['coordinates']['x']
    coordinates_y = process['coordinates']['y']
    z = process['z']
    time = process['time']
    water = process['water']
    temperature = process['temperature']

    points = [
        Point.create_move_point(x=coordinates_x, y=coordinates_y, z=z, f=5000),
    ]

    water_per_point = float(water) / (time * 10)
    for _ in range(time * 10):
        points.append(
            Point.create_point(e=water_per_point, f=0.1, t=temperature))
    return points


def _circle_to_points(process):
    coordinates_x = process['coordinates']['x']
    coordinates_y = process['coordinates']['y']
    z = process['z']
    time = process['time']
    water = process['water']
    radius = process['radius']
    cylinder = process['cylinder']
    temperature = process['temperature']

    points = []
    current_theta = 0
    rotate_theta = cylinder * 360
    step_theta = (360 * POINT_INTERVAL) / (2 * math.pi * radius)
    while current_theta < rotate_theta:
        current_theta += step_theta
        point = Point.create_point(x=radius, y=0, z=z)
        points.append(_rotate_point(point, current_theta))

    #feedrate
    path_len = (len(points) - 1) * POINT_INTERVAL
    feedrate = path_len / (time / 60)
    point_water = water / len(points)
    for point in points:
        _translate_point(point, coordinates_x, coordinates_y)
        point.t = temperature
        point.f = feedrate
        point.e = point_water

    move_point = Point.create_move_point(radius, 0, z, 5000)
    points.insert(0, move_point)

    return points


def _triangle_to_points(process):
    coordinates_x = process['coordinates']['x']
    coordinates_y = process['coordinates']['y']
    z = process['z']
    time = process['time']
    water = process['water']
    cylinder = process['cylinder']
    radius = process['radius']
    temperature = process['temperature']

    current_theta = 0
    rotate_theta = cylinder * 360
    step_theta = (360 * POINT_INTERVAL) / (2 * math.pi * radius)

    vertex = Point.create_point(x=0, y=radius)
    vertexs = [
        _rotate_point(vertex, 0),
        _rotate_point(vertex, 120),
        _rotate_point(vertex, 240),
    ]

    points = []
    path_len = 0
    side_length = (2 * radius) / math.sqrt(3)

    while current_theta < rotate_theta:
        current_theta += step_theta
        points += [_rotate_point(v, current_theta) for v in vertexs]
        path_len += side_length * 3

    feedrate = path_len / (time / 60)
    point_water = water / len(points)
    for point in points:
        _translate_point(point, coordinates_x, coordinates_y)
        point.z = z
        point.t = temperature
        point.f = feedrate
        point.e = point_water

    points.insert(0,
                  Point.create_move_point(
                      x=coordinates_x, y=coordinates_y, z=z))

    return points


def _move_to_points(process):
    coordinates_x = process['coordinates']['x']
    coordinates_y = process['coordinates']['y']
    z = process['z']
    return [
        Point.create_move_point(x=coordinates_x, y=coordinates_y, z=z, f=5000)
    ]


def _wait_to_points(process):
    return [command.Wait(process['time'])]


def _mix_to_points(process):
    return [command.Mix(process['temperature'])]


def _calibration_to_points(_):
    return [command.Calibration()]


def _home_to_points(_):
    return [command.Home()]


def _rotate_point(point, theta):
    radians = math.radians(theta)
    cos = math.cos(radians)
    sin = math.sin(radians)
    point.x = point.x * cos - point.y * sin
    point.y = point.x * sin + point.y * cos


def _translate_point(point, x, y):
    point.x += x
    point.y += y


_mapping = {
    "Spiral": _spiral_to_points,
    "FixedPoint": _fixedpoint_to_points,
    "Move": _move_to_points,
    "Wait": _wait_to_points,
    "Mix": _mix_to_points,
    "Calibration": _calibration_to_points,
    "Home": _home_to_points
}
