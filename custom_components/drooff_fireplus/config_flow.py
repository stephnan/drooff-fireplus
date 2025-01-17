"""Adds config flow for Blueprint."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, CONF_IP_ADDRESS
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from slugify import slugify

from .api import (
    DrooffFireplusApiClient,
    DrooffFireplusApiClientAuthenticationError,
    DrooffFireplusApiClientCommunicationError,
    DrooffFireplusApiClientError,
)
from .const import DOMAIN, LOGGER


class BlueprintFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Blueprint."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._test_credentials(
                    ip=user_input[CONF_IP_ADDRESS]
                )
            except DrooffFireplusApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except DrooffFireplusApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(
                    ## Do NOT use this in production code
                    ## The unique_id should never be something that can change
                    ## https://developers.home-assistant.io/docs/config_entries_config_flow_handler#unique-ids
                    unique_id=slugify(user_input[CONF_IP_ADDRESS])
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_IP_ADDRESS],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="address",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_IP_ADDRESS,
                        default=(user_input or {}).get(CONF_IP_ADDRESS, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    )
                },
            ),
            errors=_errors,
        )

    async def _test_credentials(self, ip: str) -> None:
        """Validate credentials."""
        client = DrooffFireplusApiClient(session=async_create_clientsession(self.hass), ip=ip)
        await client.async_get_data()
