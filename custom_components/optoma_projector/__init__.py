"""
Support for Optoma projector.

For more details about this component, please refer to github documentation
"""
import asyncio
import dataclasses
from typing import Callable, Dict, List, Set

from optoma_web_api import Projector

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry

from .const import (
    CONFIG_PASSWORD,
    CONFIG_URL,
    CONFIG_USERNAME,
    DEFAULT_POLL_INTERVAL,
    DOMAIN,
    INFO_FIRWMARE_VERSION,
    INFO_MODEL_NAME,
    INFO_PROJECTOR_NAME,
    LOGGER,
    MANUFACTURER_NAME,
)

PLATFORMS: List[Platform] = [
    Platform.MEDIA_PLAYER,
    # Platform.BUTTON,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SWITCH,
    # Platform.REMOTE,
]


async def update_device_registry(
    hass: HomeAssistant, config_entry: ConfigEntry, projector: Projector
):
    info = await hass.async_add_executor_job(projector.info)

    # Add device explicitly to registry so other entities just have to report the identifier to link up
    registry = device_registry.async_get(hass)

    devicename = (
        info[INFO_PROJECTOR_NAME]
        if info[INFO_PROJECTOR_NAME] != ""
        else info[INFO_MODEL_NAME]
    )

    registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        identifiers={(DOMAIN, f"{config_entry.entry_id}")},
        manufacturer=MANUFACTURER_NAME,
        name=devicename,
        model=info[INFO_MODEL_NAME],
        sw_version=info[INFO_FIRWMARE_VERSION],
        configuration_url=projector.url,
    )


async def async_setup(hass: HomeAssistant, config):
    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    # Just reload the integration on update. Crude, but it works
    await hass.config_entries.async_reload(entry.entry_id)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    def initialize_projector(projector: Projector):
        """Run a basic check that we contact the projector and login"""
        # try:
        #     projector.status()
        # except optoma_web_api.ProjectorException as e:
        #     raise ConfigEntryNotReady("Could not login to the Optoma Web API %s" % entry.title) from e
        # except Exception as e:
        #     raise ConfigEntryNotReady("Unexpected exception during initialization of %s" % entry.title) from e
        #
        # return True

    projector = Projector(
        url=entry.options[CONFIG_URL],
        username=entry.options[CONFIG_USERNAME],
        password=entry.options[CONFIG_PASSWORD],
    )

    manager = Manager(hass, entry, projector)

    # Create the background task loop
    entry.async_create_background_task(
        hass, manager.loop(), f"{DOMAIN}_{entry.options[CONFIG_URL]}"
    )

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


@dataclasses.dataclass
class ProjectorState:
    state: Dict[str, str]
    info: Dict[str, str]


class Manager:
    """Device Status Manager pattern to coordinate entity ypdates"""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, projector: Projector):
        self._hass = hass
        self._entry = entry
        self._projector = projector

        self._loop_interval = DEFAULT_POLL_INTERVAL

        self._update_callbacks: Set[Callable[[ProjectorState], None]] = set()

        self._result = ProjectorState(state={}, info={})

        self._shutdown = asyncio.Event()

    @property
    def state(self) -> ProjectorState:
        return self._result

    def update_state(self) -> ProjectorState:
        # TODO: I guess mark the projector as down?
        try:
            return ProjectorState(
                state=self._projector.status(), info=self._projector.info()
            )
        except Exception as e:
            LOGGER.warning(
                "Could not connect to projector to retrieve status", exc_info=e
            )
            return ProjectorState(state={}, info={})

    async def loop(self):
        """Projector monitoring loop"""
        LOGGER.info("Starting projector message poll loop")
        while True:
            self._result = await self._hass.async_add_executor_job(self.update_state)
            # LOGGER.debug("State Updated")
            self._call_registered_update_callbacks(self._result)

            done, _ = await asyncio.wait(
                [
                    self._hass.async_create_background_task(
                        self._shutdown.wait(), f"{DOMAIN}_wait_shutdown"
                    ),
                    self._hass.async_create_background_task(
                        asyncio.sleep(self._loop_interval),
                        f"{DOMAIN}_wait_poll_interval",
                    ),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )
            if any(t.cancelled() for t in done):
                break
            if self._shutdown.is_set():
                break
        LOGGER.info("Optoma polling loop exiting")

    async def shutdown(self):
        """Request loop shutdown"""
        self._shutdown.set()

    @property
    def projector(self) -> Projector:
        return self._projector

    def register_update_callback(self, callback: Callable[[ProjectorState], None]):
        self._update_callbacks.add(callback)

    def unregister_update_callback(self, callback: Callable[[ProjectorState], None]):
        self._update_callbacks.remove(callback)

    def _call_registered_update_callbacks(self, value: ProjectorState):
        for callback in self._update_callbacks:
            callback(value)
