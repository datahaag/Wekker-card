"""Status and exact schedule sensors for Wekker-card."""
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from .const import DOMAIN
from .entity import WekkerEntity

async def async_setup_entry(hass, entry, async_add_entities) -> None:
    controller = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        AlarmStatusSensor(controller),
        AlarmDateSensor(controller, "target", "Volgende wektijd", "mdi:alarm"),
        AlarmDateSensor(controller, "snooze_until", "Snooze tot", "mdi:sleep"),
    ])

class AlarmStatusSensor(WekkerEntity, SensorEntity):
    def __init__(self, controller) -> None:
        super().__init__(controller, "status", "Wekkerstatus", "mdi:alarm")
    @property
    def native_value(self) -> str:
        return self.controller.data["status"]

class AlarmDateSensor(WekkerEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    def __init__(self, controller, key, name, icon) -> None:
        super().__init__(controller, key, name, icon)
    @property
    def native_value(self):
        return self.controller.data[self.key]
