"""AC Infinity Coordinator."""
from __future__ import annotations

import asyncio
import contextlib
import logging

import async_timeout
from bleak.backends.device import BLEDevice

from ac_infinity_ble import ACInfinityController

from homeassistant.components import bluetooth
from homeassistant.components.bluetooth.active_update_coordinator import (
    ActiveBluetoothDataUpdateCoordinator,
)
from homeassistant.core import CoreState, HomeAssistant, callback

DEVICE_STARTUP_TIMEOUT = 30


class ACInfinityDataUpdateCoordinator(
    ActiveBluetoothDataUpdateCoordinator[None]
):
    def __init__(
        self,
        hass: HomeAssistant,
        logger: logging.Logger,
        ble_device: BLEDevice,
        controller: ACInfinityController,
    ) -> None:
        super().__init__(
            hass=hass,
            logger=logger,
            address=ble_device.address,
            needs_poll_method=self._needs_poll,
            poll_method=self._async_update,
            mode=bluetooth.BluetoothScanningMode.ACTIVE,
            connectable=True,
        )

        self.ble_device = ble_device
        self.controller = controller
        self._ready_event = asyncio.Event()
        self._was_unavailable = True

    @callback
    def _needs_poll(self, service_info, seconds_since_last_poll):
        return (
            self.hass.state == CoreState.running
            and (seconds_since_last_poll is None or seconds_since_last_poll > 30)
        )

    async def _async_update(self, service_info) -> None:
        await self.controller.update()

    async def async_wait_ready(self) -> bool:
        with contextlib.suppress(asyncio.TimeoutError):
            async with async_timeout.timeout(DEVICE_STARTUP_TIMEOUT):
                await self._ready_event.wait()
                return True
        return False
