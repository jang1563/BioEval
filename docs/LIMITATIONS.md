# BioEval Limitations

This document describes known limitations of BioEval as a benchmark for evaluating LLM biological reasoning. Users should consider these when interpreting results.

## 1. Token Budget Asymmetry

Gemini 2.5 "thinking" models consume thinking tokens from the output token budget. BioEval applies a 4x multiplier to `max_tokens` for Gemini to ensure functional parity, but this creates an asymmetry:

- Gemini models receive a larger effective output budget than other models
- Use `--equalize-tokens` for strict fairness (same `max_tokens` for all models)
- See [FAIRNESS.md](FAIRNESS.md) for full details

## 2. Keyword-Based Scoring

Six components use `phrase_match()` with word-boundary detection, stemming, and synonyms. Three components additionally use raw keyword matching for specific sub-metrics (depth indicators, refusal detection).

Known limitations:
- **Paraphrase vulnerability**: Correct answers using different terminology may score lower
- **Stemming false positives**: Short terms (2-3 characters) may match unrelated words despite word-boundary guards
- **English-only**: Stemming and synonym tables are English-only

## 3. LLM-as-Judge

BioEval optionally uses a single LLM (Claude Sonnet) as a judge for semantic evaluation.

- **No human ground truth**: Inter-rater reliability between judge and human experts has not been formally established
- **Single judge model**: Cross-model judge agreement is not measured
- **Domain bias**: The judge may share knowledge biases with evaluated models, particularly Anthropic models
- See [JUDGE_VALIDATION.md](JUDGE_VALIDATION.md) for the validation protocol

## 4. Scoring Weights

Composite scores use expert-chosen weights (e.g., CausalBio knockout: 60% effect correctness + 40% reasoning). These weights reflect domain priorities but are not empirically optimized.

- Weight sensitivity analysis is available via `bioeval sensitivity <result_file>`
- Typical +-10% perturbation produces < 5% score swing (stable)

## 5. Task Scale

BioEval contains 197 base tasks (301 with extended tier) across 9 components:

| Component | Base Tasks |
|-----------|:---------:|
| ProtoReason | 14 |
| CausalBio | 13 |
| DesignCheck | 20 |
| Adversarial | 30 |
| Calibration | 30 |
| BioSafety | 25 |
| DataInterp | 25 |
| MultiTurn | 15 |
| Debate | 25 |

Smaller components (ProtoReason, CausalBio) have wider confidence intervals.

## 6. Language

BioEval is English-only. All tasks, rubrics, and scoring mechanisms assume English-language responses. Performance on non-English biological text is not measured.

## 7. Temporal Scope

Tasks are based on biological knowledge from 2024-2026. Model performance on emerging discoveries, novel pathways, or recently revised biological understanding is not captured.

## 8. Prompt Sensitivity

BioEval uses specific prompt templates for each task type. Different prompt phrasings may favor different model architectures:

- Instruction-following models may perform better with structured prompts
- Models trained on different prompt formats may be disadvantaged
- System prompt compatibility varies across API providers
