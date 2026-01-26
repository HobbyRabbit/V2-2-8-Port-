"""The ac_infinity integration."""
from __future__ import annotations
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .coordinator import ACInfinityDataUpdateCoordinator
from .device import ACInfinityController, BLEDeviceWrapper  # BLEDeviceWrapper if you have a helper
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the AC Infinity integration (no config flow)."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up AC Infinity from a config entry."""
    address = entry.data["address"]
    ble_device = entry.data.get("ble_device")  # Should be a BLEDeviceWrapper or BleakDevice
    if not ble_device:
        _LOGGER.error("No BLE device provided for %s", address)
        return False

    # Create controller
    controller = ACInfinityController(ble_device)

    # Create coordinator
    coordinator = ACInfinityDataUpdateCoordinator(hass, _LOGGER, ble_device, controller)
    await coordinator.async_wait_ready()

    # Store references
    hass.data[DOMAIN][address] = {
        "controller": controller,
        "coordinator": coordinator,
    }

    # Forward setup to platforms
    for platform in ["switch", "sensor"]:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload AC Infinity config entry."""
    address = entry.data["address"]
    data = hass.data[DOMAIN].pop(address, None)

    if data:
        controller: ACInfinityController = data["controller"]
        await controller.disconnect()

    unload_ok = all(
        await hass.config_entries.async_forward_entry_unload(entry, platform)
        for platform in ["switch", "sensor"]
    )

    return unload_ok
