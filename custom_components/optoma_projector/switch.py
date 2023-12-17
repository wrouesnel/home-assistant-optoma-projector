async def async_setup_entry(hass, config_entry, async_add_entities):
    # domain_entry_data: DomainEntryData = hass.data[DOMAIN][config_entry.entry_id]
    #
    # entities = []
    # for zone_attr_name in ZONE_ATTRIBUTE_NAMES:
    #     if zone_subunit := getattr(domain_entry_data.api, zone_attr_name):
    #         for entity_description in ZONE_ENTITY_DESCRIPTIONS:
    #             if getattr(zone_subunit, entity_description.key, None) is not None:
    #                 entities.append(
    #                     YamahaYncaSwitch(
    #                         config_entry.entry_id, zone_subunit, entity_description
    #                     )
    #                 )
    #
    # # These are features on the SYS subunit, but they are tied to a zone
    # assert(domain_entry_data.api.sys is not None)
    # for entity_description in SYS_ENTITY_DESCRIPTIONS:
    #     assert(isinstance(entity_description.associated_zone_attr, str))
    #     if getattr(domain_entry_data.api.sys, entity_description.key, None) is not None:
    #         if zone_subunit := getattr(domain_entry_data.api, entity_description.associated_zone_attr):
    #             entities.append(
    #                 YamahaYncaSwitch(
    #                     config_entry.entry_id, domain_entry_data.api.sys, entity_description, associated_zone=zone_subunit
    #                 )
    #             )
    #
    # async_add_entities(entities)
    pass


# class OptomaProjectorSwitch(YamahaYncaSettingEntity, SwitchEntity):
#     """Representation of a switch on a Yamaha Ynca device."""
#
#     entity_description: YncaSwitchEntityDescription
#
#     @property
#     def is_on(self) -> bool | None:
#         """Return True if entity is on."""
#         return (
#             getattr(self._subunit, self.entity_description.key)
#             == self.entity_description.on
#         )
#
#     def turn_on(self, **kwargs: Any) -> None:
#         """Turn the entity on."""
#         setattr(self._subunit, self.entity_description.key, self.entity_description.on)
#
#     def turn_off(self, **kwargs: Any) -> None:
#         """Turn the entity off."""
#         setattr(self._subunit, self.entity_description.key, self.entity_description.off)
