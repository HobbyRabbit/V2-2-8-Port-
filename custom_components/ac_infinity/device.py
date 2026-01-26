from __future__ import annotations
import asyncio
import logging
from typing import List, Optional

from bleak.backends.device import BLEDevice
from bleak import BleakClient, BleakError

_LOGGER = logging.getLogger(__name__)

class ACInfinityController:
    """AC Infinity 69 Pro BLE controller."""

    def __init__(self, ble_device: BLEDevice, advertisement_data=None):
        if not ble_device and not advertisement_data:
            raise ValueError("Must provide either BLE device or advertisement_data")

        self.ble_device = ble_device
        self.address = ble_device.address
        self.advertisement_data = advertisement_data

        # Device state
        self.ports
