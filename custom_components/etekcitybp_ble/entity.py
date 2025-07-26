"""An abstract class common to all EtekcityBP entities."""

from __future__ import annotations

from collections.abc import Mapping
import logging
from typing import Any

from homeassistant.const import (
    ATTR_CONNECTIONS, 
)
from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import EtekcityBPCoordinator
from .device import EtekcityBPDevice

_LOGGER = logging.getLogger(__name__)


class EtekcityBPEntity(RestoreEntity):
    """Generic entity encapsulating common features of EtekcityBP device."""

    _device: EtekcityBPDevice
    _attr_has_entity_name = True

    def __init__(self, coordinator: EtekcityBPCoordinator) -> None:
        """Initialize the entity."""
        self._device = coordinator.device
        self._last_run_success: bool | None = None
        self._address = coordinator.address
        self._attr_unique_id = coordinator.base_unique_id
        self._attr_device_info = DeviceInfo(
            connections={(dr.CONNECTION_BLUETOOTH, self._address)},
            manufacturer=MANUFACTURER,
            name=coordinator.device_name,
        )
        if ":" not in self._address:
            # MacOS Bluetooth addresses are not mac addresses
            return
        # If the bluetooth address is also a mac address,
        # add this connection as well to prevent a new device
        # entry from being created when upgrading from a previous
        # version of the integration.
        self._attr_device_info[ATTR_CONNECTIONS].add(
            (dr.CONNECTION_NETWORK_MAC, self._address)
        )

    @property
    def sensor_data(self) -> dict[str, Any]:
        """Return parsed device data for this entity."""
        return self.coordinator.device.sensor_data

