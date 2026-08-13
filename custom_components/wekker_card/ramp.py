"""Dependency-free ramp calculations for Wekker-card."""

from __future__ import annotations

from math import ceil


def calculated_step_interval(
    ramp_minutes: float, start_volume: float, normal_volume: float
) -> float:
    """Calculate a stable Sonos update interval between 2 and 30 seconds."""
    duration_seconds = max(1.0, float(ramp_minutes) * 60.0)
    volume_steps = max(1, ceil(abs(float(normal_volume) - float(start_volume))))
    return min(30.0, max(2.0, duration_seconds / volume_steps))
