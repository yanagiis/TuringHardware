#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class HardwareError(Exception):
    def __init__(self, name, msg):
        super(HardwareError, self).__init__()
        self.name = name
        self.message = msg
