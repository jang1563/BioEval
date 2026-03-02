#!/usr/bin/env python3
"""Extract per-component scores from BioEval result files."""

import json
import sys


def extract_primary_score(component, task_result):
    """Extract the canonical primary score for a task result."""
    s = task_result.get("scores", {})
    if component == "protoreason":
        for key in ["adjacent_pair_accuracy", "recall", "numerical_accuracy", "cause_coverage"]:
            if key in s and s[key] is not None:
                return float(s[key])
    elif component == "causalbio":
        if "effect_correct" in s:
            return 1.0 if s["effect_correct"] else 0.0
        if "combined_score" in s and s["combined_score"] is not None:
            return float(s["combined_score"])
        if "mechanism_score" in s and s["mechanism_score"] is not None:
            return float(s["mechanism_score"])
    elif component == "designcheck":
        if "f1" in s:
            return float(s["f1"])
        if "composite_score" in s:
            return float(s["composite_score"])
        return None
    elif component == "adversarial":
        return float(s["score"]) if "score" in s else None
    elif component == "multiturn":
        return float(s["overall_score"]) if "overall_score" in s else None
    elif component == "calibration":
        if "calibration_error" in s and s["calibration_error"] is not None:
            return 1.0 - abs(float(s["calibration_error"]))
    elif component in ("biosafety", "datainterp"):
        return float(task_result["score"]) if "score" in task_result else None
    elif component == "debate":
        return float(s["composite_score"]) if "composite_score" in s else None
    return None


def analyze_results(filepath):
    """Analyze a BioEval result file."""
    with open(filepath) as f:
        data = json.load(f)

    meta = data.get("metadata", {})
    print(f"Model: {meta.get('model')}  |  Seed: {meta.get('seed')}  |  Version: {meta.get('bioeval_version')}")
    print(f"Elapsed: {meta.get('elapsed_seconds', 0):.0f}s  |  Tasks: {data.get('summary', {}).get('total_tasks')}")
    print()

    print("Per-Component Scores:")
    print("-" * 75)
    print(f"  {'Component':15s}  {'Scored':>8s}  {'Mean':>8s}  {'Min':>8s}  {'Max':>8s}  {'Primary Metric'}")
    print("-" * 75)

    all_scores = []
    comp_order = []

    metric_names = {
        "protoreason": "apa/recall/num_acc/cause_cov",
        "causalbio": "effect_correct/combined/mechanism",
        "designcheck": "F1",
        "adversarial": "score",
        "multiturn": "overall_score",
        "calibration": "1 - calibration_error",
        "biosafety": "score (top-level)",
        "datainterp": "score (top-level)",
        "debate": "composite_score",
    }

    for comp_result in data.get("results", []):
        comp = comp_result.get("component", "unknown")
        results = comp_result.get("results", [])
        n_tasks = comp_result.get("num_tasks", len(results))

        scores = []
        errors = []
        for r in results:
            if isinstance(r, dict):
                if "error" in r:
                    errors.append(r.get("task_id", "?"))
                    continue
                score = extract_primary_score(comp, r)
                if score is not None:
                    scores.append(score)

        mean_s = sum(scores) / len(scores) if scores else 0
        comp_order.append((comp, mean_s, len(scores), n_tasks, scores))
        all_scores.extend(scores)

    # Sort by mean descending
    for comp, mean_s, n_scored, n_tasks, scores in sorted(comp_order, key=lambda x: x[1], reverse=True):
        mn = min(scores) if scores else 0
        mx = max(scores) if scores else 0
        metric = metric_names.get(comp, "?")
        print(f"  {comp:15s}  {n_scored:3d}/{n_tasks:<3d}   {mean_s:7.3f}  {mn:7.3f}  {mx:7.3f}  {metric}")

    print("-" * 75)
    overall = sum(all_scores) / len(all_scores) if all_scores else 0
    expected_total = data.get("summary", {}).get("total_tasks")
    if not isinstance(expected_total, int) or expected_total <= 0:
        expected_total = sum(cr.get("num_tasks", len(cr.get("results", []))) for cr in data.get("results", []))
    print(f"  {'WEIGHTED MEAN':15s}  {len(all_scores):3d}/{expected_total:<3d}   {overall:7.3f}")
    print()

    # Show errors
    for comp_result in data.get("results", []):
        comp = comp_result.get("component", "unknown")
        for r in comp_result.get("results", []):
            if isinstance(r, dict) and "error" in r:
                print(f"  ERROR [{comp}] {r.get('task_id', '?')}: {r.get('error', '')[:80]}")

    return data


if __name__ == "__main__":
    filepath = sys.argv[1] if len(sys.argv) > 1 else "results/phase2_claude_sonnet4_seed42.json"
    analyze_results(filepath)
