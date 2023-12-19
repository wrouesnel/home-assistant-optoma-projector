"""
Support for Optoma projector.

For more details about this component, please refer to github documentation
"""
from typing import List

from optoma_web_api import Projector

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry

from .const import (
    CONFIG_PASSWORD,
    CONFIG_URL,
    CONFIG_USERNAME,
    CUSTOM_IMAGE_BASE_URL,
    DEFAULT_POLL_INTERVAL,
    DOMAIN,
    INFO_FIRWMARE_VERSION,
    INFO_MODEL_NAME,
    INFO_PROJECTOR_NAME,
    LOCAL_LOGO_PATH,
    LOGGER,
    MANUFACTURER_NAME,
    STATIC_IMAGE_BASE_URL,
)
from .helpers import Manager, projector_device_id

PLATFORMS: List[Platform] = [
    Platform.MEDIA_PLAYER,
    # Platform.BUTTON,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SWITCH,
    # Platform.REMOTE,
]


async def update_device_registry(
    hass: HomeAssistant, config_entry: ConfigEntry, manager: Manager
):
    # Add device explicitly to registry so other entities just have to report the identifier to link up
    registry = device_registry.async_get(hass)

    device_info = manager.state.info

    devicename = (
        device_info[INFO_PROJECTOR_NAME]
        if device_info[INFO_PROJECTOR_NAME] != ""
        else device_info[INFO_MODEL_NAME]
    )

    device_id = projector_device_id(manager)

    registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        identifiers={(DOMAIN, f"{device_id}")},
        manufacturer=MANUFACTURER_NAME,
        name=devicename,
        model=device_info[INFO_MODEL_NAME],
        sw_version=device_info[INFO_FIRWMARE_VERSION],
        configuration_url=manager.projector.url,
    )


async def async_setup(hass: HomeAssistant, config):
    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    # Just reload the integration on update. Crude, but it works
    await hass.config_entries.async_reload(entry.entry_id)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    LOGGER.debug(
        "Initializing projector object: url=%s username=%s"
        % (entry.options[CONFIG_URL], entry.options[CONFIG_USERNAME])
    )
    projector = Projector(
        url=entry.options[CONFIG_URL],
        username=entry.options[CONFIG_USERNAME],
        password=entry.options[CONFIG_PASSWORD],
    )

    LOGGER.debug("Initializing manager object: url=%s" % entry.options[CONFIG_URL])
    manager = Manager(hass, entry, projector)

    LOGGER.debug(
        "Creating background task loop for Optoma projector: %s" % projector.url
    )
    entry.async_create_background_task(
        hass, manager.loop(), f"{DOMAIN}_{entry.options[CONFIG_URL]}"
    )

    LOGGER.info(
        "Waiting for initial connection to Optoma projector: %s" % projector.url
    )
    await manager.async_wait_for_initialization()
    LOGGER.info("Projector status received: %s" % projector.url)

    await update_device_registry(hass, entry, manager)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = manager
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        manager: Manager = hass.data[DOMAIN].pop(entry.entry_id)
        await manager.shutdown()

    if len(hass.data[DOMAIN]) == 0:
        hass.data.pop(DOMAIN)

    return unload_ok
