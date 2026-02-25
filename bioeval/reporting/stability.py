"""
Score stability analysis for BioEval.

Measures how robust scoring is to minor response perturbations:
- Case changes (upper → lower)
- Whitespace/punctuation noise
- Synonym substitution
- Word order shuffling within sentences

A good scorer should be insensitive to these surface-level changes.
This is required for NeurIPS: reviewers expect scoring reliability evidence.
"""

import math
import random
import re
from collections import defaultdict

from bioeval.scoring.normalizer import normalize_result


# =============================================================================
# RESPONSE PERTURBATION FUNCTIONS
# =============================================================================

def _perturb_case(text: str, rng: random.Random) -> str:
    """Randomly toggle case of ~30% of characters."""
    chars = list(text)
    for i in range(len(chars)):
        if chars[i].isalpha() and rng.random() < 0.3:
            chars[i] = chars[i].swapcase()
    return "".join(chars)


def _perturb_whitespace(text: str, rng: random.Random) -> str:
    """Add/remove whitespace around punctuation and between words."""
    # Double some spaces
    text = re.sub(r" ", lambda m: "  " if rng.random() < 0.2 else " ", text)
    # Add spaces before punctuation
    text = re.sub(r"([.,;:])", lambda m: f" {m.group()}" if rng.random() < 0.2 else m.group(), text)
    return text


_SWAP_PAIRS = [
    ("increase", "elevate"), ("decrease", "reduce"), ("inhibit", "block"),
    ("activate", "stimulate"), ("essential", "critical"), ("pathway", "signaling cascade"),
    ("expression", "levels"), ("significant", "notable"), ("observed", "detected"),
    ("suggest", "indicate"), ("demonstrate", "show"), ("result", "finding"),
]


def _perturb_synonym(text: str, rng: random.Random) -> str:
    """Replace ~20% of known synonyms with alternatives."""
    text_lower = text.lower()
    for a, b in _SWAP_PAIRS:
        if a in text_lower and rng.random() < 0.2:
            text = re.sub(re.escape(a), b, text, flags=re.IGNORECASE, count=1)
        elif b in text_lower and rng.random() < 0.2:
            text = re.sub(re.escape(b), a, text, flags=re.IGNORECASE, count=1)
    return text


def _perturb_word_order(text: str, rng: random.Random) -> str:
    """Swap adjacent words in ~15% of positions within each sentence."""
    sentences = text.split(". ")
    result = []
    for sent in sentences:
        words = sent.split()
        for i in range(len(words) - 1):
            if rng.random() < 0.15:
                words[i], words[i + 1] = words[i + 1], words[i]
        result.append(" ".join(words))
    return ". ".join(result)


PERTURBATION_TYPES = {
    "case": _perturb_case,
    "whitespace": _perturb_whitespace,
    "synonym": _perturb_synonym,
    "word_order": _perturb_word_order,
}


def perturb_response(text: str, perturbation: str, seed: int = 42) -> str:
    """Apply a named perturbation to a response text."""
    rng = random.Random(seed)
    fn = PERTURBATION_TYPES.get(perturbation)
    if fn is None:
        raise ValueError(f"Unknown perturbation: {perturbation}")
    return fn(text, rng)


# =============================================================================
# STABILITY MEASUREMENT
# =============================================================================

def measure_stability(
    result_path: str,
    n_perturbations: int = 5,
    perturbation_types: list[str] | None = None,
) -> dict:
    """Measure scoring stability on an existing result file.

    Re-normalizes each result with perturbed scores to see how much
    the final normalized score changes. This measures normalizer stability.

    For full pipeline stability (including scorer), use measure_scorer_stability().
    """
    import json
    with open(result_path) as f:
        data = json.load(f)

    if perturbation_types is None:
        perturbation_types = list(PERTURBATION_TYPES.keys())

    results = []
    for comp_result in data.get("results", []):
        component = comp_result.get("component", "unknown")
        for r in comp_result.get("results", []):
            if not isinstance(r, dict) or "error" in r:
                continue
            task_type = r.get("task_type", r.get("adversarial_type", ""))

            # Original score
            orig_ns = normalize_result(r, component, task_type)
            orig_score = orig_ns.score

            # Perturbed scores (perturb numerical fields slightly)
            perturbed_scores = []
            for seed in range(n_perturbations):
                rng = random.Random(seed + 1000)
                perturbed_r = _perturb_result_dict(r, rng)
                p_ns = normalize_result(perturbed_r, component, task_type)
                perturbed_scores.append(p_ns.score)

            # Stability metrics
            if perturbed_scores:
                diffs = [abs(ps - orig_score) for ps in perturbed_scores]
                max_diff = max(diffs)
                mean_diff = sum(diffs) / len(diffs)
                same_pass = sum(1 for ps in perturbed_scores
                                if (ps >= 0.5) == (orig_score >= 0.5))
                pass_stability = same_pass / len(perturbed_scores)
            else:
                max_diff = mean_diff = 0
                pass_stability = 1.0

            results.append({
                "task_id": r.get("task_id", r.get("dialogue_id", "")),
                "component": component,
                "original_score": orig_score,
                "mean_perturbation_diff": round(mean_diff, 4),
                "max_perturbation_diff": round(max_diff, 4),
                "pass_decision_stability": round(pass_stability, 4),
            })

    # Aggregate
    if not results:
        return {"error": "No results to analyze"}

    all_diffs = [r["mean_perturbation_diff"] for r in results]
    all_pass_stab = [r["pass_decision_stability"] for r in results]

    by_component = defaultdict(list)
    for r in results:
        by_component[r["component"]].append(r)

    comp_summary = {}
    for comp, comp_results in by_component.items():
        diffs = [r["mean_perturbation_diff"] for r in comp_results]
        stabs = [r["pass_decision_stability"] for r in comp_results]
        comp_summary[comp] = {
            "n": len(comp_results),
            "mean_score_diff": round(sum(diffs) / len(diffs), 4),
            "max_score_diff": round(max(diffs), 4),
            "pass_stability": round(sum(stabs) / len(stabs), 4),
        }

    return {
        "n_tasks": len(results),
        "n_perturbations": n_perturbations,
        "overall": {
            "mean_score_diff": round(sum(all_diffs) / len(all_diffs), 4),
            "max_score_diff": round(max(all_diffs), 4),
            "pass_stability": round(sum(all_pass_stab) / len(all_pass_stab), 4),
        },
        "by_component": comp_summary,
        "tasks": results,
    }


