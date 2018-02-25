# -*- coding: utf-8 -*-

def gethardware():
    # Extract serial from cpuinfo file
    hardware = ""
    with open('/proc/cpuinfo', 'r') as f:
        try:
            for line in f:
                if line[0:6] == 'Hardware':
                    hardware = line[10:26]
        except:
            hardware = "ERROR"

    return hardware


HARDWARE = gethardware()
if HARDWARE == 'BCM2709':
    rGPIO.setmode(rGPIO.BCM)
