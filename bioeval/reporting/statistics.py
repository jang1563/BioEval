"""
Benchmark statistics and analysis for NeurIPS submission.

Generates comprehensive statistics about task distribution, difficulty,
inter-component balance, and scoring properties.
"""

import json
from collections import Counter


def _count_protoreason(data_tier: str) -> dict:
    """Count ProtoReason tasks by type."""
    from bioeval.protoreason.evaluator import SAMPLE_PROTOCOLS, CALCULATION_TASKS, TROUBLESHOOTING_TASKS

    n_ordering = len(SAMPLE_PROTOCOLS)
    n_missing = len(SAMPLE_PROTOCOLS)
    n_reagent = len(SAMPLE_PROTOCOLS)
    n_calc = len(CALCULATION_TASKS)
    n_troubleshoot = len(TROUBLESHOOTING_TASKS)

    counts = {
        "step_ordering": n_ordering,
        "missing_step": n_missing,
        "reagent_calculation": n_reagent,
        "calculation": n_calc,
        "troubleshooting": n_troubleshoot,
    }

    if data_tier in ("extended", "all"):
        try:
            from bioeval.protoreason.extended_data import (
                PROTOCOLS as EXT_PR,
                CALCULATION_TASKS as EXT_CALC,
                TROUBLESHOOTING_TASKS as EXT_TS,
                SAFETY_TASKS as EXT_SAFETY,
            )

            counts["step_ordering"] += len(EXT_PR)
            counts["missing_step"] += len(EXT_PR)
            counts["reagent_calculation"] += len(EXT_PR)
            counts["calculation"] += len(EXT_CALC)
            counts["troubleshooting"] += len(EXT_TS)
            counts["safety"] = len(EXT_SAFETY)
        except ImportError:
            pass

    total = sum(counts.values())
    return {"n_tasks": total, "by_type": counts, "task_types": sorted(counts.keys())}


def _count_causalbio(data_tier: str) -> dict:
    """Count CausalBio tasks by type."""
    from bioeval.causalbio.evaluator import KNOCKOUT_TASKS, PATHWAY_TASKS, DRUG_RESPONSE_TASKS, EPISTASIS_TASKS

    counts = {
        "knockout_prediction": len(KNOCKOUT_TASKS),
        "pathway_reasoning": len(PATHWAY_TASKS),
        "drug_response": len(DRUG_RESPONSE_TASKS),
        "epistasis": len(EPISTASIS_TASKS),
    }

    if data_tier in ("extended", "all"):
        try:
            from bioeval.causalbio.extended_data import (
                KNOCKOUT_TASKS as EXT_KO,
                PATHWAY_TASKS as EXT_PATH,
                DRUG_RESPONSE_TASKS as EXT_DRUG,
                EPISTASIS_TASKS as EXT_EPI,
            )

            counts["knockout_prediction"] += len(EXT_KO)
            counts["pathway_reasoning"] += len(EXT_PATH)
            counts["drug_response"] += len(EXT_DRUG)
            counts["epistasis"] += len(EXT_EPI)
        except ImportError:
            pass

    total = sum(counts.values())
    return {"n_tasks": total, "by_type": counts, "task_types": sorted(counts.keys())}


def _count_designcheck(data_tier: str) -> dict:
    """Count DesignCheck tasks."""
    from bioeval.designcheck.evaluator import FLAWED_DESIGNS

    n = len(FLAWED_DESIGNS)
    if data_tier in ("extended", "all"):
        try:
            from bioeval.designcheck.extended_data import EXTENDED_FLAWED_DESIGNS

            n += len(EXTENDED_FLAWED_DESIGNS)
        except ImportError:
            pass
    return {"n_tasks": n, "by_type": {"flaw_detection": n}}


def _count_multiturn(data_tier: str) -> dict:
    """Count MultiTurn tasks."""
    from bioeval.multiturn.dialogues import DIALOGUES

    n = len(DIALOGUES)
    if data_tier in ("extended", "all"):
        try:
            from bioeval.multiturn.extended_data import EXTENDED_DIALOGUES

            n += len(EXTENDED_DIALOGUES)
        except ImportError:
            pass
    return {"n_tasks": n}


