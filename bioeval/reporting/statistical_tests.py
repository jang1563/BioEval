"""Statistical tests for BioEval Phase 2 multi-model comparison.

Provides:
- Bootstrap confidence intervals for per-component scores
- Wilcoxon signed-rank tests for paired model comparison
- Permutation tests for small N (e.g., MultiTurn N=6)
- Effect size calculations (Cohen's d, Hedges' g, rank-biserial r)
"""

from __future__ import annotations

import math
import random
from typing import Optional


def bootstrap_ci(
    scores: list[float],
    n_bootstrap: int = 10000,
    ci: float = 0.95,
    seed: int = 42,
) -> dict:
    """Compute bootstrap confidence interval for the mean.

    Args:
        scores: List of numeric scores.
        n_bootstrap: Number of bootstrap resamples.
        ci: Confidence level (default 0.95).
        seed: Random seed for reproducibility.

    Returns:
        Dict with mean, lower, upper, std, n.
    """
    if not scores:
        return {"mean": 0.0, "lower": 0.0, "upper": 0.0, "std": 0.0, "n": 0}

    n = len(scores)
    rng = random.Random(seed)

    # Bootstrap resampling
    boot_means = []
    for _ in range(n_bootstrap):
        sample = [scores[rng.randint(0, n - 1)] for _ in range(n)]
        boot_means.append(sum(sample) / n)

    boot_means.sort()
    tail = (1 - ci) / 2
    lower_idx = max(0, int(tail * n_bootstrap))
    upper_idx = min(n_bootstrap - 1, int((1 - tail) * n_bootstrap))

    mean_score = sum(scores) / n
    std_score = math.sqrt(sum((s - mean_score) ** 2 for s in scores) / max(1, n - 1)) if n > 1 else 0.0

    return {
        "mean": round(mean_score, 4),
        "lower": round(boot_means[lower_idx], 4),
        "upper": round(boot_means[upper_idx], 4),
        "std": round(std_score, 4),
        "n": n,
    }


def wilcoxon_signed_rank(
    scores_a: list[float],
    scores_b: list[float],
    alternative: str = "two-sided",
) -> dict:
    """Paired Wilcoxon signed-rank test for model comparison.

    Args:
        scores_a: Per-task scores for model A.
        scores_b: Per-task scores for model B (same tasks, same order).
        alternative: 'two-sided', 'greater', or 'less'.

    Returns:
        Dict with test_statistic, p_value, n_pairs, cohens_d, rank_biserial_r.
    """
    if len(scores_a) != len(scores_b):
        raise ValueError(f"Score lists must have equal length: {len(scores_a)} vs {len(scores_b)}")

    n = len(scores_a)
    if n == 0:
        return {"test_statistic": 0.0, "p_value": 1.0, "n_pairs": 0, "cohens_d": 0.0, "rank_biserial_r": 0.0}

    # All differences zero → no effect, p = 1.0
    if all(a == b for a, b in zip(scores_a, scores_b)):
        return {"test_statistic": 0.0, "p_value": 1.0, "n_pairs": n, "cohens_d": 0.0, "rank_biserial_r": 0.0}

    try:
        from scipy.stats import wilcoxon as scipy_wilcoxon

        stat, p_value = scipy_wilcoxon(scores_a, scores_b, alternative=alternative, zero_method="wilcox")
    except ImportError:
        # Manual implementation
        diffs = [a - b for a, b in zip(scores_a, scores_b)]
        nonzero = [(abs(d), d) for d in diffs if d != 0]
        if not nonzero:
            return {"test_statistic": 0.0, "p_value": 1.0, "n_pairs": n, "cohens_d": 0.0, "rank_biserial_r": 0.0}

        nonzero.sort(key=lambda x: x[0])
        # Assign ranks
        ranks = list(range(1, len(nonzero) + 1))
        w_plus = sum(r for r, (_, d) in zip(ranks, nonzero) if d > 0)
        w_minus = sum(r for r, (_, d) in zip(ranks, nonzero) if d < 0)
        stat = min(w_plus, w_minus)
        # Approximate p-value using normal approximation
        nr = len(nonzero)
        mu = nr * (nr + 1) / 4
        sigma = math.sqrt(nr * (nr + 1) * (2 * nr + 1) / 24)
        z = (stat - mu) / sigma if sigma > 0 else 0
        # Two-tailed p from standard normal
        p_value = 2 * (1 - _normal_cdf(abs(z)))

    d = cohens_d(scores_a, scores_b, paired=True)
    r = rank_biserial_r(stat, n) if n > 0 else 0.0

    return {
        "test_statistic": round(float(stat), 4),
        "p_value": round(float(p_value), 6),
        "n_pairs": n,
        "cohens_d": round(d, 4),
        "rank_biserial_r": round(r, 4),
    }


