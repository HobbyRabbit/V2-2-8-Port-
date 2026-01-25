from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


PORTS = [1, 2, 3, 4, 5, 6, 7, 8]


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for port in PORTS:
        entities.append(
            ACInfinityPortSwitch(coordinator, port)
        )

    async_add_entities(entities)


class ACInfinityPortSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, port: int):
        super().__init__(coordinator)
        self._port = port
        self._attr_name = f"AC Infinity Port {port}"
        self._attr_unique_id = f"{coordinator.address}_port_{port}"

    @property
    def is_on(self) -> bool | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data["ports"][self._port]["enabled"]

    async def async_turn_on(self, **kwargs):
        await self.coordinator.controller.set_port_enabled(
            self._port, True
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self.coordinator.controller.set_port_enabled(
            self._port, False
        )
        await self.coordinator.async_request_refresh()

