#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from logzero import logger
from services.output_temp_service import OutputTempService
from services.tank_temp_service import TankTempService
from services.tank_water_service import TankWaterService
from services.refiller import Refiller
from services.heater import Heater


class ServiceManager(object):
    """ Service manager
    """

    def __init__(self):
        self._services = {}

    def import_config(self, configs, hwmanager, bus):
        """
        Args:
            configs (dict): service configuration
            hwmanager (HardwareManager): get hardware from hwmanager
            bus (bus): connect each services
        """
        for config in configs:
            service_name = list(config.keys())[0]
            if service_name not in SERVICE_MAPPING:
                logger.error("Cannot resolve '%s' service", service_name)
                continue

            if 'enable' not in config[service_name]:
                logger.warning(
                    "Cannot find enable field in '%s', default is disabled",
                    service_name)
                continue

            if config[service_name]['enable'] is not True:
                logger.info("Service '%s' is disabled'", service_name)

            service = SERVICE_MAPPING[service_name](config[service_name],
                                                    hwmanager, bus)
            if service is not None:
                logger.info("Create service instance '%s'", service_name)
                self._services[service_name] = service
            else:
                logger.error("Cannot create service instance '%s'",
                             service_name)
        return True

    def find_service(self, name):
        if name not in self._services:
            return None
        return self._services[name]


def create_output_temp_service(service_config, hwmanager, bus):
    """
    Args:
        service_config(dict): output temperautre service configuration
    """
    scan_interval_ms = service_config['scan_interval_ms']
    dev = service_config['dev']
    hardware = hwmanager.find_hardware(dev)
    if hardware is None:
        logger.error("Cannot get dev '%s' for output temp service", dev)
        return None
    return OutputTempService(hardware, scan_interval_ms, bus)


def create_tank_temp_service(service_config, hwmanager, bus):
    """
    Args:
        service_config(dict): tank temperature service configuration
    """
    scan_interval_ms = service_config['scan_interval_ms']
    dev = service_config['dev']
    hardware = hwmanager.find_hardware(dev)
    if hardware is None:
        logger.error("Cannot get dev '%s' in tank temp service", dev)
        return None
    return TankTempService(hardware, scan_interval_ms, bus)


def create_tank_water_service(service_config, hwmanager, bus):
    """
    Args:
        service_config(dict): tank water service configuration
    """
    scan_interval_ms = service_config['scan_interval_ms']
    dev = service_config['dev']
    hardware = hwmanager.find_hardware(dev)
    if hardware is None:
        logger.error("Cannot get dev '%s' in tank water service", dev)
        return None
    return TankWaterService(hardware, scan_interval_ms, bus)


def create_refiller_service(service_config, hwmanager, bus):
    """
    Args:
        service_config(dict): refiller service configuration
    """
    dev = service_config['dev']
    hardware = hwmanager.find_hardware(dev)
    if hardware is None:
        logger.error("Cannot get dev '%s' in refiller service", dev)
        return None
    return Refiller(hardware, bus)


def create_heater_service(service_config, hwmanager, bus):
    """
    Args:
        service_config(dict): heater service configuration
    """
    dev = service_config['dev']
    hardware = hwmanager.find_hardware(dev)
    if hardware is None:
        logger.error("Cannot get dev '%s' in heater service", dev)
        return None
    return Heater(hardware, bus)


SERVICE_MAPPING = {
    "output_temp_service": create_output_temp_service,
    "tank_temp_service": create_tank_temp_service,
    "tank_water_service": create_tank_water_service,
    "refiller": create_refiller_service,
    "heater": create_heater_service
}