def permutation_test(
    group_a: list[float],
    group_b: list[float],
    n_permutations: int = 10000,
    seed: int = 42,
    alternative: str = "two-sided",
) -> dict:
    """Monte Carlo permutation test for small N.

    Tests whether the mean difference between groups is significant.

    Args:
        group_a: Scores for group A.
        group_b: Scores for group B (paired, same length).
        n_permutations: Number of random permutations.
        seed: Random seed.
        alternative: 'two-sided', 'greater', or 'less'.

    Returns:
        Dict with observed_statistic, p_value, n_permutations.
    """
    if len(group_a) != len(group_b):
        raise ValueError("Groups must have equal length for paired permutation test")

    n = len(group_a)
    if n == 0:
        return {"observed_statistic": 0.0, "p_value": 1.0, "n_permutations": 0}

    diffs = [a - b for a, b in zip(group_a, group_b)]
    observed = sum(diffs) / n

    rng = random.Random(seed)
    count_extreme = 0

    for _ in range(n_permutations):
        # Randomly flip signs of differences
        perm_diffs = [d * (1 if rng.random() < 0.5 else -1) for d in diffs]
        perm_mean = sum(perm_diffs) / n

        if alternative == "two-sided":
            if abs(perm_mean) >= abs(observed):
                count_extreme += 1
        elif alternative == "greater":
            if perm_mean >= observed:
                count_extreme += 1
        elif alternative == "less":
            if perm_mean <= observed:
                count_extreme += 1

    p_value = (count_extreme + 1) / (n_permutations + 1)

    return {
        "observed_statistic": round(observed, 4),
        "p_value": round(p_value, 6),
        "n_permutations": n_permutations,
        "n": n,
    }


def cohens_d(x: list[float], y: list[float], paired: bool = False) -> float:
    """Compute Cohen's d effect size.

    Args:
        x: Scores for group/condition A.
        y: Scores for group/condition B.
        paired: If True, compute for paired differences.

    Returns:
        Cohen's d (positive means x > y).
    """
    if not x or not y:
        return 0.0

    if paired:
        diffs = [a - b for a, b in zip(x, y)]
        mean_d = sum(diffs) / len(diffs)
        std_d = math.sqrt(sum((d - mean_d) ** 2 for d in diffs) / max(1, len(diffs) - 1)) if len(diffs) > 1 else 1.0
        return mean_d / std_d if std_d > 0 else 0.0

    mean_x = sum(x) / len(x)
    mean_y = sum(y) / len(y)
    var_x = sum((v - mean_x) ** 2 for v in x) / max(1, len(x) - 1) if len(x) > 1 else 0.0
    var_y = sum((v - mean_y) ** 2 for v in y) / max(1, len(y) - 1) if len(y) > 1 else 0.0
    pooled_std = math.sqrt((var_x + var_y) / 2)
    return (mean_x - mean_y) / pooled_std if pooled_std > 0 else 0.0


def hedges_g(x: list[float], y: list[float]) -> float:
    """Compute Hedges' g (bias-corrected Cohen's d for small samples).

    Args:
        x: Scores for group A.
        y: Scores for group B.

    Returns:
        Hedges' g.
    """
    d = cohens_d(x, y)
    n = len(x) + len(y)
    # Correction factor J
    if n <= 3:
        return d
    j = 1 - (3 / (4 * (n - 2) - 1))
    return d * j


def rank_biserial_r(test_statistic: float, n: int) -> float:
    """Compute rank-biserial correlation from Wilcoxon test statistic.

    Args:
        test_statistic: Wilcoxon W statistic.
        n: Number of non-zero pairs.

    Returns:
        Rank-biserial r in [-1, 1].
    """
    if n <= 0:
        return 0.0
    max_w = n * (n + 1) / 2
    if max_w == 0:
        return 0.0
    return 1 - (2 * test_statistic / max_w)


