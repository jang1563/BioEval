# LLM-as-Judge Validation Protocol

## Overview

BioEval uses an LLM-as-Judge (default: `claude-sonnet-4-20250514`) for semantic evaluation of model responses. This document describes the validation protocol to ensure judge reliability.

## Judge Configuration

| Parameter | Value |
|-----------|-------|
| Default model | `claude-sonnet-4-20250514` |
| Temperature | 0.0 (deterministic) |
| Scoring scale | 1-5 per dimension |
| Dimensions | 6 (factual accuracy, mechanistic depth, completeness, scientific reasoning, practical applicability, appropriate uncertainty) |
| Rubric versioning | SHA-256 hash of rubric definitions |

## Score Validation

All judge scores are validated before recording:

- **Range clamping**: Scores outside [1, 5] are clamped with a warning
- **Type checking**: Non-numeric scores default to 3.0 with a warning
- **Dimension validation**: Each dimension score is independently validated
- **Parse error handling**: Failed JSON parses result in `overall_score=None` and `parse_error=True`

## Validation Metrics

### 1. Self-Consistency (Intra-Rater Reliability)

Measures whether the judge produces the same score when evaluating the same response twice.

```bash
# Re-evaluate 30 random tasks and compute agreement
bioeval agreement <result_file>  # requires --use-judge results
```

**Acceptance threshold**: Cohen's kappa >= 0.60 (substantial agreement, Landis & Koch 1977)

### 2. Auto-Judge Agreement (Inter-Method Reliability)

Measures agreement between the automated keyword/formula-based scorer and the LLM judge.

```bash
bioeval agreement <result_file>
```

Reported metrics:
- Cohen's kappa (binary pass/fail)
- Weighted kappa (ordinal scores)
- Pearson correlation (continuous scores)
- Per-component breakdown

### 3. Human Validation Pack

Generate a subset of tasks for expert review:

```bash
bioeval judge-pack <result_file> --output validation_pack.json
```

The validation pack includes:
- Stratified sample across components and score ranges
- Original task, model response, automated score, and judge score
- Blank fields for human ratings

## Kappa Interpretation (Landis & Koch 1977)

| Kappa Range | Interpretation |
|-------------|---------------|
| < 0.00 | Poor (below chance) |
| 0.00 - 0.20 | Slight agreement |
| 0.21 - 0.40 | Fair agreement |
| 0.41 - 0.60 | Moderate agreement |
| 0.61 - 0.80 | Substantial agreement |
| 0.81 - 1.00 | Almost perfect agreement |

## Limitations

1. **Single judge model**: Currently uses only Claude Sonnet as judge. Cross-model judge agreement is not yet measured.
2. **No human ground truth**: Inter-rater reliability between judge and human experts has not been formally established. The `judge-pack` command generates materials for this validation but requires manual expert annotation.
3. **Domain bias**: The judge may share knowledge biases with the models being evaluated, particularly for Anthropic models.
4. **Rubric sensitivity**: Changes to rubric definitions may affect score distributions. The `rubric_version` hash in metadata tracks this.

## Disclosure for Publication

When reporting BioEval results that include LLM-as-Judge scores:

1. Report the judge model and rubric version from result metadata
2. Report auto-judge agreement metrics (kappa, correlation)
3. Acknowledge that human inter-rater reliability has not been formally established
4. Note that the judge uses temperature=0.0 for reproducibility
