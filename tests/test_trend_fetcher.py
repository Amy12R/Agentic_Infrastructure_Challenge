from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TREND_CONTRACT_PATH = REPO_ROOT / "skills" / "skill_trend_scan_v1" / "contract.json"


def _load_json(path: Path) -> dict:
    assert path.exists(), f"Missing file: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def test_trend_contract_exists_and_has_expected_shape() -> None:
    """
    Contract-level test: ensures the trend scan SkillContract exists and has
    the minimum required fields and output structure.
    """
    contract = _load_json(TREND_CONTRACT_PATH)

    # Required SkillContract top-level fields
    for key in ["id", "name", "description", "input_schema", "output_schema", "failure_modes", "version", "spec_version", "created_at"]:
        assert key in contract, f"Contract missing required key: {key}"

    # Output schema MUST include spec_version + contract_version (per technical.md)
    output_required = contract["output_schema"].get("required", [])
    assert "spec_version" in output_required, "output_schema.required must include 'spec_version'"
    assert "contract_version" in output_required, "output_schema.required must include 'contract_version'"

    # Trend output must contain topics array
    out_props = contract["output_schema"]["properties"]
    assert "topics" in out_props, "Trend output_schema must define 'topics'"


def test_trend_fetcher_returns_structure_matching_contract() -> None:
    """
    Runtime interface test (INTENTIONALLY FAILING until implemented):

    Asserts that the trend fetcher returns data matching the contract output semantics:
    - spec_version, contract_version
    - topics: list of { topic, sources, confidence, ... }
    - each source: { title, url }
    """
    contract = _load_json(TREND_CONTRACT_PATH)

    out_props = contract["output_schema"]["properties"]
    assert "topics" in out_props, "Contract output_schema must define 'topics'"

    # --- EMPTY SLOT: this import/function does not exist yet ---
  
    from chimera.trends import fetch_trends  # type: ignore[import-not-found]

    # Minimal valid input based on the contract input_schema
    payload = {"platforms": ["web", "news"], "max_results": 3}

    result = fetch_trends(payload)  # type: ignore[name-defined]

    # Validate basic output shape (semantics, not full JSON Schema)
    assert isinstance(result, dict), "Result must be an object/dict"
    assert "spec_version" in result, "Result must include spec_version"
    assert "contract_version" in result, "Result must include contract_version"
    assert isinstance(result.get("topics"), list), "Result.topics must be a list"

    for item in result["topics"]:
        assert isinstance(item, dict), "Each topic item must be an object/dict"
        assert "topic" in item and isinstance(item["topic"], str), "Topic item must include 'topic' (string)"
        assert "confidence" in item and isinstance(item["confidence"], (int, float)), "Topic item must include 'confidence' (number)"
        assert "sources" in item and isinstance(item["sources"], list), "Topic item must include 'sources' (list)"

        for src in item["sources"]:
            assert isinstance(src, dict), "Each source must be an object/dict"
            assert "title" in src and isinstance(src["title"], str), "Source must include 'title' (string)"
            assert "url" in src and isinstance(src["url"], str), "Source must include 'url' (string)"
