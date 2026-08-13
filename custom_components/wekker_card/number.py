"""Numeric settings for Wekker-card."""
from homeassistant.components.number import NumberEntity, NumberMode
from .const import DOMAIN
from .entity import WekkerEntity

DESCRIPTIONS = (
    ("start_volume", "Startvolume", "mdi:volume-low", 1, 100, "%"),
    ("normal_volume", "Normaal wekvolume", "mdi:volume-high", 1, 100, "%"),
    ("ramp_minutes", "Opbouwtijd", "mdi:chart-line", 1, 60, "min"),
    ("snooze_minutes", "Snoozeduur", "mdi:sleep", 1, 60, "min"),
    ("light_brightness", "Doelhelderheid lichtwekker", "mdi:brightness-6", 1, 100, "%"),
)

async def async_setup_entry(hass, entry, async_add_entities) -> None:
    controller = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AlarmNumber(controller, *description) for description in DESCRIPTIONS])

class AlarmNumber(WekkerEntity, NumberEntity):
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER
    def __init__(self, controller, key, name, icon, minimum, maximum, unit) -> None:
        super().__init__(controller, key, name, icon)
        self._attr_native_min_value = minimum
        self._attr_native_max_value = maximum
        self._attr_native_unit_of_measurement = unit
    @property
    def native_value(self) -> float:
        return float(self.controller.data[self.key])
    async def async_set_native_value(self, value: float) -> None:
        await self.controller.async_set_value(self.key, float(value))
