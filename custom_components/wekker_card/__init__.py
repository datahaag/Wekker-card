"""Wekker-card: one HACS integration for backend and frontend."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.storage import Store

from .alarm import AlarmController
from .const import DOMAIN, FRONTEND_URL, PLATFORMS


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the integration domain."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Wekker-card from the UI config entry."""
    registry = er.async_get(hass)
    legacy_interval = registry.async_get_entity_id(
        "number", DOMAIN, f"{entry.entry_id}_step_interval"
    )
    if legacy_interval:
        registry.async_remove(legacy_interval)

    controller = AlarmController(hass, entry)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = controller

    if not hass.data[DOMAIN].get("frontend_registered"):
        frontend_dir = Path(__file__).parent / "frontend"
        await hass.http.async_register_static_paths(
            [StaticPathConfig("/wekker-card", str(frontend_dir), False)]
        )
        add_extra_js_url(hass, FRONTEND_URL)
        hass.data[DOMAIN]["frontend_registered"] = True

    await controller.async_initialize()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    if not hass.services.has_service(DOMAIN, "refresh_lists"):
        async def refresh_lists(_call) -> None:
            await controller.async_refresh_lists()

        async def snooze(_call) -> None:
            await controller.async_snooze()

        async def stop(_call) -> None:
            await controller.async_stop()

        async def context_button(_call) -> None:
            await controller.async_context_button()

        hass.services.async_register(DOMAIN, "refresh_lists", refresh_lists)
        hass.services.async_register(DOMAIN, "snooze", snooze)
        hass.services.async_register(DOMAIN, "stop", stop)
        hass.services.async_register(DOMAIN, "context_button", context_button)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Wekker-card."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        controller: AlarmController = hass.data[DOMAIN].pop(entry.entry_id)
        await controller.async_shutdown()
        for service in ("refresh_lists", "snooze", "stop", "context_button"):
            hass.services.async_remove(DOMAIN, service)
    return unloaded


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove settings when the integration is deleted."""
    await Store(hass, 1, f"{DOMAIN}.settings").async_remove()
