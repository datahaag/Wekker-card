"""Time entities for Wekker-card."""

from homeassistant.components.time import TimeEntity

from .const import DOMAIN
from .entity import WekkerEntity


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    controller = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            AlarmTime(controller, "weekday_time", "Wektijd maandag t/m vrijdag"),
            AlarmTime(controller, "weekend_time", "Wektijd zaterdag en zondag"),
        ]
    )


class AlarmTime(WekkerEntity, TimeEntity):
    @property
    def native_value(self):
        return self.controller.data[self.key]

    async def async_set_value(self, value) -> None:
        await self.controller.async_set_value(self.key, value)
