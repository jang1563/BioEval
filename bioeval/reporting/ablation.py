"""
Scoring ablation framework for BioEval.

Measures the contribution of each matching feature (stemming, synonyms,
word-boundary) by running the same evaluation with features toggled off.

This is critical for a NeurIPS submission: reviewers expect evidence that
scoring components are individually justified and not just complexity theater.

Usage:
    from bioeval.reporting.ablation import run_ablation
    results = run_ablation("path/to/results.json")
"""

from __future__ import annotations

from bioeval.reporting.analysis import load_and_normalize
from bioeval.scoring.matching import MatchConfig, match_config
from bioeval.scoring.normalizer import NormalizedScore, normalize_result

# =============================================================================
# ABLATION CONFIGURATIONS
# =============================================================================

ABLATION_CONFIGS = {
    "full": MatchConfig(use_stemming=True, use_synonyms=True, use_word_boundary=True),
    "no_synonyms": MatchConfig(use_stemming=True, use_synonyms=False, use_word_boundary=True),
    "no_stemming": MatchConfig(use_stemming=False, use_synonyms=False, use_word_boundary=True),
    "no_word_boundary": MatchConfig(use_stemming=True, use_synonyms=True, use_word_boundary=False),
    "exact_only": MatchConfig(use_stemming=False, use_synonyms=False, use_word_boundary=False),
}


# =============================================================================
# RE-SCORE UNDER DIFFERENT CONFIGS
# =============================================================================


def _rescore_component(raw_result: dict, component: str, task_type: str) -> NormalizedScore:
    """Re-normalize a single raw result (score is already computed, but
    some components re-use matching internally during normalization).

    For ablation purposes, we mainly care about how the scorer functions
    produce different raw scores under different matching configs.
    """
    return normalize_result(raw_result, component, task_type)


def rescore_results(result_path: str, config: MatchConfig) -> list[NormalizedScore]:
    """Re-score all results from a file under a given matching config.

    Note: This re-runs normalization but not the full evaluation pipeline.
    For a true ablation, the scoring functions themselves (in evaluator modules)
    would need to be re-run. This provides an approximation by re-running
    normalization.

    For a complete ablation, use `rescore_from_responses()` which re-runs
    the component scorers on cached model responses.
    """
    with match_config(config):
        loaded = load_and_normalize(result_path)
    return loaded["normalized"]


def rescore_from_responses(responses: list[dict], component: str, config: MatchConfig) -> list[dict]:
    """Re-score model responses under a given matching config.

    This re-runs the component's scoring function with the given config active,
    providing a true ablation.

    Args:
        responses: List of {"task": task_dict, "response": str} dicts
        component: Component name
        config: Matching configuration to use

    Returns:
        List of raw score dicts from the component scorer.
    """
    scorer = _get_scorer(component)
    if scorer is None:
        return []

    results = []
    with match_config(config):
        for item in responses:
            try:
                result = scorer(item["task"], item["response"])
                results.append(result)
            except Exception as e:
                results.append({"error": str(e), "task_id": item.get("task", {}).get("id", "unknown")})
    return results


def _get_scorer(component: str):
    """Get the scoring function for a component."""
    try:
        if component == "adversarial":
            from bioeval.adversarial.tasks import score_adversarial_response

            return lambda task, resp: score_adversarial_response(task, resp)
        elif component == "calibration":
            from bioeval.scoring.calibration import score_calibration_task

            return lambda task, resp: score_calibration_task(task, resp)
        elif component == "designcheck":
            from bioeval.designcheck.evaluator import DesignCheckEvaluator

            return None  # Requires evaluator instance
    except ImportError:
        pass
    return None


# =============================================================================
# ABLATION ANALYSIS
# =============================================================================


