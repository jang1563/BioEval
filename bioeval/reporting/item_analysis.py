"""
Item-level difficulty and discrimination analysis (IRT-lite).

Provides per-task quality metrics when results from multiple models are available:
- Item difficulty: proportion of models that pass the task (p-value)
- Item discrimination: point-biserial correlation between task score and total score
- Floor/ceiling detection: tasks that all/no models pass
- Difficulty distribution: histogram of p-values for benchmark balance

These metrics are standard in psychometrics (cf. Classical Test Theory)
and help identify uninformative tasks.
"""

import math
from collections import defaultdict
from pathlib import Path

from bioeval.reporting.analysis import load_and_normalize
from bioeval.scoring.normalizer import NormalizedScore

# =============================================================================
# ITEM DIFFICULTY (CLASSICAL P-VALUE)
# =============================================================================


def compute_item_difficulty(multi_model_results: list[dict]) -> dict:
    """Compute per-task difficulty from multiple model result files.

    Args:
        multi_model_results: List of dicts from load_and_normalize(),
            each representing one model's results.

    Returns:
        {
            task_id: {
                "p_value": float,   # proportion passing (0=hardest, 1=easiest)
                "mean_score": float,
                "std_score": float,
                "n_models": int,
                "component": str,
                "task_type": str,
            }
        }
    """
    # Collect scores per task across models
    task_scores: dict[str, list[float]] = defaultdict(list)
    task_passed: dict[str, list[bool]] = defaultdict(list)
    task_meta: dict[str, dict] = {}

    for model_data in multi_model_results:
        for ns in model_data["normalized"]:
            tid = ns.task_id
            task_scores[tid].append(ns.score)
            task_passed[tid].append(ns.passed)
            if tid not in task_meta:
                task_meta[tid] = {
                    "component": ns.component,
                    "task_type": ns.task_type,
                }

    items = {}
    for tid in task_scores:
        scores = task_scores[tid]
        passed = task_passed[tid]
        n = len(scores)
        mean = sum(scores) / n
        var = sum((s - mean) ** 2 for s in scores) / max(1, n - 1)

        items[tid] = {
            "p_value": round(sum(passed) / n, 4),
            "mean_score": round(mean, 4),
            "std_score": round(math.sqrt(var), 4),
            "n_models": n,
            **task_meta.get(tid, {}),
        }

    return items


# =============================================================================
# ITEM DISCRIMINATION (POINT-BISERIAL CORRELATION)
# =============================================================================


def compute_item_discrimination(multi_model_results: list[dict]) -> dict:
    """Compute point-biserial correlation for each task.

    Measures how well a single task discriminates between high- and
    low-performing models. Higher discrimination = more informative task.

    Point-biserial r = (M1 - M0) / S * sqrt(p * q)
    where M1 = mean total of models that passed,
          M0 = mean total of models that failed,
          S = std of all totals, p = proportion passing, q = 1 - p.
    """
    # Build model × task matrix
    model_task_scores: dict[int, dict[str, float]] = {}
    model_task_passed: dict[int, dict[str, bool]] = {}
    all_task_ids: set[str] = set()

    for i, model_data in enumerate(multi_model_results):
        model_task_scores[i] = {}
        model_task_passed[i] = {}
        for ns in model_data["normalized"]:
            model_task_scores[i][ns.task_id] = ns.score
            model_task_passed[i][ns.task_id] = ns.passed
            all_task_ids.add(ns.task_id)

    n_models = len(multi_model_results)
    if n_models < 3:
        return {tid: {"discrimination": None, "reason": "need >=3 models"} for tid in all_task_ids}

    # Compute total score per model (sum of all task scores)
    model_totals = {}
    for i in range(n_models):
        model_totals[i] = sum(model_task_scores[i].values())

    total_mean = sum(model_totals.values()) / n_models
    total_var = sum((t - total_mean) ** 2 for t in model_totals.values()) / max(1, n_models - 1)
    total_std = math.sqrt(total_var)

    discrimination = {}
    for tid in sorted(all_task_ids):
        # Models that attempted this task
        attempted = [i for i in range(n_models) if tid in model_task_passed[i]]
        if len(attempted) < 3:
            discrimination[tid] = {"discrimination": None, "reason": "insufficient data"}
            continue

        passers = [i for i in attempted if model_task_passed[i][tid]]
        failers = [i for i in attempted if not model_task_passed[i][tid]]

        p = len(passers) / len(attempted)
        q = 1 - p

        if p == 0 or p == 1 or total_std == 0:
            # No variance → discrimination undefined
            discrimination[tid] = {
                "discrimination": 0.0,
                "reason": "floor" if p == 0 else "ceiling" if p == 1 else "no_variance",
            }
            continue

        mean_pass = sum(model_totals[i] for i in passers) / len(passers)
        mean_fail = sum(model_totals[i] for i in failers) / len(failers)

        rpb = ((mean_pass - mean_fail) / total_std) * math.sqrt(p * q)
        discrimination[tid] = {
            "discrimination": round(rpb, 4),
        }

    return discrimination


