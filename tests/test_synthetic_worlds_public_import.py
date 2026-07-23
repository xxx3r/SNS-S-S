from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_PARENT = ROOT / "src" / "sim"
if str(PACKAGE_PARENT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_PARENT))

from synthetic_worlds import (  # noqa: E402
    Budget,
    ValidationError,
    build_dataset_manifest,
    generate_records,
    load_recipe,
    validate_dataset_manifest,
    validate_recipe,
    write_shards,
)

IMPORT_MANIFEST_PATH = ROOT / "src" / "sim" / "SYNTHETIC_WORLDS_IMPORT_MANIFEST.json"
APPROVED_EXPORT_MANIFEST_PATH = ROOT / "docs" / "synthetic_worlds" / "APPROVED_EXPORT_MANIFEST.json"
RECIPE_PATH = ROOT / "configs" / "synthetic_worlds" / "basic_world.json"
EXPECTED_EXPORT_SELF_HASH = "920322db9a6aaa4391a97da8f5d91b16b52cec387419cba249f13cd3cfd602fa"
FORBIDDEN_PUBLIC_MARKERS = (
    "Grav_grav",
    "relativity_engine",
    "drive.google.com",
    "MASOTimeAE",
    "QIDINN",
    "GhostFilm",
    "private-user-images",
)
FORBIDDEN_NETWORK_IMPORTS = (
    "import requests",
    "import urllib",
    "import socket",
    "import http.client",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_public_import_manifest_binds_exact_approved_bytes():
    manifest = json.loads(IMPORT_MANIFEST_PATH.read_text(encoding="utf-8"))
    assert manifest["schema_version"] == "sns.synthetic-world-import.v1"
    assert manifest["human_release_state"] == "APPROVED_FOR_PUBLIC_IMPORT"
    assert manifest["terminal_state"] == "SNS_SYNTHETIC_WORLD_CORE_IMPORTED"
    assert manifest["campaign_state"] == "NEEDS_GOVERNANCE_REVIEW"

    payload = {key: value for key, value in manifest.items() if key != "import_manifest_sha256"}
    actual_self_hash = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    assert manifest["import_manifest_sha256"] == actual_self_hash

    for entry in manifest["imported_files"]:
        path = ROOT / entry["destination_path"]
        assert path.is_file(), entry["destination_path"]
        assert path.stat().st_size == entry["bytes"]
        assert _sha256(path) == entry["sha256"]

    approved = json.loads(APPROVED_EXPORT_MANIFEST_PATH.read_text(encoding="utf-8"))
    assert approved["candidate_identity"] == "synthetic_worlds"
    assert approved["terminal_state"] == "PRIVATE_EXPORT_CANDIDATE_QUALIFIED"
    assert approved["human_release_state"] == "NOT_REVIEWED"
    assert approved["manifest_sha256"] == EXPECTED_EXPORT_SELF_HASH
    assert manifest["approved_export_manifest_self_hash"] == EXPECTED_EXPORT_SELF_HASH
    assert manifest["approved_qualification_receipt_hash"] == approved["qualification_receipt"]["receipt_sha256"]
    assert manifest["approved_candidate_file_set_hash"] == approved["qualification_receipt"]["file_set_sha256"]


def test_public_tree_has_no_private_identifiers_or_network_dependency():
    manifest = json.loads(IMPORT_MANIFEST_PATH.read_text(encoding="utf-8"))
    for entry in manifest["imported_files"]:
        path = ROOT / entry["destination_path"]
        text = path.read_text(encoding="utf-8")
        for marker in FORBIDDEN_PUBLIC_MARKERS:
            assert marker not in text, f"{marker!r} leaked into {entry['destination_path']}"
        if path.suffix == ".py":
            lowered = text.lower()
            for network_import in FORBIDDEN_NETWORK_IMPORTS:
                assert network_import not in lowered


def test_exact_import_generates_and_validates_tiny_fixture(tmp_path):
    recipe = load_recipe(str(RECIPE_PATH))
    first = list(generate_records(recipe))
    second = list(generate_records(recipe))
    assert first == second
    assert len(first) == 4

    shard_manifest = write_shards(
        first,
        tmp_path / "shards",
        shard_size=2,
        budget=Budget(max_records=4, max_shards=2, max_parameter_combinations=4, max_points_per_record=7, max_total_points=28, max_bytes=4096),
        expected_records=4,
    )
    dataset_manifest = build_dataset_manifest(recipe, shard_manifest)
    validated = validate_dataset_manifest(dataset_manifest, tmp_path / "shards", recipe)
    assert validated == first


def test_public_recipe_still_fails_closed():
    recipe = load_recipe(str(RECIPE_PATH))
    recipe["unexpected"] = "not allowed"
    with pytest.raises(ValidationError, match="unknown keys"):
        validate_recipe(recipe)

    recipe = load_recipe(str(RECIPE_PATH))
    recipe["records"] = 5
    with pytest.raises(ValidationError, match="records exceed budget"):
        validate_recipe(recipe, Budget(max_records=4))
