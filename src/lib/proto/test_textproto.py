#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib.tio import tio
from lib.proto.textproto import TextProto


class HelloReader(tio.Reader):
    def read(self, size):
        return bytes("hello\r\n", "ascii")


class OverflowReader(tio.Reader):
    def __init__(self):
        self.str = ""

    def _fill(self):
        self.str = "hello" * 204 + "abcd" + "hihihi\r\n"

    def read(self, size):
        if len(self.str) is 0:
            self._fill()
        data = self.str[:size]
        self.str = self.str[size:]
        return bytes(data, "ascii")


class NullWriter(tio.Writer):
    def write(self, data):
        pass


def test_normal_readline():
    textproto = TextProto(HelloReader(), NullWriter(), 1024)
    line = textproto.readline()
    assert line == "hello\r\n"
    line = textproto.readline()
    assert line == "hello\r\n"


def test_overflow_readline():
    textproto = TextProto(OverflowReader(), NullWriter(), 1024)
    line = textproto.readline()
    assert line == "hihihi\r\n"
    line = textproto.readline()
    assert line == "hihihi\r\n"
