# BioEval Current Status (Canonical)

Last updated: 2026-03-02
Version: `0.4.1`

This file is the canonical runtime status reference for counts, version, and reproducibility contract.

## Canonical Inventory (Code-Verified 2026-03-02)

- Base: `197`
- Extended additions: `104` (ProtoReason +45, CausalBio +34, DesignCheck +10, MultiTurn +15)
- Total unique: `301`
- Components: `protoreason` (14), `causalbio` (13), `designcheck` (20), `adversarial` (30), `multiturn` (15), `calibration` (30), `biosafety` (25), `datainterp` (25), `debate` (25)
- Tests: `433` passing

Note: Advanced tiers reuse base task IDs with the same prompts (no unique additions). Previous counts of "Advanced: 78" and "Total: 417" were inflated and have been corrected.

## CausalBio Ground Truth Contract

- `source_type`: `curated_builtin` or `external_verified`
- `source_id`: source module + task id or external dataset id
- `release`: benchmark release tag (`bioeval-vX.Y.Z`)
- `external_verified`: boolean

Base release defaults to curated built-in tasks; external verification pipelines are optional and separately declared.

## Expert Review Improvements (2026-02-28)

Phase 1 expert review (statistical, biological, SW engineering, benchmark design):

- **P0 Critical**: Python 3.9 compat (32 files), LLM Judge error handling (score=None on
  failure, timeout, XML delimiters), CLI `--temperature`/`--judge-temperature`, SQLite resilience
- **P1 Major**: Permutation test zero-diff guard, Bonferroni/BH multiple comparison correction,
  per-component equal-weighted aggregation, calibration hallucination defense
- **P2 Design**: Canary task contamination detection, EvalTask provenance fields,
  sensitivity analysis script, reproduction manifest
- **Multi-provider**: Temperature propagation to all API calls (9 evaluators),
  DeepSeek/Groq/Gemini/Together via OpenAI-compatible backend, API key validation
- **Model backend unification**: `init_model()` standalone function, `_retry_call()`
  with exponential backoff in all model wrappers, `generate_chat()` for multi-turn,
  5 standalone evaluators refactored to use unified model routing (Llama via Together API)

## Reproducibility Contract

- Use `bioeval run --all --seed 42 --temperature 0.0` for run-level reproducibility controls.
- Deterministic split logic is maintained via `bioeval.scoring.splits`.
- Judge calls use deterministic decoding (`--judge-temperature 0.0`).
- Canary contamination check via `bioeval.scoring.splits.check_canary_contamination()`.
- See `docs/REPRODUCTION_MANIFEST.md` for full field specification.

## Release Guardrail

- Run `python scripts/check_release_consistency.py` before release/merge.
- CI enforces this check.

