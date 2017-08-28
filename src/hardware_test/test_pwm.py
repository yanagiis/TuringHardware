#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import asyncio
import signal
import time
import yaml
from hardware.hw_manager import HWManager
from hardware.max31856 import MAX31856, TC


def signal_int_handler(*_):
    sys.exit(1)


def main():
    loop = asyncio.get_event_loop()
    with open('config.yaml', 'r') as file:
        configuration = yaml.load(file.read())

    hwm = HWManager()
    hwm.import_config(loop, configuration['hardwares'])
    pwm0 = hwm.find_hardware('pwm-0')

    pwm0.open()
    pwm0.dutycycle = 50
    pwm0.frequency = 10
    loop.run_until_complete(pwm0.start())
    pwm0.close()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_int_handler)
    main()
