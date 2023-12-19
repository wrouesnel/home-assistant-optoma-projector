from typing import Mapping

from optoma_web_api import STATUS_VALUE_MAP

from homeassistant.components.select import SelectEntity
from homeassistant.const import EntityCategory
from homeassistant.helpers.entity import EntityDescription

from . import Manager
from .const import DOMAIN
from .helpers import OptomaProjectorSettingEntity, projector_device_id


async def async_setup_entry(hass, config_entry, async_add_entities):
    manager: Manager = hass.data[DOMAIN][config_entry.entry_id]

    entities = []

    # Create switches for all 2-option entities
    for key, value_dict in STATUS_VALUE_MAP.items():
        # Require a mapping
        if not isinstance(value_dict, Mapping):
            continue

        # Exclude simple bools
        if all(v in ("Off", "On") for v in value_dict.values()):
            continue

        normalized_key = key.lower().replace(" ", "_")

        entity_description = EntityDescription(
            key=normalized_key,
            entity_category=EntityCategory.CONFIG,
            name=key,
        )

        new_select = OptomaProjectorSelect(
            projector_device_id(manager),
            description=entity_description,
            manager=manager,
            key=key,
        )
        new_select._attr_options = list(value_dict.values())

        entities.append(new_select)

    async_add_entities(entities)


class OptomaProjectorSelect(OptomaProjectorSettingEntity, SelectEntity):
    """Representation of a select entity on a Yamaha Ynca device."""

    _key: str
    _manager: Manager
    entity_description: EntityDescription

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""
        return self._manager.state.state.get(self._key, None)

    def select_option(self, option: str) -> None:
        """Change the selected option."""
        # if self.entity_description.enum is not None:
        #     value = [
        #         e.value
        #         for e in self.entity_description.enum
        #         if slugify(e.value) == option
        #     ]
        #
        #     if len(value) == 1:
        #         setattr(
        #             self._subunit,
        #             self.entity_description.key,
        #             self.entity_description.enum(value[0]),
        #         )
