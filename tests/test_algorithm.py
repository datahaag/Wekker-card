"""Dependency-free checks for the documented ramp algorithm."""

from math import ceil, floor


def volume(start: float, normal: float, duration: int, interval: int, elapsed: int) -> float:
    if elapsed >= duration:
        return normal
    steps = ceil(duration / interval)
    completed = min(steps, max(0, floor(elapsed / interval)))
    return start + (normal - start) * completed / max(1, steps)


def test_exact_target() -> None:
    assert volume(0.02, 0.30, 900, 30, 900) == 0.30


def test_non_divisible_interval_reaches_target() -> None:
    assert volume(0.02, 0.30, 900, 64, 900) == 0.30


def test_before_first_step_is_start() -> None:
    assert volume(0.02, 0.30, 900, 30, 29) == 0.02


def test_bounds() -> None:
    values = [volume(0.02, 0.30, 900, 37, elapsed) for elapsed in range(-5, 906)]
    assert min(values) >= 0.02
    assert max(values) <= 0.30
    assert values == sorted(values)


def test_light_uses_same_ramp_from_zero() -> None:
    assert volume(0, 70, 900, 30, 0) == 0
    assert volume(0, 70, 900, 30, 450) == 35
    assert volume(0, 70, 900, 30, 900) == 70


if __name__ == "__main__":
    tests = [value for name, value in globals().copy().items() if name.startswith("test_")]
    for test in tests:
        test()
    print(f"OK: {len(tests)} algorithm tests")
