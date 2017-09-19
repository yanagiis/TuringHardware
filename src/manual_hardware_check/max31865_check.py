#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import asyncio
import signal
import time
import yaml
from logzero import logger
from hardware.hw_manager import HWManager
from hardware.max31865 import MAX31865


def signal_int_handler(*_):
    sys.exit(1)


def main():
    with open('config.yaml', 'r') as file:
        configuration = yaml.load(file.read())

    hwm = HWManager()
    hwm.import_config(configuration['hardwares'])
    max31865 = hwm.find_hardware('max31865-0')

    if max31865.connect() is False:
        logger.error('Cannot find max31865')
        sys.exit(1)

    while True:
        print(max31865.read_measure_temp_c())
        time.sleep(0.5)
    max31865.disconnect()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_int_handler)
    main()
