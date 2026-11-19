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