# =============================================================================
# COMBINED ITEM ANALYSIS
# =============================================================================


def item_analysis(result_paths: list[str]) -> dict:
    """Full item analysis from multiple model result files.

    Returns:
        {
            "n_models": int,
            "n_tasks": int,
            "items": {task_id: {difficulty + discrimination metrics}},
            "summary": {
                "floor_tasks": [...],     # p=0, all fail
                "ceiling_tasks": [...],   # p=1, all pass
                "difficulty_histogram": {bin: count},
                "discrimination_stats": {mean, std, min, max},
                "low_discrimination": [...],  # r < 0.2
            },
            "by_component": {comp: {difficulty_mean, discrimination_mean}},
        }
    """
    # Load all results
    multi = [load_and_normalize(p) for p in result_paths]

    difficulty = compute_item_difficulty(multi)
    discrimination = compute_item_discrimination(multi)

    # Merge
    items = {}
    for tid in difficulty:
        items[tid] = {**difficulty[tid]}
        if tid in discrimination:
            items[tid].update(discrimination[tid])

    # Summary statistics
    p_values = [v["p_value"] for v in items.values()]
    disc_values = [v["discrimination"] for v in items.values() if v.get("discrimination") is not None]

    floor_tasks = [tid for tid, v in items.items() if v["p_value"] == 0.0]
    ceiling_tasks = [tid for tid, v in items.items() if v["p_value"] == 1.0]
    low_disc = [tid for tid, v in items.items() if v.get("discrimination") is not None and v["discrimination"] < 0.2]

    # Difficulty histogram (5 bins: [0,0.2), [0.2,0.4), ... [0.8,1.0])
    bins = {"0.0-0.2": 0, "0.2-0.4": 0, "0.4-0.6": 0, "0.6-0.8": 0, "0.8-1.0": 0}
    for p in p_values:
        if p < 0.2:
            bins["0.0-0.2"] += 1
        elif p < 0.4:
            bins["0.2-0.4"] += 1
        elif p < 0.6:
            bins["0.4-0.6"] += 1
        elif p < 0.8:
            bins["0.6-0.8"] += 1
        else:
            bins["0.8-1.0"] += 1

    disc_stats = {}
    if disc_values:
        disc_mean = sum(disc_values) / len(disc_values)
        disc_var = sum((d - disc_mean) ** 2 for d in disc_values) / max(1, len(disc_values) - 1)
        disc_stats = {
            "mean": round(disc_mean, 4),
            "std": round(math.sqrt(disc_var), 4),
            "min": round(min(disc_values), 4),
            "max": round(max(disc_values), 4),
            "n": len(disc_values),
        }

    # Per-component aggregates
    by_component: dict[str, dict[str, list[float]]] = defaultdict(lambda: {"p": [], "d": []})
    for tid, v in items.items():
        comp = v.get("component", "unknown")
        by_component[comp]["p"].append(v["p_value"])
        if v.get("discrimination") is not None:
            by_component[comp]["d"].append(v["discrimination"])

    comp_summary = {}
    for comp, vals in by_component.items():
        comp_summary[comp] = {
            "n_tasks": len(vals["p"]),
            "difficulty_mean": round(sum(vals["p"]) / len(vals["p"]), 4) if vals["p"] else 0,
            "discrimination_mean": round(sum(vals["d"]) / len(vals["d"]), 4) if vals["d"] else None,
        }

    return {
        "n_models": len(multi),
        "n_tasks": len(items),
        "items": items,
        "summary": {
            "floor_tasks": floor_tasks,
            "ceiling_tasks": ceiling_tasks,
            "n_floor": len(floor_tasks),
            "n_ceiling": len(ceiling_tasks),
            "difficulty_histogram": bins,
            "discrimination_stats": disc_stats,
            "low_discrimination": low_disc,
            "n_low_discrimination": len(low_disc),
        },
        "by_component": comp_summary,
    }


# =============================================================================
# SINGLE-MODEL ITEM ANALYSIS (difficulty proxy from scores)
# =============================================================================


