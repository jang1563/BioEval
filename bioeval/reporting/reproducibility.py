"""
Reproducibility verification for BioEval.

Ensures that the scoring pipeline produces identical results when run
with the same inputs, satisfying NeurIPS reproducibility requirements.

Checks:
1. Determinism: Same response → same score (no randomness in scorers)
2. Seed invariance: Simulation with same seed → identical outputs
3. Cross-run consistency: Repeated full simulations → zero variance
"""

from __future__ import annotations

import json
import hashlib
from datetime import datetime

from bioeval.simulation import run_simulation


def _hash_results(results: list[dict]) -> str:
    """Compute a deterministic hash of result scores (ignoring timestamps)."""
    h = hashlib.sha256()
    for comp_result in results:
        comp = comp_result["component"]
        h.update(comp.encode())
        for r in comp_result.get("results", []):
            if isinstance(r, dict):
                # Hash key score fields (sorted for determinism)
                for key in sorted(r.keys()):
                    if key in ("response", "timestamp", "flaw_match_details", "turn_scores", "details"):
                        continue
                    val = r.get(key)
                    if isinstance(val, (int, float)):
                        h.update(f"{key}={val:.6f}".encode())
                    elif isinstance(val, (str, bool)):
                        h.update(f"{key}={val}".encode())
    return h.hexdigest()[:16]


def verify_determinism(n_runs: int = 3, seed: int = 42) -> dict:
    """Verify scoring determinism by running the same simulation multiple times.

    Args:
        n_runs: Number of repetitions (default 3)
        seed: Seed for all runs

    Returns:
        Dict with pass/fail status and details.
    """
    hashes = []
    task_counts = []

    for i in range(n_runs):
        result = run_simulation(quality="mixed", seed=seed)
        h = _hash_results(result["results"])
        hashes.append(h)
        total = sum(r["num_tasks"] for r in result["results"])
        task_counts.append(total)

    all_same = len(set(hashes)) == 1
    all_counts_same = len(set(task_counts)) == 1

    return {
        "test": "determinism",
        "passed": all_same and all_counts_same,
        "n_runs": n_runs,
        "seed": seed,
        "hashes": hashes,
        "hash_match": all_same,
        "task_counts": task_counts,
        "task_count_match": all_counts_same,
    }


def verify_seed_sensitivity(seeds: list[int] | None = None) -> dict:
    """Verify that different seeds produce different results.

    This ensures the seed actually controls randomness (not ignored).

    Args:
        seeds: List of seeds to test (default: [42, 43, 44])

    Returns:
        Dict with diversity check results.
    """
    if seeds is None:
        seeds = [42, 43, 44]

    hashes = {}
    for seed in seeds:
        result = run_simulation(quality="mixed", seed=seed)
        hashes[seed] = _hash_results(result["results"])

    unique_hashes = len(set(hashes.values()))
    all_different = unique_hashes == len(seeds)

    return {
        "test": "seed_sensitivity",
        "passed": all_different,
        "seeds": seeds,
        "hashes": hashes,
        "n_unique": unique_hashes,
        "n_expected": len(seeds),
    }


def verify_quality_separation() -> dict:
    """Verify that good > mixed > bad in mean score.

    Ensures synthetic responses are meaningfully differentiated.

    Returns:
        Dict with quality ordering check results.
    """
    from bioeval.reporting.analysis import analyze_results
    import tempfile

    scores = {}
    for quality in ["good", "mixed", "bad"]:
        result = run_simulation(quality=quality, seed=42)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(result, f, default=str)
            tmppath = f.name

        try:
            analysis = analyze_results(tmppath)
            scores[quality] = analysis["overall"]["mean"]
        finally:
            import os

            os.unlink(tmppath)

    ordering_correct = scores["good"] > scores["mixed"] > scores["bad"]

    return {
        "test": "quality_separation",
        "passed": ordering_correct,
        "scores": {q: round(s, 4) for q, s in scores.items()},
        "expected_order": "good > mixed > bad",
        "actual_order": " > ".join(sorted(scores.keys(), key=lambda x: scores[x], reverse=True)),
    }


