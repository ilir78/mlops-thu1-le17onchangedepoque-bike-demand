import pytest


@pytest.mark.infra
def test_preflight_package_is_importable() -> None:
    import bike_demand

    assert bike_demand.__file__ is not None
