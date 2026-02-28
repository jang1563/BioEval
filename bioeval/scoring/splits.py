"""
Private test split and multi-run aggregation for BioEval.

Provides:
- Deterministic 80/20 public/private split for contamination detection
- Multi-run aggregation with Bayesian Beta-Binomial confidence intervals
"""

from __future__ import annotations

import hashlib
import logging
import math
from typing import Any, Optional

logger = logging.getLogger(__name__)

# =============================================================================
# DETERMINISTIC TEST SPLIT
# =============================================================================

# Salt ensures split is stable but not trivially reversible
_SPLIT_SALT = "bioeval_v1_private_split"
_PRIVATE_FRACTION = 0.20  # 20% private holdback


def get_split(task_id: str) -> str:
    """Return 'public' or 'private' for a given task_id.

    Uses a deterministic hash so the split is reproducible across runs.
    """
    h = hashlib.sha256(f"{_SPLIT_SALT}:{task_id}".encode()).hexdigest()
    # Use first 8 hex chars → 32-bit uniform integer
    val = int(h[:8], 16) / 0xFFFFFFFF
    return "private" if val < _PRIVATE_FRACTION else "public"


def split_tasks(tasks: list[Any], id_attr: str = "id") -> dict[str, list[Any]]:
    """Split a list of tasks into public and private sets.

    Args:
        tasks: List of task objects
        id_attr: Attribute name for task ID (default "id")

    Returns:
        {"public": [...], "private": [...]}
    """
    public, private = [], []
    for t in tasks:
        tid = getattr(t, id_attr, None) or (t.get("id") if isinstance(t, dict) else str(t))
        if get_split(str(tid)) == "private":
            private.append(t)
        else:
            public.append(t)
    return {"public": public, "private": private}


def get_split_summary(tasks: list[Any], id_attr: str = "id") -> dict:
    """Get summary statistics about the split."""
    splits = split_tasks(tasks, id_attr)
    return {
        "total": len(tasks),
        "public": len(splits["public"]),
        "private": len(splits["private"]),
        "private_fraction": len(splits["private"]) / len(tasks) if tasks else 0,
    }


# =============================================================================
# CANARY TASK CONTAMINATION DETECTION
# =============================================================================

# Canary tasks contain deliberate "fingerprint" answers that should only be
# known to someone who has seen the private task set.  If a model produces
# the exact fingerprint answer, it is strong evidence of contamination.
#
# Each canary is a (task_id, fingerprint_answer) pair.  The fingerprint is a
# short string that is NOT a plausible answer from first principles but IS
# present in the ground-truth JSON.

CANARY_TASKS: dict[str, str] = {
    # Format: task_id → fingerprint substring (case-insensitive match)
    "canary_proto_001": "zigzag-helicase-9",
    "canary_causal_001": "reverse-phospho-cascade-7",
    "canary_design_001": "inverted-blinding-matrix-3",
}


def check_canary_contamination(
    responses: dict[str, str],
) -> dict:
    """Check model responses for canary fingerprints.

    Args:
        responses: Mapping of task_id → model response text.

    Returns:
        {
            "n_canaries_tested": int,
            "n_contaminated": int,
            "contaminated_ids": [str, ...],
            "verdict": "CLEAN" | "CONTAMINATED",
        }
    """
    contaminated = []
    tested = 0
    for task_id, fingerprint in CANARY_TASKS.items():
        if task_id not in responses:
            continue
        tested += 1
        if fingerprint.lower() in responses[task_id].lower():
            contaminated.append(task_id)

    verdict = "CONTAMINATED" if contaminated else "CLEAN"
    return {
        "n_canaries_tested": tested,
        "n_contaminated": len(contaminated),
        "contaminated_ids": contaminated,
        "verdict": verdict,
    }


# =============================================================================
# MULTI-RUN AGGREGATION WITH BAYESIAN CIs
# =============================================================================


def beta_binomial_ci(
    successes: int,
    trials: int,
    alpha_prior: float = 1.0,
    beta_prior: float = 1.0,
    credible_level: float = 0.95,
) -> dict:
    """Compute Bayesian Beta-Binomial credible interval.

    Uses conjugate Beta prior with equal-tailed credible interval.
    Default: uniform prior (alpha=beta=1).

    Returns:
        {mean, lower, upper, alpha_post, beta_post}
    """
    alpha_post = alpha_prior + successes
    beta_post = beta_prior + (trials - successes)

    mean = alpha_post / (alpha_post + beta_post)

    # Approximate credible interval using normal approximation to Beta
    # For small n, use quantile function
    try:
        from scipy.stats import beta as beta_dist

        tail = (1 - credible_level) / 2
        lower = beta_dist.ppf(tail, alpha_post, beta_post)
        upper = beta_dist.ppf(1 - tail, alpha_post, beta_post)
    except ImportError:
        # Fallback: normal approximation
        var = (alpha_post * beta_post) / ((alpha_post + beta_post) ** 2 * (alpha_post + beta_post + 1))
        std = math.sqrt(var)
        z = 1.96 if credible_level == 0.95 else 2.576  # 95% or 99%
        lower = max(0.0, mean - z * std)
        upper = min(1.0, mean + z * std)

    return {
        "mean": round(mean, 4),
        "lower": round(lower, 4),
        "upper": round(upper, 4),
        "alpha_post": alpha_post,
        "beta_post": beta_post,
    }


