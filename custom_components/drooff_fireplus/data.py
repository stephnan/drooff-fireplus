"""Custom types for drooff_fireplus."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import DrooffFireplusApiClient
    from .coordinator import FirePlusDataUpdateCoordinator


type DrooffFireplusConfigEntry = ConfigEntry[DrooffFireplusData]


@dataclass
class DrooffFireplusData:
    """Data for the Drooff Fire+ integration."""

    client: DrooffFireplusApiClient
    coordinator: FirePlusDataUpdateCoordinator
    integration: Integration
