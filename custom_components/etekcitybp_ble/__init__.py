"""The EtekcityBP integration."""

from __future__ import annotations

from bleak_retry_connector import close_stale_connections_by_address

import logging

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_ADDRESS,
    CONF_MAC,
    CONF_NAME,
    Platform,
)
from homeassistant.core import CoreState, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr

from .coordinator import EtekcityConfigEntry, EtekcityBPCoordinator
from .device import EtekcityBPDevice


PLATFORMS = [Platform.BINARY_SENSOR, Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: EtekcityConfigEntry) -> bool:
    """Set up Etekcity Blood Pressure BLE device from a config entry."""
    assert entry.unique_id is not None
    if CONF_ADDRESS not in entry.data and CONF_MAC in entry.data:
        # Bleak uses addresses not mac addresses which are actually
        # UUIDs on some platforms (MacOS).
        mac = entry.data[CONF_MAC]
        if "-" not in mac:
            mac = dr.format_mac(mac)
        hass.config_entries.async_update_entry(
            entry,
            data={**entry.data, CONF_ADDRESS: mac},
        )


    address = entry.unique_id
    assert address is not None

    connectable = True

    await close_stale_connections_by_address(address)

    device = EtekcityBPDevice()

    coordinator = entry.runtime_data = EtekcityBPCoordinator(
        hass,
        _LOGGER,
        address,
        device,
        entry.unique_id,
        entry.data.get(CONF_NAME, entry.title),
        connectable,
    )

    entry.async_on_unload(coordinator.async_start())

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await hass.config_entries.async_forward_entry_setups(
        entry, PLATFORMS
    )

    return True

async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    )
