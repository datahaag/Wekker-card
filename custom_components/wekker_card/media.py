"""Small dependency-free media helpers for Wekker-card."""

from __future__ import annotations


def stop_targets(speaker: str, group_members: object) -> list[str]:
    """Return the selected media player and valid, unique group members."""
    if not speaker.startswith("media_player."):
        return []

    targets = [speaker]
    if isinstance(group_members, (list, tuple)):
        targets.extend(
            member
            for member in group_members
            if isinstance(member, str) and member.startswith("media_player.")
        )
    return list(dict.fromkeys(targets))
