# Week 2, Lab 3: same code, clean environment

## Objective and controlled inputs

Build the Lab 2 project in a clean Docker image from the committed `uv.lock`,
then run the unchanged baseline twice in disposable containers and compare with
the Lab 2 evidence. No feature, model, split, configuration or source-data
changes are part of this lab.

- Base revision on `main`: `a61f66a79a31f28472da1f0473efbec53f95d80a`
- Frozen data SHA-256: `e03de4ee4ef4dc376ac6e04bf829673c6269e8eba5c60fa121640fa2f829504f`
- Configuration: `configs/baseline.yaml`; fixed 12 predictors and Random Forest preset.
- Lock: committed `uv.lock`; Docker uses Python 3.12.15 and uv 0.12.23.
- Held-out test partition: 4,376 rows (2012-07-01 through 2012-12-31); not evaluated.

## Lab 2 reference

The committed Lab 2 report and `reports/metrics.json` record the following
validation results on the same 4,358 rows (2012-01-01 through 2012-06-30):

| Predictor | Lab 2 validation MAE (rentals/hour) |
| --- | ---: |
| Training-mean comparator | 154.231793 |
| Random Forest | 86.846857 |

Lab 2 training revision: `d3eafbf18578f7fe00b2c4bcc9bbe93c6a005031`.
Its final run IDs are documented in `reports/lab2-week-01-team.md`.

## Clean build and container evidence

Run the PowerShell procedure in `README.md` from the project root. It uses
`--pull --no-cache`, captures the full build and run output, records the image
ID, performs two fresh-container reruns, and executes the test suite inside the
image. The stale-lock probe must fail in its disposable copy.

Fill in this table from the raw output files after running the commands. Do not
copy the Lab 2 values into the Docker result fields.

| Evidence | Result |
| --- | --- |
| Lab 3 branch commit SHA | `<fill after commit>` |
| Docker image ID | `<fill from reports/lab3-image-id.txt>` |
| Clean build | `<record exit code and link reports/lab3-build.log>` |
| Container run 1 / RF run ID / MAE | `<fill from reports/lab3-run-1.log>` |
| Container run 2 / RF run ID / MAE | `<fill from reports/lab3-run-2.log>` |
| Container tests | `<record result and link reports/lab3-tests.log>` |
| Stale-lock probe | `<record expected nonzero exit>` |

## Comparison and interpretation

After capture, compare each run's `data_sha256`, partition row counts/date
bounds, ordered features and effective model settings to the Lab 2 reference.
Report the absolute MAE difference from Lab 2 for each predictor. Explain any
observed difference without changing the frozen inputs or evaluating the test
partition. Run IDs and timestamps are execution metadata and are expected to
change. Include the output logs in this report's links.

## Review

- Pull request: `<link after opening>`
- Teammate reviewer and review observation: `<complete after review>`
- Response or follow-up: `<complete after review>`

## Assistance and evidence limits

The Dockerfile, ignore rules and repeatable procedure are prepared on this branch.
The current Codex environment cannot run Docker or produce host build/run logs.
Therefore no image ID, Docker success, container metric or test result is claimed
here. The report becomes complete when the recorded commands have been run and
the evidence table and review fields are filled with observed results.
