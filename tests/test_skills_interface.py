from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "skills"


def _load_json(path: Path) -> dict:
    assert path.exists(), f"Missing file: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def _all_skill_contract_paths() -> list[Path]:
    assert SKILLS_DIR.exists(), f"Missing skills directory: {SKILLS_DIR}"
    paths = sorted(SKILLS_DIR.glob("*/contract.json"))
    assert paths, f"No contracts found under: {SKILLS_DIR}"
    return paths


def test_all_skill_contracts_have_required_fields() -> None:
    """
    Validate that each skills/*/contract.json includes required top-level fields and
    that output_schema requires spec_version and contract_version.
    """
    for contract_path in _all_skill_contract_paths():
        contract = _load_json(contract_path)

        required_top_level = [
            "id",
            "name",
            "description",
            "input_schema",
            "output_schema",
            "failure_modes",
            "version",
            "spec_version",
            "created_at",
        ]
        for key in required_top_level:
            assert key in contract, f"{contract_path}: missing required key '{key}'"

        failure_modes = contract["failure_modes"]
        assert isinstance(failure_modes, list) and failure_modes, (
            f"{contract_path}: failure_modes must be a non-empty list"
        )
        for fm in failure_modes:
            assert isinstance(fm, dict), f"{contract_path}: each failure mode must be an object"
            for k in ["code", "description", "retryable"]:
                assert k in fm, f"{contract_path}: failure mode missing '{k}'"

        out_required = contract["output_schema"].get("required", [])
        assert "spec_version" in out_required, (
            f"{contract_path}: output_schema.required must include 'spec_version'"
        )
        assert "contract_version" in out_required, (
            f"{contract_path}: output_schema.required must include 'contract_version'"
        )


def test_skills_runtime_interface_accepts_correct_parameters() -> None:
    """
    Assert that a unified runtime entrypoint exists and accepts valid inputs for a skill.
    This test is expected to fail until the runtime invocation layer is implemented.
    """
    from chimera.runtime import invoke_skill  # type: ignore[import-not-found]

    valid_write_post_input: Dict[str, Any] = {
        "topic": "Example topic",
        "platform": "x",
        "variants": 1,
    }

    out = invoke_skill("skill_write_post_v1", valid_write_post_input)  # type: ignore[name-defined]

    assert isinstance(out, dict), "invoke_skill output must be an object/dict"
    assert "spec_version" in out, "invoke_skill output must include spec_version"
    assert "contract_version" in out, "invoke_skill output must include contract_version"
    assert isinstance(out.get("items"), list), "write_post output must include items list"
    assert out["items"], "write_post output items must not be empty"
    assert isinstance(out["items"][0].get("text"), str), "each item must contain 'text' as a string"


def test_invalid_input_returns_error_contract_shape() -> None:
    """
    Assert that invalid input results in a structured error conforming to ErrorContract semantics.
    This test is expected to fail until structured error handling is implemented.
    """
    from chimera.runtime import invoke_skill  # type: ignore[import-not-found]

    invalid_input: Dict[str, Any] = {"platform": "x"}

    try:
        invoke_skill("skill_write_post_v1", invalid_input)  # type: ignore[name-defined]
        assert False, "Expected invoke_skill to fail on invalid input"
    except Exception as e:
        to_dict = getattr(e, "to_dict", None)
        assert callable(to_dict), "Expected a structured error (e.g., exception with to_dict())"

        payload = to_dict()
        assert isinstance(payload, dict), "ErrorContract payload must be a dict"
        for key in ["error_code", "error_message", "spec_version", "contract_version", "timestamp"]:
            assert key in payload, f"ErrorContract missing required key: {key}"
