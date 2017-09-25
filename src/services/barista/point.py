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

    @staticmethod
    def create_move_point(x=None, y=None, z=None, f=None):
        point = Point()
        point.x = x
        point.y = y
        point.z = z
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
