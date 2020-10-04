""" Sensor for lock-manager """

from .const import CONF_ENTITY_ID, CONF_SLOTS, CONF_START
from datetime import timedelta
from homeassistant.components.lock import DOMAIN as LOCK_DOMAIN
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):

    config = entry.data

    unique_id = entry.entry_id

    data = CodeSlotsData(hass, config)
    _LOGGER.debug("~~~~ DEBUG: %s", str(data))
    sensors = []
    x = entry.data[CONF_SLOTS]

    while x > 0:
        sensors.append(CodesSensor(data, x, unique_id))
        x -= 1

    async_add_entities(sensors, True)


class CodeSlotsData:
    """The class for handling the data retrieval."""

    def __init__(self, hass, config):
        """Initialize the data object."""
        self._hass = hass
        self._entity_id = config.get(CONF_ENTITY_ID)
        self._data = None

        self.update = Throttle(timedelta(seconds=10))(self.update)

    def update(self):
        """Get the latest data"""
        # loop to get user code data from entity_id node
        data = {}
        data[CONF_ENTITY_ID] = self._entity_id
        data["node_id"] = _get_node_id(
            self._hass.data[LOCK_DOMAIN].entities, self._entity_id
        )
        # self._hass.data["ozw"]
        _LOGGER.debug("~~~~ DEBUG: %s", str(data))
        self._data = data


class CodesSensor(Entity):
    """ Represntation of a sensor """

    def __init__(self, data, code_slot, unique_id):
        """ Initialize the sensor """
        self.data = data
        self._code_slot = code_slot
        self._state = None
        self._unique_id = unique_id
        self._name = "Test"
        self.update()

    @property
    def unique_id(self):
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return f"{self._code_slot}_{self._name}_{self._unique_id}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._name}_{self._code_slot}"

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

    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """

        self.data.update()
        # Using a dict to send the data back
        self._state = self.data._data[self.type]


def _get_node_id(entities, search=None):
    data = None
    for entity in entities:
        if search is not None and not any(map(entity.entity_id.__contains__, search)):
            continue
        data = entity.entity_id.node_id

    _LOGGER.debug("~~~ DEBUG: %s", str(data))

    return data
