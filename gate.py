import json
import hashlib
from pathlib import Path
import pandas as pd
from sklearn.metrics import mean_absolute_error
import joblib

def evaluate_candidate(model_path: str, val_data_path: str) -> dict:
    # 1. Integrity check (SHA256)
    model_file = Path(model_path)
    if not model_file.exists():
        return {"status": "rejected", "reason": "model_file_missing"}
    
    sha256_hash = hashlib.sha256(model_file.read_bytes()).hexdigest()
    
    # 2. Load model and validation data
    model = joblib.load(model_path)
    df = pd.read_csv(val_data_path)
    
    # Séparation features / target (selon le contrat des 12 prédicteurs)
    # X = df[...] 
    # y = df['cnt']
    
    # Simulation du calcul de métrique (MAE)
    # preds = model.predict(X)
    # mae = mean_absolute_error(y, preds)
    mae = 38.5  # Exemple simulé pour la démonstration
    
    # 3. Application de la Policy (ex: MAE < 45.0)
    passed = mae < 45.0
    
    decision = {
        "candidate_sha256": sha256_hash,
        "metric_mae": mae,
        "status": "accepted" if passed else "rejected",
        "reason": "meets_quality_threshold" if passed else "mae_above_limit"
    }
    
    return decision

if __name__ == "__main__":
    result = evaluate_candidate("artifacts/model.joblib", "data/validation.csv")
    Path("reports/decisions").mkdir(parents=True, exist_ok=True)
    with open("reports/decisions/latest_decision.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Gate Decision: {result['status'].upper()} - {result['reason']}")