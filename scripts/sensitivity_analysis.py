"""
Sensitivity analysis for BioEval scoring parameters.

Quantifies how sensitive the overall benchmark results are to:
1. CausalBio combined_score weighting (direction ±10%)
2. Pass threshold variation (0.4 / 0.5 / 0.6)
3. Per-component vs per-task overall aggregation

Usage:
    python scripts/sensitivity_analysis.py results/run1.json
    python scripts/sensitivity_analysis.py results/run1.json --output sensitivity_report.json
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bioeval.reporting.analysis import load_and_normalize, compute_aggregates
from bioeval.scoring.normalizer import NormalizedScore

# ── 1. Pass-threshold sensitivity ──────────────────────────────────────────


def threshold_sensitivity(
    normalized: list[NormalizedScore],
    thresholds: list[float] = None,
) -> list[dict]:
    """Compute pass-rate at various thresholds."""
    if thresholds is None:
        thresholds = [0.3, 0.4, 0.5, 0.6, 0.7]

    results = []
    for t in thresholds:
        n_pass = sum(1 for ns in normalized if ns.score >= t)
        results.append(
            {
                "threshold": t,
                "n_passed": n_pass,
                "n_total": len(normalized),
                "pass_rate": round(n_pass / len(normalized), 4) if normalized else 0.0,
            }
        )
    return results


# ── 2. CausalBio weight perturbation ──────────────────────────────────────


def causalbio_weight_sensitivity(
    normalized: list[NormalizedScore],
    perturbations: list[float] = None,
) -> list[dict]:
    """Simulate CausalBio score changes under weight perturbation.

    The default CausalBio knockout formula is:
        combined = 0.60 * direction + 0.30 * mention + 0.05 * mech + 0.05 * pheno

    We perturb the direction weight by ±delta and redistribute equally
    among the other weights, then recompute the component mean.
    """
    if perturbations is None:
        perturbations = [-0.10, -0.05, 0.0, 0.05, 0.10]

    causal_tasks = [ns for ns in normalized if ns.component == "causalbio"]
    if not causal_tasks:
        return [{"perturbation": p, "mean": None, "n": 0} for p in perturbations]

    results = []
    for delta in perturbations:
        perturbed_scores = []
        for ns in causal_tasks:
            raw = ns.raw
            # Only perturb tasks that have the relevant subscores
            dir_acc = raw.get("direction_accuracy", ns.subscores.get("direction_accuracy"))
            mention = raw.get("gene_mention_rate", ns.subscores.get("gene_mention_rate"))

            if dir_acc is not None and mention is not None:
                dir_acc = float(dir_acc)
                mention = float(mention)
                mech = float(raw.get("mechanism_mentioned", 0))
                pheno = float(raw.get("phenotype_mentioned", 0))

                w_dir = 0.60 + delta
                remaining = 1.0 - w_dir - 0.10  # keep mech+pheno at 0.10
                w_mention = max(0.0, remaining)
                score = w_dir * dir_acc + w_mention * mention + 0.05 * mech + 0.05 * pheno
                perturbed_scores.append(max(0.0, min(1.0, score)))
            else:
                # Can't perturb; use original score
                perturbed_scores.append(ns.score)

        mean = sum(perturbed_scores) / len(perturbed_scores) if perturbed_scores else 0.0
        results.append(
            {
                "perturbation": delta,
                "direction_weight": round(0.60 + delta, 2),
                "mean": round(mean, 4),
                "n": len(perturbed_scores),
            }
        )
    return results


# ── 3. Aggregation method comparison ──────────────────────────────────────


def aggregation_comparison(
    normalized: list[NormalizedScore],
    by_component: dict[str, list[NormalizedScore]],
) -> dict:
    """Compare per-task vs per-component aggregation."""
    # Per-task uniform
    task_scores = [ns.score for ns in normalized]
    task_mean = sum(task_scores) / len(task_scores) if task_scores else 0.0

    # Per-component equal
    comp_means = []
    comp_detail = {}
    for comp, ns_list in by_component.items():
        if ns_list:
            m = sum(ns.score for ns in ns_list) / len(ns_list)
            comp_means.append(m)
            comp_detail[comp] = {"mean": round(m, 4), "n": len(ns_list)}

    pc_mean = sum(comp_means) / len(comp_means) if comp_means else 0.0

    return {
        "per_task_mean": round(task_mean, 4),
        "per_component_mean": round(pc_mean, 4),
        "difference": round(task_mean - pc_mean, 4),
        "n_components": len(comp_means),
        "components": comp_detail,
    }


# ── 4. Score stability (std across components) ───────────────────────────


def score_stability(by_component: dict[str, list[NormalizedScore]]) -> dict:
    """Measure score dispersion across components."""
    comp_means = {}
    for comp, ns_list in by_component.items():
        if ns_list:
            comp_means[comp] = sum(ns.score for ns in ns_list) / len(ns_list)

    if len(comp_means) < 2:
        return {"cv": 0.0, "range": 0.0, "components": comp_means}

    vals = list(comp_means.values())
    mean = sum(vals) / len(vals)
    std = math.sqrt(sum((v - mean) ** 2 for v in vals) / (len(vals) - 1))
    cv = std / mean if mean > 0 else 0.0

    return {
        "mean": round(mean, 4),
        "std": round(std, 4),
        "cv": round(cv, 4),
        "range": round(max(vals) - min(vals), 4),
        "min_component": min(comp_means, key=comp_means.get),
        "max_component": max(comp_means, key=comp_means.get),
        "components": {k: round(v, 4) for k, v in comp_means.items()},
    }


# ── Main ──────────────────────────────────────────────────────────────────


def run_sensitivity(result_path: str) -> dict:
    """Run full sensitivity analysis on a result file."""
    loaded = load_and_normalize(result_path)
    all_ns = loaded["normalized"]
    by_comp = loaded["by_component"]

    return {
        "result_file": result_path,
        "n_tasks": len(all_ns),
        "threshold_sensitivity": threshold_sensitivity(all_ns),
        "causalbio_weight_sensitivity": causalbio_weight_sensitivity(all_ns),
        "aggregation_comparison": aggregation_comparison(all_ns, by_comp),
        "score_stability": score_stability(by_comp),
    }


def main():
    parser = argparse.ArgumentParser(description="BioEval sensitivity analysis")
    parser.add_argument("result_path", help="Path to result JSON file")
    parser.add_argument("--output", "-o", help="Output JSON file (default: stdout)")
    args = parser.parse_args()

    report = run_sensitivity(args.result_path)

    output = json.dumps(report, indent=2)
    if args.output:
        Path(args.output).write_text(output)
        print(f"Report written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
