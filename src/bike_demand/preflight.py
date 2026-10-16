"""Minimal environment preflight for the Bike Demand starter."""


def main() -> None:
    """Report that the installed project package can be imported."""
    import bike_demand

    print(f"bike_demand preflight OK: {bike_demand.__file__}")


if __name__ == "__main__":
    main()
