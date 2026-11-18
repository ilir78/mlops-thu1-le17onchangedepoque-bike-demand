# Week 2, Lab 4: Prediction API

## Implementation

- Added `src/bike_demand/api.py` with `GET /health` and `POST /predict`.
- Startup loads the existing trusted model and verifies its SHA-256, ordered
  feature list and `model_version` from the artifact metadata. No training runs
  during service startup or inference.
- The request body is a flat object with exactly the twelve training features.
  Pydantic checks integer categories, normalized finite weather values, and
  rejects extra fields and target/leakage columns with HTTP 422.
- A loaded model yields HTTP 200, a finite nonnegative prediction and its
  metadata version. Missing or invalid model artifacts yield HTTP 503 for both
  health and prediction. Invalid input is rejected before prediction.
- `Dockerfile` now starts Uvicorn on `0.0.0.0:8000`. README documents local and
  container commands. CI builds the image, runs tests inside it and exercises
  the health and prediction endpoints.

## Local verification

- `uv run --locked ruff check .`: passed.
- `uv run --locked ruff format --check .`: passed.
- `uv run --locked pytest -q`: **60 passed** on Windows, Python 3.12.14.
- A `TestClient` smoke call against the checked-in saved model returned
  `GET /health` 200 with `baseline-1619d7c827e7` and `POST /predict` 200 with
  prediction `26.61239099461242` and the same model version.
- Docker is unavailable in this local environment. The Docker image, image ID,
  container test run and HTTP responses have therefore **not been verified
  locally**; the CI workflow is configured to record them as
  `lab4-container-evidence` when run.

## Team review and submission

- Branch: `lab4-prediction-api` (local working branch).
- Pull request and teammate review: pending; no remote PR or merge is claimed.
- CI run URL, image ID and container evidence: pending the first CI run.
- The individual `reports/week-2.md` belongs in each member's private report
  repository and should describe their own contribution and any assistance.
