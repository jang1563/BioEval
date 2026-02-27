"""
Scoring feedback analysis for BioEval.

Analyzes evaluation results to detect scoring issues and suggest improvements:
- Ceiling/floor effects (scores clustering at 0 or 1)
- Component imbalance (some components much harder than others)
- Low discrimination (too many tasks with similar scores)
- Suspicious patterns (perfect scores on adversarial tasks, etc.)

Usage:
    bioeval feedback results/synthetic_good.json
"""

import json
import math
from collections import defaultdict

from bioeval.scoring.normalizer import normalize_result


def analyze_scoring_feedback(result_path: str) -> dict:
    """Analyze results and generate scoring improvement feedback.

    Args:
        result_path: Path to a result JSON file

    Returns:
        Dict with diagnostics, warnings, and suggestions.
    """
    with open(result_path) as f:
        data = json.load(f)

    diagnostics = []
    warnings = []
    suggestions = []

    # Collect normalized scores by component
    by_component = defaultdict(list)
    all_scores = []

    for comp_result in data.get("results", []):
        comp = comp_result.get("component", "unknown")
        for r in comp_result.get("results", []):
            if not isinstance(r, dict) or ("error" in r and "score" not in r):
                continue
            task_type = r.get("task_type", r.get("adversarial_type", ""))
            try:
                ns = normalize_result(r, comp, task_type)
                by_component[comp].append(
                    {
                        "task_id": r.get("task_id", r.get("dialogue_id", "")),
                        "task_type": task_type,
                        "score": ns.score,
                        "passed": ns.passed,
                    }
                )
                all_scores.append(ns.score)
            except Exception:
                pass

    if not all_scores:
        return {"error": "No scoreable results found"}

    # --- 1. Overall distribution diagnostics ---
    mean = sum(all_scores) / len(all_scores)
    variance = sum((s - mean) ** 2 for s in all_scores) / len(all_scores)
    std = math.sqrt(variance)
    n_perfect = sum(1 for s in all_scores if s >= 0.99)
    n_zero = sum(1 for s in all_scores if s <= 0.01)
    pass_rate = sum(1 for s in all_scores if s >= 0.5) / len(all_scores)

    diagnostics.append(
        {
            "type": "overall_distribution",
            "n": len(all_scores),
            "mean": round(mean, 4),
            "std": round(std, 4),
            "pass_rate": round(pass_rate, 4),
            "n_perfect": n_perfect,
            "n_zero": n_zero,
            "pct_perfect": round(n_perfect / len(all_scores) * 100, 1),
            "pct_zero": round(n_zero / len(all_scores) * 100, 1),
        }
    )

    # --- 2. Ceiling effect detection ---
    if n_perfect / len(all_scores) > 0.4:
        warnings.append(
            {
                "severity": "high",
                "type": "ceiling_effect",
                "message": f"{n_perfect}/{len(all_scores)} ({n_perfect/len(all_scores):.0%}) tasks scored perfectly. "
                "Scorer may be too lenient.",
            }
        )
        suggestions.append(
            "Consider tightening scoring criteria or adding harder tasks. "
            "NeurIPS reviewers expect meaningful score separation."
        )

    # --- 3. Floor effect detection ---
    if n_zero / len(all_scores) > 0.3:
        warnings.append(
            {
                "severity": "high",
                "type": "floor_effect",
                "message": f"{n_zero}/{len(all_scores)} ({n_zero/len(all_scores):.0%}) tasks scored zero. "
                "Scorer may be too strict or responses are genuinely poor.",
            }
        )
        suggestions.append(
            "Review zero-scoring tasks manually. If responses contain partial knowledge, "
            "consider graduated scoring instead of binary pass/fail."
        )

    # --- 4. Low variance detection ---
    if std < 0.1 and len(all_scores) > 10:
        warnings.append(
            {
                "severity": "medium",
                "type": "low_variance",
                "message": f"Score std={std:.3f} is very low. Most tasks score similarly (~{mean:.2f}). "
                "The benchmark may not discriminate well between models.",
            }
        )
        suggestions.append(
            "Add tasks of varying difficulty levels. "
            "Item analysis (bioeval item-analysis) can identify tasks needing adjustment."
        )

    # --- 5. Component imbalance ---
    comp_means = {}
    for comp, scores in by_component.items():
        comp_scores = [s["score"] for s in scores]
        comp_means[comp] = sum(comp_scores) / len(comp_scores) if comp_scores else 0

    if comp_means:
        max_mean = max(comp_means.values())
        min_mean = min(comp_means.values())
        gap = max_mean - min_mean

        diagnostics.append(
            {
                "type": "component_balance",
                "means": {k: round(v, 4) for k, v in comp_means.items()},
                "max_gap": round(gap, 4),
                "hardest": min(comp_means, key=comp_means.get),
                "easiest": max(comp_means, key=comp_means.get),
            }
        )

        if gap > 0.4:
            easy = max(comp_means, key=comp_means.get)
            hard = min(comp_means, key=comp_means.get)
            warnings.append(
                {
                    "severity": "medium",
                    "type": "component_imbalance",
                    "message": f"Large gap between easiest ({easy}: {comp_means[easy]:.2f}) "
                    f"and hardest ({hard}: {comp_means[hard]:.2f}). Gap={gap:.2f}.",
                }
            )
            suggestions.append(
                f"Rebalance difficulty: add harder tasks to {easy} "
                f"or easier tasks to {hard} for fairer cross-component comparison."
            )

    # --- 6. Per-component ceiling/floor ---
    comp_issues = {}
    for comp, scores in by_component.items():
        comp_scores = [s["score"] for s in scores]
        n = len(comp_scores)
        if n == 0:
            continue
        n_perf = sum(1 for s in comp_scores if s >= 0.99)
        n_zero = sum(1 for s in comp_scores if s <= 0.01)

        issues = []
        if n_perf / n > 0.5:
            issues.append(f"ceiling ({n_perf}/{n} perfect)")
        if n_zero / n > 0.5:
            issues.append(f"floor ({n_zero}/{n} zero)")

        comp_std = math.sqrt(sum((s - comp_means[comp]) ** 2 for s in comp_scores) / n) if n > 1 else 0
        if comp_std < 0.05 and n > 3:
            issues.append(f"low_variance (std={comp_std:.3f})")

        if issues:
            comp_issues[comp] = issues

    if comp_issues:
        diagnostics.append(
            {
                "type": "per_component_issues",
                "components": comp_issues,
            }
        )

    # --- 7. Adversarial-specific checks ---
    adv_scores = by_component.get("adversarial", [])
    if adv_scores:
        adv_pass_rate = sum(1 for s in adv_scores if s["passed"]) / len(adv_scores)
        if adv_pass_rate > 0.9:
            warnings.append(
                {
                    "severity": "low",
                    "type": "adversarial_too_easy",
                    "message": f"Adversarial pass rate is {adv_pass_rate:.0%}. "
                    "Tasks may be too easy or scorer too lenient for adversarial detection.",
                }
            )

        # Check by adversarial type
        by_atype = defaultdict(list)
        for s in adv_scores:
            by_atype[s["task_type"]].append(s["score"])
        type_means = {t: sum(ss) / len(ss) for t, ss in by_atype.items()}
        diagnostics.append(
            {
                "type": "adversarial_by_type",
                "type_means": {k: round(v, 4) for k, v in sorted(type_means.items())},
            }
        )

    # --- 8. Calibration-specific checks ---
    cal_scores = by_component.get("calibration", [])
    if cal_scores:
        cal_mean = sum(s["score"] for s in cal_scores) / len(cal_scores)
        if cal_mean < 0.4:
            suggestions.append(
                "Calibration scores are low. Check if confidence extraction "
                "(regex patterns) is robust enough for the response format."
            )

    return {
        "n_tasks": len(all_scores),
        "diagnostics": diagnostics,
        "warnings": warnings,
        "suggestions": suggestions,
        "n_warnings": len(warnings),
        "n_suggestions": len(suggestions),
    }


