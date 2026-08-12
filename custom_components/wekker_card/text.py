"""Text entity for a manual media URI."""
from homeassistant.components.text import TextEntity, TextMode
from .const import DOMAIN
from .entity import WekkerEntity

async def async_setup_entry(hass, entry, async_add_entities) -> None:
    async_add_entities([MediaUriText(hass.data[DOMAIN][entry.entry_id])])

class MediaUriText(WekkerEntity, TextEntity):
    _attr_native_min = 0
    _attr_native_max = 255
    _attr_mode = TextMode.TEXT
    def __init__(self, controller) -> None:
        super().__init__(controller, "media_uri", "Eigen stream- of muziek-URI", "mdi:music")
    @property
    def native_value(self) -> str:
        return self.controller.data["media_uri"]
    async def async_set_value(self, value: str) -> None:
        await self.controller.async_set_media_uri(value)
