"""Shared entity support for Wekker-card."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, ENTITY_IDS, NAME, VERSION


class WekkerEntity(Entity):
    """Base class for entities backed by the alarm controller."""

    _attr_should_poll = False

    def __init__(self, controller, key: str, name: str, icon: str | None = None) -> None:
        self.controller = controller
        self.key = key
        self._attr_name = name
        self._attr_unique_id = f"{controller.entry.entry_id}_{key}"
        self._attr_icon = icon
        self.entity_id = ENTITY_IDS[key]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, controller.entry.entry_id)},
            name=NAME,
            manufacturer="datahaag",
            model="Sonos Smart Alarm",
            sw_version=VERSION,
        )

    async def async_added_to_hass(self) -> None:
        """Subscribe to controller updates."""
        self.async_on_remove(self.controller.add_listener(self.async_write_ha_state))
