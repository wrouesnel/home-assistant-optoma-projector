from typing import Any, Mapping

from optoma_web_api import BUTTONS

from custom_components.optoma_projector.helpers import (
    Manager,
    OptomaProjectorSettingEntity,
    normalize_key,
    projector_device_id,
)
from homeassistant.components.button import ButtonEntity
from homeassistant.const import EntityCategory
from homeassistant.helpers.entity import EntityDescription

from .const import DOMAIN


async def async_setup_entry(hass, config_entry, async_add_entities):
    manager: Manager = hass.data[DOMAIN][config_entry.entry_id]

    entities = []

    # Create switches for all 2-option entities
    for key, value in BUTTONS.items():
        normalized_key = key.lower().replace(" ", "_")

        entity_description = EntityDescription(
            key=normalized_key,
            entity_category=EntityCategory.CONFIG,
            name=key,
        )

        entity = OptomaProjectorButton(
            projector_device_id(manager),
            description=entity_description,
            manager=manager,
            key=key,
        )

        entities.append(entity)

    async_add_entities(entities)


class OptomaProjectorButton(OptomaProjectorSettingEntity, ButtonEntity):
    """Representation of a scene button on a Yamaha Ynca device."""

    _key: str
    _manager: Manager
    entity_description: EntityDescription

    def press(self) -> None:
        set_fn = getattr(self._manager.projector, normalize_key(self._key))
        set_fn()
