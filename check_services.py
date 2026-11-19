import json
import sys
import urllib.request
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"
METADATA_PATH = Path(__file__).resolve().parents[1] / "artifacts" / "model-metadata.json"

def main():
    expected_meta = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    expected_version = expected_meta["model_version"]
    expected_sha = expected_meta["model_sha256"]

    try:
        with urllib.request.urlopen(f"{BASE_URL}/health", timeout=5) as resp:
            if resp.status != 200:
                print(f"FAIL: /health returned {resp.status}")
                sys.exit(1)
            health = json.loads(resp.read().decode())
    except Exception as e:
        print(f"FAIL: Cannot reach service at {BASE_URL}: {e}")
        sys.exit(1)

    obs_version = health.get("model_version")
    obs_sha = health.get("model_sha256")

    checks = [
        ("model_version", expected_version, obs_version),
        ("model_sha256", expected_sha, obs_sha),
    ]

    failed = False
    for name, exp, obs in checks:
        status = "ok" if exp == obs else "FAIL"
        if status == "FAIL":
            failed = True
        print(f"{name:<15} | expected: {exp} | observed: {obs} | {status}")

    if failed:
        sys.exit(1)
    print("ALL CHECKS PASSED")

if __name__ == "__main__":
    main()