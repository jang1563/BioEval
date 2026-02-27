"""Cross-benchmark adapters into BioEval canonical result schema."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from bioeval.version import __version__

SUPPORTED_BENCHMARKS = ("lab-bench", "bioprobench", "biolp-bench")
ADAPTER_VERSION = "adapter-v1"


def _safe_lower(value) -> str:
    return str(value).strip().lower() if value is not None else ""


def _load_records(payload):
    """Extract benchmark records from common JSON container patterns."""
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        raise ValueError("Input JSON must be a list or dict container")

    for key in ("results", "predictions", "items", "tasks", "examples", "data"):
        if isinstance(payload.get(key), list):
            return payload[key]

    # Single dict task
    return [payload]


def _extract_score(rec: dict) -> float:
    """Extract normalized score in [0, 1] from an external record."""
    scores = rec.get("scores", {}) if isinstance(rec.get("scores"), dict) else {}

    for key in ("score", "normalized_score", "accuracy", "f1", "exact_match"):
        if isinstance(rec.get(key), (int, float)):
            return _clamp(float(rec[key]))
        if isinstance(scores.get(key), (int, float)):
            return _clamp(float(scores[key]))

    for key in ("correct", "passed", "is_correct"):
        if isinstance(rec.get(key), bool):
            return 1.0 if rec[key] else 0.0
        if isinstance(scores.get(key), bool):
            return 1.0 if scores[key] else 0.0

    return 0.0


def _extract_task_id(rec: dict, i: int, benchmark: str) -> str:
    for key in ("task_id", "id", "qid", "example_id", "item_id"):
        value = rec.get(key)
        if value is not None:
            return str(value)
    return f"{benchmark}_{i:05d}"


def _extract_text(rec: dict, *keys) -> str:
    for key in keys:
        value = rec.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return ""


def _extract_ground_truth(rec: dict):
    for key in ("ground_truth", "target", "label", "reference", "answer"):
        if key in rec:
            return rec[key]
    return None


def _clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


def _map_lab_component(rec: dict) -> tuple[str, str]:
    """Map LAB-Bench record to BioEval component/task_type."""
    task_type = _safe_lower(rec.get("task_type") or rec.get("subtask") or rec.get("category"))
    domain = _safe_lower(rec.get("domain"))
    merged = " ".join([task_type, domain])

    if any(k in merged for k in ("protocol", "cloning", "sequence", "ord", "workflow")):
        return "protoreason", task_type or "workflow_reasoning"
    if any(k in merged for k in ("safety", "biosecurity", "dual_use")):
        return "biosafety", task_type or "safety_assessment"
    if any(k in merged for k in ("debate", "multi-agent")):
        return "debate", task_type or "debate"
    return "datainterp", task_type or "data_interpretation"


def _map_bioprobench_component(rec: dict) -> tuple[str, str]:
    """Map BioProBench record to BioEval component/task_type."""
    raw_type = _safe_lower(rec.get("task_type") or rec.get("task") or rec.get("subset"))
    ptype = _safe_lower(rec.get("protocol_task_type"))
    merged = raw_type or ptype

    if merged in ("ord", "ordering"):
        return "protoreason", "step_ordering"
    if merged in ("err", "error_detection", "error_correction"):
        return "protoreason", "troubleshooting"
    if merged in ("pqa", "qa", "question_answering"):
        return "protoreason", "protocol_qa"
    if merged in ("rea", "reasoning"):
        return "protoreason", "protocol_reasoning"
    if merged in ("gen", "generation"):
        return "protoreason", "protocol_generation"
    return "protoreason", merged or "protocol_reasoning"


def _map_biolp_component(rec: dict) -> tuple[str, str]:
    """Map BioLP-bench record to BioEval component/task_type."""
    raw_type = _safe_lower(rec.get("task_type") or rec.get("task") or rec.get("category"))
    if "debate" in raw_type:
        return "debate", raw_type
    return "designcheck", raw_type or "protocol_error_correction"


def _to_bioeval_item(rec: dict, i: int, benchmark: str, strict: bool = False) -> dict:
    if benchmark == "lab-bench":
        component, task_type = _map_lab_component(rec)
    elif benchmark == "bioprobench":
        component, task_type = _map_bioprobench_component(rec)
    elif benchmark == "biolp-bench":
        component, task_type = _map_biolp_component(rec)
    else:
        raise ValueError(f"Unsupported benchmark: {benchmark}")

    task_id = _extract_task_id(rec, i, benchmark)
    score = _extract_score(rec)
    if (
        strict
        and score == 0.0
        and not any(k in rec for k in ("score", "normalized_score", "accuracy", "f1", "exact_match", "correct", "passed"))
    ):
        raise ValueError(f"Missing score-like fields for record {task_id}")

    out = {
        "task_id": task_id,
        "task_type": task_type,
        "prompt": _extract_text(rec, "prompt", "question", "input", "task"),
        "response": _extract_text(rec, "response", "prediction", "output", "model_response"),
        "score": score,
        "passed": score >= 0.5,
        "source_benchmark": benchmark,
        "source_fields": {
            "domain": rec.get("domain"),
            "category": rec.get("category"),
            "subset": rec.get("subset"),
        },
    }

    gt = _extract_ground_truth(rec)
    if gt is not None:
        out["ground_truth"] = gt

    return {"component": component, "item": out}


def _summarize(by_component: dict[str, list[dict]]) -> dict:
    summary = {"total_tasks": 0, "by_component": {}}
    for component, rows in by_component.items():
        n = len(rows)
        completed = len([r for r in rows if "error" not in r])
        summary["total_tasks"] += n
        summary["by_component"][component] = {
            "num_tasks": n,
            "completed": completed,
        }
    return summary


def convert_benchmark_payload(
    payload,
    benchmark: str,
    model: str = "external-model",
    split: str = "all",
    strict: bool = False,
) -> dict:
    """Convert foreign benchmark payload to BioEval canonical result schema."""
    if benchmark not in SUPPORTED_BENCHMARKS:
        raise ValueError(f"Unsupported benchmark: {benchmark}. Supported: {', '.join(SUPPORTED_BENCHMARKS)}")

    records = _load_records(payload)
    by_component: dict[str, list[dict]] = {}
    for i, rec in enumerate(records):
        if not isinstance(rec, dict):
            if strict:
                raise ValueError(f"Record at index {i} must be an object")
            continue
        mapped = _to_bioeval_item(rec, i, benchmark, strict=strict)
        by_component.setdefault(mapped["component"], []).append(mapped["item"])

    results = []
    for component, rows in sorted(by_component.items()):
        results.append(
            {
                "component": component,
                "num_tasks": len(rows),
                "results": rows,
            }
        )

    return {
        "metadata": {
            "model": model,
            "components": sorted(by_component.keys()),
            "data_tier": "external",
            "split": split,
            "timestamp": datetime.now().isoformat(),
            "bioeval_version": __version__,
            "source_benchmark": benchmark,
            "adapter_version": ADAPTER_VERSION,
            "adapter_schema": "bioeval-canonical-result-v1",
        },
        "summary": _summarize(by_component),
        "results": results,
    }


def convert_benchmark_file(
    input_path: str,
    benchmark: str,
    model: str = "external-model",
    output_path: str | None = None,
    split: str = "all",
    strict: bool = False,
) -> dict:
    """Convert benchmark JSON file and optionally write output."""
    with open(input_path, encoding="utf-8") as f:
        payload = json.load(f)

    converted = convert_benchmark_payload(
        payload=payload,
        benchmark=benchmark,
        model=model,
        split=split,
        strict=strict,
    )
    converted["metadata"]["source_file"] = str(input_path)

    if output_path is not None:
        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(converted, f, indent=2, default=str)
        converted["metadata"]["output_file"] = str(out_path)

    return converted