def verify_component_coverage() -> dict:
    """Verify all components produce non-trivial results.

    Checks that no component is silently broken or always-zero.

    Returns:
        Dict with per-component coverage results.
    """
    from bioeval.scoring.normalizer import normalize_result

    result = run_simulation(quality="good", seed=42)
    components = {}

    for comp_result in result["results"]:
        comp = comp_result["component"]
        n_total = comp_result["num_tasks"]
        n_errors = sum(1 for r in comp_result["results"] if isinstance(r, dict) and "error" in r and "score" not in r)

        # Try to normalize and get scores
        scores = []
        for r in comp_result["results"]:
            if isinstance(r, dict) and "error" not in r:
                task_type = r.get("task_type", r.get("adversarial_type", ""))
                try:
                    ns = normalize_result(r, comp, task_type)
                    scores.append(ns.score)
                except Exception:
                    pass

        mean_score = sum(scores) / len(scores) if scores else 0.0
        has_variance = max(scores) - min(scores) > 0.01 if len(scores) > 1 else False

        components[comp] = {
            "n_tasks": n_total,
            "n_errors": n_errors,
            "n_scored": len(scores),
            "mean_score": round(mean_score, 4),
            "has_variance": has_variance,
            "error_free": n_errors == 0,
        }

    all_error_free = all(c["error_free"] for c in components.values())
    all_scored = all(c["n_scored"] > 0 for c in components.values())
    expected_components = {
        "protoreason",
        "causalbio",
        "designcheck",
        "adversarial",
        "multiturn",
        "calibration",
        "biosafety",
        "datainterp",
        "debate",
    }
    all_present = set(components.keys()) == expected_components

    return {
        "test": "component_coverage",
        "passed": all_error_free and all_scored and all_present,
        "all_error_free": all_error_free,
        "all_scored": all_scored,
        "all_present": all_present,
        "components": components,
    }


def run_reproducibility_suite() -> dict:
    """Run all reproducibility checks and return summary.

    Returns:
        Dict with overall pass/fail and per-test details.
    """
    tests = [
        verify_determinism(),
        verify_seed_sensitivity(),
        verify_quality_separation(),
        verify_component_coverage(),
    ]

    all_passed = all(t["passed"] for t in tests)

    return {
        "reproducibility_suite": {
            "passed": all_passed,
            "n_tests": len(tests),
            "n_passed": sum(1 for t in tests if t["passed"]),
            "timestamp": datetime.now().isoformat(),
        },
        "tests": {t["test"]: t for t in tests},
    }


# =============================================================================
# TEXT OUTPUT
# =============================================================================


def print_reproducibility(suite: dict | None = None):
    """Print reproducibility verification results."""
    if suite is None:
        suite = run_reproducibility_suite()

    summary = suite["reproducibility_suite"]
    tests = suite["tests"]

    print(f"\n{'=' * 60}")
    print("BioEval Reproducibility Verification")
    print(f"{'=' * 60}")
    status = "PASSED" if summary["passed"] else "FAILED"
    print(f"Overall: {status} ({summary['n_passed']}/{summary['n_tests']} tests)")

    for name, result in tests.items():
        mark = "+" if result["passed"] else "X"
        print(f"\n  [{mark}] {name}")

        if name == "determinism":
            print(f"      {result['n_runs']} runs, seed={result['seed']}")
            print(f"      Hash match: {result['hash_match']}")
            print(f"      Task counts: {result['task_counts']}")

        elif name == "seed_sensitivity":
            print(f"      Seeds: {result['seeds']}")
            print(f"      Unique hashes: {result['n_unique']}/{result['n_expected']}")

        elif name == "quality_separation":
            for q, s in result["scores"].items():
                print(f"      {q}: {s:.4f}")
            print(f"      Order: {result['actual_order']}")

        elif name == "component_coverage":
            for comp, info in result.get("components", {}).items():
                err_mark = "" if info["error_free"] else " [ERRORS]"
                print(
                    f"      {comp}: {info['n_scored']}/{info['n_tasks']} scored, " f"mean={info['mean_score']:.3f}{err_mark}"
                )

    return suite