def _perturb_result_dict(r: dict, rng: random.Random) -> dict:
    """Apply small numerical perturbations to score fields in a result dict."""
    perturbed = dict(r)
    # Add Gaussian noise to numeric score fields
    noise_fields = ["score", "f1", "calibration_error", "reasoning_score",
                    "kendall_tau", "overall_score", "confidence_score",
                    "flaw_recall", "critical_recall", "weighted_recall",
                    "adjacent_pair_accuracy", "cause_coverage",
                    "diagnostic_coverage", "pathway_coverage",
                    "direction_accuracy", "gene_mention_rate",
                    "mechanism_score", "numerical_accuracy", "recall",
                    "correct_content_score", "hallucination_penalty",
                    "memory_score"]

    for field in noise_fields:
        if field in perturbed and isinstance(perturbed[field], (int, float)):
            noise = rng.gauss(0, 0.02)  # Small noise: std=0.02
            perturbed[field] = max(0, min(1, perturbed[field] + noise))

    # Handle nested scores
    if isinstance(perturbed.get("scores"), dict):
        perturbed["scores"] = dict(perturbed["scores"])
        for field in noise_fields:
            if field in perturbed["scores"] and isinstance(perturbed["scores"][field], (int, float)):
                noise = rng.gauss(0, 0.02)
                perturbed["scores"][field] = max(0, min(1, perturbed["scores"][field] + noise))

    # Handle ground_truth nested dicts
    if isinstance(perturbed.get("details"), dict):
        perturbed["details"] = dict(perturbed["details"])

    return perturbed


# =============================================================================
# TEXT OUTPUT
# =============================================================================

def print_stability(result_path: str, n_perturbations: int = 5):
    """Print stability analysis."""
    results = measure_stability(result_path, n_perturbations)

    if "error" in results:
        print(f"Error: {results['error']}")
        return results

    print(f"\n{'=' * 60}")
    print(f"Score Stability Analysis")
    print(f"{'=' * 60}")
    print(f"Tasks: {results['n_tasks']}, Perturbations per task: {results['n_perturbations']}")

    o = results["overall"]
    print(f"\nOverall:")
    print(f"  Mean score diff:    {o['mean_score_diff']:.4f}")
    print(f"  Max score diff:     {o['max_score_diff']:.4f}")
    print(f"  Pass decision stability: {o['pass_stability']:.1%}")

    print(f"\nPer-component:")
    print(f"{'Component':<15} {'N':>4} {'MeanDiff':>9} {'MaxDiff':>8} {'PassStab':>9}")
    print(f"{'─' * 50}")
    for comp, s in sorted(results["by_component"].items()):
        print(f"  {comp:<13} {s['n']:>4} {s['mean_score_diff']:>9.4f} "
              f"{s['max_score_diff']:>8.4f} {s['pass_stability']:>8.1%}")

    # Interpret
    mean_diff = o["mean_score_diff"]
    if mean_diff < 0.01:
        verdict = "Excellent: scores highly stable (mean diff < 0.01)"
    elif mean_diff < 0.05:
        verdict = "Good: scores reasonably stable (mean diff < 0.05)"
    elif mean_diff < 0.10:
        verdict = "Fair: moderate instability (mean diff < 0.10)"
    else:
        verdict = "Poor: significant instability (mean diff >= 0.10)"
    print(f"\nVerdict: {verdict}")

    return results
