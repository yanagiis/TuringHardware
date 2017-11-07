# -*- coding: utf-8 -*-

import json


class Wait(object):
    def __init__(self, time):
        self.time = time

    def toDict(self):
        return {"name": "wait", "time": self.time}


class Mix(object):
    def __init__(self, temperature):
        self.temperature = temperature

    def toDict(self):
        return {"name": "mix", "t": self.temperature}


class Calibration(object):
    def toDict(self):
        return {"name": "calibration"}


class Home(object):
    def toDict(self):
        return {"name": "home"}
