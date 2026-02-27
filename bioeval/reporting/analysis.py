"""
Result analysis pipeline for BioEval.

Analyzes evaluation result JSON files to produce:
- Per-component aggregate scores
- Cross-model comparison tables
- Expected Calibration Error (ECE)
- Score distribution statistics
"""

import json
import math
from collections import defaultdict
from pathlib import Path

from bioeval.scoring.normalizer import normalize_result, NormalizedScore

# =============================================================================
# RESULT LOADING & NORMALIZATION
# =============================================================================


def load_and_normalize(result_path: str) -> dict:
    """Load a result JSON file and normalize all scores.

    Returns:
        {
            "metadata": {...},
            "normalized": [NormalizedScore, ...],
            "by_component": {comp: [NormalizedScore, ...]},
        }
    """
    with open(result_path) as f:
        data = json.load(f)

    all_normalized = []
    by_component: dict[str, list[NormalizedScore]] = defaultdict(list)

    for comp_result in data.get("results", []):
        component = comp_result.get("component", "unknown")
        for r in comp_result.get("results", []):
            if isinstance(r, dict) and "error" in r and "score" not in r:
                continue

            task_type = r.get("task_type", "")
            # Flatten nested "scores" dict into top-level for normalizer
            if isinstance(r.get("scores"), dict):
                merged = {**r, **r["scores"]}
            else:
                merged = r

            # Infer task_type from task_id when not explicitly stored
            if not task_type:
                task_id = merged.get("task_id", "")
                if "ordering" in task_id:
                    task_type = "step_ordering"
                elif "missing" in task_id:
                    task_type = "missing_step"
                elif "calc" in task_id:
                    task_type = "calculation"
                elif "trouble" in task_id or "ts_" in task_id:
                    task_type = "troubleshooting"
                elif "safety" in task_id:
                    task_type = "safety"
                elif task_id.startswith("ko_"):
                    task_type = "knockout_prediction"
                elif task_id.startswith("pathway_"):
                    task_type = "pathway_reasoning"
                elif task_id.startswith("epistasis_"):
                    task_type = "epistasis"
                elif task_id.startswith("drug_"):
                    task_type = "drug_response"
                elif task_id.startswith("design_"):
                    task_type = "flaw_detection"
                elif task_id.startswith("cal_"):
                    task_type = "calibration"

            ns = normalize_result(merged, component, task_type)

            all_normalized.append(ns)
            by_component[component].append(ns)

    return {
        "metadata": data.get("metadata", {}),
        "normalized": all_normalized,
        "by_component": dict(by_component),
    }


# =============================================================================
# AGGREGATE STATISTICS
# =============================================================================


