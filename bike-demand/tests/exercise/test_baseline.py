import json
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from bike_demand.preflight import sha256
from bike_demand.split import partition_summary, split_data
from bike_demand.train import (
    compare_mean,
    load_config,
    reload_validation,
    select_features,
    train_baseline,
)
from bike_demand.validate import FEATURES, load_data

pytestmark = pytest.mark.exercise
FIXTURES = Path(__file__).parents[1] / "fixtures"


def test_numeric_csv_text_and_missing_hours_are_valid():
    frame = load_data(FIXTURES / "missing-hours.csv")
    assert len(frame) == 6
    assert frame["hr"].nunique() < 24


@pytest.mark.parametrize(
    ("name", "message"), [("missing-temp.csv", "temp"), ("hum-out-of-range.csv", "hum")]
)
def test_supplied_faults(name, message):
    with pytest.raises(ValueError, match=message):
        load_data(FIXTURES / name)


def test_fault_b_rejects_out_of_range_weather_category(tmp_path):
    control_path = FIXTURES / "missing-hours.csv"
    control = load_data(control_path)
    assert len(control) == 6

    invalid = pd.read_csv(control_path)
    columns_before = list(invalid.columns)
    invalid.loc[0, "weathersit"] = 5
    fault_path = tmp_path / "fault-b-weathersit.csv"
    invalid.to_csv(fault_path, index=False)

    assert list(pd.read_csv(fault_path).columns) == columns_before
    with pytest.raises(ValueError, match="weathersit"):
        load_data(fault_path)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("season", 0),
        ("season", 5),
        ("season", 1.5),
        ("yr", 2),
        ("mnth", 13),
        ("hr", 24),
        ("hr", -1),
        ("holiday", 2),
        ("weekday", 7),
        ("workingday", 2),
        ("weathersit", 0),
        ("temp", -0.01),
        ("atemp", 1.1),
        ("hum", 1.2),
        ("windspeed", float("inf")),
        ("cnt", -1),
        ("registered", 0.5),
        ("casual", -1),
        ("instant", 0),
        ("instant", 0.5),
        ("temp", "not-a-number"),
        ("hum", None),
        ("dteday", "not-a-date"),
        ("dteday", "2013-01-01"),
        ("dteday", "2010-12-31"),
    ],
)
def test_invalid_values_are_rejected(tmp_path, field, value):
    frame = pd.read_csv(FIXTURES / "missing-hours.csv").astype(object)
    frame.loc[0, field] = value
    path = tmp_path / "invalid.csv"
    frame.to_csv(path, index=False)
    before = path.read_bytes()
    with pytest.raises(ValueError, match=field):
        load_data(path)
    assert path.read_bytes() == before


def test_duplicate_identity(tmp_path):
    frame = pd.read_csv(FIXTURES / "missing-hours.csv")
    frame.loc[1, "instant"] = frame.loc[0, "instant"]
    path = tmp_path / "duplicate.csv"
    frame.to_csv(path, index=False)
    with pytest.raises(ValueError, match="instant"):
        load_data(path)


def test_partition_boundaries_order_disjoint_and_complete():
    frame = load_data(FIXTURES / "missing-hours.csv")
    parts = split_data(frame.iloc[::-1])
    assert {key: list(part["instant"]) for key, part in parts.items()} == {
        "train": [1, 2],
        "validation": [3, 4],
        "test": [5, 6],
    }
    ids = [set(part["instant"]) for part in parts.values()]
    assert set.union(*ids) == set(frame["instant"])
    assert all(not a & b for a, b in combinations(ids, 2))
    for part in parts.values():
        assert part.equals(part.sort_values(["dteday", "hr", "instant"]))
    summary = partition_summary(parts)
    assert summary["train"]["first_key"] == "2011-01-01,0,1"
    assert summary["train"]["last_key"] == "2011-12-31,23,2"
    assert summary["validation"]["first_key"] == "2012-01-01,0,3"
    assert summary["validation"]["last_key"] == "2012-06-30,23,4"
    assert summary["test"]["first_key"] == "2012-07-01,0,5"
    assert summary["test"]["last_key"] == "2012-12-31,23,6"


def test_split_rejects_empty_partition():
    frame = load_data(FIXTURES / "missing-hours.csv")
    with pytest.raises(ValueError, match="nonempty"):
        split_data(frame.iloc[:4])


def test_split_rejects_unassigned_row():
    frame = load_data(FIXTURES / "missing-hours.csv")
    frame.loc[0, "dteday"] = pd.Timestamp("2010-12-31")
    with pytest.raises(ValueError, match="complete"):
        split_data(frame)


def test_banned_features_and_order():
    frame = load_data(FIXTURES / "missing-hours.csv")
    predictors = select_features(frame, list(FEATURES))
    assert list(predictors.columns) == list(FEATURES)
    assert not {"cnt", "casual", "registered", "instant", "dteday"} & set(
        predictors.columns
    )
    with pytest.raises(ValueError, match="features"):
        select_features(frame, [*FEATURES, "cnt"])
    with pytest.raises(ValueError, match="features"):
        select_features(frame, list(reversed(FEATURES)))


def test_mean_uses_train_only():
    mean, mae = compare_mean(pd.Series([10, 30]), pd.Series([40, 60]))
    assert mean == 20
    assert mae == 30


def test_saved_model_readback_rerun_and_held_test(tmp_path):
    (tmp_path / "data/raw").mkdir(parents=True)
    data = tmp_path / "data/raw/hour.csv"
    data.write_bytes((FIXTURES / "missing-hours.csv").read_bytes())
    fixture = pd.read_csv(data)
    manifest = {
        "sha256": sha256(data),
        "bytes": data.stat().st_size,
        "header": list(fixture.columns),
        "rows": len(fixture),
    }
    (tmp_path / "data/manifest.json").write_text(json.dumps(manifest))
    config = Path("configs/baseline.yaml").resolve()
    first = train_baseline(tmp_path, config)
    parts = split_data(load_data(data))
    predictions, mae = reload_validation(tmp_path, parts["validation"], list(FEATURES))
    assert np.isfinite(predictions).all()
    assert mae == first["validation_mae"]["random_forest"]
    # Change only held test labels in this synthetic fixture. No raw course data is changed.
    fixture.loc[fixture["dteday"] >= "2012-07-01", "cnt"] = 999999
    fixture.to_csv(data, index=False)
    manifest.update(sha256=sha256(data), bytes=data.stat().st_size)
    (tmp_path / "data/manifest.json").write_text(json.dumps(manifest))
    second = train_baseline(tmp_path, config)
    assert first["validation_mae"] == second["validation_mae"]
    assert first["naive_run_id"] != second["naive_run_id"]
    assert first["model_run_id"] != second["model_run_id"]
    assert first["model_version"] != second["model_version"]
    assert first["readback"]["logged_model_bytes_match"]
    assert second["readback"]["reload_mae_delta"] == 0
    assert (
        len((tmp_path / "reports/metrics-history.jsonl").read_text().splitlines()) == 2
    )
    assert "test_mae" not in json.dumps(second)
    assert second["partitions"]["test"]["rows"] == 2
    assert load_config(config)["features"] == list(FEATURES)
