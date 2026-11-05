# Week 2, Lab 3: same code, clean environment

## Objective and controlled inputs

Build the Lab 2 project in a clean Docker image from the committed `uv.lock`,
then run the unchanged baseline twice in disposable containers and compare with
the Lab 2 evidence. No feature, model, split, configuration or source-data
changes are part of this lab.

- Base revision on `main`: `a61f66a79a31f28472da1f0473efbec53f95d80a`
- PR branch revision tested: `377e20d1d812f00ce7d93ca61622c80d7d654b60`
- GitHub Actions pull-request merge revision used to build the image:
  `7eaa4d1951c7f17c485b6ce7bdab8232cdeeaa3b`
- Frozen data SHA-256: `e03de4ee4ef4dc376ac6e04bf829673c6269e8eba5c60fa121640fa2f829504f`
- Configuration: `configs/baseline.yaml`; fixed 12 predictors and Random Forest preset.
- Lock: committed `uv.lock`; Docker uses Python 3.12.15 and uv 0.12.23.
- The image label and both MLflow records contain the tested merge revision; `.git`
  remains outside the image and the run records report `working_tree_dirty: false`.
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

GitHub Actions run [#14](https://github.com/ilir78/mlops-thu1-le17onchangedepoque-bike-demand/actions/runs/42062139325)
built the image with `--pull --no-cache`, inspected its revision label, ran
two fresh containers, ran the full test suite inside the image and verified that
a deliberately stale lock is rejected. Both the quality and container jobs
succeeded. The raw CI artifact is available [here](https://github.com/ilir78/mlops-thu1-le17onchangedepoque-bike-demand/actions/runs/42062139325/artifacts/13432452814);
the captured logs and image identifiers are also committed beside this report.

| Evidence | Result |
| --- | --- |
| PR branch revision tested | `377e20d1d812f00ce7d93ca61622c80d7d654b60` |
| Image source revision label | `7eaa4d1951c7f17c485b6ce7bdab8232cdeeaa3b` |
| Docker image ID | `sha256:2e7f43636b1813aa71b7b62e8d86cea71afb65334403f216cc5f913b00f59846` |
| Clean Docker build | Passed in GitHub Actions run #14; [build log](lab3-build.log) |
| Container run 1 | Comparator run `9392da4041dd4ef49ea2640ebb8d5726`; RF run `cde833ac1c2544a995ddf6d254adc3bd`; [log](lab3-run-1.log) |
| Container run 2 | Comparator run `ebf110dda8bb49158163763a5d3cb5e0`; RF run `f5a26dd736aa4bf0a5b63abbdfafab18`; [log](lab3-run-2.log) |
| Container tests | 48 passed, 1 warning; [test log](lab3-tests.log) |
| Stale-lock probe | Expected nonzero exit; uv reported that `uv.lock` needed updating while `--locked` was set; [log](lab3-stale-lock-probe.log) |
| Image ID and revision files | [image ID](lab3-image-id.txt), [source revision](lab3-image-revision.txt) |

The workflow checked out GitHub's pull-request merge revision
`7eaa4d1951c7f17c485b6ce7bdab8232cdeeaa3b`; it is therefore the recorded image
label and `training_commit`. The branch revision identifies the PR source at
the time of that run.

## Comparison and interpretation

Both clean-container executions used the same SHA-256, the same 12 ordered
predictors, the same configuration and the same partition boundaries as Lab 2:

| Partition | Rows | Dates |
| --- | ---: | --- |
| Train | 8,645 | 2011-01-01 to 2011-12-31 |
| Validation | 4,358 | 2012-01-01 to 2012-06-30 |
| Test (not scored) | 4,376 | 2012-07-01 to 2012-12-31 |

| Predictor | Lab 2 MAE | Container run 1 MAE | Container run 2 MAE | Difference from Lab 2 |
| --- | ---: | ---: | ---: | ---: |
| Training-mean comparator | 154.231793 | 154.231793 | 154.231793 | 0.000000 |
| Random Forest | 86.846857 | 86.846857 | 86.846857 | 0.000000 |

The metrics match Lab 2 exactly in both runs. Random Forest settings remained
`n_estimators=50`, `max_depth=10`, `random_state=42` and `n_jobs=1`.
The MLflow run IDs and execution timestamps differ as expected. The held-out
test partition remained unscored.

## Review

- Pull request: [Lab 3 PR #3](https://github.com/ilir78/mlops-thu1-le17onchangedepoque-bike-demand/pull/3)
- Teammate reviewer and review observation: **Pending peer review**
- Response or follow-up: **Pending peer review**

## Assistance and evidence limits

The container build and runs were executed by GitHub Actions on a clean
Ubuntu runner; this is Linux-container evidence, not a local Windows Docker run.
The image, raw output logs, image ID and revision label are recorded above and
in the committed evidence files.