def compute_aggregates(normalized: list[NormalizedScore]) -> dict:
    """Compute aggregate statistics from normalized scores."""
    if not normalized:
        return {"n": 0}

    scores = [ns.score for ns in normalized]
    passed = [ns.passed for ns in normalized]

    n = len(scores)
    mean = sum(scores) / n
    variance = sum((s - mean) ** 2 for s in scores) / max(1, n - 1)
    std = math.sqrt(variance)

    # Percentiles (sorted)
    sorted_scores = sorted(scores)
    p25 = sorted_scores[n // 4] if n >= 4 else sorted_scores[0]
    p50 = sorted_scores[n // 2] if n >= 2 else sorted_scores[0]
    p75 = sorted_scores[3 * n // 4] if n >= 4 else sorted_scores[-1]

    return {
        "n": n,
        "mean": round(mean, 4),
        "std": round(std, 4),
        "min": round(min(scores), 4),
        "max": round(max(scores), 4),
        "p25": round(p25, 4),
        "median": round(p50, 4),
        "p75": round(p75, 4),
        "pass_rate": round(sum(passed) / n, 4),
        "n_passed": sum(passed),
    }


def analyze_results(result_path: str) -> dict:
    """Full analysis of a result file.

    Returns structured analysis with per-component and overall statistics.
    """
    loaded = load_and_normalize(result_path)
    metadata = loaded["metadata"]
    all_ns = loaded["normalized"]
    by_comp = loaded["by_component"]

    analysis = {
        "metadata": metadata,
        "overall": compute_aggregates(all_ns),
        "by_component": {},
        "by_task_type": {},
    }

    # Per-component
    for comp, ns_list in by_comp.items():
        comp_agg = compute_aggregates(ns_list)

        # Per-task-type within component
        by_type: dict[str, list[NormalizedScore]] = defaultdict(list)
        for ns in ns_list:
            by_type[ns.task_type].append(ns)

        type_aggs = {}
        for tt, tt_list in by_type.items():
            type_aggs[tt] = compute_aggregates(tt_list)

        comp_agg["by_task_type"] = type_aggs
        analysis["by_component"][comp] = comp_agg

    # Global by-task-type
    all_by_type: dict[str, list[NormalizedScore]] = defaultdict(list)
    for ns in all_ns:
        all_by_type[ns.task_type].append(ns)
    for tt, tt_list in all_by_type.items():
        analysis["by_task_type"][tt] = compute_aggregates(tt_list)

    # Calibration-specific: ECE
    if "calibration" in by_comp:
        analysis["calibration_analysis"] = _compute_ece(by_comp["calibration"])

    return analysis


# =============================================================================
# CALIBRATION ANALYSIS (ECE)
# =============================================================================


def _compute_ece(cal_scores: list[NormalizedScore], n_bins: int = 5) -> dict:
    """Compute Expected Calibration Error from calibration results."""
    # Extract confidence and correctness from raw results
    points = []
    for ns in cal_scores:
        conf = ns.subscores.get("confidence_score", 0.5)
        correct = ns.subscores.get("is_correct", 0.0)
        points.append((conf, correct))

    if not points:
        return {"ece": 0.0, "mce": 0.0, "n_bins": 0, "bins": []}

    # Bin by confidence
    bin_width = 1.0 / n_bins
    bins = []
    total_ece = 0.0
    max_ce = 0.0

    for i in range(n_bins):
        lo = i * bin_width
        hi = (i + 1) * bin_width
        in_bin = [(c, cor) for c, cor in points if lo <= c < hi or (i == n_bins - 1 and c == hi)]

        if not in_bin:
            bins.append({"bin_range": f"[{lo:.1f}, {hi:.1f})", "n": 0, "avg_confidence": 0, "avg_accuracy": 0, "gap": 0})
            continue

        avg_conf = sum(c for c, _ in in_bin) / len(in_bin)
        avg_acc = sum(cor for _, cor in in_bin) / len(in_bin)
        gap = abs(avg_conf - avg_acc)
        weight = len(in_bin) / len(points)

        total_ece += weight * gap
        max_ce = max(max_ce, gap)

        bins.append(
            {
                "bin_range": f"[{lo:.1f}, {hi:.1f})",
                "n": len(in_bin),
                "avg_confidence": round(avg_conf, 3),
                "avg_accuracy": round(avg_acc, 3),
                "gap": round(gap, 3),
            }
        )

    # Overconfidence/underconfidence
    overconf = sum(1 for c, cor in points if c >= 0.7 and cor < 0.5)
    underconf = sum(1 for c, cor in points if c < 0.4 and cor >= 0.5)

    return {
        "ece": round(total_ece, 4),
        "mce": round(max_ce, 4),
        "overconfidence_rate": round(overconf / len(points), 3) if points else 0,
        "underconfidence_rate": round(underconf / len(points), 3) if points else 0,
        "n_tasks": len(points),
        "bins": bins,
    }


# =============================================================================
# CROSS-MODEL COMPARISON
# =============================================================================


def compare_models(result_paths: list[str]) -> dict:
    """Compare results from multiple model evaluations.

    Args:
        result_paths: List of result JSON file paths

    Returns:
        Comparison table with per-component scores for each model.
    """
    models = {}
    for path in result_paths:
        analysis = analyze_results(path)
        model_name = analysis["metadata"].get("model", Path(path).stem)
        models[model_name] = analysis

    # Build comparison table
    components = sorted(set(comp for a in models.values() for comp in a.get("by_component", {})))

    comparison = {
        "models": list(models.keys()),
        "components": components,
        "table": {},  # model → component → score
    }

    for model_name, analysis in models.items():
        comparison["table"][model_name] = {
            "overall": analysis["overall"]["mean"],
            "pass_rate": analysis["overall"]["pass_rate"],
        }
        for comp in components:
            comp_data = analysis.get("by_component", {}).get(comp, {})
            comparison["table"][model_name][comp] = {
                "mean": comp_data.get("mean", None),
                "pass_rate": comp_data.get("pass_rate", None),
                "n": comp_data.get("n", 0),
            }

    return comparison


# =============================================================================
# CONTAMINATION DETECTION
# =============================================================================


def detect_contamination(result_path: str) -> dict:
    """Check for potential data contamination by comparing public vs private splits.

    A large gap (public >> private) suggests the model may have seen public tasks
    during training.
    """
    from bioeval.scoring.splits import get_split

    loaded = load_and_normalize(result_path)
    all_ns = loaded["normalized"]

    public_scores = []
    private_scores = []
    for ns in all_ns:
        split = get_split(ns.task_id)
        if split == "public":
            public_scores.append(ns.score)
        else:
            private_scores.append(ns.score)

    if not public_scores or not private_scores:
        return {"error": "Insufficient data for contamination analysis"}

    pub_mean = sum(public_scores) / len(public_scores)
    priv_mean = sum(private_scores) / len(private_scores)
    gap = pub_mean - priv_mean

    # Statistical significance (two-sample t-test approximation)
    pub_var = sum((s - pub_mean) ** 2 for s in public_scores) / max(1, len(public_scores) - 1)
    priv_var = sum((s - priv_mean) ** 2 for s in private_scores) / max(1, len(private_scores) - 1)
    se = math.sqrt(pub_var / len(public_scores) + priv_var / len(private_scores))
    t_stat = gap / se if se > 0 else 0

    # Rough interpretation
    if abs(t_stat) > 2.0 and gap > 0.1:
        verdict = "WARNING: Possible contamination (public >> private)"
    elif abs(t_stat) > 1.5 and gap > 0.05:
        verdict = "MILD: Slight public advantage, monitor"
    else:
        verdict = "OK: No evidence of contamination"

    return {
        "public_mean": round(pub_mean, 4),
        "private_mean": round(priv_mean, 4),
        "gap": round(gap, 4),
        "t_statistic": round(t_stat, 3),
        "n_public": len(public_scores),
        "n_private": len(private_scores),
        "verdict": verdict,
    }


# =============================================================================
# TEXT FORMATTING
# =============================================================================


def print_analysis(result_path: str):
    """Print formatted analysis of a result file."""
    analysis = analyze_results(result_path)
    meta = analysis["metadata"]

    print(f"\n{'=' * 65}")
    print(f"BioEval Result Analysis")
    print(f"{'=' * 65}")
    print(f"Model: {meta.get('model', 'unknown')}")
    print(f"Tier: {meta.get('data_tier', 'unknown')}")
    print(f"Date: {meta.get('timestamp', 'unknown')}")

    overall = analysis["overall"]
    print(
        f"\nOverall: mean={overall['mean']:.3f} (std={overall['std']:.3f}), "
        f"pass_rate={overall['pass_rate']:.1%} ({overall['n_passed']}/{overall['n']})"
    )

    print(f"\n{'─' * 65}")
    print(f"{'Component':<15} {'N':>4} {'Mean':>7} {'Std':>7} {'Pass%':>7} {'Med':>7}")
    print(f"{'─' * 65}")
    for comp in sorted(analysis["by_component"]):
        c = analysis["by_component"][comp]
        print(f"{comp:<15} {c['n']:>4} {c['mean']:>7.3f} {c['std']:>7.3f} " f"{c['pass_rate']:>6.1%} {c['median']:>7.3f}")

        # Sub-types
        for tt in sorted(c.get("by_task_type", {})):
            tc = c["by_task_type"][tt]
            print(f"  └ {tt:<12} {tc['n']:>4} {tc['mean']:>7.3f} {tc['std']:>7.3f} " f"{tc['pass_rate']:>6.1%}")

    # Calibration
    if "calibration_analysis" in analysis:
        cal = analysis["calibration_analysis"]
        print(f"\n{'─' * 65}")
        print(f"Calibration Analysis:")
        print(f"  ECE = {cal['ece']:.4f}, MCE = {cal['mce']:.4f}")
        print(f"  Overconfidence rate: {cal['overconfidence_rate']:.1%}")
        print(f"  Underconfidence rate: {cal['underconfidence_rate']:.1%}")
        print(f"  Reliability diagram:")
        for b in cal["bins"]:
            if b["n"] > 0:
                bar = "█" * int(b["avg_accuracy"] * 20)
                print(
                    f"    {b['bin_range']:<12} n={b['n']:>2} "
                    f"conf={b['avg_confidence']:.2f} acc={b['avg_accuracy']:.2f} "
                    f"gap={b['gap']:.2f} {bar}"
                )

    # Contamination
    contam = detect_contamination(result_path)
    if "error" not in contam:
        print(f"\n{'─' * 65}")
        print(f"Contamination Check:")
        print(f"  Public: {contam['public_mean']:.3f} (n={contam['n_public']})")
        print(f"  Private: {contam['private_mean']:.3f} (n={contam['n_private']})")
        print(f"  Gap: {contam['gap']:.3f}, t={contam['t_statistic']:.2f}")
        print(f"  Verdict: {contam['verdict']}")


def format_comparison_table(result_paths: list[str], fmt: str = "markdown") -> str:
    """Generate a comparison table in markdown or LaTeX format."""
    comp = compare_models(result_paths)
    models = comp["models"]
    components = comp["components"]

    if fmt == "latex":
        lines = [r"\begin{tabular}{l" + "c" * len(models) + "}"]
        lines.append(r"\toprule")
        lines.append("Component & " + " & ".join(models) + r" \\")
        lines.append(r"\midrule")
        for c in components:
            row = [c]
            for m in models:
                val = comp["table"][m].get(c, {})
                if isinstance(val, dict):
                    row.append(f"{val.get('mean', 0):.3f}")
                else:
                    row.append("--")
            lines.append(" & ".join(row) + r" \\")
        lines.append(r"\midrule")
        # Overall
        row = ["**Overall**"]
        for m in models:
            row.append(f"{comp['table'][m].get('overall', 0):.3f}")
        lines.append(" & ".join(row) + r" \\")
        lines.append(r"\bottomrule")
        lines.append(r"\end{tabular}")
        return "\n".join(lines)

    # Markdown
    header = "| Component | " + " | ".join(models) + " |"
    sep = "|" + "|".join(["---"] * (len(models) + 1)) + "|"
    rows = [header, sep]
    for c in components:
        row = [c]
        for m in models:
            val = comp["table"][m].get(c, {})
            if isinstance(val, dict) and val.get("mean") is not None:
                row.append(f"{val['mean']:.3f}")
            else:
                row.append("--")
        rows.append("| " + " | ".join(row) + " |")
    # Overall
    row = ["**Overall**"]
    for m in models:
        row.append(f"{comp['table'][m].get('overall', 0):.3f}")
    rows.append("| " + " | ".join(row) + " |")
    return "\n".join(rows)
