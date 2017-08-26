#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import yaml
from hardware.hw_manager import HWManager


def main():
    loop = asyncio.get_event_loop()

    with open('config.yaml', 'r') as file:
        configuration = yaml.load(file.read())

    hwm = HWManager()
    hwm.import_config(loop, configuration['hardwares'])


if __name__ == '__main__':
    main()
