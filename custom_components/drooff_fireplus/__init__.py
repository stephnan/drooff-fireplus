"""
Custom integration to integrate drooff_fireplus with Home Assistant.

For more details about this integration, please refer to
https://github.com/stephnan/drooff_fireplus
"""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.const import Platform, CONF_IP_ADDRESS
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.loader import async_get_loaded_integration

from .api import DrooffFireplusApiClient
from .const import DOMAIN, LOGGER
from .coordinator import FirePlusDataUpdateCoordinator
from .data import DrooffFireplusData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from .data import DrooffFireplusConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: DrooffFireplusConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    coordinator = FirePlusDataUpdateCoordinator(
        hass=hass,
        logger=LOGGER,
        name=DOMAIN,
        update_interval=timedelta(seconds=entry.data["interval"]),
    )
    entry.runtime_data = DrooffFireplusData(
        client=DrooffFireplusApiClient(session=async_get_clientsession(hass), ip=entry.data[CONF_IP_ADDRESS]),
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: DrooffFireplusConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: DrooffFireplusConfigEntry,
) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