def run_ablation(result_path: str, configs: dict[str, MatchConfig] | None = None) -> dict:
    """Run ablation analysis on a result file.

    Compares scores under different matching configurations to measure
    the contribution of each feature.

    Args:
        result_path: Path to evaluation result JSON file.
        configs: Dict of config_name → MatchConfig. Defaults to ABLATION_CONFIGS.

    Returns:
        {
            "configs": {name: {mean, std, n, pass_rate}},
            "deltas": {name: {delta_mean, delta_pass_rate}},  # vs full
            "per_component": {comp: {config: {mean, pass_rate}}},
            "feature_contributions": {feature: delta},
        }
    """
    if configs is None:
        configs = ABLATION_CONFIGS

    # Score under each config
    config_results: dict[str, list[NormalizedScore]] = {}
    for name, cfg in configs.items():
        config_results[name] = rescore_results(result_path, cfg)

    # Compute aggregates per config
    import math

    config_stats: dict[str, dict] = {}
    for name, ns_list in config_results.items():
        scores = [ns.score for ns in ns_list]
        passed = [ns.passed for ns in ns_list]
        n = len(scores)
        if n == 0:
            config_stats[name] = {"n": 0}
            continue
        mean = sum(scores) / n
        var = sum((s - mean) ** 2 for s in scores) / max(1, n - 1)
        config_stats[name] = {
            "n": n,
            "mean": round(mean, 4),
            "std": round(math.sqrt(var), 4),
            "pass_rate": round(sum(passed) / n, 4),
        }

    # Deltas vs "full" config
    full_stats = config_stats.get("full", {})
    deltas = {}
    for name, stats in config_stats.items():
        if name == "full" or stats.get("n", 0) == 0:
            continue
        deltas[name] = {
            "delta_mean": round(stats["mean"] - full_stats.get("mean", 0), 4),
            "delta_pass_rate": round(stats["pass_rate"] - full_stats.get("pass_rate", 0), 4),
        }

    # Per-component breakdown
    from collections import defaultdict

    per_component: dict[str, dict[str, dict]] = defaultdict(dict)
    for name, ns_list in config_results.items():
        by_comp: dict[str, list] = defaultdict(list)
        for ns in ns_list:
            by_comp[ns.component].append(ns)
        for comp, comp_ns in by_comp.items():
            scores = [ns.score for ns in comp_ns]
            passed = [ns.passed for ns in comp_ns]
            n = len(scores)
            per_component[comp][name] = {
                "n": n,
                "mean": round(sum(scores) / n, 4) if n else 0,
                "pass_rate": round(sum(passed) / n, 4) if n else 0,
            }

    # Feature contribution estimates
    # Each feature's contribution ≈ full_score - score_without_feature
    feature_contributions = {}
    if "full" in config_stats and config_stats["full"].get("n", 0) > 0:
        full_mean = config_stats["full"]["mean"]
        if "no_synonyms" in config_stats and config_stats["no_synonyms"].get("n", 0) > 0:
            feature_contributions["synonyms"] = round(full_mean - config_stats["no_synonyms"]["mean"], 4)
        if "no_stemming" in config_stats and config_stats["no_stemming"].get("n", 0) > 0:
            # Stemming contribution = full - no_stemming (which also disables synonyms)
            # Pure stemming = no_synonyms - no_stemming
            feature_contributions["stemming"] = round(
                config_stats.get("no_synonyms", {}).get("mean", full_mean) - config_stats["no_stemming"]["mean"], 4
            )
        if "no_word_boundary" in config_stats and config_stats["no_word_boundary"].get("n", 0) > 0:
            feature_contributions["word_boundary"] = round(full_mean - config_stats["no_word_boundary"]["mean"], 4)

    return {
        "configs": config_stats,
        "deltas": deltas,
        "per_component": dict(per_component),
        "feature_contributions": feature_contributions,
    }


# =============================================================================
# TEXT OUTPUT
# =============================================================================


def print_ablation(result_path: str):
    """Print formatted ablation analysis."""
    results = run_ablation(result_path)

    print(f"\n{'=' * 65}")
    print("Scoring Ablation Analysis")
    print(f"{'=' * 65}")

    # Config comparison table
    print(f"\n{'Config':<20} {'N':>4} {'Mean':>7} {'Std':>7} {'Pass%':>7}")
    print(f"{'─' * 50}")
    for name in ["full", "no_synonyms", "no_stemming", "no_word_boundary", "exact_only"]:
        if name in results["configs"] and results["configs"][name].get("n", 0) > 0:
            s = results["configs"][name]
            print(f"{name:<20} {s['n']:>4} {s['mean']:>7.3f} {s['std']:>7.3f} {s['pass_rate']:>6.1%}")

    # Deltas
    if results["deltas"]:
        print(f"\nDeltas vs full:")
        for name, d in results["deltas"].items():
            print(f"  {name:<20} mean: {d['delta_mean']:+.4f}  pass_rate: {d['delta_pass_rate']:+.4f}")

    # Feature contributions
    if results["feature_contributions"]:
        print(f"\nFeature contributions (mean score increase):")
        for feat, delta in sorted(results["feature_contributions"].items(), key=lambda x: abs(x[1]), reverse=True):
            bar = "+" * max(0, int(abs(delta) * 100))
            sign = "+" if delta >= 0 else "-"
            print(f"  {feat:<20} {sign}{abs(delta):.4f} {bar}")

    # Per-component
    if results["per_component"]:
        print(f"\nPer-component (full vs exact_only):")
        print(f"{'Component':<15} {'Full':>7} {'Exact':>7} {'Delta':>7}")
        print(f"{'─' * 40}")
        for comp in sorted(results["per_component"]):
            full_m = results["per_component"][comp].get("full", {}).get("mean", 0)
            exact_m = results["per_component"][comp].get("exact_only", {}).get("mean", 0)
            delta = full_m - exact_m
            print(f"  {comp:<13} {full_m:>7.3f} {exact_m:>7.3f} {delta:>+7.3f}")

    return results
