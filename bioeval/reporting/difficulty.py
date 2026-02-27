"""
Task difficulty analysis and rebalancing for BioEval.

Analyzes the difficulty distribution of tasks across components and
provides rebalancing recommendations. A well-designed benchmark should
have a spread of difficulty levels, not clustering at extremes.

Difficulty levels:
- Easy (score >= 0.8): Most models should pass
- Medium (0.4 <= score < 0.8): Discriminating tasks
- Hard (score < 0.4): Challenging for all models

For NeurIPS, reviewers expect evidence that the benchmark
differentiates between models (not all-easy or all-hard).
"""

import json
import math
from collections import defaultdict

from bioeval.scoring.normalizer import normalize_result


def analyze_difficulty(result_path: str) -> dict:
    """Analyze task difficulty distribution from results.

    Args:
        result_path: Path to result JSON file

    Returns:
        Dict with difficulty analysis and rebalancing recommendations.
    """
    with open(result_path) as f:
        data = json.load(f)

    by_component = defaultdict(list)
    all_items = []

    for comp_result in data.get("results", []):
        comp = comp_result.get("component", "unknown")
        for r in comp_result.get("results", []):
            if not isinstance(r, dict) or ("error" in r and "score" not in r):
                continue
            task_type = r.get("task_type", r.get("adversarial_type", ""))
            task_id = r.get("task_id", r.get("dialogue_id", ""))
            try:
                ns = normalize_result(r, comp, task_type)
                item = {
                    "task_id": task_id,
                    "component": comp,
                    "task_type": task_type,
                    "score": ns.score,
                    "difficulty": _classify_difficulty(ns.score),
                }
                by_component[comp].append(item)
                all_items.append(item)
            except Exception:
                pass

    if not all_items:
        return {"error": "No scoreable results found"}

    # Overall distribution
    overall = _compute_distribution(all_items)

    # Per-component
    comp_distributions = {}
    for comp, items in by_component.items():
        comp_distributions[comp] = _compute_distribution(items)

    # Per-task-type
    by_type = defaultdict(list)
    for item in all_items:
        by_type[item["task_type"]].append(item)
    type_distributions = {}
    for tt, items in by_type.items():
        type_distributions[tt] = _compute_distribution(items)

    # Recommendations
    recommendations = _generate_recommendations(overall, comp_distributions)

    # Ideal vs actual comparison
    ideal_target = {"easy": 0.25, "medium": 0.50, "hard": 0.25}
    balance_score = _compute_balance_score(overall, ideal_target)

    return {
        "n_tasks": len(all_items),
        "overall": overall,
        "by_component": comp_distributions,
        "by_task_type": type_distributions,
        "balance_score": round(balance_score, 4),
        "ideal_target": ideal_target,
        "recommendations": recommendations,
        "hardest_tasks": sorted(all_items, key=lambda x: x["score"])[:5],
        "easiest_tasks": sorted(all_items, key=lambda x: x["score"], reverse=True)[:5],
    }


def _classify_difficulty(score: float) -> str:
    """Classify a score into difficulty level."""
    if score >= 0.8:
        return "easy"
    elif score >= 0.4:
        return "medium"
    else:
        return "hard"


def _compute_distribution(items: list[dict]) -> dict:
    """Compute difficulty distribution stats for a set of items."""
    n = len(items)
    if n == 0:
        return {"n": 0}

    scores = [item["score"] for item in items]
    mean = sum(scores) / n
    variance = sum((s - mean) ** 2 for s in scores) / n if n > 1 else 0
    std = math.sqrt(variance)

    easy = sum(1 for item in items if item["difficulty"] == "easy")
    medium = sum(1 for item in items if item["difficulty"] == "medium")
    hard = sum(1 for item in items if item["difficulty"] == "hard")

    return {
        "n": n,
        "mean": round(mean, 4),
        "std": round(std, 4),
        "min": round(min(scores), 4),
        "max": round(max(scores), 4),
        "easy": easy,
        "medium": medium,
        "hard": hard,
        "pct_easy": round(easy / n * 100, 1),
        "pct_medium": round(medium / n * 100, 1),
        "pct_hard": round(hard / n * 100, 1),
    }


