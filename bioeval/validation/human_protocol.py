"""
Human Validation Protocol for BioEval

Provides tools for domain experts to annotate and validate benchmark tasks.
Generates annotation worksheets (JSON) and computes inter-rater statistics.

Usage:
    # Generate annotation worksheets
    python -m bioeval.validation.human_protocol generate --component designcheck --out worksheets/

    # Compute inter-rater agreement after annotation
    python -m bioeval.validation.human_protocol agree worksheets/annotator_a.json worksheets/annotator_b.json
"""

import json
import math
import os
from datetime import datetime
from pathlib import Path


# =============================================================================
# ANNOTATION SCHEMA
# =============================================================================

QUALITY_DIMENSIONS = {
    "scientific_accuracy": {
        "description": "Is the ground truth (expected answer / flaws / etc.) scientifically correct?",
        "scale": [1, 2, 3, 4, 5],
        "anchors": {
            1: "Major factual errors in ground truth",
            3: "Mostly correct with minor issues",
            5: "Completely accurate and up-to-date",
        },
    },
    "difficulty_calibration": {
        "description": "Is the task appropriately challenging for a frontier LLM?",
        "scale": [1, 2, 3, 4, 5],
        "anchors": {
            1: "Trivially easy — any undergrad could answer",
            3: "Moderate — requires graduate-level biology knowledge",
            5: "Expert level — requires specialist domain knowledge",
        },
    },
    "answer_uniqueness": {
        "description": "Is there one clearly correct answer, or is it ambiguous?",
        "scale": [1, 2, 3, 4, 5],
        "anchors": {
            1: "Highly ambiguous — multiple valid answers",
            3: "Mostly unambiguous with minor alternatives",
            5: "Single correct answer, no ambiguity",
        },
    },
    "prompt_clarity": {
        "description": "Is the question/prompt clear and unambiguous?",
        "scale": [1, 2, 3, 4, 5],
        "anchors": {
            1: "Confusing or misleading prompt",
            3: "Understandable but could be clearer",
            5: "Crystal clear, no room for misinterpretation",
        },
    },
    "relevance": {
        "description": "Does this task test a skill that matters for real-world biology AI?",
        "scale": [1, 2, 3, 4, 5],
        "anchors": {
            1: "Not relevant to real biology workflows",
            3: "Somewhat relevant",
            5: "Directly tests a critical real-world capability",
        },
    },
}


def _load_tasks_for_component(component: str) -> list[dict]:
    """Load tasks from a component for annotation."""
    if component == "protoreason":
        from bioeval.protoreason.evaluator import ProtoReasonEvaluator
        ev = ProtoReasonEvaluator("claude-sonnet-4-20250514")
        tasks = ev.load_tasks(data_tier="extended")
    elif component == "causalbio":
        from bioeval.causalbio.evaluator import CausalBioEvaluator
        ev = CausalBioEvaluator("claude-sonnet-4-20250514")
        tasks = ev.load_tasks(data_tier="extended")
    elif component == "designcheck":
        from bioeval.designcheck.evaluator import DesignCheckEvaluator
        ev = DesignCheckEvaluator("claude-sonnet-4-20250514")
        tasks = ev.load_tasks(data_tier="extended")
    elif component == "adversarial":
        from bioeval.adversarial.tasks import AdversarialEvaluator
        ev = AdversarialEvaluator("claude-sonnet-4-20250514")
        tasks = ev.load_tasks()
    elif component == "multiturn":
        from bioeval.multiturn.dialogues import MultiTurnEvaluator
        ev = MultiTurnEvaluator("claude-sonnet-4-20250514")
        tasks = ev.load_tasks(data_tier="extended")
    elif component == "calibration":
        from bioeval.scoring.calibration import CalibrationEvaluator
        ev = CalibrationEvaluator("claude-sonnet-4-20250514")
        tasks = ev.load_tasks()
    else:
        raise ValueError(f"Unknown component: {component}")

    result = []
    for t in tasks:
        entry = {
            "task_id": t.id if hasattr(t, "id") else "unknown",
            "component": component,
            "task_type": t.task_type if hasattr(t, "task_type") else "unknown",
            "prompt": t.prompt if hasattr(t, "prompt") else "",
        }
        if hasattr(t, "ground_truth"):
            gt = t.ground_truth
            entry["ground_truth_summary"] = (
                json.dumps(gt, indent=2, default=str)[:500]
                if isinstance(gt, dict)
                else str(gt)[:500]
            )
        result.append(entry)
    return result


