import json
import os
import sys
import urllib.request
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent
DEFAULT_BASE_URL = "http://127.0.0.1:8000"
METADATA_PATH = REPOSITORY_ROOT / "bike-demand" / "artifacts" / "model-metadata.json"


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
        return False
    print("ALL CHECKS PASSED")
    return True


def main() -> int:
    base_url = os.environ.get("BIKE_DEMAND_BASE_URL", DEFAULT_BASE_URL)
    token = os.environ.get("BIKE_DEMAND_ID_TOKEN")
    return 0 if check_service(base_url, token=token) else 1


if __name__ == "__main__":
    sys.exit(main())
