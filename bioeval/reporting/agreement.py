"""
Inter-rater agreement analysis for BioEval.

Computes Cohen's kappa and related agreement metrics between:
- Automated scorer vs LLM judge
- Multiple LLM judges (if available)
- Scorer vs human annotations (for validation)

Required for NeurIPS: demonstrates scoring reliability beyond
a single automated metric.
"""

import json
import math
from collections import defaultdict

from bioeval.scoring.normalizer import normalize_result


# =============================================================================
# COHEN'S KAPPA AND AGREEMENT METRICS
# =============================================================================

def cohens_kappa(rater1: list[int], rater2: list[int]) -> float:
    """Compute Cohen's kappa for two lists of binary ratings.

    Args:
        rater1: List of 0/1 ratings from rater 1
        rater2: List of 0/1 ratings from rater 2

    Returns:
        Kappa statistic (-1 to 1). 1 = perfect agreement, 0 = chance.
    """
    if len(rater1) != len(rater2) or len(rater1) == 0:
        return 0.0

    n = len(rater1)
    # Build confusion matrix
    a = sum(1 for r1, r2 in zip(rater1, rater2) if r1 == 1 and r2 == 1)
    b = sum(1 for r1, r2 in zip(rater1, rater2) if r1 == 1 and r2 == 0)
    c = sum(1 for r1, r2 in zip(rater1, rater2) if r1 == 0 and r2 == 1)
    d = sum(1 for r1, r2 in zip(rater1, rater2) if r1 == 0 and r2 == 0)

    # Observed agreement
    po = (a + d) / n

    # Expected agreement
    p1_yes = (a + b) / n
    p2_yes = (a + c) / n
    p1_no = (c + d) / n
    p2_no = (b + d) / n
    pe = p1_yes * p2_yes + p1_no * p2_no

    if pe == 1.0:
        return 1.0 if po == 1.0 else 0.0

    return (po - pe) / (1 - pe)


def weighted_kappa(rater1: list[float], rater2: list[float], n_bins: int = 5) -> float:
    """Compute weighted (linear) Cohen's kappa for ordinal/continuous scores.

    Discretizes continuous scores into bins before computing kappa.

    Args:
        rater1: List of scores (0-1) from rater 1
        rater2: List of scores (0-1) from rater 2
        n_bins: Number of bins for discretization

    Returns:
        Weighted kappa statistic.
    """
    if len(rater1) != len(rater2) or len(rater1) == 0:
        return 0.0

    def _bin(score):
        return min(int(score * n_bins), n_bins - 1)

    bins1 = [_bin(s) for s in rater1]
    bins2 = [_bin(s) for s in rater2]

    n = len(bins1)
    # Build confusion matrix
    matrix = [[0] * n_bins for _ in range(n_bins)]
    for b1, b2 in zip(bins1, bins2):
        matrix[b1][b2] += 1

    # Weight matrix (linear weights)
    weights = [[abs(i - j) / (n_bins - 1) for j in range(n_bins)] for i in range(n_bins)]

    # Row/column marginals
    row_totals = [sum(matrix[i]) for i in range(n_bins)]
    col_totals = [sum(matrix[i][j] for i in range(n_bins)) for j in range(n_bins)]

    # Observed weighted disagreement
    wo = sum(weights[i][j] * matrix[i][j]
             for i in range(n_bins) for j in range(n_bins)) / n

    # Expected weighted disagreement
    we = sum(weights[i][j] * row_totals[i] * col_totals[j]
             for i in range(n_bins) for j in range(n_bins)) / (n * n)

    if we == 0:
        return 1.0 if wo == 0 else 0.0

    return 1 - (wo / we)


def percent_agreement(rater1: list[int], rater2: list[int]) -> float:
    """Simple percent agreement between two raters."""
    if len(rater1) != len(rater2) or len(rater1) == 0:
        return 0.0
    matches = sum(1 for r1, r2 in zip(rater1, rater2) if r1 == r2)
    return matches / len(rater1)


def correlation(x: list[float], y: list[float]) -> float:
    """Pearson correlation between two score lists."""
    if len(x) != len(y) or len(x) < 2:
        return 0.0
    n = len(x)
    mx = sum(x) / n
    my = sum(y) / n
    sx = math.sqrt(sum((xi - mx) ** 2 for xi in x) / n)
    sy = math.sqrt(sum((yi - my) ** 2 for yi in y) / n)
    if sx == 0 or sy == 0:
        return 0.0
    cov = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / n
    return cov / (sx * sy)


# =============================================================================
# AGREEMENT ANALYSIS FROM RESULT FILES
# =============================================================================

