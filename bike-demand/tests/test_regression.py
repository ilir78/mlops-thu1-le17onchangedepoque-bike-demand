"""Recompute the committed validation score without touching the held-out test set."""

import json
from pathlib import Path

import pytest

from bike_demand.split import split_data
from bike_demand.train import fit_evaluate, load_config
from bike_demand.validate import load_data

pytestmark = pytest.mark.regression


def test_random_forest_validation_mae_matches_recorded_result() -> None:
    root = Path(__file__).resolve().parents[1]
    recorded = json.loads((root / "reports/metrics.json").read_text(encoding="utf-8"))
    config = load_config(root / "configs/baseline.yaml")
    partitions = split_data(load_data(root / config["data"]))

    # The test partition (July–December 2012) is intentionally never passed here.
    _, _, observed_mae = fit_evaluate(
        partitions["train"], partitions["validation"], config
    )
    expected_mae = recorded["validation_mae"]["random_forest"]

    # Fixed data, split, seed and single-thread model reproduce the recorded float.
    assert observed_mae == expected_mae
