"""Provides the EtekcityBP ActiveBluetooth DataUpdateCoordinator."""

from __future__ import annotations

import asyncio
import logging

from bleak import BleakClient

from typing import TYPE_CHECKING

from homeassistant.components import bluetooth
from homeassistant.components.bluetooth.active_update_processor import (
    ActiveBluetoothProcessorCoordinator,
)
from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothDataUpdate,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import CoreState, HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    CHARACTERISTIC_BLOOD_PRESSURE,
    CLIENT_CHARACTERISTIC_CONFIG_HANDLE,
    CLIENT_CHARACTERISTIC_CONFIG_DATA,
    HW_REVISION_STRING_CHARACTERISTIC_UUID,
    SW_REVISION_STRING_CHARACTERISTIC_UUID,
)
from .device import EtekcityBPDevice


_LOGGER = logging.getLogger(__name__)

DEVICE_STARTUP_TIMEOUT = 30

type EtekcityConfigEntry = ConfigEntry[EtekcityBPCoordinator]

class EtekcityBPCoordinator(
    ActiveBluetoothProcessorCoordinator [None]
):
    """Class to manage fetching data."""

    def __init__(
        self,
        hass: HomeAssistant,
        logger: logging.Logger,
        address: str,
        device: EtekcityBPDevice,
        base_unique_id: str,
        device_name: str,
        connectable: bool,
    ) -> None:
        """Initialize data coordinator."""
        super().__init__(
            hass=hass,
            logger=logger,
            address=address,
            mode=bluetooth.BluetoothScanningMode.ACTIVE,
            update_method=self._update_method,
            needs_poll_method=self._needs_poll,
            poll_method=self._async_update,
            connectable=connectable,
        )
        self.address = address
        self.device = device
        self.device_name = device_name
        self.base_unique_id = base_unique_id

        _LOGGER.debug(f"Scanner count: {bluetooth.async_scanner_count(hass, connectable=True)}")
        if bluetooth.async_scanner_count(hass, connectable=True) < 1:
            _LOGGER.error("No Bluetooth scanner available, cannot start coordinator")
            raise ConfigEntryNotReady("No Bluetooth scanner available")

    @callback
    def _needs_poll(
        self,
        service_info: bluetooth.BluetoothServiceInfoBleak,
        seconds_since_last_poll: float | None,
    ) -> bool:
        # Only poll if hass is running, we need to poll,
        # and we actually have a way to connect to the device
        needs_poll = (
            self.hass.state == CoreState.running
            and self.device.poll_needed(seconds_since_last_poll)
            and bool(
                bluetooth.async_ble_device_from_address(
                    self.hass, service_info.device.address, connectable=True
                )
            )
        )
        return needs_poll

    def _update_method(self, service_info) -> PassiveBluetoothDataUpdate:
        """Update method for the coordinator."""
        # This method is called when the coordinator is updated.
        # It can be used to update the device state or perform other actions.
        _LOGGER.info("Device %s is now available", self.device_name)

    async def _async_update(
        self, service_info: bluetooth.BluetoothServiceInfoBleak
    ) -> None:
        """Poll the device."""
        while self._available:
            try:
                _LOGGER.debug(f"Connecting to device {service_info.device.address}")
                async with BleakClient(service_info.device) as client:
                    if (not client.is_connected):
                        raise "client not connected"

                    # Get Hardware and Firmware version
                    try:
                        if not self.device.data.hw_version:
                            _LOGGER.debug("Reading hardware version")
                            self.device.data.hw_version = (
                                await client.read_gatt_char(
                                    HW_REVISION_STRING_CHARACTERISTIC_UUID
                                )
                            ).decode()

                        if not self.device.data.sw_version:
                            _LOGGER.debug("Reading software version")
                            self.device.data.sw_version = (
                                await client.read_gatt_char(
                                    SW_REVISION_STRING_CHARACTERISTIC_UUID
                                )
                            ).decode()
                    except Exception as e:
                        _LOGGER.warning(f"Error reading version info: {e}")
                        self.device.data.hw_version = "Unknown"
                        self.device.data.sw_version = "Unknown"

                    # Enable notifications to get BP values
                    _LOGGER.debug ("Starting notifications")
                    await client.start_notify(CHARACTERISTIC_BLOOD_PRESSURE, self._notification_handler)
                    await client.write_gatt_descriptor(CLIENT_CHARACTERISTIC_CONFIG_HANDLE, CLIENT_CHARACTERISTIC_CONFIG_DATA)
                    await asyncio.sleep(4)

                    _LOGGER.debug ("Pausing notification processing")
                    async with asyncio.timeout(10):
                        await client.stop_notify(CHARACTERISTIC_BLOOD_PRESSURE)
                    await asyncio.sleep(1)
            except Exception as e:
                _LOGGER.debug(f"Error {e}; Long pausing notification processing")
                await asyncio.sleep(20)

    @callback
    async def _notification_handler(self, handle, data):
        """Handle notifications from the device."""
        _LOGGER.debug(f"Notification - Handle: {handle}, Data: {data.hex()}")

        await self.device.update(data)

    @callback
    def _async_handle_unavailable(
        self, service_info: bluetooth.BluetoothServiceInfoBleak
    ) -> None:
        """Handle the device going unavailable."""
        super()._async_handle_unavailable(service_info)
        _LOGGER.info("Device %s is unavailable", self.device_name)


    @callback
    def _async_handle_bluetooth_event(
        self,
        service_info: bluetooth.BluetoothServiceInfoBleak,
        change: bluetooth.BluetoothChange,
    ) -> None:
        """Handle a Bluetooth event."""
        super()._async_handle_bluetooth_event(service_info, change)
        # Process incoming advertisement data
        _LOGGER.debug(f"service_info: {service_info}")
        _LOGGER.debug(f"change: {change}")

        if not (
            self.device.parse_advertisement_data(
                service_info.device, service_info.advertisement
            )
        ):
            return

    async def async_unload_entry(self) -> bool:
        """Unload a config entry."""
        self._available = False
        return True
