"""Static contract checks for the reusable retro card and Sonos selector."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = (ROOT / "packages" / "wekker_card.yaml").read_text(encoding="utf-8")
DASHBOARD = (ROOT / "dashboard" / "wekker-card.yaml").read_text(encoding="utf-8")
CARD = (ROOT / "custom_cards" / "wekker-card" / "wekker-card.js").read_text(encoding="utf-8")
INSTALLER = (ROOT / "install.sh").read_text(encoding="utf-8")


def test_reusable_custom_card() -> None:
    assert "type: custom:wekker-card" in DASHBOARD
    assert 'customElements.define("wekker-card"' in CARD
    assert 'customElements.define("sonos-smart-alarm-card"' not in CARD
    assert 'data-tab="clock"' in CARD
    assert 'data-tab="settings"' in CARD
    assert 'data-action="toggle-alarm"' in CARD


def test_prominent_times() -> None:
    assert "_updateLocalClock()" in CARD
    assert "_nextAlarmLabel()" in CARD
    assert "sensor.sonos_wekker_huidige_tijd" not in CARD
    assert "sensor.sonos_wekker_volgende_wektijd" not in CARD
    assert 'class="schedule-times"' in CARD
    assert "MA–VR" in CARD
    assert "ZA–ZO" in CARD


def test_sonos_selector_contract() -> None:
    assert "integration_entities('sonos')" in PACKAGE
    assert "entity.startswith('media_player.')" in PACKAGE
    assert "input_select.sonos_alarm_speaker_select" in PACKAGE
    assert "input_select.sonos_alarm_speaker_select" in CARD
    assert "trigger.to_state.state.split(' — ')[-1]" in PACKAGE


def test_card_is_dependency_free() -> None:
    assert "import " not in CARD
    assert "require(" not in CARD


def test_optional_light_alarm_contract() -> None:
    assert "input_boolean.sonos_alarm_light_enabled" in PACKAGE
    assert "input_boolean.sonos_alarm_light_initialized" in PACKAGE
    assert "input_select.sonos_alarm_light_select" in PACKAGE
    assert "input_number.sonos_alarm_light_brightness" in PACKAGE
    assert "script.sonos_alarm_set_light" in PACKAGE
    assert "light.turn_on" in PACKAGE
    assert "switch.turn_on" in PACKAGE
    assert "homeassistant.turn_off" in PACKAGE
    assert "states.switch" in PACKAGE
    assert "LAMP · " in PACKAGE
    assert "SCHAKELAAR · " in PACKAGE
    assert 'this._select(c.light_select_entity, "Lamp of schakelaar")' in CARD
    assert 'lightEntity.startsWith("switch.")' in CARD
    assert "sonos_smart_alarm_initialize_light" in PACKAGE
    assert 'data-action="toggle-light"' in CARD
    assert "_attribute(lightEntity, \"brightness\", null)" in CARD
    assert '["light", "switch"]' in CARD


def test_official_sonos_favorites_contract() -> None:
    assert "input_select.sonos_alarm_favorite_select" in PACKAGE
    assert "sonos_smart_alarm_discover_favorites" in PACKAGE
    assert "state_attr(entity, 'items')" in PACKAGE
    assert "favorite_item_id" in PACKAGE
    assert "Handmatige URI / eigen stream" in PACKAGE
    assert "input_select.sonos_alarm_favorite_select" in CARD
    assert 'class="source-line"' in CARD


def test_installer_deploys_card_globally() -> None:
    assert 'PACKAGE_TARGET="$CONFIG_DIR/packages/wekker_card.yaml"' in INSTALLER
    assert 'INVALID_PACKAGE_TARGET="$CONFIG_DIR/packages/wekker-card.yaml"' in INSTALLER
    assert 'DISABLED_PACKAGE_TARGET="$CONFIG_DIR/packages/wekker_card.yaml.disabled"' in INSTALLER
    assert 'INVALID_PACKAGE_SOURCE="$SCRIPT_DIR/packages/wekker-card.yaml"' in INSTALLER
    assert 'LEGACY_PACKAGE_TARGET="$CONFIG_DIR/packages/sonos_smart_alarm.yaml"' in INSTALLER
    assert 'DASHBOARD_TARGET="$CONFIG_DIR/dashboards/wekker-card.yaml"' in INSTALLER
    assert 'LEGACY_DASHBOARD_TARGET="$CONFIG_DIR/dashboards/sonos-smart-alarm.yaml"' in INSTALLER
    assert 'CARD_TARGET="$CONFIG_DIR/www/community/wekker-card/wekker-card.js"' in INSTALLER
    assert "/local/community/wekker-card/wekker-card.js?v=1.10.0" in INSTALLER
    assert "resource_mode:" in INSTALLER
    assert "registreert zichzelf via de officiële Lovelace-API" in INSTALLER
    assert 'cp "$CARD_SOURCE" "$CARD_TARGET"' in INSTALLER
    assert 'rm -f "$LEGACY_CARD_ROOT"' in INSTALLER
    assert 'rm -f "$LEGACY_CARD_FOLDER"' in INSTALLER
    assert 'rm -f "$LEGACY_CARD_COMMUNITY_UPPER"' in INSTALLER
    assert 'rm -f "$LEGACY_PACKAGE_TARGET"' in INSTALLER
    assert 'rm -f "$INVALID_PACKAGE_TARGET"' in INSTALLER
    assert 'rm -f "$DISABLED_PACKAGE_TARGET"' in INSTALLER
    assert 'rm -f "$INVALID_PACKAGE_SOURCE"' in INSTALLER
    assert "Oude Wekker-cardmodule- en resourceregels uit configuration.yaml verwijderd" in INSTALLER
    assert "sonos-smart-alarm-card\\.js" in INSTALLER
    assert "Wekker-card\\/wekker-card\\.js" in INSTALLER
    assert 'grep -Fq \'customElements.define("wekker-card"\'' in INSTALLER


def test_controller_is_event_driven() -> None:
    assert "trigger: time_pattern" not in PACKAGE
    assert "input_datetime.sonos_alarm_start" in PACKAGE
    assert "at: input_datetime.sonos_alarm_target" in PACKAGE
    assert "at: input_datetime.sonos_alarm_snooze_until" in PACKAGE
    assert "event_type: wekker_card_refresh_lists" in PACKAGE
    assert "sonos_alarm_refresh_lists" in PACKAGE
    assert 'data-action="refresh-lists"' in CARD
    assert "mode: single" in PACKAGE
    assert "max_exceeded: silent" in PACKAGE
    assert "Geen Sonos-speler geselecteerd" in PACKAGE
    assert "Geen lamp of schakelaar geselecteerd" in PACKAGE
    assert "desired_options" in PACKAGE


if __name__ == "__main__":
    tests = [value for name, value in globals().copy().items() if name.startswith("test_")]
    for test in tests:
        test()
    print(f"OK: {len(tests)} dashboard contract tests")
