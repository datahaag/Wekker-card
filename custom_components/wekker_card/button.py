"""Action buttons for Wekker-card."""
from homeassistant.components.button import ButtonEntity
from .const import DOMAIN
from .entity import WekkerEntity

async def async_setup_entry(hass, entry, async_add_entities) -> None:
    controller = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        AlarmButton(controller, "snooze", "Snooze", "mdi:sleep", "async_snooze"),
        AlarmButton(controller, "stop", "Stop wekcyclus", "mdi:stop-circle", "async_stop"),
        AlarmButton(controller, "refresh", "Keuzelijsten verversen", "mdi:refresh", "async_refresh_lists"),
    ])

class AlarmButton(WekkerEntity, ButtonEntity):
    def __init__(self, controller, key, name, icon, method) -> None:
        super().__init__(controller, key, name, icon)
        self.method = method
    async def async_press(self) -> None:
        await getattr(self.controller, self.method)()
