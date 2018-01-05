# -*- coding: utf-8 -*-

import math
from time import sleep
from services.barista.point import Point
from services.barista import command

POINT_INTERVAL = 2
MOVE_FEEDRATE = 5000


class Coordinates(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    @staticmethod
    def delta(src, dst):
        return (dst.x - src.x, dst.y - src.y, dst.z - src.z)

    @staticmethod
    def distance(src, dst):
        (delta_x, delta_y, delta_z) = Coordinates.delta(src, dst)
        return math.sqrt(delta_x**2 + delta_y**2 + delta_z**2)


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

    src = Coordinates(x=coordinates_x + radius_from, y=coordinates_y, z=z_from)
    dst = Coordinates(x=coordinates_x + radius_to, y=coordinates_y, z=z_to)
    center = Coordinates(x=coordinates_x, y=coordinates_y, z=z_from)

    points = _make_spiral(src, dst, center, cylinder)

    path_len = (len(points) - 1) * POINT_INTERVAL
    feedrate = path_len / (time / 60)
    point_water = water / len(points)
    for point in points:
        point.t = temperature
        point.f = feedrate
        point.e = point_water

    move_point = Point.create_move_point(radius_from, 0, z_from, MOVE_FEEDRATE)
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
        Point.create_move_point(
            x=coordinates_x, y=coordinates_y, z=z, f=MOVE_FEEDRATE),
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

    src = Coordinates(x=coordinates_x + radius, y=coordinates_y, z=z)
    dst = Coordinates(x=coordinates_x + radius, y=coordinates_y, z=z)
    center = Coordinates(x=coordinates_x, y=coordinates_y, z=z)

    points = _make_spiral(src, dst, center, cylinder)

    path_len = (len(points) - 1) * POINT_INTERVAL
    feedrate = path_len / (time / 60)
    point_water = water / len(points)
    for point in points:
        point.t = temperature
        point.f = feedrate
        point.e = point_water

    move_point = Point.create_move_point(coordinates_x + radius, 0, z,
                                         MOVE_FEEDRATE)
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

    center = Coordinates(x=coordinates_x, y=coordinates_y, z=z)
    vertex = Coordinates(x=coordinates_x, y=coordinates_y + radius, z=z)

    vertexs = [
        _rotate_coord(vertex, 0, center),
        _rotate_coord(vertex, 120, center),
        _rotate_coord(vertex, 240, center),
        _rotate_coord(vertex, 360, center),
    ]

    rotate_theta_per_cylinder = int(360 / cylinder)

    points = []
    theta = 0
    for c in range(0, cylinder):
        begin = _rotate_coord(vertexs[0], theta, center)
        points.append(
            Point.create_move_point(
                x=begin.x, y=begin.y, z=begin.z, f=MOVE_FEEDRATE))
        for i in range(0, len(vertexs) - 1):
            src = _rotate_coord(vertexs[i], theta, center)
            dst = _rotate_coord(vertexs[i + 1], theta, center)
            line = _make_line(src, dst)
            points += line
        theta += rotate_theta_per_cylinder

    total_len = 3 * math.sqrt(3) * radius
    feedrate = total_len / (time / 60)
    point_water = (len(points) - cylinder) / water

    for point in points:
        point.t = temperature
        point.f = feedrate
        point.e = point_water

    return points


def _move_to_points(process):
    coordinates_x = process['coordinates']['x']
    coordinates_y = process['coordinates']['y']
    z = process['z']
    return [
        Point.create_move_point(
            x=coordinates_x, y=coordinates_y, z=z, f=MOVE_FEEDRATE)
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
    return Point.create_point(
        x=point.x * cos - point.y * sin,
        y=point.x * sin + point.y * cos,
        z=point.z,
        e=point.e,
        e1=point.e1,
        e2=point.e2,
        f=point.f)


def _translate_point(point, x, y):
    point.x += x
    point.y += y


def _make_line(src, dst):
    (delta_x, delta_y, delta_z) = Coordinates.delta(src, dst)
    distance = Coordinates.distance(src, dst)
    num_points = int(distance / POINT_INTERVAL)
    (step_x, step_y, step_z) = (delta_x / num_points, delta_y / num_points,
                                delta_z / num_points)

    coord = Coordinates(src.x, src.y, src.z)
    points = []
    num_count = 0
    while num_count < num_points:
        points.append(Point.create_point(x=coord.x, y=coord.y, z=coord.z))
        coord.x += step_x
        coord.y += step_y
        coord.z += step_z
        num_count += 1

    return points


def _make_spiral(src, dst, center, cylinder):
    rotate_theta = cylinder * 360
    radius_src = Coordinates.distance(center, src)
    radius_dst = Coordinates.distance(center, dst)

    radius_acc_per_degree = (radius_dst - radius_src) / rotate_theta
    z_acc_per_degree = (dst.z - src.z) / rotate_theta

    points = []
    radius = radius_src
    current_theta = 0
    while current_theta < rotate_theta:
        theta = (360 * POINT_INTERVAL) / (2 * math.pi * radius)
        radius += (radius_acc_per_degree * theta)
        current_theta += theta
        coord = Coordinates(x=radius, y=0, z=src.z)
        coord = _rotate_coord(coord, current_theta, center)
        coord.z += z_acc_per_degree
        points.append(Point.create_point(x=coord.x, y=coord.y, z=coord.z))
    return points


def _rotate_coord(coord, theta, center):
    radians = math.radians(theta)
    cos = math.cos(radians)
    sin = math.sin(radians)
    return Coordinates(
        x=coord.x * cos - coord.y * sin + center.x,
        y=coord.x * sin + coord.y * cos + center.y,
        z=coord.z)


_mapping = {
    "Spiral": _spiral_to_points,
    "FixedPoint": _fixedpoint_to_points,
    "Move": _move_to_points,
    "Wait": _wait_to_points,
    "Mix": _mix_to_points,
    "Calibration": _calibration_to_points,
    "Home": _home_to_points,
    "Triangle": _triangle_to_points,
    "Circle": _circle_to_points,
}
