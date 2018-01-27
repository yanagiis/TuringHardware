#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import signal

from hardware.smoothie import Smoothie
from hardware.uart import UART, UARTConfig

stop_flag = False


def main():
    parser = argparse.ArgumentParser(description="Smoothie client")
    parser.add_argument(
        '--baudrate',
        dest='baudrate',
        default=115200,
        help='smoothie baudrate')
    parser.add_argument('dev', dest='device', help='smoothie device path')

    args = parser.parse_args()

    config = UARTConfig()
    config.baudrate = args.baudrate

    uart = UART(args.dev, config)
    smoothie = Smoothie(uart)

    if smoothie.connect(3) is False:
        print("Failed to connect to smoothie '%s'" % args.dev)
        return

    signal.signal(signal.SIGINT, stop)

    global stop_flag
    while not stop_flag:
        command = input(" > ")
        smoothie.send(command)
        resp = smoothie.recv()
        print(" < %s" % resp)

    smoothie.disconnect()


def stop():
    global stop_flag
    stop_flag = True


if __name__ == "__main__":
    main()
