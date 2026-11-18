import hashlib
import json

import joblib
import numpy as np
import pytest
from fastapi.testclient import TestClient
from sklearn.dummy import DummyRegressor

from bike_demand import api

VALID = {
    "season": 1,
    "yr": 0,
    "mnth": 1,
    "hr": 0,
    "holiday": 0,
    "weekday": 6,
    "workingday": 0,
    "weathersit": 1,
    "temp": 0.24,
    "atemp": 0.28,
    "hum": 0.81,
    "windspeed": 0.0,
}


@pytest.fixture
def install_model(tmp_path, monkeypatch):
    model_path = tmp_path / "model.joblib"
    model = DummyRegressor(strategy="constant", constant=42).fit(
        np.zeros((1, 12)), [42]
    )
    joblib.dump(model, model_path)
    version = "test-model-42"
    metadata_path = tmp_path / "model-metadata.json"
    metadata_path.write_text(
        json.dumps(
            {
                "features": list(api.FEATURES),
                "model_version": version,
                "model_sha256": hashlib.sha256(model_path.read_bytes()).hexdigest(),
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(api, "MODEL_PATH", model_path)
    monkeypatch.setattr(api, "METADATA_PATH", metadata_path)
    return model_path, metadata_path


def test_health_and_predict_return_loaded_model_version(install_model):
    with TestClient(api.app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json() == {"status": "ok", "model_version": "test-model-42"}

        response = client.post("/predict", json=VALID)
        assert response.status_code == 200
        assert response.json() == {
            "prediction": 42.0,
            "model_version": "test-model-42",
        }


@pytest.mark.parametrize(
    "change",
    [
        {"season": 5},
        {"hr": -1},
        {"temp": 1.1},
        {"hum": float("nan")},
        {"season": "1"},
        {"cnt": 7},
        {"surprise": 7},
        {"season": None},
    ],
)
def test_invalid_requests_are_rejected_before_inference(install_model, change):
    payload = {**VALID, **change}
    with TestClient(api.app) as client:
        if isinstance(change.get("hum"), float) and np.isnan(change["hum"]):
            body = json.dumps({**VALID, "hum": 0.81}).replace(
                '"hum": 0.81', '"hum": 1e999'
            )
            response = client.post(
                "/predict",
                content=body,
                headers={"Content-Type": "application/json"},
            )
        else:
            response = client.post("/predict", json=payload)
        assert response.status_code == 422


def test_missing_model_reports_503(monkeypatch, tmp_path):
    monkeypatch.setattr(api, "MODEL_PATH", tmp_path / "missing.joblib")
    monkeypatch.setattr(api, "METADATA_PATH", tmp_path / "missing.json")
    with TestClient(api.app) as client:
        assert client.get("/health").status_code == 503
        assert client.post("/predict", json=VALID).status_code == 503


def test_missing_required_field_is_rejected(install_model):
    payload = {key: value for key, value in VALID.items() if key != "hr"}
    with TestClient(api.app) as client:
        assert client.post("/predict", json=payload).status_code == 422


def test_model_checksum_mismatch_reports_503(install_model):
    model_path, _ = install_model
    model_path.write_bytes(model_path.read_bytes() + b"tampered")
    with TestClient(api.app) as client:
        assert client.get("/health").status_code == 503
        assert client.post("/predict", json=VALID).status_code == 503
