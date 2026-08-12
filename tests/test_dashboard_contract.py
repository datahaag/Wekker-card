"""Static contracts for the combined integration and retro card."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components" / "wekker_card"
ALARM = (COMPONENT / "alarm.py").read_text(encoding="utf-8")
INIT = (COMPONENT / "__init__.py").read_text(encoding="utf-8")
CARD = (COMPONENT / "frontend" / "wekker-card.js").read_text(encoding="utf-8")

def test_one_hacs_integration() -> None:
    assert (COMPONENT / "manifest.json").is_file()
    assert (COMPONENT / "config_flow.py").is_file()
    assert "async_register_static_paths" in INIT
    assert "add_extra_js_url" in INIT
    assert "/wekker-card" in INIT

def test_event_driven_controller() -> None:
    assert "async_track_point_in_time" in ALARM
    assert "time_pattern" not in ALARM
    assert "async_track_time_interval" not in ALARM
    assert "async_schedule_next" in ALARM
    assert "async_snooze" in ALARM
    assert "async_stop" in ALARM

def test_sonos_and_light_discovery() -> None:
    assert 'entry.platform == "sonos"' in ALARM
    assert 'state.attributes.get("items")' in ALARM
    assert '("light", "LAMP")' in ALARM
    assert '("switch", "SCHAKELAAR")' in ALARM
    assert "favorite_item_id" in ALARM

def test_card_uses_integration_entities() -> None:
    required = ["switch.wekker_card_enabled", "sensor.wekker_card_status", "sensor.wekker_card_snooze_until", "select.wekker_card_speaker", "select.wekker_card_favorite", "select.wekker_card_light", "button.wekker_card_snooze", "button.wekker_card_stop", "button.wekker_card_refresh"]
    for entity_id in required:
        assert entity_id in CARD
    assert 'customElements.define("wekker-card"' in CARD
    assert 'data-tab="clock"' in CARD and 'data-tab="settings"' in CARD

if __name__ == "__main__":
    tests = [value for name, value in globals().copy().items() if name.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS: {test.__name__}")
    print(f"OK: {len(tests)} integration contract tests")
