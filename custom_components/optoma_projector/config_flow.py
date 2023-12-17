from typing import Any

import voluptuous as vol

from homeassistant import config_entries

from .const import CONFIG_PASSWORD, CONFIG_URL, CONFIG_USERNAME, DOMAIN


class OptomaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore
    """Handle a config flow for Optomo Projector"""

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            await self.async_set_unique_id(user_input["url"])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title="Optoma Projector",
                data={},
                options={
                    CONFIG_URL: user_input[CONFIG_URL],
                    CONFIG_USERNAME: user_input[CONFIG_USERNAME],
                    CONFIG_PASSWORD: user_input[CONFIG_PASSWORD],
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONFIG_URL): str,
                    vol.Required(CONFIG_USERNAME, default="admin"): str,
                    vol.Required(CONFIG_PASSWORD, default="admin"): str,
                }
            ),
        )
