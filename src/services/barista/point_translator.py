# -*- coding: utf-8 -*-


def point_to_gcode(point):

    if point.x is None and point.y is None and point.z is None:
        return None
    if point.f is None:
        return None

    gcode = "G1"
    if point.x is not None:
        gcode += " X%0.5f" % point.x
    if point.y is not None:
        gcode += " Y%0.5f" % point.y
    if point.z is not None:
        gcode += " Z%0.5f" % point.z

    gcode += " F%0.5f" % point.f
    return gcode


def point_to_hcode(point):

    if point.e1 is None and point.e2 is None:
        return None
    if point.time is None:
        return None

    hcode = "H"
    if point.e1 is not None:
        hcode += " E0 %0.5f" % point.e1
    if point.e2 is not None:
        hcode += " E1 %0.5f" % point.e2
    hcode += " T %0.5f" % point.time
    return hcode
