#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
from hardware.hwmanager import HWManager

def main():
    with open('config.yaml', 'r') as file:
        configuration = yaml.load(file.read())
        hwm = HWManager()
        hwm.import_config(configuration['hardwares'])

if __name__ == '__main__':
    main()
