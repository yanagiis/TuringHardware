#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from logzero import logger
from hardware.max31865 import MAX31865, MAX31865Config
from hardware.max31856 import MAX31856, MAX31856Config
from hardware.pwm import SWPWM, PWMConfig
from hardware.smoothie import Smoothie
from hardware.extruder import Extruder
from hardware.spi import HWSPI, SPIConfig
from hardware.uart import UART, UARTConfig


class HWManager(object):
    """ hardware manager (like Linux device tree)
    """

    def __init__(self):
        self._hardwares = {}

    def import_config(self, loop, configs):
        """
        Args:
            loop (asyncio.loop): used by hardware
            configs (dict): hardware configuration
        """
        for config in configs:
            hardware_type = list(config.keys())[0]
            if hardware_type not in HARDWARE_MAPPING:
                logger.error("Cannot resolve '%s' type", hardware_type)
                continue
            driver = HARDWARE_MAPPING[hardware_type](config[hardware_type],
                                                     self, loop)

            name = config[hardware_type]['name']
            if driver is not None:
                logger.info("Create hardware instance '%s'", name)
                self._hardwares[name] = driver
            else:
                logger.info("Cannot create hardware instance '%s'", name)

    def find_hardware(self, name):
        if name not in self._hardwares:
            return None
        return self._hardwares[name]


def create_max31856(hardware_config, hwm, _):
    tc_type = hardware_config['tc_type']
    sample_avg = hardware_config['sample_avg']
    dev = hardware_config['dev']

    config = MAX31856Config()

    if tc_type == 'B':
        config.tc_type = MAX31856.B_TYPE
    elif tc_type == 'E':
        config.tc_type = MAX31856.E_TYPE
    elif tc_type == 'J':
        config.tc_type = MAX31856.J_TYPE
    elif tc_type == 'K':
        config.tc_type = MAX31856.K_TYPE
    elif tc_type == 'N':
        config.tc_type = MAX31856.N_TYPE
    elif tc_type == 'R':
        config.tc_type = MAX31856.R_TYPE
    elif tc_type == 'S':
        config.tc_type = MAX31856.S_TYPE
    elif tc_type == 'T':
        config.tc_type = MAX31856.T_TYPE
    else:
        logger.error("Unknown '%s' - tc_type: '%s'", hardware_config['name'],
                     hardware_config['tc_type'])
        return None

    if sample_avg == 1:
        config.sample_avg = MAX31856.SAMPLE_AVG_1
    elif sample_avg == 2:
        config.sample_avg = MAX31856.SAMPLE_AVG_2
    elif sample_avg == 4:
        config.sample_avg = MAX31856.SAMPLE_AVG_4
    elif sample_avg == 8:
        config.sample_avg = MAX31856.SAMPLE_AVG_8
    elif sample_avg == 16:
        config.sample_avg = MAX31856.SAMPLE_AVG_16
    else:
        logger.error("Unsupport '%s' - sample average: '%d'",
                     hardware_config['name'], hardware_config['sample_avg'])
        return None

    spidev = hwm.find_hardware(dev)
    if spidev is None:
        logger.warning("Cannot find hardware '%s' for now", dev)
        return ValueError("Cannot find hardware '%s' for now" % dev)

    return MAX31856(spidev, config)


def create_max31865(hardware_config, hwm, _):
    dev = hardware_config['dev']
    wire = hardware_config['wire']
    spidev = hwm.find_hardware(dev)
    if spidev is None:
        logger.warning("Cannot find hardware '%s' for now", dev)
        return None

    config = MAX31865Config()
    if wire == 2:
        config.wire = MAX31865.WIRE_2
    elif wire == 3:
        config.wire = MAX31865.WIRE_3
    elif wire == 4:
        config.wire = MAX31865.WIRE_4
    else:
        logger.error("Unsupport '%s' wire setting: '%d'",
                     hardware_config['name'], wire)

    return MAX31865(spidev, config)


def create_pwm(hardware_config, _, loop):
    gpio_pin = hardware_config['gpio']
    config = PWMConfig()
    config.dutycycle = hardware_config['dutycycle']
    config.frequency = hardware_config['frequency']
    return SWPWM(gpio_pin, config, loop)


def create_smoothie(hardware_config, hwm, _):
    dev = hardware_config['dev']
    uartdev = hwm.find_hardware(dev)
    if uartdev is None:
        logger.warning("Cannot find hardware '%s' for now",
                       hardware_config['name'])
        return None

    return Smoothie(uartdev)


def create_extruder(hardware_config, hwm, _):
    dev = hardware_config['dev']
    uartdev = hwm.find_hardware(dev)
    if uartdev is None:
        logger.warning("Cannot find hardware '%s' for now",
                       hardware_config['name'])
        return None

    return Extruder(uartdev)


def create_hwspi(hardware_config, *_):
    spi_config = SPIConfig()
    spi_config.speed = hardware_config['speed']
    spi_config.mode = hardware_config['mode']
    number = hardware_config['number']
    chipselect = hardware_config['chipselect']
    return HWSPI(number, chipselect, spi_config)


def create_uart(hardware_config, *_):
    uart_config = UARTConfig()
    uart_config.baudrate = hardware_config['baudrate']
    uart_config.rtscts = hardware_config['rtscts']
    uart_config.dsrdtr = hardware_config['dsrdtr']
    uart_config.read_timeout = hardware_config['read_timeout']
    uart_config.write_timeout = hardware_config['write_timeout']
    return UART(hardware_config['devpath'], uart_config)


HARDWARE_MAPPING = {
    "max31856": create_max31856,
    "max31865": create_max31865,
    "swpwm": create_pwm,
    "smoothie": create_smoothie,
    "extruder": create_extruder,
    "hwspi": create_hwspi,
    "uart": create_uart
}
