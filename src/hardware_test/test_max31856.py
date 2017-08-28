#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import signal
import time
import yaml
from hardware.hw_manager import HWManager
from hardware.max31856 import MAX31856, TC

main_stop = False


def signal_int_handler(*_):
    main_stop = True


def main():
    loop = asyncio.get_event_loop()
    with open('config.yaml', 'r') as file:
        configuration = yaml.load(file.read())

    hwm = HWManager()
    hwm.import_config(loop, configuration['hardwares'])
    max31856 = hwm.find_hardware('max31856-0')

    max31856.connect()
    max31856.tc_type = TC.T_TYPE
    max31856.mode = MAX31856.MODE_AUTOMATIC
    while not main_stop:
        print(max31856.read_measure_temp_c())
        time.sleep(0.5)
    max31856.disconnect()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_int_handler)
    main()