def analyze_agreement(result_path: str) -> dict:
    """Analyze agreement between automated scorer and LLM judge.

    Requires result file with both "scores" and "judge_scores" fields.

    Args:
        result_path: Path to result JSON file

    Returns:
        Dict with agreement metrics.
    """
    with open(result_path) as f:
        data = json.load(f)

    paired_scores = []  # (auto_score, judge_score, component, task_id)

    for comp_result in data.get("results", []):
        comp = comp_result.get("component", "unknown")
        for r in comp_result.get("results", []):
            if not isinstance(r, dict):
                continue

            # Get automated score
            task_type = r.get("task_type", r.get("adversarial_type", ""))
            try:
                ns = normalize_result(r, comp, task_type)
                auto_score = ns.score
            except Exception:
                continue

            # Get judge score
            judge = r.get("judge_scores", {})
            if not judge or "error" in judge:
                continue
            judge_score = judge.get("overall_score")
            if judge_score is None:
                continue

            paired_scores.append({
                "task_id": r.get("task_id", r.get("dialogue_id", "")),
                "component": comp,
                "auto_score": auto_score,
                "judge_score": judge_score,
                "auto_passed": auto_score >= 0.5,
                "judge_passed": judge_score >= 0.5,
            })

    if not paired_scores:
        return {"error": "No paired auto+judge scores found. Run with --use-judge."}

    # Compute metrics
    auto_binary = [1 if p["auto_passed"] else 0 for p in paired_scores]
    judge_binary = [1 if p["judge_passed"] else 0 for p in paired_scores]
    auto_continuous = [p["auto_score"] for p in paired_scores]
    judge_continuous = [p["judge_score"] for p in paired_scores]

    kappa = cohens_kappa(auto_binary, judge_binary)
    w_kappa = weighted_kappa(auto_continuous, judge_continuous)
    pct_agree = percent_agreement(auto_binary, judge_binary)
    corr = correlation(auto_continuous, judge_continuous)

    # Per-component
    by_component = defaultdict(list)
    for p in paired_scores:
        by_component[p["component"]].append(p)

    comp_metrics = {}
    for comp, items in by_component.items():
        a_bin = [1 if p["auto_passed"] else 0 for p in items]
        j_bin = [1 if p["judge_passed"] else 0 for p in items]
        a_cont = [p["auto_score"] for p in items]
        j_cont = [p["judge_score"] for p in items]
        comp_metrics[comp] = {
            "n": len(items),
            "kappa": round(cohens_kappa(a_bin, j_bin), 4),
            "weighted_kappa": round(weighted_kappa(a_cont, j_cont), 4),
            "percent_agreement": round(percent_agreement(a_bin, j_bin), 4),
            "correlation": round(correlation(a_cont, j_cont), 4),
        }

    # Disagreement analysis: where do auto and judge disagree most?
    disagreements = [p for p in paired_scores if p["auto_passed"] != p["judge_passed"]]

    return {
        "n_paired": len(paired_scores),
        "overall": {
            "cohens_kappa": round(kappa, 4),
            "weighted_kappa": round(w_kappa, 4),
            "percent_agreement": round(pct_agree, 4),
            "pearson_correlation": round(corr, 4),
        },
        "by_component": comp_metrics,
        "n_disagreements": len(disagreements),
        "disagreement_rate": round(len(disagreements) / len(paired_scores), 4) if paired_scores else 0,
        "disagreements": disagreements[:10],  # Top 10
        "interpretation": _interpret_kappa(kappa),
    }


def analyze_agreement_from_scores(
    auto_scores: list[float],
    judge_scores: list[float],
) -> dict:
    """Compute agreement from raw score lists (for testing/validation).

    Args:
        auto_scores: Automated scorer outputs (0-1)
        judge_scores: Judge outputs (0-1)

    Returns:
        Dict with agreement metrics.
    """
    auto_binary = [1 if s >= 0.5 else 0 for s in auto_scores]
    judge_binary = [1 if s >= 0.5 else 0 for s in judge_scores]

    kappa = cohens_kappa(auto_binary, judge_binary)
    w_kappa = weighted_kappa(auto_scores, judge_scores)
    pct = percent_agreement(auto_binary, judge_binary)
    corr = correlation(auto_scores, judge_scores)

    return {
        "n": len(auto_scores),
        "cohens_kappa": round(kappa, 4),
        "weighted_kappa": round(w_kappa, 4),
        "percent_agreement": round(pct, 4),
        "pearson_correlation": round(corr, 4),
        "interpretation": _interpret_kappa(kappa),
    }


def _interpret_kappa(kappa: float) -> str:
    """Interpret kappa using Landis & Koch (1977) scale."""
    if kappa < 0:
        return "Poor (below chance)"
    elif kappa < 0.20:
        return "Slight agreement"
    elif kappa < 0.40:
        return "Fair agreement"
    elif kappa < 0.60:
        return "Moderate agreement"
    elif kappa < 0.80:
        return "Substantial agreement"
    else:
        return "Almost perfect agreement"


# =============================================================================
# TEXT OUTPUT
# =============================================================================

def print_agreement(result_path: str):
    """Print agreement analysis."""
    result = analyze_agreement(result_path)

    if "error" in result:
        print(f"Error: {result['error']}")
        return result

    print(f"\n{'=' * 60}")
    print("Inter-Rater Agreement: Automated Scorer vs LLM Judge")
    print(f"{'=' * 60}")
    print(f"Paired tasks: {result['n_paired']}")

    o = result["overall"]
    print(f"\nOverall Metrics:")
    print(f"  Cohen's kappa:       {o['cohens_kappa']:.4f}")
    print(f"  Weighted kappa:      {o['weighted_kappa']:.4f}")
    print(f"  Percent agreement:   {o['percent_agreement']:.1%}")
    print(f"  Pearson correlation: {o['pearson_correlation']:.4f}")
    print(f"  Interpretation:      {result['interpretation']}")

    print(f"\nPer-Component:")
    print(f"{'Component':<15} {'N':>4} {'Kappa':>7} {'WKappa':>7} {'Agree':>7} {'Corr':>7}")
    print(f"{'─' * 52}")
    for comp, m in sorted(result["by_component"].items()):
        print(f"  {comp:<13} {m['n']:>4} {m['kappa']:>7.4f} "
              f"{m['weighted_kappa']:>7.4f} {m['percent_agreement']:>6.1%} "
              f"{m['correlation']:>7.4f}")

    print(f"\nDisagreements: {result['n_disagreements']} "
          f"({result['disagreement_rate']:.1%} of paired)")

    return result
