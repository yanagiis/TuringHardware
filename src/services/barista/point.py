# -*- coding: utf-8 -*-


class Point(object):
    """
    Attributes:
        x (float): coordinates x (mm)
        y (float): coordinates y (mm)
        z (float): coordinates z (mm)
        f (float): feedrate per minute (mm/min)
        e (float): water yield (ml)
        e1 (float): water yield of extruder 1
        e2 (float): water yield of extruder 2
        t (float): target water temperature
        time (flota): water time of extruder 1 and 2
    """

    def __init__(self):
        self.x = None
        self.y = None
        self.z = None
        self.f = None
        self.e = None
        self.e1 = None
        self.e2 = None
        self.t = None
        self.time = None

    def toDict(self):
        _dict = {'name': 'point'}
        if self.x is not None:
            _dict['x'] = self.x
        if self.y is not None:
            _dict['y'] = self.y
        if self.z is not None:
            _dict['z'] = self.z
        if self.e is not None:
            _dict['e'] = self.e
        if self.f is not None:
            _dict['f'] = self.f
        if self.e1 is not None:
            _dict['e1'] = self.e1
        if self.e2 is not None:
            _dict['e2'] = self.e2
        if self.t is not None:
            _dict['t'] = self.t
        if self.time is not None:
            _dict['time'] = self.time
        return _dict

    @staticmethod
    def load(dicts):
        point = Point()
        if 'x' in dicts:
            point.x = dicts['x']
        if 'y' in dicts:
            point.y = dicts['y']
        if 'z' in dicts:
            point.z = dicts['z']
        if 'f' in dicts:
            point.f = dicts['f']
        if 'e' in dicts:
            point.e = dicts['e']
        if 'e1' in dicts:
            point.e1 = dicts['e1']
        if 'e2' in dicts:
            point.e2 = dicts['e2']
        if 't' in dicts:
            point.t = dicts['t']
        if 'time' in dicts:
            point.time = dicts['time']
        return point

    @staticmethod
    def create_move_point(x=None, y=None, z=None, f=None):
        point = Point()
        point.x = x
        point.y = y
        point.z = z
        point.f = f
        return point

    @staticmethod
    def create_point(x=None,
                     y=None,
                     z=None,
                     f=None,
                     e=None,
                     e1=None,
                     e2=None,
                     t=None,
                     time=None):
        point = Point()
        point.x = x
        point.y = y
        point.z = z
        point.f = f
        point.e = e
        point.e1 = e1
        point.e2 = e2
        point.t = t
        point.time = time
        return point
