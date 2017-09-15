#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import argparse
import yaml
from contextlib import suppress
from hardware.hw_manager import HWManager
from services.service_manager import ServiceManager
from services.nats_bus import NatsBus


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
    bus = NatsBus(bus_config['host'], bus_config['port'])
    await bus.start()

    svm = ServiceManager()
    svm.import_config(configuration['services'], hwm, bus)

    while True:
        await bus.pub('hello.world', b"helloworld")
        await asyncio.sleep(1)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    pending = asyncio.Task.all_tasks()
    for task in pending:
        task.cancel()
        with suppress(asyncio.CancelledError):
            loop.run_until_complete(task)
