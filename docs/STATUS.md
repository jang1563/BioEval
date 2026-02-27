# BioEval Current Status (Canonical)

Last updated: 2026-02-27  
Version: `0.3.0`

This file is the canonical runtime status reference for counts, version, and reproducibility contract.

## Canonical Inventory (Code-Verified 2026-02-27)

- Base: `178`
- Extended additions: `123` (ProtoReason +45, CausalBio +34, DesignCheck +20, MultiTurn +24)
- Total unique: `301`
- Components: `protoreason` (14), `causalbio` (13), `designcheck` (10), `adversarial` (30), `multiturn` (6), `calibration` (30), `biosafety` (25), `datainterp` (25), `debate` (25)
- Tests: `299` passing

Note: Advanced tiers reuse base task IDs with the same prompts (no unique additions). Previous counts of "Advanced: 78" and "Total: 417" were inflated and have been corrected.

## CausalBio Ground Truth Contract

- `source_type`: `curated_builtin` or `external_verified`
- `source_id`: source module + task id or external dataset id
- `release`: benchmark release tag (`bioeval-vX.Y.Z`)
- `external_verified`: boolean

Base release defaults to curated built-in tasks; external verification pipelines are optional and separately declared.

## Reproducibility Contract

- Use `bioeval run --all --seed 42` for run-level reproducibility controls.
- Deterministic split logic is maintained via `bioeval.scoring.splits`.
- Judge calls use deterministic decoding (`temperature=0.0`).

## Release Guardrail

- Run `python scripts/check_release_consistency.py` before release/merge.
- CI enforces this check.

