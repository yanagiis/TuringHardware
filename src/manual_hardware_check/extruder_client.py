#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import signal

from hardware.extruder import Extruder
from hardware.uart import UART, UARTConfig

stop_flag = False


def main():
    parser = argparse.ArgumentParser(description="Extruder client")
    parser.add_argument(
        '--baudrate',
        dest='baudrate',
        default=115200,
        help='extruder baudrate')
    parser.add_argument('dev', dest='device', help='extruder device path')

    args = parser.parse_args()

    config = UARTConfig()
    config.baudrate = args.baudrate

    uart = UART(args.dev, config)
    extruder = Extruder(uart)

    if extruder.connect(3) is False:
        print("Failed to connect to extruder '%s'" % args.dev)
        return

    signal.signal(signal.SIGINT, stop)

    global stop_flag
    while not stop_flag:
        command = input(" > ")
        extruder.send(command)
        resp = extruder.recv()
        print(" < %s" % resp)

    extruder.disconnect()


def stop():
    global stop_flag
    stop_flag = True


if __name__ == "__main__":
    main()
