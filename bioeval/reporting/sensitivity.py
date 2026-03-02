"""Weight sensitivity analysis for BioEval scoring formulas.

Measures how sensitive composite scores are to weight choices by
perturbing each weight vector and re-computing scores from existing
sub-scores.  No API calls required -- purely arithmetic re-computation.
"""

from __future__ import annotations

import json
import math
import random
from typing import Optional


# ── Weight Registry ──────────────────────────────────────────────────
# Canonical weight vectors extracted from scoring code.
# Keys: (component, task_type) or (component, "composite").

WEIGHT_REGISTRY: dict[tuple[str, str], dict[str, float]] = {
    ("protoreason", "troubleshooting"): {
        "cause_coverage": 0.5,
        "diagnostic_coverage": 0.3,
        "has_ranking": 0.2,
    },
    ("causalbio", "knockout_prediction"): {
        "effect_correct": 0.6,
        "reasoning_score": 0.4,
    },
    ("causalbio", "epistasis"): {
        "interaction_correct": 0.6,
        "mechanism_score": 0.4,
    },
    ("debate", "composite"): {
        "accuracy": 0.25,
        "reasoning": 0.30,
        "correction": 0.20,
        "dissent": 0.15,
        "efficiency": 0.10,
    },
}


# ── Perturbation Engine ──────────────────────────────────────────────


def perturb_weights(
    weights: dict[str, float],
    delta: float = 0.1,
    n_samples: int = 1000,
    seed: int = 42,
) -> list[dict[str, float]]:
    """Generate perturbation samples of a weight vector.

    Each weight is jittered by Uniform(-delta, +delta), then the
    vector is clamped to non-negative and renormalized to sum to 1.0.

    Args:
        weights: Original weight vector {name: value}.
        delta: Max jitter per weight (default +-10%).
        n_samples: Number of perturbation samples.
        seed: Random seed for reproducibility.

    Returns:
        List of perturbed weight dicts, each summing to 1.0.
    """
    rng = random.Random(seed)
    keys = sorted(weights.keys())
    base = [weights[k] for k in keys]
    samples = []

    for _ in range(n_samples):
        perturbed = [max(0.0, w + rng.uniform(-delta, delta)) for w in base]
        total = sum(perturbed)
        if total <= 0:
            # Fallback to equal weights if all became zero
            perturbed = [1.0 / len(keys)] * len(keys)
            total = 1.0
        normalized = [w / total for w in perturbed]
        samples.append(dict(zip(keys, normalized)))

    return samples


def _compute_score(
    subscores: dict[str, float],
    weights: dict[str, float],
) -> float:
    """Compute weighted sum from sub-scores and weights."""
    return sum(weights.get(k, 0.0) * subscores.get(k, 0.0) for k in weights)


def sensitivity_analysis(
    result_file: str,
    delta: float = 0.1,
    n_samples: int = 1000,
    seed: int = 42,
) -> dict:
    """Run weight sensitivity analysis on a result file.

    For each component/task_type in WEIGHT_REGISTRY, perturb the
    weight vector and re-compute scores from saved sub-scores.

    Args:
        result_file: Path to BioEval result JSON.
        delta: Max weight perturbation (default +-10%).
        n_samples: Number of perturbation samples.
        seed: Random seed.

    Returns:
        Dict with per-component sensitivity metrics:
        {component_tasktype: {original_mean, perturbed_mean, std,
         max_swing, min_score, max_score}}
    """
    with open(result_file) as f:
        data = json.load(f)

    results = data.get("results", [])
    analysis = {}

    for (comp, task_type), orig_weights in WEIGHT_REGISTRY.items():
        # Find matching component results
        comp_result = None
        for r in results:
            if r.get("component") == comp:
                comp_result = r
                break
        if comp_result is None:
            continue

        # Extract sub-scores for each task
        task_subscores = []
        for task_r in comp_result.get("results", []):
            if not isinstance(task_r, dict) or "error" in task_r:
                continue
            scores = task_r.get("scores", {})
            subscores = {}

            if comp == "debate" and task_type == "composite":
                subscores = {
                    "accuracy": scores.get("outcome_accuracy", 0.0),
                    "reasoning": scores.get("reasoning_quality", 0.0),
                    "correction": ((1.0 - scores.get("sycophancy_score", 0.0)) * scores.get("correction_rate", 0.0)),
                    "dissent": scores.get("dissent_preservation", 0.0),
                    "efficiency": min(
                        1.0,
                        1000.0 / max(1, scores.get("total_tokens", 1000)),
                    ),
                }
            else:
                # Generic: use weight keys to look up sub-scores
                for key in orig_weights:
                    subscores[key] = float(scores.get(key, 0.0))

            if subscores:
                task_subscores.append(subscores)

        if not task_subscores:
            continue

        # Compute original scores
        orig_scores = [_compute_score(ss, orig_weights) for ss in task_subscores]
        orig_mean = sum(orig_scores) / len(orig_scores)

        # Perturb and re-score
        perturbations = perturb_weights(orig_weights, delta, n_samples, seed)
        perturbed_means = []
        for pw in perturbations:
            p_scores = [_compute_score(ss, pw) for ss in task_subscores]
            perturbed_means.append(sum(p_scores) / len(p_scores))

        p_mean = sum(perturbed_means) / len(perturbed_means)
        p_std = math.sqrt(sum((m - p_mean) ** 2 for m in perturbed_means) / len(perturbed_means))
        p_min = min(perturbed_means)
        p_max = max(perturbed_means)

        key = f"{comp}_{task_type}"
        analysis[key] = {
            "component": comp,
            "task_type": task_type,
            "n_tasks": len(task_subscores),
            "original_weights": orig_weights,
            "original_mean": round(orig_mean, 4),
            "perturbed_mean": round(p_mean, 4),
            "perturbed_std": round(p_std, 4),
            "max_swing": round(p_max - p_min, 4),
            "min_score": round(p_min, 4),
            "max_score": round(p_max, 4),
            "delta": delta,
            "n_samples": n_samples,
        }

    return analysis


def print_sensitivity(analysis: dict) -> None:
    """Print a human-readable sensitivity analysis report."""
    if not analysis:
        print("No weight vectors found in results.")
        return

    print(f"\n{'=' * 70}")
    print("WEIGHT SENSITIVITY ANALYSIS")
    print(f"{'=' * 70}")
    print(f"  {'Component':30s} {'Original':>8s} {'Mean':>8s}" f" {'Std':>6s} {'Swing':>7s} {'Range':>15s}")
    print(f"{'-' * 70}")

    for key, info in sorted(analysis.items()):
        label = f"{info['component']}/{info['task_type']}"
        print(
            f"  {label:30s} {info['original_mean']:8.4f}"
            f" {info['perturbed_mean']:8.4f}"
            f" {info['perturbed_std']:6.4f}"
            f" {info['max_swing']:7.4f}"
            f" [{info['min_score']:.4f},{info['max_score']:.4f}]"
        )

    print(f"{'-' * 70}")
    print("  Interpretation: Swing < 0.05 = stable, " "0.05-0.10 = moderate, > 0.10 = sensitive")
    print()
