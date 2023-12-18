from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription

from . import Manager, ProjectorState
from .const import DOMAIN


class OptomaProjectorSettingEntity:
    """
    Common code for OptomaProjector settings entities.
    Entities derived from this also need to derive from the standard HA entities.
    """

    _attr_has_entity_name = True

    def __init__(
        self, unique_id: str, description: EntityDescription, manager: Manager, key: str
    ):
        self.entity_description = description

        self._manager = manager
        self._key = key

        self._device_id = unique_id

        # Need to provide type annotations since in MRO for subclasses this class is before the
        # HA entity that actually defines the _attr_* methods
        self._attr_device_info: DeviceInfo | None = DeviceInfo(
            identifiers={(DOMAIN, unique_id)}
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
