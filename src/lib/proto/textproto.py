#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib.tio import tio


class TextProto(object):
    """ TextProto (inspired from golang net/textproto)

    """

    def __init__(self, reader, writer, max_buffer_size):
        """
        Args:
            reader (lib.tio.Reader): reader TextProto read from
            writer (lib.tio.Writer): writer TextProto write into
            max_buffer_size (int): maximum buffer size this TextProto can use
        """

        if (not isinstance(reader, tio.Reader)):
            raise TypeError("arg 'reader' is not tio.Reader")
        if (not isinstance(writer, tio.Writer)):
            raise TypeError("arg 'writer' is not tio.Writer")

        self._reader = reader
        self._writer = writer
        self._max_buffer_size = max_buffer_size
        self._buf = ''

    def readline(self):
        """
        Returns:
            bytes: return a line read from reader
        """
        while True:
            index = self._buf.find('\n')
            if index == -1:
                if len(self._buf) == self._max_buffer_size:
                    self._buf = ''
                else:
                    self._buf += self._reader.read(self._max_buffer_size -
                                                   len(self._buf)).decode()
            else:
                line = self._buf[:index + 1]
                self._buf = self._buf[index + 1:]
                return line

    def writeline(self, data):
        """
        Args:
            data (bytes): write data with '\r\n' into writer
        """
        self._writer.write(data + "\r\n")