def _compute_balance_score(distribution: dict, target: dict) -> float:
    """Compute how well the actual distribution matches the ideal target.

    Returns 0-1 score where 1 = perfect match to ideal distribution.
    Uses chi-squared-like measure.
    """
    n = distribution["n"]
    if n == 0:
        return 0.0

    actual = {
        "easy": distribution["easy"] / n,
        "medium": distribution["medium"] / n,
        "hard": distribution["hard"] / n,
    }

    # Mean absolute deviation from target
    mad = sum(abs(actual[k] - target[k]) for k in target) / len(target)
    # Convert to 0-1 score (0 deviation = 1.0 score)
    return max(0, 1.0 - mad * 2)  # Scale: 0.5 mad → 0.0 score


def _generate_recommendations(overall: dict, by_component: dict) -> list[str]:
    """Generate rebalancing recommendations."""
    recs = []
    n = overall["n"]
    if n == 0:
        return recs

    # Overall imbalance
    pct_easy = overall["pct_easy"]
    pct_hard = overall["pct_hard"]
    pct_medium = overall["pct_medium"]

    if pct_easy > 50:
        recs.append(
            f"Too many easy tasks ({pct_easy:.0f}%). Add harder tasks or "
            "tighten scoring criteria to improve discrimination."
        )
    if pct_hard > 50:
        recs.append(
            f"Too many hard tasks ({pct_hard:.0f}%). Consider adding baseline " "tasks that competent models should pass."
        )
    if pct_medium < 30:
        recs.append(
            f"Only {pct_medium:.0f}% medium-difficulty tasks. The ideal is ~50%. "
            "Medium tasks provide the best model discrimination."
        )

    # Per-component imbalance
    for comp, dist in by_component.items():
        cn = dist["n"]
        if cn < 3:
            continue
        c_easy = dist["pct_easy"]
        c_hard = dist["pct_hard"]

        if c_easy > 70:
            recs.append(f"{comp}: {c_easy:.0f}% easy — add challenging tasks " "for this component.")
        if c_hard > 70:
            recs.append(f"{comp}: {c_hard:.0f}% hard — add easier baseline tasks " "for this component.")

    # Cross-component gap
    if by_component:
        means = {c: d["mean"] for c, d in by_component.items() if d["n"] > 0}
        if means:
            max_c = max(means, key=means.get)
            min_c = min(means, key=means.get)
            gap = means[max_c] - means[min_c]
            if gap > 0.3:
                recs.append(
                    f"Cross-component gap: {max_c} ({means[max_c]:.2f}) vs "
                    f"{min_c} ({means[min_c]:.2f}). Consider rebalancing "
                    "difficulty across components for fairer comparison."
                )

    if not recs:
        recs.append("Difficulty distribution looks well-balanced. No changes needed.")

    return recs


# =============================================================================
# TEXT OUTPUT
# =============================================================================


def print_difficulty(result_path: str):
    """Print difficulty analysis and recommendations."""
    result = analyze_difficulty(result_path)

    if "error" in result:
        print(f"Error: {result['error']}")
        return result

    print(f"\n{'=' * 60}")
    print("Task Difficulty Analysis")
    print(f"{'=' * 60}")
    print(f"Tasks: {result['n_tasks']}")
    print(f"Balance score: {result['balance_score']:.2f} (1.0 = ideal)")

    o = result["overall"]
    print(f"\nOverall Distribution:")
    print(f"  Mean score: {o['mean']:.3f} (std: {o['std']:.3f})")
    print(f"  Easy   (>=0.8): {o['easy']:>3} ({o['pct_easy']:>5.1f}%)")
    print(f"  Medium (0.4-0.8): {o['medium']:>3} ({o['pct_medium']:>5.1f}%)")
    print(f"  Hard   (<0.4): {o['hard']:>3} ({o['pct_hard']:>5.1f}%)")
    ideal = result["ideal_target"]
    print(f"  Target:         {ideal['easy']*100:.0f}% / {ideal['medium']*100:.0f}% / {ideal['hard']*100:.0f}%")

    print(f"\nPer-Component:")
    print(f"{'Component':<15} {'N':>4} {'Mean':>6} {'Easy':>5} {'Med':>5} {'Hard':>5}")
    print(f"{'─' * 45}")
    for comp, d in sorted(result["by_component"].items()):
        print(
            f"  {comp:<13} {d['n']:>4} {d['mean']:>6.3f} "
            f"{d['pct_easy']:>4.0f}% {d['pct_medium']:>4.0f}% {d['pct_hard']:>4.0f}%"
        )

    print(f"\nHardest tasks:")
    for t in result["hardest_tasks"][:5]:
        print(f"  {t['task_id']:<25} {t['component']:<13} {t['score']:.3f}")

    print(f"\nEasiest tasks:")
    for t in result["easiest_tasks"][:5]:
        print(f"  {t['task_id']:<25} {t['component']:<13} {t['score']:.3f}")

    print(f"\nRecommendations:")
    for i, rec in enumerate(result["recommendations"], 1):
        print(f"  {i}. {rec}")

    return result


