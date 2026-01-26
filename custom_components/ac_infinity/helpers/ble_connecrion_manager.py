# custom_components/ac_infinity/helpers/ble_connection_manager.py
from __future__ import annotations
import asyncio
import logging
from contextlib import asynccontextmanager
from bleak import BleakClient

_LOGGER = logging.getLogger(__name__)

class BLEConnectionManager:
    """Persistent BleakClient manager for one device."""

    def __init__(self, address: str):
        self.address = address
        self._client: BleakClient | None = None
        self._lock = asyncio.Lock()

    async def _ensure_connected(self) -> BleakClient:
        async with self._lock:
            if self._client and self._client.is_connected:
                return self._client
            if self._client:
                try:
                    await self._client.disconnect()
                except Exception:
                    _LOGGER.debug("disconnect failed during recreate", exc_info=True)
                self._client = None
            client = BleakClient(self.address, timeout=15.0)
            await client.connect()
            self._client = client
            _LOGGER.debug("BleakClient connected to %s", self.address)
            return self._client

    @asynccontextmanager
    async def client(self):
        """Async contextmanager returning a connected BleakClient."""
        client = await self._ensure_connected()
        try:
            yield client
        except Exception:
            _LOGGER.exception("BLE operation failed")
            raise

    async def disconnect(self) -> None:
        async with self._lock:
            if self._client:
                try:
                    await self._client.disconnect()
                except Exception:
                    _LOGGER.debug("disconnect error", exc_info=True)
                self._client = None
