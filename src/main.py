#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import argparse
import signal

import yaml
from hardware.hw_manager import HWManager
from services.service_manager import ServiceManager
from services.nats_bus import NatsBus
from backend.server import start_backend

stop_flag = False


async def main():

    parser = argparse.ArgumentParser(description="Turing hardware")
    parser.add_argument(
        'configuration', help='Turing hardware and service configuraiton')
    args = parser.parse_args()

    with open(args.configuration, 'r') as file:
        configuration = yaml.load(file.read())

    hwm = HWManager()
    hwm.import_config(configuration['hardwares'])
    bus_config = configuration['bus']

    svm = ServiceManager()
    await svm.import_config(configuration['services'], hwm, bus_config['host'],
                      bus_config['port'])
    svm.start_all_services()

    bus = NatsBus(bus_config['host'], bus_config['port'])
    await bus.start()

    await start_backend(configuration['backend'], bus)

    signal.signal(signal.SIGINT, stop)

    while stop_flag is not True:
        await asyncio.sleep(0.5)

    await svm.stop_all_services()


def stop(_signal, _frame):
    global stop_flag
    stop_flag = True


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