def compare_models(
    results_a: dict,
    results_b: dict,
    extract_score_fn=None,
) -> dict:
    """Full statistical comparison of two model result files.

    Args:
        results_a: BioEval result dict for model A.
        results_b: BioEval result dict for model B.
        extract_score_fn: Function(component, task_result) -> float|None.

    Returns:
        Comparison dict with per-component statistics.
    """
    if extract_score_fn is None:
        from bioeval.reporting.statistical_tests import _default_extract_score

        extract_score_fn = _default_extract_score

    comparison = {
        "model_a": results_a.get("metadata", {}).get("model", "unknown"),
        "model_b": results_b.get("metadata", {}).get("model", "unknown"),
        "by_component": {},
    }

    # Index results by component
    comps_a = {r["component"]: r for r in results_a.get("results", [])}
    comps_b = {r["component"]: r for r in results_b.get("results", [])}

    all_comps = sorted(set(list(comps_a.keys()) + list(comps_b.keys())))

    for comp in all_comps:
        # Extract per-task scores
        scores_a = _extract_task_scores(comp, comps_a.get(comp, {}), extract_score_fn)
        scores_b = _extract_task_scores(comp, comps_b.get(comp, {}), extract_score_fn)

        ci_a = bootstrap_ci(list(scores_a.values()))
        ci_b = bootstrap_ci(list(scores_b.values()))

        # Paired comparison on shared tasks
        shared_ids = sorted(set(scores_a.keys()) & set(scores_b.keys()))
        paired_a = [scores_a[tid] for tid in shared_ids]
        paired_b = [scores_b[tid] for tid in shared_ids]

        if len(shared_ids) >= 6:
            if len(shared_ids) < 20:
                # Small N: use permutation test
                test_result = permutation_test(paired_a, paired_b)
                test_type = "permutation"
            else:
                test_result = wilcoxon_signed_rank(paired_a, paired_b)
                test_type = "wilcoxon"
        else:
            test_result = {"p_value": None, "test_statistic": None}
            test_type = "insufficient_n"

        comparison["by_component"][comp] = {
            "model_a": ci_a,
            "model_b": ci_b,
            "n_shared_tasks": len(shared_ids),
            "test_type": test_type,
            "test_result": test_result,
            "effect_size": {
                "cohens_d": round(cohens_d(paired_a, paired_b, paired=True), 4) if shared_ids else None,
                "hedges_g": round(hedges_g(paired_a, paired_b), 4) if shared_ids else None,
            },
        }

    return comparison


def _extract_task_scores(component: str, comp_result: dict, extract_fn) -> dict[str, float]:
    """Extract task_id -> score mapping from a component result."""
    scores = {}
    for r in comp_result.get("results", []):
        if not isinstance(r, dict) or "error" in r:
            continue
        task_id = r.get("task_id", "")
        score = extract_fn(component, r)
        if score is not None:
            scores[task_id] = score
    return scores


def _default_extract_score(component: str, task_result: dict) -> Optional[float]:
    """Default score extraction using canonical field mapping."""
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


def _normal_cdf(z: float) -> float:
    """Approximate standard normal CDF using Abramowitz & Stegun."""
    if z < -8:
        return 0.0
    if z > 8:
        return 1.0
    t = 1.0 / (1.0 + 0.2316419 * abs(z))
    d = 0.3989422804014327  # 1/sqrt(2*pi)
    p = (
        d
        * math.exp(-z * z / 2)
        * (t * (0.319381530 + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429)))))
    )
    return 1.0 - p if z > 0 else p


def print_comparison(comparison: dict) -> None:
    """Pretty-print a model comparison."""
    print(f"\nModel Comparison: {comparison['model_a']} vs {comparison['model_b']}")
    print("=" * 90)
    print(f"  {'Component':15s} {'Model A':>12s} {'Model B':>12s} {'Diff':>8s} {'p-value':>10s} {'Effect':>8s} {'Sig':>5s}")
    print("-" * 90)

    for comp, data in sorted(comparison["by_component"].items()):
        mean_a = data["model_a"]["mean"]
        mean_b = data["model_b"]["mean"]
        diff = mean_a - mean_b
        p = data["test_result"].get("p_value")
        d = data["effect_size"].get("cohens_d", 0)

        p_str = f"{p:.4f}" if p is not None else "N/A"
        sig = "*" if p is not None and p < 0.05 else ""
        if p is not None and p < 0.01:
            sig = "**"
        if p is not None and p < 0.001:
            sig = "***"

        ci_a = f"{mean_a:.3f} [{data['model_a']['lower']:.3f},{data['model_a']['upper']:.3f}]"
        ci_b = f"{mean_b:.3f} [{data['model_b']['lower']:.3f},{data['model_b']['upper']:.3f}]"

        print(f"  {comp:15s} {ci_a:>25s} {ci_b:>25s} {diff:+.3f} {p_str:>10s} d={d:+.2f} {sig:>5s}")

    print("-" * 90)
