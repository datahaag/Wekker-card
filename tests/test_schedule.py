"""Behavior tests for STOP-aware alarm scheduling."""

from datetime import datetime, time
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "custom_components" / "wekker_card" / "schedule.py"
SPEC = spec_from_file_location("wekker_card_schedule", MODULE_PATH)
SCHEDULE = module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(SCHEDULE)


def test_normal_schedule_uses_today_when_still_upcoming() -> None:
    now = datetime(2026, 8, 13, 6, 30)
    assert SCHEDULE.next_alarm_target(now, time(7), time(9)) == datetime(2026, 8, 13, 7)


def test_stop_during_ramp_skips_current_target() -> None:
    now = datetime(2026, 8, 13, 6, 50)
    stopped_target = datetime(2026, 8, 13, 7)
    assert SCHEDULE.next_alarm_target(now, time(7), time(9), stopped_target) == datetime(2026, 8, 14, 7)


def test_friday_stop_uses_weekend_time() -> None:
    now = datetime(2026, 8, 14, 6, 50)
    stopped_target = datetime(2026, 8, 14, 7)
    assert SCHEDULE.next_alarm_target(now, time(7), time(9), stopped_target) == datetime(2026, 8, 15, 9)


if __name__ == "__main__":
    tests = [value for name, value in globals().copy().items() if name.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS: {test.__name__}")
    print(f"OK: {len(tests)} schedule tests")
