"""Team-name helpers used by the course workflow."""

import re


def normalize_team_slug(name: str) -> str:
    """Convert a team name to a lowercase, hyphen-separated slug.

    Leading and trailing whitespace is removed, and each run of whitespace is
    replaced with one hyphen. Names containing only whitespace are rejected.
    """
    trimmed_name = name.strip()
    if not trimmed_name:
        raise ValueError("team name must not be blank")

    return re.sub(r"\s+", "-", trimmed_name).lower()
