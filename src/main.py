#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import argparse
import yaml
from hardware.hw_manager import HWManager


def main():

    parser = argparse.ArgumentParser(description="Turing hardware")
    parser.add_argument(
        'configuration', help='Turing hardware and service configuraiton')
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    with open(args.configuration, 'r') as file:
        configuration = yaml.load(file.read())

    hwm = HWManager()
    hwm.import_config(loop, configuration['hardwares'])


if __name__ == '__main__':
    main()
