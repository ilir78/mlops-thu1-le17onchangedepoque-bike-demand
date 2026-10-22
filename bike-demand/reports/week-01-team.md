# Week 1 team evidence (Labs 1–2)

## Team and roles

- Team members, Lab 2 lead, reviewer and evidence recorder: complete with the group; names were not available in this local copy.

## Repository, setup and checks

- Source scaffold: `minhtc-uca/mlops-course/bike-demand`; local branch: `lab02/data-baseline`.
- Code commits: `65b0fc0` (validation, split, predictors and Fault B), `d5ea1c8` (partition end keys). Execution revision: `d3eafbf`.
- Setup: `uv 0.12.23`, Python 3.12.14, `uv sync --locked --python <Python 3.12.14>`; preflight passed. `uv python install 3.12` could not create its version-link directory in this Windows sandbox, so the bundled 3.12 interpreter was used.
- `ruff check .` and `ruff format --check .`: passed. `pytest -q -m infra`: 9 passed. `pytest -q -m exercise`: 36 passed. `pytest -q`: 48 passed (one SQLAlchemy deprecation warning).
- `python -m bike_demand.validate --data data/raw/hour.csv`: validated 17,379 rows. The canonical CSV still matches `data/manifest.json`; SHA-256 `e03de4ee4ef4dc376ac6e04bf829673c6269e8eba5c60fa121640fa2f829504f`.

## Data validation and faults

- Validator enforces the required columns, unique positive integer `instant`, parseable dates within 2011–2012, integer category domains, finite normalised weather values in `[0, 1]`, and nonnegative integer counts. It never repairs or rewrites the source.
- Fault A (worked example): remove `temp` from a copy; rejection names the missing field. The six-row valid control passes.
- Fault B (own choice): set `weathersit=5` in a separate six-row copy, retaining every column. Rejected with `weathersit: require integers in [1, 4]`; the valid control passes. Test: `test_fault_b_rejects_out_of_range_weather_category`.

## Split and baseline evidence

- Ordered predictors: `season, yr, mnth, hr, holiday, weekday, workingday, weathersit, temp, atemp, hum, windspeed`. The target components and identity/date fields are excluded.
- Train: 8,645 rows, 2011-01-01 to 2011-12-31; first key `2011-01-01,0,1`, last key `2011-12-31,23,8645`.
- Validation: 4,358 rows, 2012-01-01 to 2012-06-30; first key `2012-01-01,0,8646`, last key `2012-06-30,23,13003`.
- Test: 4,376 rows, 2012-07-01 to 2012-12-31; first key `2012-07-01,0,13004`, last key `2012-12-31,23,17379`. Held; no test metric was computed.
- Training-label mean: 143.7944 rentals/hour. Validation MAE on the same 4,358 rows: mean `154.2318`, fixed Random Forest `86.8469` rentals/hour. This is the observed comparison, not a promised threshold.
- Final MLflow run IDs: mean `abe0e29ae8b240728c03ca023ba7e208`; Random Forest `5253a2f8bcce4c2cbaf44e24555da8fd`. RF model version `baseline-1619d7c827e7`; `training_commit=d3eafbf18578f7fe00b2c4bcc9bbe93c6a005031`; `working_tree_dirty=false`.
- Reload evidence: validation MAE `86.84685685591091`, delta `0`; metadata matches and logged model bytes match. Outputs: `artifacts/model.joblib`, `artifacts/model-metadata.json`, `reports/metrics.json`; local run store: `tracking/mlflow.db` and `tracking/artifacts/` (keep out of Git).
- An initial run attempt left a failed MLflow run (`b6dd7518bc8c430c846b5c768ee0c1e6`) when Windows denied access to its default temporary directory. A retry using a workspace temporary directory completed. Earlier successful trial runs also remain in the local tracking database; the run IDs above identify the final execution with partition endpoint keys. The unchanged-config stretch was not attempted.

## Review, contribution and next action

- This is a local copy of the course scaffold, not the private team repository. No PR was pushed, no teammate review was performed, and no remote CI result is claimed. Transfer/review this branch in the team repository and record the real reviewer observation, response and CI revision.
- Codex assistance: implemented Lab 2 validation, chronological split, mean/RF predictors, Fault B test and evidence. The full suite exposed one remaining Lab 1 whitespace-normalisation failure in this course copy; the helper was repaired so all supplied tests pass. Team members should review these changes and record their own contributions.
- Next action: Amine and teammate review the local diff, move it to the private team repository, then record the actual PR/CI and peer-review results. No merge is recorded here.
