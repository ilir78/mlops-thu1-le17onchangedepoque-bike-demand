def normalize_team_slug(team_name: str) -> str:
    words = team_name.split()
    if not words:
        raise ValueError(
            "Team name must contain at least one non-whitespace character."
        )
    return "-".join(words).lower()
