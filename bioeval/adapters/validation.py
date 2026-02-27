"""Validation helpers for external benchmark adapter inputs."""

from __future__ import annotations

import json
from pathlib import Path

from bioeval.adapters.cross_benchmark import SUPPORTED_BENCHMARKS, _load_records


def _has_any_key(rec: dict, keys: tuple[str, ...]) -> bool:
    return any(k in rec for k in keys)


def _check_lab_bench(rec: dict, idx: int, issues: list[dict]):
    if not _has_any_key(rec, ("task_type", "category")):
        issues.append(
            {
                "severity": "error",
                "index": idx,
                "field": "task_type/category",
                "message": "LAB-Bench record missing task type/category",
            }
        )
    if not _has_any_key(rec, ("domain",)):
        issues.append({"severity": "warning", "index": idx, "field": "domain", "message": "LAB-Bench record missing domain"})


def _check_bioprobench(rec: dict, idx: int, issues: list[dict]):
    valid = {"ord", "err", "pqa", "rea", "gen"}
    task_type = str(rec.get("task_type", "")).strip().lower()
    if not task_type:
        issues.append(
            {"severity": "error", "index": idx, "field": "task_type", "message": "BioProBench record missing task_type"}
        )
        return
    if task_type not in valid:
        issues.append(
            {
                "severity": "warning",
                "index": idx,
                "field": "task_type",
                "message": f"Unknown BioProBench task_type '{task_type}'",
            }
        )


def _check_biolp_bench(rec: dict, idx: int, issues: list[dict]):
    if not _has_any_key(rec, ("category", "task_type")):
        issues.append(
            {
                "severity": "error",
                "index": idx,
                "field": "category/task_type",
                "message": "BioLP-bench record missing category/task_type",
            }
        )


def validate_benchmark_payload(payload, benchmark: str) -> dict:
    """Validate external benchmark payload before conversion."""
    if benchmark not in SUPPORTED_BENCHMARKS:
        raise ValueError(f"Unsupported benchmark: {benchmark}. Supported: {', '.join(SUPPORTED_BENCHMARKS)}")

    records = _load_records(payload)
    issues: list[dict] = []
    valid_records = 0

    for i, rec in enumerate(records):
        if not isinstance(rec, dict):
            issues.append({"severity": "error", "index": i, "field": "record", "message": "Record must be a JSON object"})
            continue

        if not _has_any_key(rec, ("task_id", "id", "qid", "example_id", "item_id")):
            issues.append({"severity": "error", "index": i, "field": "id", "message": "Missing task identifier field"})

        if not _has_any_key(rec, ("prompt", "question", "input", "task")):
            issues.append(
                {
                    "severity": "warning",
                    "index": i,
                    "field": "prompt/question/input/task",
                    "message": "No prompt-like field found",
                }
            )

        if not _has_any_key(rec, ("response", "prediction", "output", "model_response")):
            issues.append(
                {
                    "severity": "warning",
                    "index": i,
                    "field": "response/prediction/output/model_response",
                    "message": "No response-like field found",
                }
            )

        if not _has_any_key(
            rec, ("score", "normalized_score", "accuracy", "f1", "exact_match", "correct", "passed", "is_correct")
        ):
            issues.append({"severity": "error", "index": i, "field": "score", "message": "Missing score-like field"})

        if benchmark == "lab-bench":
            _check_lab_bench(rec, i, issues)
        elif benchmark == "bioprobench":
            _check_bioprobench(rec, i, issues)
        elif benchmark == "biolp-bench":
            _check_biolp_bench(rec, i, issues)

        valid_records += 1

    n_errors = len([x for x in issues if x["severity"] == "error"])
    n_warnings = len([x for x in issues if x["severity"] == "warning"])
    return {
        "ok": n_errors == 0,
        "benchmark": benchmark,
        "n_records": len(records),
        "n_valid_records": valid_records,
        "n_errors": n_errors,
        "n_warnings": n_warnings,
        "issues": issues,
    }


def validate_benchmark_file(input_path: str, benchmark: str) -> dict:
    """Validate benchmark JSON file."""
    with open(input_path, encoding="utf-8") as f:
        payload = json.load(f)
    return validate_benchmark_payload(payload, benchmark)


def apply_strict_mode(validation_result: dict) -> dict:
    """Apply strict pass/fail policy (warnings become failures)."""
    out = dict(validation_result)
    out["strict_ok"] = out.get("n_errors", 0) == 0 and out.get("n_warnings", 0) == 0
    return out


def schema_path_for_benchmark(benchmark: str) -> Path:
    """Return bundled JSON Schema path for benchmark adapter input."""
    if benchmark not in SUPPORTED_BENCHMARKS:
        raise ValueError(f"Unsupported benchmark: {benchmark}. Supported: {', '.join(SUPPORTED_BENCHMARKS)}")
    root = Path(__file__).resolve().parent.parent.parent
    schema_dir = root / "examples" / "adapters" / "schemas"
    return schema_dir / f"{benchmark}_input.schema.json"


def validate_with_jsonschema(payload, benchmark: str) -> dict:
    """Validate payload using bundled JSON Schema (requires jsonschema package)."""
    schema_path = schema_path_for_benchmark(benchmark)
    if not schema_path.exists():
        return {
            "ok": False,
            "benchmark": benchmark,
            "schema_path": str(schema_path),
            "n_errors": 1,
            "issues": [
                {
                    "severity": "error",
                    "field": "schema",
                    "message": f"Schema file not found: {schema_path}",
                }
            ],
        }

    try:
        import jsonschema
    except ImportError:
        return {
            "ok": False,
            "benchmark": benchmark,
            "schema_path": str(schema_path),
            "n_errors": 1,
            "issues": [
                {
                    "severity": "error",
                    "field": "schema",
                    "message": "jsonschema package not installed",
                }
            ],
        }

    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)

    try:
        jsonschema.validate(instance=payload, schema=schema)
        return {
            "ok": True,
            "benchmark": benchmark,
            "schema_path": str(schema_path),
            "n_errors": 0,
            "issues": [],
        }
    except jsonschema.exceptions.ValidationError as e:
        path = ".".join(str(p) for p in e.path) if e.path else "$"
        return {
            "ok": False,
            "benchmark": benchmark,
            "schema_path": str(schema_path),
            "n_errors": 1,
            "issues": [
                {
                    "severity": "error",
                    "field": f"schema@{path}",
                    "message": e.message,
                }
            ],
        }
