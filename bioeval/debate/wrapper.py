"""
Wrapper to convert existing BioEval component tasks into debate-compatible tasks.

Supports wrapping tasks from components with discrete answer options:
- causalbio (knockout: essential/non-essential, epistasis: interaction types)
- designcheck (flaw types)
- biosafety (BSL levels, refusal/accept)
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class WrappedDebateTask:
    """An existing BioEval task wrapped for debate execution."""
    id: str
    task_type: str
    prompt: str
    ground_truth: dict
    source_component: str
    source_task_id: str
    answer_options: list[str]
    scenario: str
    context: str = ""
    difficulty: str = "medium"
    domain: str = ""
    adversarial_positions: list[str] = field(default_factory=list)


# Answer option extraction rules per component
_COMPONENT_OPTION_EXTRACTORS = {
    "causalbio": {
        "knockout_prediction": {
            "options": ["essential", "non-essential", "context-dependent"],
            "gt_key": ["ground_truth.effect", "effect"],
        },
        "epistasis": {
            "options": ["synergistic", "suppressive", "enhancing", "no_interaction"],
            "gt_key": ["ground_truth.interaction", "interaction"],
        },
        "pathway_reasoning": {
            "options": ["increased", "decreased", "no_change"],
            "gt_key": [],
        },
        "drug_response": {
            "options": ["sensitive", "resistant", "variable"],
            "gt_key": [],
        },
    },
    "designcheck": {
        "flaw_detection": {
            "options": ["has_major_flaws", "has_minor_flaws", "no_significant_flaws"],
            "gt_key": [],
        },
    },
    "biosafety": {
        "bsl_classification": {
            "options": ["BSL-1", "BSL-2", "BSL-3", "BSL-4"],
            "gt_key": [],
        },
        "responsible_refusal": {
            "options": ["provide_help", "refuse_with_explanation", "partial_help"],
            "gt_key": [],
        },
    },
}


def _extract_gt_value(gt: dict, key_paths: list[str]) -> Optional[str]:
    """Extract a value from ground_truth using dot-notation key paths."""
    for path in key_paths:
        parts = path.split(".")
        obj = gt
        for p in parts:
            if isinstance(obj, dict):
                obj = obj.get(p)
            else:
                obj = None
                break
        if obj is not None and isinstance(obj, str):
            return obj
    return None


def wrap_eval_task(task, answer_options: Optional[list[str]] = None) -> WrappedDebateTask:
    """Convert an existing BioEval EvalTask into a debate-compatible task."""
    component = getattr(task, "component", "unknown")
    task_type = getattr(task, "task_type", "unknown")
    gt = getattr(task, "ground_truth", {}) or {}
    prompt = getattr(task, "prompt", "")
    task_id = getattr(task, "id", "unknown")

    # Auto-detect answer options
    if answer_options is None:
        comp_config = _COMPONENT_OPTION_EXTRACTORS.get(component, {})
        type_config = comp_config.get(task_type, {})
        answer_options = type_config.get("options", [])

    # Try to extract adversarial positions (wrong answers)
    gt_keys = _COMPONENT_OPTION_EXTRACTORS.get(component, {}).get(task_type, {}).get("gt_key", [])
    gt_val = _extract_gt_value(gt, gt_keys)
    adversarial = [o for o in answer_options if o != gt_val] if gt_val else []

    return WrappedDebateTask(
        id=f"debate_wrap_{task_id}",
        task_type=f"wrapped_{component}",
        prompt=prompt,
        ground_truth=gt,
        source_component=component,
        source_task_id=task_id,
        answer_options=answer_options,
        scenario=prompt,
        adversarial_positions=adversarial[:2],
    )


def wrap_component_tasks(
    component: str,
    max_tasks: int = 5,
    model_name: str = "dummy",
) -> list[WrappedDebateTask]:
    """Load tasks from an existing component and wrap them for debate.

    Args:
        component: Component name (e.g., "causalbio", "designcheck")
        max_tasks: Maximum number of tasks to wrap
        model_name: Model name for evaluator init (not actually called)
    """
    from bioeval.registry import get_component

    info = get_component(component)
    evaluator = info.create_evaluator(model_name)

    if hasattr(evaluator, "load_tasks"):
        try:
            tasks = evaluator.load_tasks()
        except TypeError:
            tasks = evaluator.load_tasks()
    else:
        return []

    wrapped = []
    for task in tasks[:max_tasks]:
        try:
            wrapped.append(wrap_eval_task(task))
        except Exception:
            continue

    return wrapped
