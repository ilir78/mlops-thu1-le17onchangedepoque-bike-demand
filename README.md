# mlops-thu1-le17onchangedepoque-bike-demand

## Project Scope
* **User + Goal :** Estimer la demande horaire de vélos à partir de données calendaires et météorologiques pour les opérateurs et analyses opérationnelles[cite: 3, 68].
* **Inputs :** 12 variables ordonnées de calendrier et de météo (saison, heure, température, humidité, vent, etc.), excluant `cnt`, `casual` et `registered`[cite: 46, 47].
* **Output :** Une prédiction numérique non négative du nombre total de locations par heure (`cnt`) accompagnée de la version du modèle[cite: 21, 46].
* **Scope :** Validation des données, découpage chronologique strict, entraînement d'une baseline et d'une Random Forest, packaging Docker et service de prédiction API[cite: 1, 39, 48, 51].
* **Non-Goals :** Pas de recherche d'hyperparamètres poussée, pas de plateforme cloud complexe au-delà du conteneur local[cite: 40].
* **Verification :** Validation via des tests automatisés (`pytest`), l'exécution de pipelines de build et la vérification du comportement de l'API (codes de statut et validation Pydantic)[cite: 18, 24].


## Lab 5: Service Deployment & Observability

### Part 1: Service Operations
* **Settings:** What changes between laptop and container? 
  * *Choice:* Environment variables, execution paths, and network interfaces (`0.0.0.0` vs `127.0.0.1`). *Rejected:* Hardcoding local paths. *Why:* Containers require isolated port bindings and paths anchored to `/app`.
* **Model:** Where does it come from at start-up? 
  * *Choice:* Loaded from the pre-packaged `artifacts/model.joblib` baked into the image. *Rejected:* Dynamic remote download. *Why:* Guarantees a fully reproducible self-contained unit.
* **Ready:** When do you call the service "ready"? 
  * *Choice:* When the lifespan successfully loads the model and verifies its SHA256 checksum. *Rejected:* Immediate boot status. *Why:* Prevents returning 200 OK with missing artifacts.
* **Broken:** What does it say if the model is missing? 
  * *Choice:* Returns HTTP `503 Service Unavailable`. *Rejected:* Crashing container. *Why:* Allows health checks to handle it gracefully.
* **Log line:** What must one request tell an operator? 
  * *Choice:* Structured JSON logs containing event, method, path, status, latency in ms, and active model version[cite: 125]. *Rejected:* Unstructured prints. *Why:* Enables reliable log parsing.

### Part 2: Evidence & Security
* **Secrets:** What must never appear in a log? 
  * *Choice:* API keys, credentials, or raw feature payloads. *Rejected:* Full request dumping. *Why:* Security and privacy compliance.
* **Identity:** Which ID shows which model is running? 
  * *Choice:* `model_version` and `model_sha256`[cite: 146]. *Rejected:* Git commit alone. *Why:* Directly tracks the active physical model artifact.
* **Expected:** Who knows the expected model, and when? 
  * *Choice:* The team via `artifacts/model-metadata.json`[cite: 58]. *Rejected:* Runtime guessing. *Why:* Ensures traceability.
* **Promise:** What does "deployed" promise to others? 
  * *Choice:* An isolated container running the validated API, logging events, and enforcing Pydantic constraints[cite: 24, 117]. *Rejected:* Local script execution. *Why:* Guarantees parity.
* **Failure:** Break it once: what does it leave behind? 
  * *Choice:* A `503` response and a structured JSON error log entry[cite: 122, 129]. *Rejected:* Silent drops. *Why:* Instant diagnostic capability.

## Lab 6: CI Checks & Regression Tests

### Continuous integration

The active workflow is `.github/workflows/ci.yml` at the repository root. Pull requests targeting `main` run the same checks as pushes to `main`: locked dependency sync, Ruff lint and formatting, the full pytest suite (including API, infrastructure, service identity and regression checks), plus a Docker build that runs the suite inside the image and exercises `/health` and `/predict`. The container evidence and JUnit report are retained as workflow artifacts. Actions are pinned to commit SHAs. The jobs run on GitHub-hosted Ubuntu runners so they start from a clean machine and do not depend on a developer's local state.

The `deploy` job requires both `quality` and `container` to pass and runs only after a push to `main`; a pull request cannot deploy. This makes the merge to `main` the release gate. Deploy authentication uses GitHub OIDC / Google Workload Identity Federation, with `id-token: write` scoped to the deploy job; no service-account key is stored in GitHub. Configure these repository Actions variables before enabling deployment: `GCP_PROJECT_ID`, `GCP_REGION`, `GCP_ARTIFACT_REGISTRY`, `CLOUD_RUN_SERVICE`, `GCP_WIF_PROVIDER` (full provider resource name), and `GCP_DEPLOY_SERVICE_ACCOUNT` (service-account email). The identity checker compares the live `/health` model version and SHA256 with the metadata committed in this repository. It checks a tagged, no-traffic candidate before migration, checks the stable service after migration, and restores the captured prior revision traffic split if the live check fails. The workflow artifact records the deployed image, revision, URL and previous traffic split. A successful GitHub run plus its `lab6-deploy-evidence` artifact is the deployment evidence; until configured and run, deployment is not claimed as verified.

### Regression protection

`bike-demand/tests/test_regression.py` refits the fixed Random Forest using only the chronological train and validation partitions and recomputes the recorded validation MAE in `bike-demand/reports/metrics.json` (`86.84685685591091`). It never reads the held-out July–December 2012 test partition. The assertion is exact because the frozen dataset, locked dependencies, fixed random seed and single-thread model reproduce the same floating-point result in the current environment. A model/data/split change that alters the measured score must therefore update the reviewed baseline intentionally; a broad tolerance could hide a meaningful regression. The workflow also injects a disposable +1 prediction defect on the runner, confirms that the regression test fails, restores the source, and reruns the test green. Logs are kept in the quality job workspace and can be downloaded as workflow evidence.

The CI fault-injection proves that the guard catches a plausible prediction defect and is repaired in the same CI job. The lab's peer-authored defect exercise still requires a teammate to choose and introduce a defect without telling the author, open a PR, and record the red check and subsequent repaired green check on that PR. Those human review events must be completed by the team; the automated probe is not represented as a substitute.