def generate_worksheet(
    component: str,
    annotator_name: str = "",
    output_dir: str = "worksheets",
) -> str:
    """Generate a JSON annotation worksheet for a component.

    Returns:
        Path to the generated worksheet file.
    """
    tasks = _load_tasks_for_component(component)

    worksheet = {
        "metadata": {
            "component": component,
            "annotator": annotator_name,
            "generated_at": datetime.now().isoformat(),
            "num_tasks": len(tasks),
            "instructions": (
                "For each task, rate every quality dimension on a 1-5 scale. "
                "Add free-text comments in the 'comments' field. "
                "Set 'flag_for_removal' to true if the task should be dropped."
            ),
        },
        "dimensions": QUALITY_DIMENSIONS,
        "annotations": [],
    }

    for task in tasks:
        annotation = {
            **task,
            "ratings": {dim: None for dim in QUALITY_DIMENSIONS},
            "comments": "",
            "flag_for_removal": False,
            "suggested_fix": "",
        }
        worksheet["annotations"].append(annotation)

    os.makedirs(output_dir, exist_ok=True)
    safe_name = annotator_name.replace(" ", "_").lower() or "blank"
    path = os.path.join(output_dir, f"{component}_{safe_name}.json")
    with open(path, "w") as f:
        json.dump(worksheet, f, indent=2, default=str)

    return path


# =============================================================================
# INTER-RATER AGREEMENT
# =============================================================================

def _cohens_kappa(ratings_a: list, ratings_b: list) -> float:
    """Compute Cohen's kappa for two raters on ordinal data.

    Treats each distinct value as a nominal category.
    """
    assert len(ratings_a) == len(ratings_b)
    n = len(ratings_a)
    if n == 0:
        return 0.0

    categories = sorted(set(ratings_a) | set(ratings_b))
    cat_idx = {c: i for i, c in enumerate(categories)}
    k = len(categories)

    # Confusion matrix
    matrix = [[0] * k for _ in range(k)]
    for a, b in zip(ratings_a, ratings_b):
        matrix[cat_idx[a]][cat_idx[b]] += 1

    # Observed agreement
    po = sum(matrix[i][i] for i in range(k)) / n

    # Expected agreement
    row_sums = [sum(matrix[i]) for i in range(k)]
    col_sums = [sum(matrix[j][i] for j in range(k)) for i in range(k)]
    pe = sum(row_sums[i] * col_sums[i] for i in range(k)) / (n * n)

    if pe == 1.0:
        return 1.0
    return (po - pe) / (1.0 - pe)


def _weighted_kappa(ratings_a: list[int], ratings_b: list[int]) -> float:
    """Compute linearly-weighted Cohen's kappa for ordinal scales."""
    assert len(ratings_a) == len(ratings_b)
    n = len(ratings_a)
    if n == 0:
        return 0.0

    categories = sorted(set(ratings_a) | set(ratings_b))
    cat_idx = {c: i for i, c in enumerate(categories)}
    k = len(categories)

    matrix = [[0] * k for _ in range(k)]
    for a, b in zip(ratings_a, ratings_b):
        matrix[cat_idx[a]][cat_idx[b]] += 1

    max_dist = k - 1 if k > 1 else 1

    # Weighted observed & expected
    row_sums = [sum(matrix[i]) for i in range(k)]
    col_sums = [sum(matrix[j][i] for j in range(k)) for i in range(k)]

    wo = 0.0
    we = 0.0
    for i in range(k):
        for j in range(k):
            w = 1.0 - abs(i - j) / max_dist
            wo += w * matrix[i][j] / n
            we += w * (row_sums[i] * col_sums[j]) / (n * n)

    if we == 1.0:
        return 1.0
    return (wo - we) / (1.0 - we)