# =============================================================================
# TASK METADATA ANALYSIS (INTENDED DIFFICULTY & DOMAIN COVERAGE)
# =============================================================================


def analyze_task_metadata(data_tier: str = "all") -> dict:
    """Analyze intended difficulty and domain coverage across all tasks.

    Reads task definitions (not results) to report the benchmark's
    structural properties — useful for NeurIPS paper table.

    Args:
        data_tier: Data tier to load tasks from.

    Returns:
        Dict with task counts, difficulty distribution, domain coverage.
    """
    from collections import defaultdict

    components = {}
    domains = defaultdict(int)
    difficulties = defaultdict(int)
    total = 0

    # ProtoReason
    try:
        from bioeval.simulation import _bypass_model_init

        with _bypass_model_init():
            from bioeval.protoreason.evaluator import ProtoReasonEvaluator

            pr = ProtoReasonEvaluator("dummy")
            tasks = pr.load_tasks(data_tier=data_tier)
        by_type = defaultdict(int)
        for t in tasks:
            by_type[t.task_type] += 1
        components["protoreason"] = {"n": len(tasks), "task_types": dict(by_type)}
        total += len(tasks)
        for t in tasks:
            domains["molecular_biology"] += 1
    except Exception:
        pass

    # CausalBio
    try:
        with _bypass_model_init():
            from bioeval.causalbio.evaluator import CausalBioEvaluator

            cb = CausalBioEvaluator("dummy")
            tasks = cb.load_tasks(data_tier=data_tier)
        by_type = defaultdict(int)
        for t in tasks:
            by_type[t.task_type] += 1
        components["causalbio"] = {"n": len(tasks), "task_types": dict(by_type)}
        total += len(tasks)
        for t in tasks:
            domains["cancer_biology"] += 1
    except Exception:
        pass

    # DesignCheck
    try:
        with _bypass_model_init():
            from bioeval.designcheck.evaluator import DesignCheckEvaluator

            dc = DesignCheckEvaluator("dummy")
            tasks = dc.load_tasks(data_tier=data_tier)
        components["designcheck"] = {"n": len(tasks), "task_types": {"flaw_detection": len(tasks)}}
        total += len(tasks)
        for _ in tasks:
            domains["experimental_design"] += 1
    except Exception:
        pass

    # Adversarial
    try:
        from bioeval.adversarial.tasks import ADVERSARIAL_TASKS

        by_type = defaultdict(int)
        by_domain = defaultdict(int)
        by_diff = defaultdict(int)
        for t in ADVERSARIAL_TASKS:
            atype = t.adversarial_type.value if hasattr(t.adversarial_type, "value") else str(t.adversarial_type)
            by_type[atype] += 1
            by_domain[t.domain] += 1
            by_diff[t.difficulty] += 1
            difficulties[t.difficulty] += 1
            domains[t.domain] += 1
        components["adversarial"] = {
            "n": len(ADVERSARIAL_TASKS),
            "task_types": dict(by_type),
            "domains": dict(by_domain),
            "intended_difficulty": dict(by_diff),
        }
        total += len(ADVERSARIAL_TASKS)
    except Exception:
        pass

    # MultiTurn
    try:
        from bioeval.multiturn.dialogues import DIALOGUES
        from bioeval.multiturn.extended_data import EXTENDED_DIALOGUES

        if data_tier in ("extended", "all"):
            dialogues = list(DIALOGUES) + EXTENDED_DIALOGUES
        else:
            dialogues = list(DIALOGUES)
        by_type = defaultdict(int)
        by_domain = defaultdict(int)
        by_diff = defaultdict(int)
        for d in dialogues:
            dtype = d.dialogue_type.value if hasattr(d.dialogue_type, "value") else str(d.dialogue_type)
            by_type[dtype] += 1
            by_domain[d.domain] += 1
            diff = d.difficulty if hasattr(d, "difficulty") else "medium"
            by_diff[diff] += 1
            difficulties[diff] += 1
            domains[d.domain] += 1
        components["multiturn"] = {
            "n": len(dialogues),
            "task_types": dict(by_type),
            "domains": dict(by_domain),
            "intended_difficulty": dict(by_diff),
        }
        total += len(dialogues)
    except Exception:
        pass

    # Calibration
    try:
        from bioeval.scoring.calibration import CALIBRATION_TEST_TASKS

        by_type = defaultdict(int)
        for t in CALIBRATION_TEST_TASKS:
            by_type[t["correct_behavior"]] += 1
        components["calibration"] = {
            "n": len(CALIBRATION_TEST_TASKS),
            "task_types": dict(by_type),
        }
        total += len(CALIBRATION_TEST_TASKS)
    except Exception:
        pass

    # BioSafety
    try:
        from bioeval.biosafety.tasks import BIOSAFETY_TASKS

        by_type = defaultdict(int)
        by_domain = defaultdict(int)
        by_diff = defaultdict(int)
        for t in BIOSAFETY_TASKS:
            stype = t.safety_type.value if hasattr(t.safety_type, "value") else str(t.safety_type)
            by_type[stype] += 1
            by_domain[t.domain] += 1
            by_diff[t.difficulty] += 1
            difficulties[t.difficulty] += 1
            domains[t.domain] += 1
        components["biosafety"] = {
            "n": len(BIOSAFETY_TASKS),
            "task_types": dict(by_type),
            "domains": dict(by_domain),
            "intended_difficulty": dict(by_diff),
        }
        total += len(BIOSAFETY_TASKS)
    except Exception:
        pass

    # DataInterp
    try:
        from bioeval.datainterp.tasks import DATA_INTERP_TASKS

        by_type = defaultdict(int)
        by_domain = defaultdict(int)
        by_diff = defaultdict(int)
        for t in DATA_INTERP_TASKS:
            itype = t.interp_type.value if hasattr(t.interp_type, "value") else str(t.interp_type)
            by_type[itype] += 1
            by_domain[t.domain] += 1
            by_diff[t.difficulty] += 1
            difficulties[t.difficulty] += 1
            domains[t.domain] += 1
        components["datainterp"] = {
            "n": len(DATA_INTERP_TASKS),
            "task_types": dict(by_type),
            "domains": dict(by_domain),
            "intended_difficulty": dict(by_diff),
        }
        total += len(DATA_INTERP_TASKS)
    except Exception:
        pass

    return {
        "total_tasks": total,
        "data_tier": data_tier,
        "components": components,
        "domain_coverage": dict(domains),
        "n_domains": len(domains),
        "intended_difficulty": dict(difficulties),
    }


def print_task_metadata(data_tier: str = "all"):
    """Print task metadata analysis."""
    meta = analyze_task_metadata(data_tier)

    print(f"\n{'=' * 60}")
    print("BioEval Task Metadata")
    print(f"{'=' * 60}")
    print(f"Data tier: {meta['data_tier']}")
    print(f"Total tasks: {meta['total_tasks']}")
    print(f"Unique domains: {meta['n_domains']}")

    print(f"\nPer-Component:")
    print(f"{'Component':<15} {'N':>4}  Task Types")
    print(f"{'─' * 60}")
    for comp, info in sorted(meta["components"].items()):
        types_str = ", ".join(f"{k}({v})" for k, v in sorted(info["task_types"].items()))
        print(f"  {comp:<13} {info['n']:>4}  {types_str}")

    if meta["intended_difficulty"]:
        print(f"\nIntended Difficulty (from task metadata):")
        for diff, count in sorted(meta["intended_difficulty"].items()):
            print(f"  {diff:<10} {count}")

    print(f"\nDomain Coverage:")
    for domain, count in sorted(meta["domain_coverage"].items(), key=lambda x: -x[1]):
        print(f"  {domain:<25} {count:>3}")

    return meta
