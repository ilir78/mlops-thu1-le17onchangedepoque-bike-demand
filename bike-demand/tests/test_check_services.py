"""Tests for the Lab 5 live model identity checker."""

import importlib.util
import json
from pathlib import Path
from urllib.request import Request

import pytest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "check_services", ROOT / "check_services.py"
)
assert SPEC and SPEC.loader
check_services = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check_services)

pytestmark = pytest.mark.servicecheck


class Response:
    status = 200

    def __init__(self, payload: dict):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode()


def test_live_check_sends_bearer_token_and_matches_identity(tmp_path: Path) -> None:
    metadata = tmp_path / "metadata.json"
    expected = {"model_version": "v1", "model_sha256": "abc"}
    metadata.write_text(json.dumps(expected), encoding="utf-8")
    seen: dict = {}

    def fake_urlopen(request: Request, timeout: int):
        seen["url"] = request.full_url
        seen["authorization"] = request.get_header("Authorization")
        seen["timeout"] = timeout
        return Response(expected)

    assert check_services.check_service(
        "https://tagged.example",
        token="id-token",
        metadata_path=metadata,
        urlopen=fake_urlopen,
    )
    assert seen == {
        "url": "https://tagged.example/health",
        "authorization": "Bearer id-token",
        "timeout": 10,
    }


def test_live_check_fails_on_wrong_model_sha(tmp_path: Path) -> None:
    metadata = tmp_path / "metadata.json"
    metadata.write_text(
        json.dumps({"model_version": "v1", "model_sha256": "expected"}),
        encoding="utf-8",
    )
    assert not check_services.check_service(
        "https://service.example",
        metadata_path=metadata,
        urlopen=lambda *_args, **_kwargs: Response(
            {"model_version": "v1", "model_sha256": "different"}
        ),
    )