# =============================================================================
# TEXT OUTPUT
# =============================================================================


def print_feedback(result_path: str):
    """Print scoring feedback analysis."""
    fb = analyze_scoring_feedback(result_path)

    if "error" in fb:
        print(f"Error: {fb['error']}")
        return fb

    print(f"\n{'=' * 60}")
    print("BioEval Scoring Feedback Analysis")
    print(f"{'=' * 60}")
    print(f"Tasks analyzed: {fb['n_tasks']}")

    # Diagnostics
    for d in fb["diagnostics"]:
        if d["type"] == "overall_distribution":
            print(f"\nScore Distribution:")
            print(f"  Mean: {d['mean']:.3f} (std: {d['std']:.3f})")
            print(f"  Pass rate: {d['pass_rate']:.1%}")
            print(f"  Perfect scores: {d['n_perfect']} ({d['pct_perfect']}%)")
            print(f"  Zero scores: {d['n_zero']} ({d['pct_zero']}%)")

        elif d["type"] == "component_balance":
            print(f"\nComponent Means:")
            for comp, mean in sorted(d["means"].items()):
                print(f"  {comp:<15} {mean:.3f}")
            print(f"  Gap: {d['max_gap']:.3f} (easiest={d['easiest']}, hardest={d['hardest']})")

        elif d["type"] == "adversarial_by_type":
            print(f"\nAdversarial by Type:")
            for t, m in d["type_means"].items():
                print(f"  {t:<25} {m:.3f}")

    # Warnings
    if fb["warnings"]:
        print(f"\nWarnings ({fb['n_warnings']}):")
        for w in fb["warnings"]:
            sev = w["severity"].upper()
            print(f"  [{sev}] {w['type']}: {w['message']}")

    # Suggestions
    if fb["suggestions"]:
        print(f"\nSuggestions ({fb['n_suggestions']}):")
        for i, s in enumerate(fb["suggestions"], 1):
            print(f"  {i}. {s}")

    if not fb["warnings"] and not fb["suggestions"]:
        print("\nNo issues detected. Scoring pipeline looks healthy.")

    return fb
