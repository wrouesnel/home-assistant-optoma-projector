"""
Support for Optoma projector.

For more details about this component, please refer to github documentation
"""
import logging

import voluptuous as vol

from custom_components.optoma_projector.media_player import OptomaProjector

from .const import DOMAIN, LOGGER


def setup(hass, config):
    return True


# async def async_setup_platform(hass, config, async_add_entities):
#     """Set up the Optoma media player platform."""
#
#     if DATA_OPTOMA not in hass.data:
#         hass.data[DATA_OPTOMA] = []
#
#     name = config.get(CONF_NAME)
#     port = config.get(CONF_PORT)
#     _LOGGER.info("Name for the optoma Projector is: %s", name)
#
#     optoma = OptomaProjector(name, port)
#
#     hass.data[DATA_OPTOMA].append(optoma)
#     async_add_entities([optoma], update_before_add=True)
#
#     async def async_service_handler(service):
#         """Handle for services."""
#         entity_ids = service.data.get(ATTR_ENTITY_ID)
#         if entity_ids:
#             devices = [device for device in hass.data[DATA_OPTOMA]
#                        if device.entity_id in entity_ids]
#         else:
#             devices = hass.data[DATA_OPTOMA]
#         for device in devices:
#             device.async_schedule_update_ha_state(True)
#
# async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
#     """Unload a config entry."""
