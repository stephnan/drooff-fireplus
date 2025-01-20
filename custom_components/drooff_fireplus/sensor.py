"""Sensor platform for drooff_fireplus."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aioesphomeapi.connection import dataclass
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.const import PERCENTAGE, UnitOfPressure, UnitOfTemperature, UnitOfPower
from homeassistant.helpers.device_registry import DeviceInfo

from .entity import DrooffFireplusEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import FirePlusDataUpdateCoordinator
    from .data import DrooffFireplusConfigEntry


@dataclass(frozen=True, kw_only=True)
class DrooffFireplusSensorEntityDescription(SensorEntityDescription):
    """Description of a Drooff Fireplus sensor."""

    entity_object: str


"""
get descriptions from here
https://openhabforum.de/viewtopic.php?t=4386&start=20

"""
ENTITY_DESCRIPTIONS = (
    DrooffFireplusSensorEntityDescription(
        key="drooff_fireplus.brennraumtemperatur",
        name="Brennraumtemperatur",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:fire",
        entity_object="TEMPERATUR",
    ),
    DrooffFireplusSensorEntityDescription(
        key="drooff_fireplus.luftschieber",
        name="Luftschieber",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:air-filter",
        entity_object="SCHIEBER",
    ),
    DrooffFireplusSensorEntityDescription(
        key="drooff_fireplus.feinzug",
        name="Feinzug",
        native_unit_of_measurement=UnitOfPressure.PA,
        icon="mdi:home-roof",
        entity_object="FEINZUG",
    ),
    DrooffFireplusSensorEntityDescription(
        key="drooff_fireplus.status",
        name="Betriebsstatus",
        icon="mdi:fireplace",
        entity_object="STATUS",
    ),
    DrooffFireplusSensorEntityDescription(
        key="drooff_fireplus.led_status",
        name="LED Streifen",
        icon="mdi:led-strip",
        entity_object="LED",
    ),
    DrooffFireplusSensorEntityDescription(
        key="drooff_fireplus.led_helligkeit",
        name="LED Streifen",
        icon="mdi:led-strip",
        native_unit_of_measurement=PERCENTAGE,
        entity_object="HELLIGKEIT",
    ),
    DrooffFireplusSensorEntityDescription(
        key="drooff_fireplus.betriebsart",
        name="Betriebart",
        icon="mdi:campfire",
        entity_object="BETRIEBSART",
    ),
    DrooffFireplusSensorEntityDescription(
        key="drooff_fireplus.abbrand",
        name="Abbrand",
        icon="mdi:campfire",
        entity_object="ABBRAND",
    ),
    DrooffFireplusSensorEntityDescription(
        key="drooff_fireplus.leistung",
        name="Leistung",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        icon="mdi:heat-wave",
        entity_object="LEISTUNG",
    ),
    DrooffFireplusSensorEntityDescription(
        key="drooff_fireplus.lautstaerke",
        name="Lautstärke",
        icon="mdi:volume-high",
        native_unit_of_measurement=PERCENTAGE,
        entity_object="LAUTSTAERKE",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: DrooffFireplusConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        DrooffFireplusSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
            entity_object=entity_description.entity_object,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class DrooffFireplusSensor(DrooffFireplusEntity, SensorEntity):
    """drooff_fireplus Sensor class."""

    def __init__(
        self,
        coordinator: FirePlusDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
        entity_object: str,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self.entity_position = entity_object
        self._attr_unique_id = entity_description.key
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    coordinator.config_entry.domain,
                    coordinator.config_entry.entry_id,
                ),
            },
        )

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        return self.coordinator.data[self.entity_position]
