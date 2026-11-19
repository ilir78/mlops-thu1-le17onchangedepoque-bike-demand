# Week 3 — Lab 6: GitHub Actions, CI Checks & Regression Tests

## Work completed in this branch

- Replaced the repository-root workflow with PR-to-main CI and main-only deployment jobs.
- Added lint, formatting, full pytest, container build/test and API smoke checks on clean GitHub-hosted Ubuntu runners.
- Added a deterministic validation-metric regression test, which uses train and validation only and does not score the held-out test partition.
- Added a runner-only injected prediction defect. CI must record its failing regression run, restore the original source, then pass the regression test.
- Made the Lab 5 live model identity checker accept a service URL and OIDC identity token from the environment; added tests for identity comparison and bearer authorization.
- Added a Cloud Run candidate check before traffic migration and a saved traffic split to restore when the stable live check fails.
- Documented the CI and deployment choices in the repository README.

## Evidence and current limitations

The committed validation record is `86.84685685591091` MAE. A deterministic refit was previously measured at the same value (delta 0.0). The runner's JUnit report, fault-injection logs, Docker logs, health response and prediction response are emitted as workflow evidence. These artifacts do not exist until the workflow runs on GitHub.

Cloud Run deployment needs repository Actions variables: `GCP_PROJECT_ID`, `GCP_REGION`, `GCP_ARTIFACT_REGISTRY`, `CLOUD_RUN_SERVICE`, `GCP_WIF_PROVIDER`, and `GCP_DEPLOY_SERVICE_ACCOUNT`. No Cloud Run deployment is claimed until those are supplied and a successful main workflow is recorded. The teammate-authored surprise-defect PR is also a required team exercise and cannot be simulated as a real peer review by this implementation.

## Team follow-up

1. Configure the six GCP repository variables and confirm the workload identity provider permits this repository and branch.
2. Merge this Lab 6 PR only after its CI jobs pass; observe the main deployment and retain the deployment evidence artifact.
3. Have a teammate privately select a realistic defect, open the exercise PR, capture the failing check, then fix it and capture the green check on that same PR.
4. Add the two reviewed PRs to the team report and create the annotated `m3` tag after both are reviewed.
