"""Lock Manager Integration."""

import fileinput
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv, entity_platform
import logging
import os
from .const import (
    CONF_ALARM_LEVEL,
    CONF_ALARM_TYPE,
    CONF_ENTITY_ID,
    CONF_LOCK_NAME,
    CONF_OZW,
    CONF_PATH,
    CONF_SENSOR_NAME,
    CONF_SLOTS,
    CONF_START,
    DOMAIN,
    VERSION,
    ISSUE_URL,
    PLATFORM,
)
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

ATTR_NAME = "lockname"
SERVICE_GENERATE_PACKAGE = "generate_package"


async def async_setup(hass, config_entry):
    """ Disallow configuration via YAML """

    return True


async def async_setup_entry(hass, config_entry):
    """Set up is called when Home Assistant is loading our component."""
    _LOGGER.info(
        "Version %s is starting, if you have any issues please report" " them here: %s",
        VERSION,
        ISSUE_URL,
    )

    config_entry.options = config_entry.data
    config_entry.add_update_listener(update_listener)

    async def _generate_package(service):
        """Generate the package files"""
        _LOGGER.debug("DEBUG: %s", service)
        name = service.data[ATTR_NAME]
        entry = config_entry
        _LOGGER.debug("Starting file generation...")

        _LOGGER.debug(
            "DEBUG conf_lock: %s name: %s", entry.options[CONF_LOCK_NAME], name
        )
        if entry.options[CONF_LOCK_NAME] == name:
            lockname = entry.options[CONF_LOCK_NAME]
            inputlockpinheader = "input_text." + lockname + "_pin_"
            activelockheader = "binary_sensor.active_" + lockname + "_"
            lockentityname = entry.options[CONF_ENTITY_ID]
            sensorname = lockname
            doorsensorentityname = entry.options[CONF_SENSOR_NAME] or ""
            sensoralarmlevel = entry.options[CONF_ALARM_LEVEL]
            sensoralarmtype = entry.options[CONF_ALARM_TYPE]
            using_ozw = entry.options[CONF_OZW]
            dummy = "foobar"

            output_path = entry.options[CONF_PATH] + lockname + "/"

            """Check to see if the path exists, if not make it"""
            pathcheck = os.path.isdir(output_path)
            if not pathcheck:
                try:
                    os.makedirs(output_path)
                    _LOGGER.debug("Creating packages directory")
                except Exception as err:
                    _LOGGER.critical("Error creating directory: %s", str(err))

            """Clean up directory"""
            _LOGGER.debug("Cleaning up directory: %s", str(output_path))
            for file in os.listdir(output_path):
                os.remove(output_path + file)

            _LOGGER.debug("Created packages directory")

            # Generate list of code slots
            code_slots = entry.options[CONF_SLOTS]
            start_from = entry.options[CONF_START]

            x = start_from
            activelockheaders = []
            while code_slots > 0:
                activelockheaders.append(activelockheader + str(x))
                x += 1
                code_slots -= 1
            activelockheaders = ",".join(map(str, activelockheaders))

            # Generate pin slots
            code_slots = entry.options[CONF_SLOTS]

            x = start_from
            inputlockpinheaders = []
            while code_slots > 0:
                inputlockpinheaders.append(inputlockpinheader + str(x))
                x += 1
                code_slots -= 1
            inputlockpinheaders = ",".join(map(str, inputlockpinheaders))

            _LOGGER.debug("Creating common YAML file...")
            replacements = {
                "LOCKNAME": lockname,
                "CASE_LOCK_NAME": lockname,
                "INPUTLOCKPINHEADER": inputlockpinheaders,
                "ACTIVELOCKHEADER": activelockheaders,
                "LOCKENTITYNAME": lockentityname,
                "SENSORNAME": sensorname,
                "DOORSENSORENTITYNAME": doorsensorentityname,
                "SENSORALARMTYPE": sensoralarmtype,
                "SENSORALARMLEVEL": sensoralarmlevel,
                "USINGOZW": using_ozw,
            }
            # Replace variables in common file
            output = open(output_path + lockname + "_lock_manager_common.yaml", "w+",)
            infile = open(os.path.dirname(__file__) + "/lock_manager_common.yaml", "r")
            with infile as file1:
                for line in file1:
                    for src, target in replacements.items():
                        line = line.replace(src, target)
                    output.write(line)
            _LOGGER.debug("Common YAML file created")
            _LOGGER.debug("Creating lovelace header...")
            # Replace variables in lovelace file
            output = open(output_path + lockname + "_lovelace", "w+",)
            infile = open(os.path.dirname(__file__) + "/lovelace.head", "r")
            with infile as file1:
                for line in file1:
                    for src, target in replacements.items():
                        line = line.replace(src, target)
                    output.write(line)
            _LOGGER.debug("Lovelace header created")
            _LOGGER.debug("Creating per slot YAML and lovelace cards...")
            # Replace variables in code slot files
            code_slots = entry.options[CONF_SLOTS]

            x = start_from
            while code_slots > 0:
                replacements = {
                    "LOCKNAME": lockname,
                    "CASE_LOCK_NAME": lockname,
                    "TEMPLATENUM": str(x),
                }
                output = open(
                    output_path + lockname + "_lock_manager_" + str(x) + ".yaml", "w+",
                )
                infile = open(os.path.dirname(__file__) + "/lock_manager.yaml", "r")
                with infile as file1:
                    for line in file1:
                        for src, target in replacements.items():
                            line = line.replace(src, target)
                        output.write(line)

                # Loop the lovelace code slot files
                output = open(output_path + lockname + "_lovelace", "a",)
                infile = open(os.path.dirname(__file__) + "/lovelace.code", "r")
                with infile as file1:
                    for line in file1:
                        for src, target in replacements.items():
                            line = line.replace(src, target)
                        output.write(line)
                x += 1
                code_slots -= 1
            _LOGGER.debug("Package generation complete")

    hass.services.async_register(
        DOMAIN,
        SERVICE_GENERATE_PACKAGE,
        _generate_package,
        schema=vol.Schema({vol.Optional(ATTR_NAME): vol.Coerce(str)}),
    )

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(config_entry, PLATFORM)
    )

    #    servicedata = {"lockname": config_entry.options[CONF_LOCK_NAME]}
    #    await hass.services.async_call(DOMAIN, SERVICE_GENERATE_PACKAGE, servicedata)

    return True


async def async_unload_entry(hass, config_entry):
    """Handle removal of an entry."""

    return True


async def update_listener(hass, entry):
    """Update listener."""
    entry.data = entry.options

    servicedata = {"lockname": entry.options[CONF_LOCK_NAME]}
    await hass.services.async_call(DOMAIN, SERVICE_GENERATE_PACKAGE, servicedata)