def compute_agreement(file_a: str, file_b: str) -> dict:
    """Compute inter-rater agreement statistics between two annotated worksheets.

    Returns dict with per-dimension and overall kappa scores.
    """
    with open(file_a) as f:
        ws_a = json.load(f)
    with open(file_b) as f:
        ws_b = json.load(f)

    ann_a = {a["task_id"]: a for a in ws_a["annotations"]}
    ann_b = {b["task_id"]: b for b in ws_b["annotations"]}

    common_ids = sorted(set(ann_a) & set(ann_b))
    if not common_ids:
        return {"error": "No common task IDs between worksheets"}

    dimension_results = {}
    all_a_ratings = []
    all_b_ratings = []

    for dim in QUALITY_DIMENSIONS:
        a_vals = []
        b_vals = []
        for tid in common_ids:
            ra = ann_a[tid]["ratings"].get(dim)
            rb = ann_b[tid]["ratings"].get(dim)
            if ra is not None and rb is not None:
                a_vals.append(ra)
                b_vals.append(rb)

        if len(a_vals) < 2:
            dimension_results[dim] = {"n": len(a_vals), "kappa": None, "weighted_kappa": None}
            continue

        kappa = _cohens_kappa(a_vals, b_vals)
        w_kappa = _weighted_kappa(a_vals, b_vals)
        mean_a = sum(a_vals) / len(a_vals)
        mean_b = sum(b_vals) / len(b_vals)

        dimension_results[dim] = {
            "n": len(a_vals),
            "kappa": round(kappa, 3),
            "weighted_kappa": round(w_kappa, 3),
            "mean_a": round(mean_a, 2),
            "mean_b": round(mean_b, 2),
        }
        all_a_ratings.extend(a_vals)
        all_b_ratings.extend(b_vals)

    # Overall kappa
    overall_kappa = _cohens_kappa(all_a_ratings, all_b_ratings) if all_a_ratings else 0.0
    overall_w_kappa = _weighted_kappa(all_a_ratings, all_b_ratings) if all_a_ratings else 0.0

    # Flagging agreement
    flags_a = [ann_a[tid].get("flag_for_removal", False) for tid in common_ids]
    flags_b = [ann_b[tid].get("flag_for_removal", False) for tid in common_ids]
    flag_agree = sum(a == b for a, b in zip(flags_a, flags_b)) / len(common_ids)

    return {
        "annotator_a": ws_a["metadata"].get("annotator", "A"),
        "annotator_b": ws_b["metadata"].get("annotator", "B"),
        "common_tasks": len(common_ids),
        "overall_kappa": round(overall_kappa, 3),
        "overall_weighted_kappa": round(overall_w_kappa, 3),
        "flag_agreement": round(flag_agree, 3),
        "by_dimension": dimension_results,
    }


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description="BioEval Human Validation Protocol")
    sub = parser.add_subparsers(dest="cmd")

    gen = sub.add_parser("generate", help="Generate annotation worksheet")
    gen.add_argument("--component", "-c", required=True, help="Component name")
    gen.add_argument("--annotator", "-a", default="", help="Annotator name")
    gen.add_argument("--out", "-o", default="worksheets", help="Output directory")

    agr = sub.add_parser("agree", help="Compute inter-rater agreement")
    agr.add_argument("file_a", help="Annotator A worksheet JSON")
    agr.add_argument("file_b", help="Annotator B worksheet JSON")

    args = parser.parse_args()

    if args.cmd == "generate":
        path = generate_worksheet(args.component, args.annotator, args.out)
        print(f"Worksheet generated: {path}")
    elif args.cmd == "agree":
        result = compute_agreement(args.file_a, args.file_b)
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
