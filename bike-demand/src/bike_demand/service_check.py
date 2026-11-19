"""Compare the live prediction service's model identity with local metadata."""

import json
import os
import sys
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BASE_URL = "http://127.0.0.1:8000"
METADATA_PATH = PROJECT_ROOT / "artifacts" / "model-metadata.json"


def check_service(
    base_url: str,
    *,
    token: str | None = None,
    metadata_path: Path = METADATA_PATH,
    urlopen=urllib.request.urlopen,
) -> bool:
    expected_meta = json.loads(metadata_path.read_text(encoding="utf-8"))
    expected_version = expected_meta["model_version"]
    expected_sha = expected_meta["model_sha256"]

    try:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        request = urllib.request.Request(
            f"{base_url.rstrip('/')}/health", headers=headers
        )
        with urlopen(request, timeout=10) as resp:
            if resp.status != 200:
                print(f"FAIL: /health returned {resp.status}")
                return False
            health = json.loads(resp.read().decode())
    except Exception as error:
        print(f"FAIL: Cannot reach service at {base_url}: {error}")
        return False

    observed = {
        "model_version": health.get("model_version"),
        "model_sha256": health.get("model_sha256"),
    }
    expected = {
        "model_version": expected_version,
        "model_sha256": expected_sha,
    }
    failed = False
    for name, expected_value in expected.items():
        observed_value = observed[name]
        status = "ok" if expected_value == observed_value else "FAIL"
        failed |= status == "FAIL"
        print(
            f"{name:<15} | expected: {expected_value} | "
            f"observed: {observed_value} | {status}"
        )

    if failed:
        return False
    print("ALL CHECKS PASSED")
    return True


def main() -> int:
    base_url = os.environ.get("BIKE_DEMAND_BASE_URL", DEFAULT_BASE_URL)
    token = os.environ.get("BIKE_DEMAND_ID_TOKEN")
    return 0 if check_service(base_url, token=token) else 1


if __name__ == "__main__":
    sys.exit(main())
