"""Event-driven Sonos and light alarm controller."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from datetime import datetime, timedelta, time
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import async_call_later, async_track_point_in_time
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    DEFAULTS,
    DOMAIN,
    FAVORITE_MANUAL,
    LIGHT_NONE,
    MEDIA_TYPE_OPTIONS,
    SEPARATOR,
    SPEAKER_NONE,
    STATUS_OPTIONS,
)
from .media import stop_targets
from .ramp import calculated_step_interval

_LOGGER = logging.getLogger(__name__)
_STORE_VERSION = 1
_STORE_KEY = f"{DOMAIN}.settings"


class AlarmController:
    """Own settings, exact timers and the active alarm task."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.data: dict[str, Any] = dict(DEFAULTS)
        self.speaker_options = [SPEAKER_NONE]
        self.light_options = [LIGHT_NONE]
        self.favorite_options = [FAVORITE_MANUAL]
        self._listeners: set[Callable[[], None]] = set()
        self._store: Store[dict[str, Any]] = Store(hass, _STORE_VERSION, _STORE_KEY)
        self._timer_cancels: list[Callable[[], None]] = []
        self._refresh_cancel: Callable[[], None] | None = None
        self._ramp_task: asyncio.Task | None = None

    async def async_initialize(self) -> None:
        """Load settings, import legacy helpers and restore exact timers."""
        loaded = await self._store.async_load()
        if loaded:
            self._load_serialized(loaded)
        else:
            self._import_legacy_states()
            await self._store.async_save(self._serialize())

        await self.async_refresh_lists()
        self._refresh_cancel = async_call_later(
            self.hass, 15, lambda _now: self.hass.async_create_task(self.async_refresh_lists())
        )

        legacy_enabled = self.hass.states.get("input_boolean.sonos_alarm_enabled")
        if legacy_enabled is not None and legacy_enabled.state == "on":
            await self._call("input_boolean", "turn_off", "input_boolean.sonos_alarm_enabled")

        now = dt_util.now()
        snooze_until = self.data.get("snooze_until")
        if self.data["enabled"] and self.data["status"] == "snoozed" and snooze_until and snooze_until > now:
            self._schedule_snooze_end(snooze_until)
        elif self.data["enabled"] and self.data["status"] == "ramping" and self.data.get("target") and self.data["target"] > now:
            self._schedule_target_callback(self.data["target"])
            await self.async_start_ramp()
        elif self.data["enabled"] and self.data["status"] == "ringing":
            await self.async_ring()
        elif self.data["enabled"]:
            await self.async_schedule_next()
        else:
            self.data["status"] = "idle"
            self.data["target"] = None
            self.data["start"] = None
        self._notify()

    async def async_shutdown(self) -> None:
        """Stop callbacks without operating selected devices."""
        self._cancel_timers()
        if self._refresh_cancel:
            self._refresh_cancel()
            self._refresh_cancel = None
        self._cancel_ramp()
        await self._store.async_save(self._serialize())

    @callback
    def add_listener(self, listener: Callable[[], None]) -> Callable[[], None]:
        """Subscribe an entity to state changes."""
        self._listeners.add(listener)

        @callback
        def remove_listener() -> None:
            self._listeners.discard(listener)

        return remove_listener

    @callback
    def _notify(self) -> None:
        for listener in tuple(self._listeners):
            listener()

    @callback
    def _queue_save(self) -> None:
        self._store.async_delay_save(self._serialize, 1)

    def _serialize(self) -> dict[str, Any]:
        result = dict(self.data)
        for key in ("weekday_time", "weekend_time"):
            value = result.get(key)
            result[key] = value.isoformat() if isinstance(value, time) else value
        for key in ("target", "start", "snooze_until"):
            value = result.get(key)
            result[key] = value.isoformat() if isinstance(value, datetime) else None
        return result

    def _load_serialized(self, loaded: dict[str, Any]) -> None:
        self.data.update({key: value for key, value in loaded.items() if key in self.data})
        for key in ("weekday_time", "weekend_time"):
            value = self.data.get(key)
            if isinstance(value, str):
                try:
                    self.data[key] = time.fromisoformat(value)
                except ValueError:
                    self.data[key] = DEFAULTS[key]
        for key in ("target", "start", "snooze_until"):
            value = self.data.get(key)
            if isinstance(value, str):
                try:
                    parsed = datetime.fromisoformat(value)
                    self.data[key] = dt_util.as_local(parsed) if parsed.tzinfo else parsed.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)
                except ValueError:
                    self.data[key] = None
        if self.data.get("status") not in STATUS_OPTIONS:
            self.data["status"] = "idle"
        if self.data.get("media_type") not in MEDIA_TYPE_OPTIONS:
            self.data["media_type"] = "music"

    def _legacy_state(self, entity_id: str, default: Any = None) -> Any:
        state = self.hass.states.get(entity_id)
        if state is None or state.state in ("unknown", "unavailable", ""):
            return default
        return state.state

    def _import_legacy_states(self) -> None:
        """Import settings once from the old YAML package without deleting it."""
        legacy_weekday = self._legacy_state("input_datetime.sonos_alarm_weekday_time")
        legacy_weekend = self._legacy_state("input_datetime.sonos_alarm_weekend_time")
        for key, raw in (("weekday_time", legacy_weekday), ("weekend_time", legacy_weekend)):
            if raw:
                try:
                    self.data[key] = time.fromisoformat(raw)
                except ValueError:
                    pass

        mappings = {
            "start_volume": "input_number.sonos_alarm_start_volume",
            "normal_volume": "input_number.sonos_alarm_normal_volume",
            "ramp_minutes": "input_number.sonos_alarm_ramp_minutes",
            "snooze_minutes": "input_number.sonos_alarm_snooze_minutes",
            "light_brightness": "input_number.sonos_alarm_light_brightness",
        }
        for key, entity_id in mappings.items():
            raw = self._legacy_state(entity_id)
            if raw is not None:
                try:
                    self.data[key] = float(raw)
                except ValueError:
                    pass

        self.data["enabled"] = self._legacy_state("input_boolean.sonos_alarm_enabled", "off") == "on"
        self.data["light_enabled"] = self._legacy_state("input_boolean.sonos_alarm_light_enabled", "off") == "on"
        self.data["speaker_entity"] = self._legacy_state("input_text.sonos_alarm_speaker", "")
        self.data["light_entity"] = self._legacy_state("input_text.sonos_alarm_light", "")
        self.data["media_uri"] = self._legacy_state("input_text.sonos_alarm_media_uri", "")
        media_type = self._legacy_state("input_select.sonos_alarm_media_type", "music")
        self.data["media_type"] = media_type if media_type in MEDIA_TYPE_OPTIONS else "music"

    async def async_set_enabled(self, enabled: bool) -> None:
        self.data["enabled"] = enabled
        if enabled:
            self.data["status"] = "idle"
            await self.async_schedule_next()
        else:
            await self.async_stop(schedule_next=False)
        self._changed()

    async def async_set_light_enabled(self, enabled: bool) -> None:
        self.data["light_enabled"] = enabled
        if not enabled:
            await self._set_light(0)
        elif self.data["status"] == "ringing":
            await self._set_light(float(self.data["light_brightness"]))
        elif self.data["status"] == "ramping":
            await self.async_start_ramp()
        self._changed()

    async def async_set_value(self, key: str, value: Any) -> None:
        old_light = self.data.get("light_entity")
        self.data[key] = value

        if key == "speaker_option":
            self.data["speaker_entity"] = self._entity_from_option(value, "media_player")
        elif key == "light_option":
            self.data["light_entity"] = self._entity_from_option(value, ("light", "switch"))
            if old_light and old_light != self.data["light_entity"] and self.data["status"] in ("ramping", "ringing"):
                await self._turn_off(old_light)
        elif key == "favorite_option" and value != FAVORITE_MANUAL:
            self.data["media_uri"] = value.rsplit(SEPARATOR, 1)[-1]
            self.data["media_type"] = "favorite_item_id"

        if key in ("weekday_time", "weekend_time", "ramp_minutes") and self.data["enabled"]:
            await self.async_schedule_next()
        elif key in ("start_volume", "normal_volume", "light_brightness", "light_option") and self.data["status"] == "ramping":
            await self.async_start_ramp()
        self._changed()

    async def async_set_media_uri(self, value: str) -> None:
        self.data["media_uri"] = value.strip()
        self.data["media_type"] = "music"
        self.data["favorite_option"] = FAVORITE_MANUAL
        self._changed()

    @callback
    def _changed(self) -> None:
        self._queue_save()
        self._notify()

    async def async_schedule_next(self) -> None:
        """Calculate and schedule the next target and ramp start exactly once."""
        self._cancel_timers()
        self._cancel_ramp()
        if not self.data["enabled"]:
            return

        now = dt_util.now()
        target = self._target_for_date(now, now.date())
        if target <= now:
            tomorrow = (now + timedelta(days=1)).date()
            target = self._target_for_date(now, tomorrow)
        start = target - timedelta(minutes=float(self.data["ramp_minutes"]))
        self.data["target"] = target
        self.data["start"] = start
        self.data["snooze_until"] = None
        self.data["status"] = "idle"

        async def start_alarm(_now) -> None:
            await self.async_start_ramp()

        if start > now:
            self._timer_cancels.append(async_track_point_in_time(self.hass, start_alarm, start))
        elif target > now:
            self.hass.async_create_task(self.async_start_ramp())
        self._schedule_target_callback(target)
        self._changed()

    def _schedule_target_callback(self, target: datetime) -> None:
        async def reach_target(_now) -> None:
            if self.data["status"] != "snoozed":
                await self.async_ring()

        self._timer_cancels.append(async_track_point_in_time(self.hass, reach_target, target))

    def _target_for_date(self, reference: datetime, date_value) -> datetime:
        alarm_time = self.data["weekday_time"] if date_value.weekday() < 5 else self.data["weekend_time"]
        return datetime.combine(date_value, alarm_time, tzinfo=reference.tzinfo)

    async def async_start_ramp(self) -> None:
        """Start or recalculate the active volume and brightness ramp."""
        self._cancel_ramp()
        target = self.data.get("target")
        start = self.data.get("start")
        if not self.data["enabled"] or not target or not start or dt_util.now() >= target:
            if self.data["enabled"]:
                await self.async_ring()
            return
        if not self._media_is_valid():
            _LOGGER.warning("Wekker-card kan niet starten: kies een Sonos-speler en wekbron")
            return

        self.data["status"] = "ramping"
        self._changed()
        self._ramp_task = self.hass.async_create_task(self._run_ramp())

    async def _run_ramp(self) -> None:
        try:
            await self._play_media(self._current_volume_fraction())
            while self.data["enabled"] and self.data["status"] == "ramping":
                now = dt_util.now()
                target = self.data.get("target")
                if not target or now >= target:
                    break
                fraction = self._ramp_fraction(now)
                desired_volume = self._volume_for_fraction(fraction)
                await self._set_volume(desired_volume)
                await self._set_light(float(self.data["light_brightness"]) * fraction)
                remaining = max(0.1, (target - now).total_seconds())
                interval = calculated_step_interval(
                    self.data["ramp_minutes"],
                    self.data["start_volume"],
                    self.data["normal_volume"],
                )
                await asyncio.sleep(min(interval, remaining))
            if self.data["enabled"] and self.data["status"] == "ramping":
                await self.async_ring()
        except asyncio.CancelledError:
            raise
        except Exception:  # Home Assistant service failures must not kill future scheduling.
            _LOGGER.exception("Onverwachte fout tijdens de Wekker-card-opbouw")

    async def async_ring(self) -> None:
        """Reach the configured target level and keep the selected media playing."""
        if not self.data["enabled"] or not self._media_is_valid():
            return
        current = self.hass.states.get(self.data["speaker_entity"])
        volume = float(self.data["normal_volume"]) / 100
        if current is None or current.state not in ("playing", "buffering"):
            await self._play_media(volume)
        else:
            await self._set_volume(volume)
        await self._set_light(float(self.data["light_brightness"]))
        self.data["status"] = "ringing"
        self.data["snooze_until"] = None
        self._changed()

    async def async_snooze(self) -> None:
        """Pause an active alarm and schedule one exact snooze callback."""
        if self.data["status"] not in ("ramping", "ringing"):
            return
        self._cancel_ramp()
        await self._stop_media()
        await self._set_light(0)
        snooze_until = dt_util.now() + timedelta(minutes=float(self.data["snooze_minutes"]))
        self.data["status"] = "snoozed"
        self.data["snooze_until"] = snooze_until
        self._schedule_snooze_end(snooze_until)
        self._changed()

    async def async_context_button(self) -> None:
        """Snooze an active cycle or stop while currently snoozed."""
        if self.data["status"] in ("ramping", "ringing"):
            await self.async_snooze()
        elif self.data["status"] == "snoozed":
            await self.async_stop()

    def _schedule_snooze_end(self, snooze_until: datetime) -> None:
        async def end_snooze(_now) -> None:
            if self.data["enabled"] and self.data["status"] == "snoozed":
                await self.async_ring()

        self._timer_cancels.append(async_track_point_in_time(self.hass, end_snooze, snooze_until))

    async def async_stop(self, schedule_next: bool = True) -> None:
        """Stop the current cycle while optionally keeping the weekly schedule enabled."""
        self._cancel_ramp()
        self._cancel_timers()
        await self._stop_media()
        await self._set_light(0)
        self.data["status"] = "idle"
        self.data["snooze_until"] = None
        self._changed()
        if schedule_next and self.data["enabled"]:
            await self.async_schedule_next()

    async def async_refresh_lists(self) -> None:
        """Discover Sonos players, all lights/switches and Sonos favorites on demand."""
        registry = er.async_get(self.hass)
        speakers: list[str] = []
        favorites: list[str] = []
        for state in self.hass.states.async_all("media_player"):
            entry = registry.async_get(state.entity_id)
            if entry and entry.platform == "sonos":
                name = state.attributes.get("friendly_name") or state.entity_id
                speakers.append(f"{name}{SEPARATOR}{state.entity_id}")

        for state in self.hass.states.async_all("sensor"):
            entry = registry.async_get(state.entity_id)
            items = state.attributes.get("items")
            if entry and entry.platform == "sonos" and isinstance(items, dict):
                favorites.extend(f"{name}{SEPARATOR}{favorite_id}" for favorite_id, name in items.items())

        lights: list[str] = []
        for domain, prefix in (("light", "LAMP"), ("switch", "SCHAKELAAR")):
            for state in self.hass.states.async_all(domain):
                name = state.attributes.get("friendly_name") or state.entity_id
                lights.append(f"{prefix} · {name}{SEPARATOR}{state.entity_id}")

        self.speaker_options = [SPEAKER_NONE, *sorted(set(speakers), key=str.casefold)]
        self.light_options = [LIGHT_NONE, *sorted(set(lights), key=str.casefold)]
        self.favorite_options = [FAVORITE_MANUAL, *sorted(set(favorites), key=str.casefold)]
        self._restore_selected_options()
        self._notify()

    def _restore_selected_options(self) -> None:
        speaker = self.data.get("speaker_entity", "")
        self.data["speaker_option"] = next(
            (item for item in self.speaker_options if item.endswith(f"{SEPARATOR}{speaker}")), SPEAKER_NONE
        )
        light = self.data.get("light_entity", "")
        self.data["light_option"] = next(
            (item for item in self.light_options if item.endswith(f"{SEPARATOR}{light}")), LIGHT_NONE
        )
        media_uri = self.data.get("media_uri", "")
        self.data["favorite_option"] = next(
            (item for item in self.favorite_options if item.endswith(f"{SEPARATOR}{media_uri}")), FAVORITE_MANUAL
        )

    def _entity_from_option(self, option: str, domains: str | tuple[str, ...]) -> str:
        domains = (domains,) if isinstance(domains, str) else domains
        entity_id = option.rsplit(SEPARATOR, 1)[-1]
        return entity_id if any(entity_id.startswith(f"{domain}.") for domain in domains) else ""

    def _media_is_valid(self) -> bool:
        return self.data["speaker_entity"].startswith("media_player.") and bool(self.data["media_uri"])

    def _ramp_fraction(self, now: datetime | None = None) -> float:
        now = now or dt_util.now()
        start = self.data["start"]
        target = self.data["target"]
        duration = max(1.0, (target - start).total_seconds())
        return min(1.0, max(0.0, (now - start).total_seconds() / duration))

    def _volume_for_fraction(self, fraction: float) -> float:
        start = float(self.data["start_volume"]) / 100
        normal = float(self.data["normal_volume"]) / 100
        return start + (normal - start) * fraction

    def _current_volume_fraction(self) -> float:
        return self._volume_for_fraction(self._ramp_fraction())

    async def _play_media(self, volume: float) -> None:
        await self._set_volume(volume)
        await self._call(
            "media_player",
            "play_media",
            self.data["speaker_entity"],
            media_content_id=self.data["media_uri"],
            media_content_type=self.data["media_type"],
            enqueue="replace",
        )

    async def _set_volume(self, volume: float) -> None:
        speaker = self.data.get("speaker_entity", "")
        if speaker.startswith("media_player."):
            await self._call("media_player", "volume_set", speaker, volume_level=min(1.0, max(0.0, volume)))

    async def _stop_media(self) -> None:
        speaker = self.data.get("speaker_entity", "")
        if not speaker.startswith("media_player."):
            return

        # A Sonos favorite can be a live stream and the selected room can be a
        # member of a Sonos group. Pause first because that reliably silences
        # live streams, then stop as a second supported shutdown command.
        state = self.hass.states.get(speaker)
        group_members = state.attributes.get("group_members", []) if state else []
        targets = stop_targets(speaker, group_members)

        await self._call("media_player", "media_pause", targets)
        await self._call("media_player", "media_stop", targets)
        await self._call("media_player", "volume_set", targets, volume_level=0)

    async def _set_light(self, brightness_pct: float) -> None:
        entity_id = self.data.get("light_entity", "")
        if not entity_id:
            return
        desired = min(100, max(0, brightness_pct)) if self.data["light_enabled"] else 0
        if desired <= 0:
            await self._turn_off(entity_id)
        elif entity_id.startswith("switch."):
            await self._call("switch", "turn_on", entity_id)
        elif entity_id.startswith("light."):
            await self._call("light", "turn_on", entity_id, brightness_pct=round(desired))

    async def _turn_off(self, entity_id: str) -> None:
        if entity_id.startswith(("light.", "switch.")):
            await self._call(entity_id.split(".", 1)[0], "turn_off", entity_id)

    async def _call(
        self, domain: str, service: str, entity_id: str | list[str], **data: Any
    ) -> None:
        if not entity_id or not self.hass.services.has_service(domain, service):
            return
        try:
            await self.hass.services.async_call(
                domain, service, {"entity_id": entity_id, **data}, blocking=True
            )
        except Exception:  # Device availability must not break the scheduler.
            _LOGGER.warning("Actie %s.%s voor %s is mislukt", domain, service, entity_id, exc_info=True)

    @callback
    def _cancel_timers(self) -> None:
        for cancel in self._timer_cancels:
            cancel()
        self._timer_cancels.clear()

    @callback
    def _cancel_ramp(self) -> None:
        task = self._ramp_task
        if task and task is not asyncio.current_task() and not task.done():
            task.cancel()
        self._ramp_task = None
