from typing import List

from optoma_web_api import STATUS_VALUE_MAP

from homeassistant.components.media_player import (
    _LOGGER,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo

from . import Manager, ProjectorState
from .const import DOMAIN, INFO_MODEL_NAME, INFO_PROJECTOR_NAME, LOGGER


async def async_setup_entry(hass, config_entry: ConfigEntry, async_add_entities):
    manager: Manager = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        OptomaProjector(
            config_entry.entry_id,
            manager,
        )
    ]

    async_add_entities(entities)


class OptomaProjector(MediaPlayerEntity):
    """Representation of Optoma Projector Device."""

    def __init__(self, unique_id: str, manager: Manager):
        """Initialize entity to control Optoma projector."""

        self._manager = manager
        self._source_list: List[str] = list(STATUS_VALUE_MAP["Source"].values())

        # State caches
        self._state: MediaPlayerState = MediaPlayerState.OFF
        self._name: str = ""
        self._source = ""

        LOGGER.debug("Initialized Optoma Projector: %s" % self._manager.projector.url)

        self._device_id = unique_id
        self._attr_unique_id = self._device_id

        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, self._device_id)})

        # Register callbacks with the manager
        self._manager.register_update_callback(self._get_state)

    def _get_state(self, state: ProjectorState):
        """State function invoked by the manager callback"""
        self._state = (
            MediaPlayerState.ON
            if state.state.get("Power Status", "Off") == "On"
            else MediaPlayerState.OFF
        )
        self._name = (
            state.info[INFO_PROJECTOR_NAME]
            if state.info.get(INFO_PROJECTOR_NAME, "") != ""
            else state.info.get(INFO_MODEL_NAME, "")
        )
        self._source = state.state.get("Source")

    def update_callback(self):
        self.schedule_update_ha_state()  # type: ignore

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return (
            MediaPlayerEntityFeature.TURN_ON | MediaPlayerEntityFeature.TURN_OFF
        )  # | MediaPlayerEntityFeature.SELECT_SOURCE

    def turn_on(self):
        """Turn on optoma."""
        LOGGER.info("Projector Power On")
        self._manager.projector.power_on()

    def turn_off(self):
        """Turn off optoma."""
        LOGGER.info("Projector Power Off")
        self._manager._projector.power_off()

    @property
    def source_list(self):
        """List of available input sources."""
        return self._source_list

    @property
    def source(self):
        """Get current input sources."""
        return self._source

    # async def async_select_source(self, source):
    #     """Select input source."""
    #     _LOGGER.info("Setting source to: %s", source)
    #     self._projector.send_command(source)

    @property
    def should_poll(self):
        """Return True if the entity requires polling from HA"""
        return False
