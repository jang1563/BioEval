# BioEval Score Field Mapping

> Last updated: 2026-02-27

Each component stores scores in different field structures. This document maps the canonical primary metric for each component.

## Score Location by Component

| Component | Primary Metric | Field Path | Score Range | Notes |
|-----------|---------------|------------|:-----------:|-------|
| ProtoReason (ordering) | Adjacent pair accuracy | `scores.adjacent_pair_accuracy` | 0–1 | Kendall's tau also at `scores.kendall_tau` |
| ProtoReason (missing) | Recall | `scores.recall` | 0–1 | Missing step detection rate |
| ProtoReason (calculation) | Numerical accuracy | `scores.numerical_accuracy` | 0–1 | Fraction of values correct |
| ProtoReason (troubleshooting) | Cause coverage | `scores.cause_coverage` | 0–1 | Fraction of known causes mentioned |
| CausalBio (knockout) | Effect correct | `scores.effect_correct` | bool | Binary: essential/non-essential prediction |
| CausalBio (pathway) | Combined score | `scores.combined_score` | 0–1 | pathway_coverage × direction_accuracy |
| CausalBio (epistasis) | Mechanism score | `scores.mechanism_score` | 0–1 | Also: `scores.interaction_type_correct` (bool) |
| CausalBio (drug) | Combined score | `scores.combined_score` | 0–1 | gene_mention_rate × direction_accuracy |
| DesignCheck | F1 | `scores.f1` | 0–1 | Harmonic mean of recall and precision |
| DesignCheck | Composite | `scores.composite_score` | 0–1 | 0.70 × weighted_recall + quality bonuses |
| Adversarial | Score | `scores.score` | 0–1 | Includes hallucination/behavior penalties |
| MultiTurn | Overall score | `scores.overall_score` | 0–1 | Aggregated turn-level scores |
| Calibration | Calibration error | `scores.calibration_error` | 0–1 | Lower is better. Invert for 0–1 score |
| BioSafety | Score | `result.score` (top-level) | 0–1 | `scores{}` dict is empty |
| DataInterp | Score | `result.score` (top-level) | 0–1 | `scores{}` dict is empty |
| Debate | Composite score | `scores.composite_score` | 0–1 | 0.40×accuracy + 0.25×correction + 0.15×efficiency + 0.20×reasoning |

## Structural Inconsistency

BioSafety and DataInterp store `score` at the **result top-level** instead of inside `scores{}`. All other components use `scores.{metric_name}`.

## Extracting a Canonical Score

To extract a single representative score per task:

```python
def extract_primary_score(component: str, task_result: dict) -> float | None:
    s = task_result.get("scores", {})

    if component == "protoreason":
        for key in ["adjacent_pair_accuracy", "recall", "numerical_accuracy", "cause_coverage"]:
            if key in s and s[key] is not None:
                return float(s[key])
    elif component == "causalbio":
        if "effect_correct" in s:
            return 1.0 if s["effect_correct"] else 0.0
        if "combined_score" in s and s["combined_score"] is not None:
            return float(s["combined_score"])
        if "mechanism_score" in s and s["mechanism_score"] is not None:
            return float(s["mechanism_score"])
    elif component == "designcheck":
        return float(s["f1"]) if "f1" in s else None
    elif component == "adversarial":
        return float(s["score"]) if "score" in s else None
    elif component == "multiturn":
        return float(s["overall_score"]) if "overall_score" in s else None
    elif component == "calibration":
        if "calibration_error" in s and s["calibration_error"] is not None:
            return 1.0 - abs(float(s["calibration_error"]))
    elif component in ("biosafety", "datainterp"):
        return float(task_result["score"]) if "score" in task_result else None
    elif component == "debate":
        return float(s["composite_score"]) if "composite_score" in s else None

    return None
```
