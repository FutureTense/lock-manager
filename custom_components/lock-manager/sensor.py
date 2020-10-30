""" Sensor for lock-manager """

from .const import CONF_ENTITY_ID, CONF_SLOTS, CONF_LOCK_NAME, ZWAVE_NETWORK
from datetime import timedelta
from homeassistant.components.ozw import DOMAIN as OZW_DOMAIN
from openzwavemqtt.const import CommandClass
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
import logging


MANAGER = "manager"
ATTR_VALUES = "values"
ATTR_NODE_ID = "node_id"
COMMAND_CLASS_USER_CODE = 99

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):

    config = entry.data

    unique_id = entry.entry_id

    data = CodeSlotsData(hass, config)
    sensors = []
    x = entry.data[CONF_SLOTS]

    while x > 0:
        sensor_name = f"code_slot_{x}"
        sensors.append(
            CodesSensor(data, sensor_name, x, entry.data[CONF_LOCK_NAME], unique_id)
        )
        x -= 1

    async_add_entities(sensors, True)


class CodeSlotsData:
    """The class for handling the data retrieval."""

    def __init__(self, hass, config):
        """Initialize the data object."""
        self._hass = hass
        self._entity_id = config.get(CONF_ENTITY_ID)
        self._data = None

        self.update = Throttle(timedelta(seconds=5))(self.update)

    def update(self):
        """Get the latest data"""
        # loop to get user code data from entity_id node
        instance_id = 1  # default
        data = {}
        data[CONF_ENTITY_ID] = self._entity_id
        # data["node_id"] = _get_node_id(self._hass, self._entity_id)
        data[ATTR_NODE_ID] = self._get_node_id()

        # pull the codes for ozw
        if OZW_DOMAIN in self._hass.data:
            if data[ATTR_NODE_ID] is not None:
                manager = self._hass.data[OZW_DOMAIN][MANAGER]
                lock_values = (
                    manager.get_instance(instance_id)
                    .get_node(data[ATTR_NODE_ID])
                    .values()
                )
                for value in lock_values:
                    if value.command_class == CommandClass.USER_CODE:
                        _LOGGER.debug(
                            "DEBUG: code_slot_%s value: %s",
                            str(value.index),
                            str(value.value),
                        )
                        # do not update if the code contains *s
                        code = value.value
                        if "*" in str(value.value):
                            _LOGGER.debug("DEBUG: Ignoring code slot with * in value.")
                            code = "unknown"
                        sensor_name = f"code_slot_{value.index}"
                        data[sensor_name] = code

                self._data = data

        # pull codes for zwave
        elif ZWAVE_NETWORK in self._hass.data:
            if data[ATTR_NODE_ID] is not None:
                network = self._hass.data[ZWAVE_NETWORK]
                lock_values = (
                    network.nodes[data[ATTR_NODE_ID]]
                    .get_values(class_id=COMMAND_CLASS_USER_CODE)
                    .values()
                )
                for value in lock_values:
                    _LOGGER.debug(
                        "DEBUG: code_slot_%s value: %s",
                        str(value.index),
                        str(value.data),
                    )
                    # do not update if the code contains *s
                    code = value.data
                    if "*" in str(value.data):
                        _LOGGER.debug("DEBUG: Ignoring code slot with * in value.")
                        code = "unknown"
                    sensor_name = f"code_slot_{value.index}"
                    data[sensor_name] = code

                self._data = data

    def _get_node_id(self):
        data = None
        test = self._hass.states.get(self._entity_id)
        if test is not None:
            try:
                data = test.attributes["node_id"]
            except Exception as err:
                _LOGGER.error(
                    "Error acquiring node id from entity %s: %s",
                    self._entity_id,
                    str(err),
                )

        return data


class CodesSensor(Entity):
    """ Represntation of a sensor """

    def __init__(self, data, sensor_name, code_slot, lock_name, unique_id):
        """ Initialize the sensor """
        self.data = data
        self._code_slot = code_slot
        self._state = None
        self._unique_id = unique_id
        self._name = sensor_name
        self._lock_name = lock_name
        self.update()

    @property
    def unique_id(self):
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return f"{self._lock_name}_{self._name}_{self._unique_id}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._lock_name}_{self._name}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Return the icon."""
        return "mdi:lock-smart"

    @property
    def device_state_attributes(self):
        """Return device specific state attributes."""
        attr = {}

        return attr

    @property
    def available(self):
        """Return if entity is available."""
        if self._state is not None:
            return True
        return False

    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """

        self.data.update()
        # Using a dict to send the data back

        if self.data._data is not None:
            try:
                self._state = self.data._data[self._name]
            except Exception as err:
                _LOGGER.warning(
                    "Code slot %s had no value: %s", str(self._name), str(err)
                )