def aggregate_multi_run(run_results: list[dict]) -> dict:
    """Aggregate results from multiple runs of the same evaluation.

    Args:
        run_results: List of result dicts, each with a "results" key
                     containing per-task results.

    Returns:
        Aggregated statistics with CIs.
    """
    if not run_results:
        return {"error": "No runs provided"}

    n_runs = len(run_results)

    # Collect per-component scores across runs
    by_component: dict[str, list[dict]] = {}
    for run in run_results:
        for comp_result in run.get("results", []):
            comp = comp_result.get("component", "unknown")
            if comp not in by_component:
                by_component[comp] = []
            by_component[comp].append(comp_result)

    aggregated = {
        "n_runs": n_runs,
        "by_component": {},
    }

    for comp, comp_runs in by_component.items():
        # Extract numeric scores from each run
        run_scores = []
        for cr in comp_runs:
            results = cr.get("results", [])
            if not results:
                continue
            n_passed = 0
            score_values: list[float] = []
            for r in results:
                if not isinstance(r, dict) or ("error" in r and "score" not in r):
                    continue
                score = _extract_primary_score(comp, r)
                if score is None:
                    task_id = r.get("task_id", "unknown")
                    logger.warning(
                        "Could not extract score for %s task %s; " "available keys: scores=%s, top=%s",
                        comp,
                        task_id,
                        list(r.get("scores", {}).keys()) if isinstance(r.get("scores"), dict) else "N/A",
                        [k for k in r if k not in ("response", "prompt", "scores")],
                    )
                    continue
                score_values.append(score)
                if score >= 0.5:
                    n_passed += 1

            n_scored = len(score_values)
            if n_scored > 0:
                run_scores.append(
                    {
                        "mean_score": sum(score_values) / n_scored,
                        "pass_rate": n_passed / n_scored,
                        "n_tasks": n_scored,
                        "n_passed": n_passed,
                    }
                )

        if not run_scores:
            aggregated["by_component"][comp] = {"n_runs": 0}
            continue

        # Aggregate across runs
        mean_scores = [rs["mean_score"] for rs in run_scores]
        pass_rates = [rs["pass_rate"] for rs in run_scores]

        overall_mean = sum(mean_scores) / len(mean_scores)
        overall_std = (
            math.sqrt(sum((s - overall_mean) ** 2 for s in mean_scores) / max(1, len(mean_scores) - 1))
            if len(mean_scores) > 1
            else 0.0
        )

        # Beta-Binomial CI on pass rate
        total_passed = sum(rs["n_passed"] for rs in run_scores)
        total_tasks = sum(rs["n_tasks"] for rs in run_scores)
        ci = beta_binomial_ci(total_passed, total_tasks)

        aggregated["by_component"][comp] = {
            "n_runs": len(run_scores),
            "mean_score": round(overall_mean, 4),
            "std_score": round(overall_std, 4),
            "pass_rate_ci": ci,
            "per_run_scores": [round(s, 4) for s in mean_scores],
        }

    return aggregated


def _extract_primary_score(component: str, task_result: dict) -> Optional[float]:
    """Extract a canonical per-task score in [0, 1] when available."""
    scores_obj = task_result.get("scores", {})
    s = scores_obj if isinstance(scores_obj, dict) else {}

    def _get_num(d: dict, key: str) -> Optional[float]:
        v = d.get(key)
        return float(v) if isinstance(v, (int, float)) else None

    if component == "protoreason":
        for key in ("adjacent_pair_accuracy", "recall", "numerical_accuracy", "cause_coverage"):
            v = _get_num(s, key)
            if v is not None:
                return v
            v = _get_num(task_result, key)
            if v is not None:
                return v
        return None

    if component == "causalbio":
        # Prefer combined_score (available for all 4 task types: knockout, pathway,
        # epistasis, drug_response) as it captures effect + reasoning + context.
        for key in ("combined_score",):
            v = _get_num(s, key)
            if v is not None:
                return v
            v = _get_num(task_result, key)
            if v is not None:
                return v
        # Fallback: binary effect correctness or mechanism score
        effect = s.get("effect_correct", task_result.get("effect_correct"))
        if isinstance(effect, bool):
            return 1.0 if effect else 0.0
        for key in ("mechanism_score",):
            v = _get_num(s, key)
            if v is not None:
                return v
            v = _get_num(task_result, key)
            if v is not None:
                return v
        return None

    if component == "designcheck":
        # Keep backward compatibility with existing reporting pipeline.
        for key in ("f1", "composite_score"):
            v = _get_num(s, key)
            if v is not None:
                return v
            v = _get_num(task_result, key)
            if v is not None:
                return v
        return None

    if component == "adversarial":
        v = _get_num(s, "score")
        if v is not None:
            return v
        return _get_num(task_result, "score")

    if component == "multiturn":
        v = _get_num(s, "overall_score")
        if v is not None:
            return v
        return _get_num(task_result, "overall_score")

    if component == "calibration":
        cal_err = _get_num(s, "calibration_error")
        if cal_err is None:
            cal_err = _get_num(task_result, "calibration_error")
        if cal_err is None:
            return None
        return 1.0 - abs(cal_err)

    if component in ("biosafety", "datainterp"):
        for key in ("score",):
            v = _get_num(task_result, key)
            if v is not None:
                return v
            v = _get_num(s, key)
            if v is not None:
                return v
        return None

    if component == "debate":
        v = _get_num(s, "composite_score")
        if v is not None:
            return v
        return _get_num(task_result, "composite_score")

    # Generic fallback
    for key in ("score", "f1", "accuracy"):
        v = _get_num(s, key)
        if v is not None:
            return v
        v = _get_num(task_result, key)
        if v is not None:
            return v
    return None
