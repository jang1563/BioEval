"""Tests for cross-benchmark adapter conversion into BioEval schema."""

import json
import os
import tempfile
from pathlib import Path

import pytest


def test_convert_lab_bench_payload():
    from bioeval.adapters.cross_benchmark import convert_benchmark_payload

    payload = [
        {
            "id": "lab_001",
            "task_type": "protocol_ordering",
            "question": "Order these PCR steps.",
            "prediction": "denaturation -> annealing -> extension",
            "label": "denaturation -> annealing -> extension",
            "accuracy": 1.0,
            "domain": "protocols",
        },
        {
            "id": "lab_002",
            "task_type": "figure_interpretation",
            "question": "Interpret this dose-response curve.",
            "prediction": "IC50 is lower in treated group",
            "score": 0.7,
            "domain": "figures",
        },
    ]

    converted = convert_benchmark_payload(payload, benchmark="lab-bench", model="lab-model")
    assert converted["metadata"]["source_benchmark"] == "lab-bench"
    assert converted["summary"]["total_tasks"] == 2
    components = {r["component"] for r in converted["results"]}
    assert "protoreason" in components
    assert "datainterp" in components


def test_convert_bioprobench_payload():
    from bioeval.adapters.cross_benchmark import convert_benchmark_payload

    payload = {
        "predictions": [
            {
                "task_id": "bp_001",
                "task_type": "ORD",
                "input": "Order the protocol steps",
                "output": "A -> B -> C",
                "target": "A -> B -> C",
                "normalized_score": 0.9,
            },
            {
                "task_id": "bp_002",
                "task_type": "ERR",
                "input": "Find the protocol error",
                "output": "Missing wash step",
                "correct": True,
            },
        ]
    }

    converted = convert_benchmark_payload(payload, benchmark="bioprobench", model="bp-model")
    assert converted["summary"]["total_tasks"] == 2
    assert len(converted["results"]) == 1
    assert converted["results"][0]["component"] == "protoreason"
    task_types = {r["task_type"] for r in converted["results"][0]["results"]}
    assert "step_ordering" in task_types
    assert "troubleshooting" in task_types


def test_convert_biolp_bench_payload():
    from bioeval.adapters.cross_benchmark import convert_benchmark_payload

    payload = {
        "items": [
            {
                "item_id": "lp_001",
                "category": "protocol_error_correction",
                "prompt": "Identify and fix the error.",
                "response": "Correct concentration is 10 mM.",
                "f1": 0.8,
            }
        ]
    }

    converted = convert_benchmark_payload(payload, benchmark="biolp-bench", model="lp-model")
    assert converted["summary"]["total_tasks"] == 1
    assert converted["results"][0]["component"] == "designcheck"
    item = converted["results"][0]["results"][0]
    assert item["passed"] is True
    assert item["score"] == 0.8


def test_convert_benchmark_file_writes_output():
    from bioeval.adapters.cross_benchmark import convert_benchmark_file

    payload = [{"id": "lab_x", "task_type": "figure_interpretation", "score": 0.6}]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as inf:
        json.dump(payload, inf)
        input_path = inf.name

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as outf:
        output_path = outf.name

    try:
        converted = convert_benchmark_file(
            input_path=input_path,
            benchmark="lab-bench",
            model="external-test",
            output_path=output_path,
        )
        assert os.path.exists(output_path)
        assert converted["metadata"]["output_file"] == output_path
        with open(output_path) as f:
            written = json.load(f)
        assert written["summary"]["total_tasks"] == 1
    finally:
        os.unlink(input_path)
        os.unlink(output_path)


def test_validate_adapter_payload_passes_for_template_like_data():
    from bioeval.adapters.validation import validate_benchmark_payload

    payload = [
        {
            "id": "lab_val_001",
            "task_type": "protocol_ordering",
            "domain": "protocols",
            "question": "Order steps",
            "prediction": "A->B->C",
            "score": 1.0,
        }
    ]

    result = validate_benchmark_payload(payload, benchmark="lab-bench")
    assert result["ok"] is True
    assert result["n_errors"] == 0


def test_validate_adapter_payload_fails_missing_score():
    from bioeval.adapters.validation import validate_benchmark_payload

    payload = [
        {
            "task_id": "bp_val_001",
            "task_type": "ORD",
            "input": "Order steps",
            "output": "A->B->C",
        }
    ]

    result = validate_benchmark_payload(payload, benchmark="bioprobench")
    assert result["ok"] is False
    assert result["n_errors"] >= 1


def test_apply_strict_mode_fails_on_warnings():
    from bioeval.adapters.validation import apply_strict_mode, validate_benchmark_payload

    payload = [
        {
            "id": "lab_warn_001",
            "task_type": "protocol_ordering",
            "score": 1.0
        }
    ]
    result = validate_benchmark_payload(payload, benchmark="lab-bench")
    assert result["ok"] is True
    assert result["n_warnings"] >= 1

    strict = apply_strict_mode(result)
    assert strict["strict_ok"] is False


def test_adapter_schema_json_files_are_valid_json():
    root = Path(__file__).resolve().parent.parent
    schema_dir = root / "examples" / "adapters" / "schemas"
    expected = [
        schema_dir / "lab-bench_input.schema.json",
        schema_dir / "bioprobench_input.schema.json",
        schema_dir / "biolp-bench_input.schema.json",
    ]
    for p in expected:
        assert p.exists()
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        assert "$schema" in data
        assert "oneOf" in data


def test_schema_path_for_benchmark_exists():
    from bioeval.adapters.validation import schema_path_for_benchmark

    for b in ("lab-bench", "bioprobench", "biolp-bench"):
        p = schema_path_for_benchmark(b)
        assert p.exists()


def test_validate_with_jsonschema_if_available():
    pytest.importorskip("jsonschema")

    from bioeval.adapters.validation import validate_with_jsonschema

    payload = [
        {
            "id": "lab_schema_001",
            "task_type": "protocol_ordering",
            "score": 0.8
        }
    ]
    result = validate_with_jsonschema(payload, "lab-bench")
    assert result["ok"] is True


def test_validate_with_jsonschema_rejects_invalid_container_if_available():
    pytest.importorskip("jsonschema")

    from bioeval.adapters.validation import validate_with_jsonschema

    payload = {"not_records": 1}
    result = validate_with_jsonschema(payload, "lab-bench")
    assert result["ok"] is False
