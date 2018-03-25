# -*- coding: utf-8 -*-

import RPi.GPIO as rGPIO


def gethardware():
    # Extract serial from cpuinfo file
    hardware = ""
    with open('/proc/cpuinfo', 'r') as f:
        try:
            for line in f:
                if line[0:8] == 'Hardware':
                    hardware = line[11:]
        except:
            hardware = "ERROR"

    return hardware


HARDWARE = gethardware()
if 'BCM2709' in HARDWARE:
    rGPIO.setmode(rGPIO.BCM)
