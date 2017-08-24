#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class IO(object):
    def open(self):
        """ open the I/O device
        Returns:
            bool: return True if open success, otherwise return False
        """
        raise NotImplementedError

    def close(self):
        """ close the I/O device
        Returns:
            void
        """
        raise NotImplementedError


class Reader(object):
    def read(self, size):
        """ read data
        Args:
            size (int): number of data to read
        Returns:
            bytes: array of byte
        """
        raise NotImplementedError


class Writer(object):
    def write(self):
        """ write data
        Returns:
            int: number of data write into
        """
        raise NotImplementedError
