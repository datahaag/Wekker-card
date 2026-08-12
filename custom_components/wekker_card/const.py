"""Constants for Wekker-card."""

from __future__ import annotations

from datetime import time
from typing import Final

from homeassistant.const import Platform

DOMAIN: Final = "wekker_card"
NAME: Final = "Wekker-card"
VERSION: Final = "2.0.0"

PLATFORMS: Final = (
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.TEXT,
    Platform.TIME,
)

FRONTEND_URL: Final = f"/wekker-card/wekker-card.js?v={VERSION}"

DEFAULTS: Final = {
    "enabled": False,
    "light_enabled": False,
    "weekday_time": time(7, 0),
    "weekend_time": time(9, 0),
    "start_volume": 2.0,
    "normal_volume": 30.0,
    "ramp_minutes": 15.0,
    "step_interval": 30.0,
    "snooze_minutes": 9.0,
    "light_brightness": 70.0,
    "speaker_entity": "",
    "speaker_option": "Geen Sonos-speler geselecteerd",
    "light_entity": "",
    "light_option": "Geen lamp of schakelaar geselecteerd",
    "favorite_option": "Handmatige URI / eigen stream",
    "media_uri": "",
    "media_type": "music",
    "status": "idle",
    "target": None,
    "start": None,
    "snooze_until": None,
}

STATUS_OPTIONS: Final = ("idle", "ramping", "ringing", "snoozed")
MEDIA_TYPE_OPTIONS: Final = ("music", "playlist", "favorite_item_id")

SPEAKER_NONE: Final = "Geen Sonos-speler geselecteerd"
LIGHT_NONE: Final = "Geen lamp of schakelaar geselecteerd"
FAVORITE_MANUAL: Final = "Handmatige URI / eigen stream"
SEPARATOR: Final = " — "

ENTITY_IDS: Final = {
    "enabled": "switch.wekker_card_enabled",
    "light_enabled": "switch.wekker_card_light_enabled",
    "weekday_time": "time.wekker_card_weekday",
    "weekend_time": "time.wekker_card_weekend",
    "start_volume": "number.wekker_card_start_volume",
    "normal_volume": "number.wekker_card_normal_volume",
    "ramp_minutes": "number.wekker_card_ramp_minutes",
    "step_interval": "number.wekker_card_step_interval",
    "snooze_minutes": "number.wekker_card_snooze_minutes",
    "light_brightness": "number.wekker_card_light_brightness",
    "speaker_option": "select.wekker_card_speaker",
    "light_option": "select.wekker_card_light",
    "favorite_option": "select.wekker_card_favorite",
    "media_type": "select.wekker_card_media_type",
    "media_uri": "text.wekker_card_media_uri",
    "status": "sensor.wekker_card_status",
    "target": "sensor.wekker_card_next_alarm",
    "snooze_until": "sensor.wekker_card_snooze_until",
    "snooze": "button.wekker_card_snooze",
    "stop": "button.wekker_card_stop",
    "refresh": "button.wekker_card_refresh",
}
