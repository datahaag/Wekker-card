"""Behavior tests for the automatically calculated ramp interval."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "custom_components" / "wekker_card" / "ramp.py"
SPEC = spec_from_file_location("wekker_card_ramp", MODULE_PATH)
assert SPEC and SPEC.loader
RAMP = module_from_spec(SPEC)
SPEC.loader.exec_module(RAMP)


def test_default_settings_use_about_one_percent_per_step() -> None:
    assert RAMP.calculated_step_interval(15, 2, 30) == 30


def test_short_ramp_updates_more_frequently() -> None:
    assert RAMP.calculated_step_interval(1, 0, 30) == 2


def test_interval_is_always_safely_bounded() -> None:
    assert RAMP.calculated_step_interval(60, 2, 3) == 30
    assert RAMP.calculated_step_interval(0, 0, 100) == 2


if __name__ == "__main__":
    tests = [value for name, value in globals().copy().items() if name.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS: {test.__name__}")
    print(f"OK: {len(tests)} automatic interval tests")
