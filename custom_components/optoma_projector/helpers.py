import asyncio
import dataclasses
from typing import Callable, Dict, Set

from optoma_web_api import Projector

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription

from .const import DEFAULT_POLL_INTERVAL, DOMAIN, INFO_MAC_ADDRESS, LOGGER


@dataclasses.dataclass
class ProjectorState:
    # Projector State
    state: Dict[str, str]
    # Projector Info
    info: Dict[str, str]
    # Availability - whether this info is fresh
    available: bool


class Manager:
    """Device Status Manager pattern to coordinate entity ypdates"""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, projector: Projector):
        self._hass = hass
        self._entry = entry
        self._projector = projector

        self._loop_interval = DEFAULT_POLL_INTERVAL

        self._update_callbacks: Set[Callable[[ProjectorState], None]] = set()

        self._result = ProjectorState(state={}, info={}, available=False)

        # This flag becomes true once we've executed at least 1 successful projector
        # poll loop, which means we have data about the device ready.
        self._initialized = asyncio.Event()

        self._shutdown = asyncio.Event()

    @property
    def initialized(self) -> bool:
        return self._initialized.is_set()

    @property
    def projector(self) -> Projector:
        return self._projector

    @property
    def state(self) -> ProjectorState:
        return self._result

    async def async_wait_for_initialization(self):
        return await self._initialized.wait()

    def update_state(self) -> ProjectorState:
        try:
            return ProjectorState(
                state=self._projector.status(),
                info=self._projector.info(),
                available=True,
            )
        except Exception as e:
            LOGGER.debug("Exception during projector connection", exc_info=e)
            LOGGER.warning("Could not connect to projector to retrieve status")
            return dataclasses.replace(self._result, available=False)

    async def async_update_state(self) -> ProjectorState:
        """Async version of update state"""
        return await self._hass.async_add_executor_job(self.update_state)

    async def loop(self):
        """Projector monitoring loop"""
        LOGGER.info("Projector initial state retrieval")
        self._result = await self.async_update_state()
        self._initialized.set()

        LOGGER.info("Starting projector message poll loop")
        while True:
            new_result = await self.async_update_state()
            if not self._result.available and new_result.available:
                LOGGER.info("Projector has became available")
            elif self._result.available and not new_result.available:
                LOGGER.warn("Projector has become unavailable")
            self._result = new_result
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

    def register_update_callback(self, callback: Callable[[ProjectorState], None]):
        self._update_callbacks.add(callback)

    def unregister_update_callback(self, callback: Callable[[ProjectorState], None]):
        self._update_callbacks.remove(callback)

    def _call_registered_update_callbacks(self, value: ProjectorState):
        for callback in self._update_callbacks:
            callback(value)


def projector_device_id(manager: Manager) -> str:
    device_id = manager.state.info[INFO_MAC_ADDRESS].replace(":", "")
    return device_id


def normalize_key(key: str) -> str:
    return key.lower().replace(" ", "_")


class OptomaProjectorSettingEntity:
    """
    Common code for OptomaProjector settings entities.
    Entities derived from this also need to derive from the standard HA entities.
    """

    _attr_has_entity_name = True

    def __init__(
        self, device_id: str, description: EntityDescription, manager: Manager, key: str
    ):
        self.entity_description = description

        self._manager = manager
        self._key = key

        self._device_id = device_id

        # Need to provide type annotations since in MRO for subclasses this class is before the
        # HA entity that actually defines the _attr_* methods
        self._attr_device_info: DeviceInfo | None = DeviceInfo(
            identifiers={(DOMAIN, device_id)}
        )
        self._attr_translation_key: str | None = self.entity_description.key
        self._attr_unique_id: str | None = (
            f"{self._device_id}_{self.entity_description.key}"
        )
        pass

    def update_callback(self, value: ProjectorState):
        self.schedule_update_ha_state()  # type: ignore

    async def async_added_to_hass(self):
        self._manager.register_update_callback(self.update_callback)

    async def async_will_remove_from_hass(self):
        self._manager.unregister_update_callback(self.update_callback)

    @property
    def available(self):
        # Most projector functions can't be modified if the projector isn't powered on
        return True if self._key in self._manager.state.state else False
