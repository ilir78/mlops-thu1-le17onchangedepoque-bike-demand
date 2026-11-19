"""Validated HTTP API for the saved bike-demand model with structured logging."""

from __future__ import annotations

import hashlib
import json
import logging
import time
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

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("bike_demand_api")

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "artifacts" / "model.joblib"
METADATA_PATH = ROOT / "artifacts" / "model-metadata.json"


class PredictionRequest(BaseModel):
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


def _load_model() -> tuple[object, str, str]:
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
    return joblib.load(MODEL_PATH), version, digest


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.model, app.state.model_version, app.state.model_sha256 = _load_model()
        app.state.model_error = None
    except Exception as exc:
        app.state.model = None
        app.state.model_version = None
        app.state.model_sha256 = None
        app.state.model_error = str(exc)
    yield


app = FastAPI(title="Bike Demand Prediction API", lifespan=lifespan)


@app.middleware("http")
async def structured_logging_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    status_code = 500
    event = "error"
    try:
        response = await call_next(request)
        status_code = response.status_code
        event = "scored" if status_code == 200 else "rejected"
        return response
    except Exception:
        event = "exception"
        raise
    finally:
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        log_payload = {
            "event": event,
            "path": request.url.path,
            "method": request.method,
            "status": status_code,
            "ms": duration_ms,
            "model": getattr(app.state, "model_version", "unknown"),
        }
        logger.info(json.dumps(log_payload))


@app.exception_handler(RequestValidationError)
async def validation_error_response(request: Request, exc: RequestValidationError):
    detail = [
        {"loc": list(error["loc"]), "msg": error["msg"], "type": error["type"]}
        for error in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": detail})


@app.get("/health")
def health():
    if getattr(app.state, "model", None) is None:
        raise HTTPException(status_code=503, detail="model unavailable")
    return {
        "status": "ok",
        "model_version": app.state.model_version,
        "model_sha256": app.state.model_sha256,
    }


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