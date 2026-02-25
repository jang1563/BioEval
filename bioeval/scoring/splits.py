"""
Private test split and multi-run aggregation for BioEval.

Provides:
- Deterministic 80/20 public/private split for contamination detection
- Multi-run aggregation with Bayesian Beta-Binomial confidence intervals
"""

import hashlib
import math
from typing import Any


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
# MULTI-RUN AGGREGATION WITH BAYESIAN CIs
# =============================================================================

def beta_binomial_ci(
    successes: int, trials: int,
    alpha_prior: float = 1.0, beta_prior: float = 1.0,
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
            # Count pass/total for binary metrics
            n_tasks = cr.get("num_tasks", len(results))
            n_passed = 0
            score_sum = 0.0
            score_count = 0
            for r in results:
                if isinstance(r, dict):
                    # Try common score fields
                    score = r.get("score", r.get("scores", {}).get("score") if isinstance(r.get("scores"), dict) else None)
                    if isinstance(score, (int, float)):
                        score_sum += score
                        score_count += 1
                        if score >= 0.5:
                            n_passed += 1
                    elif r.get("effect_correct") or r.get("is_correct"):
                        n_passed += 1
                        score_sum += 1.0
                        score_count += 1
                    else:
                        score_count += 1

            if score_count > 0:
                run_scores.append({
                    "mean_score": score_sum / score_count,
                    "pass_rate": n_passed / n_tasks if n_tasks > 0 else 0,
                    "n_tasks": n_tasks,
                    "n_passed": n_passed,
                })

        if not run_scores:
            aggregated["by_component"][comp] = {"n_runs": 0}
            continue

        # Aggregate across runs
        mean_scores = [rs["mean_score"] for rs in run_scores]
        pass_rates = [rs["pass_rate"] for rs in run_scores]

        overall_mean = sum(mean_scores) / len(mean_scores)
        overall_std = math.sqrt(sum((s - overall_mean) ** 2 for s in mean_scores) / max(1, len(mean_scores) - 1)) if len(mean_scores) > 1 else 0.0

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
