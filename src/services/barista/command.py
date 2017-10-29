# -*- coding: utf-8 -*-

import json


class Wait(object):
    def __init__(self, time):
        self.time = time

    def toJSON(self):
        return json.dumps({"name": "wait", "time": self.time})


class Mix(object):
    def __init__(self, temperature):
        self.temperature = temperature

    def toJSON(self):
        return json.dumps({"name": "mix", "t": self.temperature})


class Calibration(object):
    def toJSON(self):
        return json.dumps({"name": "calibration"})


class Home(object):
    def toJSON(self):
        return json.dumps({"name": "home"})
