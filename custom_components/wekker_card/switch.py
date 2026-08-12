"""Switch entities for Wekker-card."""

from homeassistant.components.switch import SwitchEntity

from .const import DOMAIN
from .entity import WekkerEntity


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    controller = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            AlarmSwitch(controller, "enabled", "Wekker", "mdi:alarm-check"),
            AlarmSwitch(controller, "light_enabled", "Lichtwekker", "mdi:lightbulb-on-outline"),
        ]
    )


class AlarmSwitch(WekkerEntity, SwitchEntity):
    @property
    def is_on(self) -> bool:
        return bool(self.controller.data[self.key])

    async def async_turn_on(self, **kwargs) -> None:
        if self.key == "enabled":
            await self.controller.async_set_enabled(True)
        else:
            await self.controller.async_set_light_enabled(True)

    async def async_turn_off(self, **kwargs) -> None:
        if self.key == "enabled":
            await self.controller.async_set_enabled(False)
        else:
            await self.controller.async_set_light_enabled(False)
