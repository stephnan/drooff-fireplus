"""BlueprintEntity class."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION
from .coordinator import FirePlusDataUpdateCoordinator


class DrooffFireplusEntity(CoordinatorEntity[FirePlusDataUpdateCoordinator]):
    """BlueprintEntity class."""

    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: FirePlusDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)

