"""Dynamic selection entities for Wekker-card."""
from homeassistant.components.select import SelectEntity
from .const import DOMAIN, MEDIA_TYPE_OPTIONS
from .entity import WekkerEntity

async def async_setup_entry(hass, entry, async_add_entities) -> None:
    controller = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        AlarmSelect(controller, "speaker_option", "Sonos-speler", "mdi:speaker-multiple", "speaker_options"),
        AlarmSelect(controller, "favorite_option", "Sonos-favoriet of radiostation", "mdi:radio", "favorite_options"),
        AlarmSelect(controller, "light_option", "Lamp of schakelaar", "mdi:lightbulb-group", "light_options"),
        AlarmSelect(controller, "media_type", "Mediatype", "mdi:playlist-music", None),
    ])

class AlarmSelect(WekkerEntity, SelectEntity):
    def __init__(self, controller, key, name, icon, options_attribute) -> None:
        super().__init__(controller, key, name, icon)
        self.options_attribute = options_attribute
    @property
    def current_option(self) -> str:
        return self.controller.data[self.key]
    @property
    def options(self) -> list[str]:
        if self.options_attribute:
            return list(getattr(self.controller, self.options_attribute))
        return list(MEDIA_TYPE_OPTIONS)
    async def async_select_option(self, option: str) -> None:
        if option in self.options:
            await self.controller.async_set_value(self.key, option)
