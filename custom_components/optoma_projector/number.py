from typing import Any, Mapping

from optoma_web_api import STATUS_VALUE_MAP

from custom_components.optoma_projector import Manager, ProjectorState
from custom_components.optoma_projector.helpers import OptomaProjectorSettingEntity
from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory
from homeassistant.helpers.entity import EntityDescription

from .const import DOMAIN, LOGGER


async def async_setup_entry(hass, config_entry, async_add_entities):
    manager: Manager = hass.data[DOMAIN][config_entry.entry_id]

    entities = []

    # Create switches for all 2-option entities
    for key, value_dict in STATUS_VALUE_MAP.items():
        if isinstance(value_dict, int):
            continue

        normalized_key = key.lower().replace(" ", "_")

        entity_description = EntityDescription(
            key=normalized_key,
            entity_category=EntityCategory.CONFIG,
            name=key,
        )

        new_number = OptomaProjectorNumber(
            unique_id=config_entry.entry_id,
            description=entity_description,
            manager=manager,
            key=key,
        )
        new_number._attr_native_min_value = -100
        new_number._attr_native_max_value = 100
        new_number._attr_native_step = 1
        new_number._attr_mode = NumberMode.BOX
        new_number._attr_native_unit_of_measurement = None

        entities.append(new_number)

    async_add_entities(entities)


class OptomaProjectorNumber(OptomaProjectorSettingEntity, NumberEntity):
    """Representation of a number on a Yamaha Ynca device."""

    entity_description: EntityDescription

    @property
    def native_value(self) -> float | None:
        """Return the value reported by the number."""
        return self._manager.state.state.get(self._key, None)

    # @property
    # def native_max_value(self) -> float:
    #     """Return the maximum value."""
    #     if fn := self.entity_description.native_max_value_fn:
    #         return fn(self._associated_zone)
    #     return super().native_max_value

    def set_native_value(self, value: float) -> None:
        # setattr(self._subunit, self.entity_description.key, value)
        pass
