"""Support for EtekcityBP sensors."""

from __future__ import annotations

from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)

from homeassistant.components.bluetooth import async_last_service_info
from homeassistant.const import (
        EntityCategory,
        SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        UnitOfPressure,
)
from homeassistant.const import (
    STATE_UNAVAILABLE, 
    STATE_UNKNOWN
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    BPM,
    HW_VERSION_KEY,
    SW_VERSION_KEY,
)
from .coordinator import EtekcityConfigEntry, EtekcityBPCoordinator
from .entity import EtekcityBPEntity

import logging

IGNORED_STATES = {STATE_UNAVAILABLE, STATE_UNKNOWN}

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES: dict[str, SensorEntityDescription] = {
    "rssi": SensorEntityDescription(
        key="rssi",
        translation_key="bluetooth_signal",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "systolic0": SensorEntityDescription(
        key="systolic0",
        name ="Systolic Pressure User 1",
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.MMHG,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision = 0,
        suggested_unit_of_measurement=UnitOfPressure.MMHG,
    ),
    "diastolic0": SensorEntityDescription(
        key="diastolic0",
        name ="Diastolic Pressure User 1",
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.MMHG,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision = 0,
        suggested_unit_of_measurement=UnitOfPressure.MMHG,
    ),
    "systolickpa0": SensorEntityDescription(
        key="systolickpa0",
        name ="Systolic (kPa) User 1",
        device_class=SensorDeviceClass.PRESSURE,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfPressure.KPA,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision = 1,
        suggested_unit_of_measurement=UnitOfPressure.KPA,
    ),
    "diastolickpa0": SensorEntityDescription(
        key="diastolickpa0",
        name ="Diastolic (kPa) User 1",
        device_class=SensorDeviceClass.PRESSURE,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfPressure.KPA,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision = 1,
        suggested_unit_of_measurement=UnitOfPressure.KPA,
    ),
    "pulse0": SensorEntityDescription(
        key="pulse0",
        name ="Pulse User 1",
        icon="mdi:heart-pulse",
        native_unit_of_measurement=BPM,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision = 0,
    ),
    "systolic1": SensorEntityDescription(
        key="systolic1",
        name ="Systolic Pressure User 2",
        entity_registry_enabled_default=False,
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.MMHG,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision = 0,
        suggested_unit_of_measurement=UnitOfPressure.MMHG,
    ),
    "diastolic1": SensorEntityDescription(
        key="diastolic1",
        name ="Diastolic Pressure User 2",
        entity_registry_enabled_default=False,
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.MMHG,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision = 0,
        suggested_unit_of_measurement=UnitOfPressure.MMHG,
    ),
    "systolickpa1": SensorEntityDescription(
        key="systolickpa1",
        name ="Systolic (kPa) User 2",
        device_class=SensorDeviceClass.PRESSURE,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfPressure.KPA,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision = 1,
        suggested_unit_of_measurement=UnitOfPressure.KPA,
    ),
    "diastolickap1": SensorEntityDescription(
        key="diastolickap1",
        name ="Diastolic (kPa) User 2",
        device_class=SensorDeviceClass.PRESSURE,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfPressure.KPA,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision = 1,
        suggested_unit_of_measurement=UnitOfPressure.KPA,
    ),
    "pulse1": SensorEntityDescription(
        key="pulse1",
        name ="Pulse User 2",
        icon="mdi:heart-pulse",
        entity_registry_enabled_default=False,
        native_unit_of_measurement=BPM,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision = 0,
    ),
    "display_units": SensorEntityDescription(
        key="display_units",
        name ="Display Units",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "error_code": SensorEntityDescription(
        key="error_code",
        name ="Error Code",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:alert-circle-outline",
    ),  
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EtekcityConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the sensor entities for the EtekcityBP integration."""
    coordinator = entry.runtime_data

    entities = [
        EtekcityBPSensor(coordinator, sensor)
        for sensor in SENSOR_TYPES
        if sensor != "rssi" 
    ]
    entities.append(EtekcityBPRSSISensor(coordinator, "rssi"))
    async_add_entities(entities)

   
class EtekcityBPSensor(EtekcityBPEntity, RestoreSensor):
    """Representation of a EtekcityBP sensor."""
    def __init__(
        self,
        coordinator: EtekcityBPCoordinator,
        sensor: str,
    ) -> None:
        """Initialize the EtekcityBP sensor."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._sensor = sensor
        self._attr_unique_id = f"{coordinator.base_unique_id}-{sensor}"
        self.entity_description = SENSOR_TYPES[sensor]

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        await super().async_added_to_hass()

        # Set initial state based on the last known state and sensor data
        last_state = await self.async_get_last_state()
        last_sensor_data = await self.async_get_last_sensor_data()

        if not last_state or not last_sensor_data or last_state.state in IGNORED_STATES:
            return
        self._attr_native_value = last_sensor_data.native_value
        self._device.update_value(self._sensor, last_sensor_data.native_value)

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        value = self.sensor_data.get(self._sensor, self._attr_native_value)
        return value


class EtekcityBPRSSISensor(EtekcityBPSensor):
    """Representation of a EtekcityBP RSSI sensor."""
    _hw_version = None
    _sw_version = None

    @property
    def native_value(self) -> str | int | None:
        """Return the state of the sensor."""
        self._update_device_info()

        if service_info := async_last_service_info(
            self.hass, self._address, self.coordinator.connectable
        ):
            return service_info.rssi
        return None

    def _update_device_info(self):
        """Update DeviceInfo."""
        if self._hw_version is None or self._sw_version is None:
            if self.coordinator.device.data.hw_version is not None:
                self._hw_version = self.coordinator.device.data.hw_version
                self._sw_version = self.coordinator.device.data.sw_version

                device_registry = dr.async_get(self.hass)
                device_entry = device_registry.async_get_device(
                    connections={(dr.CONNECTION_BLUETOOTH, self.coordinator.device.address)}
                )
                device_registry.async_update_device(
                    device_entry.id, hw_version=self._hw_version, sw_version=self._sw_version
                )
                self._attr_device_info.update(
                    {HW_VERSION_KEY: self._hw_version, SW_VERSION_KEY: self._sw_version}
                )