#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib.proto.textproto import TextProto
from logzero import logger


class Extruder(object):
    def __init__(self, uartdev):
        """
        Args:
            uartdev (UART)
        """
        self._uart = uartdev
        self._textproto = TextProto(self._uart, self._uart, 64)

    def connect(self, retry_times):
        """ Connect to extruder
        Try to connect extruder and check the function is worked or not
        Args:
            retry_times (int): retry times for connect to Smoothie board
        Returns:
            bool: True if connect success, otherwise return False
        """
        logger.info("Connect to extruder ...")
        for _ in range(retry_times):
            self._uart.open()
            if self.execute('') is not True:
                self._uart.close()
                continue

            logger.info("Connect to extruder successfully")
            return True
        logger.error("Failed to connect extruder")
        return False

    def disconnect(self):
        self._uart.close()

    def execute(self, cmd):
        """ Send a command and wait response
        Args:
            cmd (str): Gcode to write
        Returns:
            bool: True if smoothie response 'ok', otherwise return False
        """
        self.send(cmd)
        if self.recv() != 'ok':
            return False
        return True

    def send(self, cmd):
        """
        Args:
            cmd (str): Hcode to write
        """
        checksum = 0
        for character in cmd:
            checksum += ord(character)
        checksum += ord(' ')
        cmd += "S %x" % checksum

        self._textproto.writeline(cmd)

    def recv(self):
        """ Recieve a response
        Returns:
            string: response
        """
        return self._textproto.readline().strip()
