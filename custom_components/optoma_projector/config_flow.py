from typing import Any

import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN


class OptomaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore
    """Handle a config flow for Optomo Projector"""

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            await self.async_set_unique_id(user_input["url"])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title="Optoma Projector Connection Details",
                data={},
                options={
                    "url": user_input["url"],
                    "username": user_input["username"],
                    "password": user_input["password"],
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("url"): str,
                    vol.Required("username", default="admin"): str,
                    vol.Required("password", default="admin"): str,
                }
            ),
        )
