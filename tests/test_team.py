import pytest

from bike_demand.team import normalize_team_slug


@pytest.mark.lab1
def test_normalize_team_slug_trims_and_lowercases() -> None:
    assert normalize_team_slug(" Team Blue ") == "team-blue"


@pytest.mark.lab1
def test_normalize_team_slug_collapses_whitespace_runs() -> None:
    assert normalize_team_slug("North\tShore\nBikes") == "north-shore-bikes"


@pytest.mark.lab1
@pytest.mark.parametrize("name", ["", " ", "\t\n"])
def test_normalize_team_slug_rejects_blank_names(name: str) -> None:
    with pytest.raises(ValueError, match="must not be blank"):
        normalize_team_slug(name)
