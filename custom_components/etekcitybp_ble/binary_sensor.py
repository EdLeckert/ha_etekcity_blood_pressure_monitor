"""Support for EtekcityBP sensors."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from homeassistant.const import (
    STATE_UNAVAILABLE, 
    STATE_UNKNOWN
)

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import EtekcityConfigEntry, EtekcityBPCoordinator
from .entity import EtekcityBPEntity

IGNORED_STATES = {STATE_UNAVAILABLE, STATE_UNKNOWN}

import logging

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES: dict[str, BinarySensorEntityDescription] = {
    "irregular_heartbeat0": BinarySensorEntityDescription(
        key="irregular_heartbeat0",
        name ="Irregular Heartbeat User 1",
        device_class=BinarySensorDeviceClass.PROBLEM,
        icon="mdi:heart-multiple",
    ),
    "irregular_heartbeat1": BinarySensorEntityDescription(
        key="irregular_heartbeat1",
        name ="Irregular Heartbeat User 2",
        entity_registry_enabled_default=False,
        device_class=BinarySensorDeviceClass.PROBLEM,
        icon="mdi:heart-multiple",
    ),
    "motion_indicator0": BinarySensorEntityDescription(
        key="motion_indicator0",
        name ="Motion User 1",
        device_class=BinarySensorDeviceClass.PROBLEM,
        icon="mdi:hand-wave-outline",
    ),
    "motion_indicator1": BinarySensorEntityDescription(
        key="motion_indicator1",
        name ="Motion User 2",
        entity_registry_enabled_default=False,
        device_class=BinarySensorDeviceClass.PROBLEM,
        icon="mdi:hand-wave-outline",
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EtekcityConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the binary sensor entities for the EtekcityBP integration."""
    coordinator = entry.runtime_data

    entities = [
        EtekcityBPBinarySensor(coordinator, sensor)
        for sensor in SENSOR_TYPES
    ]
    async_add_entities(entities)

   
class EtekcityBPBinarySensor(EtekcityBPEntity, BinarySensorEntity):
    """Representation of a EtekcityBP binary sensor."""
    def __init__(
        self,
        coordinator: EtekcityBPCoordinator,
        sensor: str,
    ) -> None:
        """Initialize the EtekcityBP binary sensor."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._sensor = sensor
        self._attr_unique_id = f"{coordinator.base_unique_id}-{sensor}"
        self.entity_description = SENSOR_TYPES[sensor]

    @property
    def is_on(self) -> bool | None:
        """Return the state of the binary sensor."""
        value = self.sensor_data.get(self._sensor, self._attr_is_on)
        return value

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        await super().async_added_to_hass()

        # Set initial state based on the last known state and sensor data
        last_state = await self.async_get_last_state()

        if not last_state or last_state.state in IGNORED_STATES:
            return

        value = True if last_state.state == "on" else False
        self._attr_native_value = value
        self._device.update_value(self._sensor, value)
