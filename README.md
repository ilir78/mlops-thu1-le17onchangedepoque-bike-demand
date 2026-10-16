# mlops-thu1-le17onchangedepoque-bike-demand

## Project Scope
* **User + Goal :** Estimer la demande horaire de vélos à partir de données calendaires et météorologiques pour les opérateurs et analyses opérationnelles[cite: 3, 68].
* **Inputs :** 12 variables ordonnées de calendrier et de météo (saison, heure, température, humidité, vent, etc.), excluant `cnt`, `casual` et `registered`[cite: 46, 47].
* **Output :** Une prédiction numérique non négative du nombre total de locations par heure (`cnt`) accompagnée de la version du modèle[cite: 21, 46].
* **Scope :** Validation des données, découpage chronologique strict, entraînement d'une baseline et d'une Random Forest, packaging Docker et service de prédiction API[cite: 1, 39, 48, 51].
* **Non-Goals :** Pas de recherche d'hyperparamètres poussée, pas de plateforme cloud complexe au-delà du conteneur local[cite: 40].
* **Verification :** Validation via des tests automatisés (`pytest`), l'exécution de pipelines de build et la vérification du comportement de l'API (codes de statut et validation Pydantic)[cite: 18, 24].
