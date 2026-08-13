"""Behavior tests for robust Sonos stop targeting."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "custom_components" / "wekker_card" / "media.py"
SPEC = spec_from_file_location("wekker_card_media", MODULE_PATH)
assert SPEC and SPEC.loader
MEDIA = module_from_spec(SPEC)
SPEC.loader.exec_module(MEDIA)


def test_selected_speaker_is_always_targeted() -> None:
    assert MEDIA.stop_targets("media_player.woonkamer", []) == ["media_player.woonkamer"]


def test_sonos_group_members_are_included_once() -> None:
    assert MEDIA.stop_targets(
        "media_player.woonkamer",
        ["media_player.keuken", "media_player.woonkamer", "media_player.keuken"],
    ) == ["media_player.woonkamer", "media_player.keuken"]


def test_invalid_entities_and_attributes_are_ignored() -> None:
    assert MEDIA.stop_targets("media_player.woonkamer", ["light.keuken", None, 42]) == [
        "media_player.woonkamer"
    ]
    assert MEDIA.stop_targets("media_player.woonkamer", "media_player.keuken") == [
        "media_player.woonkamer"
    ]
    assert MEDIA.stop_targets("light.woonkamer", ["media_player.keuken"]) == []


if __name__ == "__main__":
    tests = [value for name, value in globals().copy().items() if name.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS: {test.__name__}")
    print(f"OK: {len(tests)} stop target tests")
