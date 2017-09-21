# -*- coding: utf-8 -*-


class MockPID(object):
    def __init__(self):
        self.compute_result = 0

    def compute(self, *_):
        return self.compute_result
