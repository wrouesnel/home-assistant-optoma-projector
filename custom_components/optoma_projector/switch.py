from typing import Any, Mapping

from optoma_web_api import STATUS_VALUE_MAP

from custom_components.optoma_projector.helpers import (
    Manager,
    OptomaProjectorSettingEntity,
    normalize_key,
    projector_device_id,
)
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory
from homeassistant.helpers.entity import EntityDescription

from .const import DOMAIN, LOGGER


async def async_setup_entry(hass, config_entry, async_add_entities):
    manager: Manager = hass.data[DOMAIN][config_entry.entry_id]

    entities = []

    # Create switches for all 2-option entities
    for key, value_dict in STATUS_VALUE_MAP.items():
        if not isinstance(value_dict, Mapping):
            continue

        if len(value_dict) != 2:
            continue

        # Check the values are 0 and 1
        if any(v not in ("Off", "On") for v in value_dict.values()):
            continue

        normalized_key = key.lower().replace(" ", "_")

        entity_description = EntityDescription(
            key=normalized_key,
            entity_category=EntityCategory.CONFIG,
            name=key,
        )

        new_switch = OptomaProjectorSwitch(
            projector_device_id(manager),
            description=entity_description,
            manager=manager,
            key=key,
        )

        entities.append(new_switch)

    async_add_entities(entities)


class OptomaProjectorSwitch(OptomaProjectorSettingEntity, SwitchEntity):
    """Representation of a switch on a Yamaha Ynca device."""

    _key: str
    _manager: Manager
    entity_description: EntityDescription

    @property
    def is_on(self) -> bool | None:
        """Return True if entity is on."""
        result = self._manager.state.state.get(self._key, None)
        if result is None:
            return result
        return True if result == "On" else False

    def turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        set_fn = getattr(self._manager.projector, normalize_key(self._key))
        set_fn("On")

    def turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        set_fn = getattr(self._manager.projector, normalize_key(self._key))
        set_fn("Off")
