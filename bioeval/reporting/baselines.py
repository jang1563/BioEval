"""Random and naive baselines for BioEval components.

Provides analytically derived or Monte-Carlo estimated baseline scores
for each component, enabling comparison of model performance against
chance-level performance.  No API calls required.
"""

from __future__ import annotations

import math
import random


def compute_random_baselines(seed: int = 42) -> dict[str, dict]:
    """Compute expected random-baseline scores for each component.

    These represent the expected score if responses contained no
    meaningful content (random predictions, no reasoning, etc.).

    Returns:
        Dict mapping component name to baseline info.
    """
    rng = random.Random(seed)

    # ProtoReason: step_ordering — random permutation gives tau ~ 0
    # normalized score = (tau + 1) / 2 = (0 + 1) / 2 = 0.5
    proto_ordering = 0.50
    # calculation — random number → accuracy ~ 0
    proto_calculation = 0.0
    # troubleshooting — random → coverage ~ 0 for all sub-scores
    proto_troubleshooting = 0.0
    # Average across task types (weighted by approximate task counts)
    proto_avg = (proto_ordering * 4 + proto_calculation * 5 + proto_troubleshooting * 4) / 13

    # CausalBio: knockout — binary prediction gives 0.5 accuracy
    # score = 0.6 * correct + 0.4 * reasoning
    # random: correct ~ 0.5, reasoning ~ 0 → 0.6 * 0.5 = 0.30
    causal_knockout = 0.30
    # pathway — random coverage ~ 0
    causal_pathway = 0.0
    # epistasis — binary, same as knockout
    causal_epistasis = 0.30
    causal_avg = (causal_knockout * 5 + causal_pathway * 4 + causal_epistasis * 4) / 13

    # DesignCheck: random flaw guessing → very low F1
    # With ~5 possible flaws per design and random guessing,
    # expected precision and recall are both very low
    designcheck = 0.05

    # Adversarial: always accepting premise → score 0
    adversarial = 0.0

    # MultiTurn: no memory across turns → ~0.2 (some turns may pass trivially)
    multiturn = 0.20

    # Calibration: always 50% confidence
    # For tasks requiring high confidence: error = |1.0 - 0.5| = 0.5
    # For tasks requiring low confidence: error = |0.0 - 0.5| = 0.5
    # Average calibration error ~ 0.5 → score = 1 - 0.5 = 0.5
    calibration = 0.50

    # BioSafety: generic boilerplate → element coverage ~ 0
    biosafety = 0.10

    # DataInterp: no numerical answer → accuracy 0, interpretation ~ 0
    datainterp = 0.05

    # Debate: single model (no debate correction) → roughly
    # accuracy ~ 0.5 (binary), reasoning ~ 0, no correction
    debate = 0.25 * 0.5 + 0.10 * 1.0  # accuracy + efficiency

    return {
        "protoreason": {
            "random_baseline": round(proto_avg, 3),
            "method": "analytical (ordering: tau=0, others: coverage=0)",
            "components": {
                "step_ordering": proto_ordering,
                "calculation": proto_calculation,
                "troubleshooting": proto_troubleshooting,
            },
        },
        "causalbio": {
            "random_baseline": round(causal_avg, 3),
            "method": "analytical (binary prediction 50%, reasoning=0)",
            "components": {
                "knockout_prediction": causal_knockout,
                "pathway_reasoning": causal_pathway,
                "epistasis": causal_epistasis,
            },
        },
        "designcheck": {
            "random_baseline": designcheck,
            "method": "analytical (random flaw guessing, low F1)",
        },
        "adversarial": {
            "random_baseline": adversarial,
            "method": "analytical (always accept premise → score 0)",
        },
        "multiturn": {
            "random_baseline": multiturn,
            "method": "estimated (no memory across turns)",
        },
        "calibration": {
            "random_baseline": calibration,
            "method": "analytical (always 50% confidence → error 0.5)",
        },
        "biosafety": {
            "random_baseline": biosafety,
            "method": "estimated (generic safety boilerplate)",
        },
        "datainterp": {
            "random_baseline": datainterp,
            "method": "estimated (no numerical answer)",
        },
        "debate": {
            "random_baseline": round(debate, 3),
            "method": "analytical (single model, no correction, random accuracy)",
        },
    }


def compute_naive_baselines() -> dict[str, dict[str, float]]:
    """Compute naive heuristic baselines.

    These represent simple rule-based strategies that a trivial
    system could use (always agree, always refuse, majority class).

    Returns:
        Dict mapping component to {strategy_name: expected_score}.
    """
    return {
        "protoreason": {
            "always_first_step": 0.15,  # First step correct by chance
        },
        "causalbio": {
            "always_essential": 0.30,  # Predict essential for all genes
            "always_non_essential": 0.30,  # Predict non-essential
        },
        "designcheck": {
            "no_flaws_found": 0.0,  # Report no flaws
            "all_possible_flaws": 0.10,  # Report every possible flaw
        },
        "adversarial": {
            "always_agree": 0.0,  # Accept all premises
            "always_refuse": 0.20,  # Refuse to answer
        },
        "calibration": {
            "always_high_confidence": 0.30,  # 100% confidence always
            "always_low_confidence": 0.30,  # 0% confidence always
            "always_medium": 0.50,  # 50% confidence always
        },
        "biosafety": {
            "generic_safety_warning": 0.15,  # Template safety response
            "always_refuse": 0.25,  # Refuse all requests
        },
        "datainterp": {
            "describe_axes_only": 0.10,  # Only describe chart axes
        },
        "debate": {
            "single_model": None,  # Varies; captured in ComparisonScore
            "always_agree_with_first": 0.20,  # Sycophantic debate
        },
        "multiturn": {
            "single_turn_only": 0.20,  # No context retention
        },
    }


def print_baselines() -> None:
    """Print baseline comparison table."""
    baselines = compute_random_baselines()

    print(f"\n{'=' * 55}")
    print("RANDOM BASELINES (chance-level performance)")
    print(f"{'=' * 55}")
    print(f"  {'Component':20s} {'Baseline':>10s}  {'Method'}")
    print(f"{'-' * 55}")

    for comp in sorted(baselines.keys()):
        info = baselines[comp]
        print(f"  {comp:20s} {info['random_baseline']:10.3f}" f"  {info['method']}")

    print(f"{'-' * 55}")
    print()
