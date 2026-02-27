"""Human validation pack generation for judge reliability studies."""

from __future__ import annotations

import csv
import json
import random
from pathlib import Path

from bioeval.reporting.agreement import analyze_agreement
from bioeval.scoring.normalizer import normalize_result


def _collect_candidates(result_data: dict) -> list[dict]:
    """Collect tasks that have both automated and judge scores."""
    rows = []
    for comp_result in result_data.get("results", []):
        component = comp_result.get("component", "unknown")
        for r in comp_result.get("results", []):
            if not isinstance(r, dict):
                continue
            judge = r.get("judge_scores", {})
            if not isinstance(judge, dict) or "error" in judge:
                continue
            judge_score = judge.get("overall_score")
            if not isinstance(judge_score, (int, float)):
                continue

            task_type = r.get("task_type", r.get("adversarial_type", ""))
            try:
                auto_score = normalize_result(r, component, task_type).score
            except Exception:
                auto_score = None

            rows.append({
                "task_id": r.get("task_id", r.get("dialogue_id", "")),
                "component": component,
                "task_type": task_type,
                "task_prompt": r.get("prompt", ""),
                "model_response": r.get("response", ""),
                "auto_score": auto_score,
                "judge_score": float(judge_score),
            })
    return rows


def generate_judge_validation_pack(
    result_file: str,
    output_dir: str = "results/validation",
    sample_size: int = 50,
    seed: int = 42,
) -> dict:
    """Generate a CSV/JSON pack for human-vs-judge validation."""
    with open(result_file) as f:
        data = json.load(f)

    candidates = _collect_candidates(data)
    if not candidates:
        return {"error": "No valid judge-scored tasks found in result file."}

    rng = random.Random(seed)
    n = min(max(1, sample_size), len(candidates))
    sampled = rng.sample(candidates, n)

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    stem = Path(result_file).stem
    csv_path = out_dir / f"{stem}_human_panel_sample.csv"
    summary_path = out_dir / f"{stem}_judge_validation_summary.json"

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "task_id",
                "component",
                "task_type",
                "task_prompt",
                "model_response",
                "auto_score",
                "judge_score",
                "human_score",
                "human_notes",
            ],
        )
        writer.writeheader()
        for row in sampled:
            writer.writerow({
                **row,
                "human_score": "",
                "human_notes": "",
            })

    agreement = analyze_agreement(result_file)
    summary = {
        "result_file": str(result_file),
        "output_dir": str(out_dir),
        "sample_size": n,
        "seed": seed,
        "n_candidates": len(candidates),
        "csv_path": str(csv_path),
        "agreement_snapshot": agreement,
    }
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)

    return {
        "ok": True,
        "sample_size": n,
        "csv_path": str(csv_path),
        "summary_path": str(summary_path),
    }