def single_model_item_analysis(result_path: str) -> dict:
    """Item analysis from a single model's results.

    Without multiple models, we can't compute true discrimination.
    Instead, we provide score-based difficulty and flag extremes.
    """
    loaded = load_and_normalize(result_path)
    all_ns = loaded["normalized"]

    items = {}
    by_component: dict[str, list[float]] = defaultdict(list)

    for ns in all_ns:
        items[ns.task_id] = {
            "score": ns.score,
            "passed": ns.passed,
            "component": ns.component,
            "task_type": ns.task_type,
        }
        by_component[ns.component].append(ns.score)

    scores = [ns.score for ns in all_ns]
    if not scores:
        return {"error": "No results to analyze"}

    mean_score = sum(scores) / len(scores)

    # Flag extremes
    perfect = [tid for tid, v in items.items() if v["score"] >= 0.99]
    zero = [tid for tid, v in items.items() if v["score"] <= 0.01]

    # Difficulty distribution
    bins = {"0.0-0.2": 0, "0.2-0.4": 0, "0.4-0.6": 0, "0.6-0.8": 0, "0.8-1.0": 0}
    for s in scores:
        if s < 0.2:
            bins["0.0-0.2"] += 1
        elif s < 0.4:
            bins["0.2-0.4"] += 1
        elif s < 0.6:
            bins["0.4-0.6"] += 1
        elif s < 0.8:
            bins["0.6-0.8"] += 1
        else:
            bins["0.8-1.0"] += 1

    comp_summary = {}
    for comp, comp_scores in by_component.items():
        comp_summary[comp] = {
            "n_tasks": len(comp_scores),
            "mean_score": round(sum(comp_scores) / len(comp_scores), 4),
        }

    return {
        "n_tasks": len(items),
        "mean_score": round(mean_score, 4),
        "items": items,
        "summary": {
            "n_perfect": len(perfect),
            "perfect_tasks": perfect,
            "n_zero": len(zero),
            "zero_tasks": zero,
            "score_histogram": bins,
        },
        "by_component": comp_summary,
    }


# =============================================================================
# TEXT OUTPUT
# =============================================================================


def print_item_analysis(result_paths: list[str]):
    """Print formatted item analysis."""
    if len(result_paths) == 1:
        analysis = single_model_item_analysis(result_paths[0])
        print(f"\n{'=' * 60}")
        print(f"Item Analysis (single model)")
        print(f"{'=' * 60}")
        print(f"Tasks: {analysis['n_tasks']}, Mean score: {analysis['mean_score']:.3f}")

        s = analysis["summary"]
        print(f"Perfect scores: {s['n_perfect']}, Zero scores: {s['n_zero']}")
        print(f"\nScore distribution:")
        for bin_label, count in s["score_histogram"].items():
            bar = "#" * count
            print(f"  {bin_label}: {count:>3} {bar}")

        print(f"\nPer-component:")
        for comp, info in sorted(analysis["by_component"].items()):
            print(f"  {comp:<15} n={info['n_tasks']:>3}  mean={info['mean_score']:.3f}")
        return analysis

    analysis = item_analysis(result_paths)
    print(f"\n{'=' * 60}")
    print(f"Item Analysis ({analysis['n_models']} models, {analysis['n_tasks']} tasks)")
    print(f"{'=' * 60}")

    s = analysis["summary"]
    print(f"\nFloor tasks (all fail): {s['n_floor']}")
    for tid in s["floor_tasks"][:10]:
        print(f"  - {tid}")

    print(f"Ceiling tasks (all pass): {s['n_ceiling']}")
    for tid in s["ceiling_tasks"][:10]:
        print(f"  - {tid}")

    print(f"\nDifficulty distribution (p-value):")
    for bin_label, count in s["difficulty_histogram"].items():
        bar = "#" * count
        print(f"  {bin_label}: {count:>3} {bar}")

    if s["discrimination_stats"]:
        ds = s["discrimination_stats"]
        print(f"\nDiscrimination: mean={ds['mean']:.3f}, std={ds['std']:.3f}, " f"range=[{ds['min']:.3f}, {ds['max']:.3f}]")

    print(f"Low discrimination (r < 0.2): {s['n_low_discrimination']}")

    print(f"\nPer-component:")
    print(f"{'Component':<15} {'N':>4} {'Diff':>7} {'Disc':>7}")
    print(f"{'─' * 35}")
    for comp, info in sorted(analysis["by_component"].items()):
        disc_str = f"{info['discrimination_mean']:.3f}" if info["discrimination_mean"] is not None else "  N/A"
        print(f"  {comp:<13} {info['n_tasks']:>4} {info['difficulty_mean']:>7.3f} {disc_str:>7}")

    return analysis
