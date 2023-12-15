import logging
from typing import Dict, List, Optional

_LOGGER = logging.getLogger()

from optoma_web_api import STATUS_VALUE_MAP, Projector

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)


class OptomaProjector(MediaPlayerEntity):
    """Representation of Optoma Projector Device."""

    def __init__(self, name: str, projector: Projector):
        """Initialize entity to control Optoma projector."""

        self._name = name
        self._projector = projector
        self._source_list: List[str] = list(STATUS_VALUE_MAP["Source"].values())
        self._state: Optional[Dict[str, str]] = None
        _LOGGER.debug("Initialized Optoma Projector")

    async def async_update(self):
        """Update state of device."""
        self._state = self._projector.status()

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return (
            MediaPlayerState.ON
            if self._state["Power Status"] == "On"
            else MediaPlayerState.OFF
        )

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return (
            MediaPlayerEntityFeature.TURN_ON | MediaPlayerEntityFeature.TURN_OFF
        )  # | MediaPlayerEntityFeature.SELECT_SOURCE

    async def turn_on(self):
        """Turn on optoma."""
        self._projector.power_on()

    async def turn_off(self):
        """Turn off optoma."""
        self._projector.power_off()

    @property
    def source_list(self):
        """List of available input sources."""
        return self._source_list

    @property
    def source(self):
        """Get current input sources."""
        return self._state["Source"][self._source]

    # async def async_select_source(self, source):
    #     """Select input source."""
    #     _LOGGER.info("Setting source to: %s", source)
    #     self._projector.send_command(source)

    @property
    def should_poll(self):
        """Return True if the entity requires polling from HA"""
        return True