def _collect_task_ids(data_tier: str) -> list[str]:
    """Collect all task IDs for split statistics."""
    ids = []

    # ProtoReason
    from bioeval.protoreason.evaluator import SAMPLE_PROTOCOLS, CALCULATION_TASKS, TROUBLESHOOTING_TASKS

    for name in SAMPLE_PROTOCOLS:
        for suffix in ["ordering", "missing", "reagent"]:
            ids.append(f"proto_{name}_{suffix}")
    for t in CALCULATION_TASKS:
        ids.append(t.get("id", f"calc_{len(ids)}"))
    for t in TROUBLESHOOTING_TASKS:
        ids.append(t.get("id", f"ts_{len(ids)}"))

    # CausalBio
    from bioeval.causalbio.evaluator import KNOCKOUT_TASKS, PATHWAY_TASKS, DRUG_RESPONSE_TASKS, EPISTASIS_TASKS

    for t in KNOCKOUT_TASKS + PATHWAY_TASKS + DRUG_RESPONSE_TASKS + EPISTASIS_TASKS:
        ids.append(t.get("id", f"cb_{len(ids)}"))

    # DesignCheck
    from bioeval.designcheck.evaluator import FLAWED_DESIGNS

    for d in FLAWED_DESIGNS:
        ids.append(d.get("id", f"dc_{len(ids)}"))

    # Adversarial
    from bioeval.adversarial.tasks import ADVERSARIAL_TASKS

    for t in ADVERSARIAL_TASKS:
        ids.append(t.id)

    # MultiTurn
    from bioeval.multiturn.dialogues import DIALOGUES

    for d in DIALOGUES:
        ids.append(d.id if hasattr(d, "id") else f"mt_{len(ids)}")

    # Calibration
    from bioeval.scoring.calibration import CALIBRATION_TEST_TASKS

    for t in CALIBRATION_TEST_TASKS:
        ids.append(t["id"])

    # Extended data
    if data_tier in ("extended", "all"):
        try:
            from bioeval.designcheck.extended_data import EXTENDED_FLAWED_DESIGNS

            for d in EXTENDED_FLAWED_DESIGNS:
                ids.append(d.get("id", f"dc_ext_{len(ids)}"))
        except ImportError:
            pass
        try:
            from bioeval.multiturn.extended_data import EXTENDED_DIALOGUES

            for d in EXTENDED_DIALOGUES:
                ids.append(d.id if hasattr(d, "id") else f"mt_ext_{len(ids)}")
        except ImportError:
            pass

    return ids


def compute_benchmark_statistics(data_tier: str = "base") -> dict:
    """Compute comprehensive benchmark statistics.

    Does NOT instantiate evaluators or require API keys.
    """
    stats = {
        "data_tier": data_tier,
        "components": {},
        "totals": {},
    }

    stats["components"]["protoreason"] = _count_protoreason(data_tier)
    stats["components"]["causalbio"] = _count_causalbio(data_tier)
    stats["components"]["designcheck"] = _count_designcheck(data_tier)

    # Adversarial (no tier distinction)
    from bioeval.adversarial.tasks import ADVERSARIAL_TASKS

    adv_types = Counter(t.adversarial_type.value for t in ADVERSARIAL_TASKS)
    adv_diff = Counter(t.difficulty for t in ADVERSARIAL_TASKS)
    stats["components"]["adversarial"] = {
        "n_tasks": len(ADVERSARIAL_TASKS),
        "by_type": dict(adv_types),
        "by_difficulty": dict(adv_diff),
    }

    stats["components"]["multiturn"] = _count_multiturn(data_tier)

    # Calibration
    from bioeval.scoring.calibration import CALIBRATION_TEST_TASKS

    cal_types = Counter(t["correct_behavior"] for t in CALIBRATION_TEST_TASKS)
    stats["components"]["calibration"] = {
        "n_tasks": len(CALIBRATION_TEST_TASKS),
        "by_behavior": dict(cal_types),
    }

    # Split stats
    from bioeval.scoring.splits import get_split

    all_ids = _collect_task_ids(data_tier)
    split_counts = Counter(get_split(tid) for tid in all_ids)
    total = sum(c["n_tasks"] for c in stats["components"].values())

    stats["totals"] = {
        "total_tasks": total,
        "n_components": 6,
        "n_task_ids": len(all_ids),
        "split_public": split_counts.get("public", 0),
        "split_private": split_counts.get("private", 0),
        "private_fraction": round(split_counts.get("private", 0) / len(all_ids), 3) if all_ids else 0,
    }

    # Prompt length stats from adversarial (always available, no evaluator needed)
    prompt_lengths = [len(t.question) for t in ADVERSARIAL_TASKS]
    if prompt_lengths:
        prompt_lengths.sort()
        stats["prompt_stats"] = {
            "n_prompts": len(prompt_lengths),
            "min_length": prompt_lengths[0],
            "max_length": prompt_lengths[-1],
            "median_length": prompt_lengths[len(prompt_lengths) // 2],
            "mean_length": round(sum(prompt_lengths) / len(prompt_lengths), 1),
        }

    return stats


def print_statistics(data_tier: str = "base"):
    """Print formatted benchmark statistics."""
    stats = compute_benchmark_statistics(data_tier)

    print(f"\n{'=' * 60}")
    print(f"BioEval Benchmark Statistics (tier: {data_tier})")
    print(f"{'=' * 60}")

    print(f"\nTotal tasks: {stats['totals']['total_tasks']}")
    print(f"Components: {stats['totals']['n_components']}")
    print(
        f"Public/Private split: "
        f"{stats['totals']['split_public']}/{stats['totals']['split_private']} "
        f"({stats['totals']['private_fraction']:.1%} private)"
    )

    print(f"\n--- Per-Component ---")
    for comp, info in stats["components"].items():
        print(f"\n  {comp}: {info['n_tasks']} tasks")
        if "by_type" in info:
            for t, n in sorted(info["by_type"].items()):
                print(f"    {t}: {n}")
        if "by_difficulty" in info:
            print(f"    Difficulty: {dict(info['by_difficulty'])}")
        if "by_behavior" in info:
            for b, n in sorted(info["by_behavior"].items()):
                print(f"    {b}: {n}")

    if "prompt_stats" in stats:
        ps = stats["prompt_stats"]
        print(f"\n--- Prompt Statistics (adversarial) ---")
        print(f"  N prompts: {ps['n_prompts']}")
        print(
            f"  Length: min={ps['min_length']}, median={ps['median_length']}, "
            f"max={ps['max_length']}, mean={ps['mean_length']}"
        )

    return stats
