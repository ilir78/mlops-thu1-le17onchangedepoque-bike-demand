"""Validated HTTP API for the saved bike-demand model."""

from __future__ import annotations

import hashlib
import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from bike_demand.validate import FEATURES

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "artifacts" / "model.joblib"
METADATA_PATH = ROOT / "artifacts" / "model-metadata.json"


class PredictionRequest(BaseModel):
    """Exactly the twelve ordered model predictors; unknown fields are rejected."""

    model_config = ConfigDict(extra="forbid")

    season: Annotated[int, Field(strict=True, ge=1, le=4)]
    yr: Annotated[int, Field(strict=True, ge=0, le=1)]
    mnth: Annotated[int, Field(strict=True, ge=1, le=12)]
    hr: Annotated[int, Field(strict=True, ge=0, le=23)]
    holiday: Annotated[int, Field(strict=True, ge=0, le=1)]
    weekday: Annotated[int, Field(strict=True, ge=0, le=6)]
    workingday: Annotated[int, Field(strict=True, ge=0, le=1)]
    weathersit: Annotated[int, Field(strict=True, ge=1, le=4)]
    temp: Annotated[float, Field(strict=True, ge=0, le=1, allow_inf_nan=False)]
    atemp: Annotated[float, Field(strict=True, ge=0, le=1, allow_inf_nan=False)]
    hum: Annotated[float, Field(strict=True, ge=0, le=1, allow_inf_nan=False)]
    windspeed: Annotated[float, Field(strict=True, ge=0, le=1, allow_inf_nan=False)]


def _load_model() -> tuple[object, str]:
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    if metadata.get("features") != list(FEATURES):
        raise ValueError("model metadata has an unexpected feature order")
    model_bytes = MODEL_PATH.read_bytes()
    digest = hashlib.sha256(model_bytes).hexdigest()
    if metadata.get("model_sha256") != digest:
        raise ValueError("saved model checksum does not match its metadata")
    version = metadata.get("model_version")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("model metadata has no usable model_version")
    return joblib.load(MODEL_PATH), version


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.model, app.state.model_version = _load_model()
        app.state.model_error = None
    except Exception as exc:
        # Keep the API up so health and prediction can report unavailable (503).
        app.state.model = None
        app.state.model_version = None
        app.state.model_error = str(exc)
    yield


app = FastAPI(title="Bike Demand Prediction API", lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_error_response(request: Request, exc: RequestValidationError):
    # Pydantic error inputs can contain NaN/Infinity, which are not JSON values.
    detail = [
        {"loc": list(error["loc"]), "msg": error["msg"], "type": error["type"]}
        for error in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": detail})


@app.get("/health")
def health():
    if getattr(app.state, "model", None) is None:
        raise HTTPException(status_code=503, detail="model unavailable")
    return {"status": "ok", "model_version": app.state.model_version}


@app.post("/predict")
def predict(request: PredictionRequest):
    model = getattr(app.state, "model", None)
    if model is None:
        raise HTTPException(status_code=503, detail="model unavailable")
    values = request.model_dump()
    features = pd.DataFrame([values], columns=FEATURES)
    prediction = float(model.predict(features)[0])
    if not np.isfinite(prediction):
        raise HTTPException(
            status_code=503, detail="model returned an unusable prediction"
        )
    return {
        "prediction": max(0.0, prediction),
        "model_version": app.state.model_version,
    }
