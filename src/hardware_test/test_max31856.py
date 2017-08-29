#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import asyncio
import signal
import time
import yaml
from hardware.hw_manager import HWManager
from hardware.max31856 import MAX31856


def signal_int_handler(*_):
    sys.exit(1)


def main():
    loop = asyncio.get_event_loop()
    with open('config.yaml', 'r') as file:
        configuration = yaml.load(file.read())

    hwm = HWManager()
    hwm.import_config(loop, configuration['hardwares'])
    max31856 = hwm.find_hardware('max31856-0')

    if max31856.connect() == False:
        sys.exit(1)

    max31856.tc_type = MAX31856.T_TYPE
    max31856.mode = MAX31856.MODE_AUTOMATIC
    while True:
        print(max31856.read_measure_temp_c())
        time.sleep(0.5)
    max31856.disconnect()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_int_handler)
    main()
