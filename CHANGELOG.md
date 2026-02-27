# Changelog

All notable changes to BioEval will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-02-27

### Changed

- Synchronized package/documentation version metadata to `0.3.0`
- Updated README component/task inventory to match live CLI inventory
- Clarified CausalBio data provenance language (curated built-in tasks + optional external loaders)
- Enabled fail-fast CI behavior for formatting, typing, and test steps
- Added deterministic run-level seed contract to CLI (`bioeval run --seed`)
- Added release guardrail script (`scripts/check_release_consistency.py`) and CI enforcement
- Added `judge-pack` CLI command for human validation sampling from judge-scored runs
- Added cross-benchmark adapter (`bioeval adapt`) for LAB-Bench, BioProBench, BioLP-bench to canonical BioEval JSON
- Added adapter input template JSON files under `examples/adapters/` for all supported benchmarks
- Added adapter input validator command (`bioeval validate-adapter`) with per-benchmark schema checks
- Added `validate-adapter --strict` mode and benchmark JSON Schema references under `examples/adapters/schemas/`
- Added `validate-adapter --schema-check` for bundled JSON Schema validation
- Tightened adapter schema containers to require at least one record-list key (`results/predictions/items/tasks/examples/data`)
- Added `scripts/run_quality_checks.py` for one-shot local quality verification (pytest + release + optional lint/type checks)
- Simplified CI to a unified quality gate via `scripts/run_quality_checks.py --require-tools`
- Normalized MultiTurn score ingestion across dialogue/CLI result formats
- Standardized local quality tooling with `black + ruff + pre-commit`

## [0.1.0] - 2025-01-08

### Added

- **Core Evaluation Framework**
  - 6 evaluation components: ProtoReason, CausalBio, DesignCheck, Adversarial, MultiTurn, Calibration
  - 170+ evaluation tasks across all components
  - Support for Claude (Anthropic) and GPT (OpenAI) models

- **Prompt Enhancement System**
  - Calibration enhancement: Reduces overconfidence by requiring explicit evidence listing
  - Context defense: Filters misleading/irrelevant information
  - Edge case recognition: Catches boundary conditions
  - Nonsense detection: Catches hallucination traps with entity verification
  - Chain-of-thought: Structured 6-step reasoning for causal biology questions
  - Configurable via `PromptEnhancementConfig` dataclass

- **Evaluation Infrastructure**
  - Async execution with automatic rate limiting (10x faster)
  - SQLite-based response caching
  - LLM-as-Judge scoring with structured rubrics
  - Automated comparison testing (enhanced vs baseline)

- **Results & Visualization**
  - JSON output format for all evaluations
  - HTML comparison reports
  - Results visualization script
  - Jupyter notebooks for analysis

- **Documentation**
  - Comprehensive README with examples
  - Configuration documentation
  - API usage examples

### Performance Results

Initial evaluation with Claude Sonnet 4 shows:

| Test Type | Baseline | Enhanced | Improvement |
|-----------|----------|----------|-------------|
| False Premise | 60% | 100% | +40% |
| Plausible Nonsense | 67% | 100% | +33% |
| Edge Case | 75% | 100% | +25% |
| Hallucination Trap | 80% | 100% | +20% |
| **Overall** | 62.5% | 83.3% | **+20.8%** |

## [Unreleased]

### Planned
- Additional protocol tasks from protocols.io
- Extended DepMap integration
- Multi-language support
- Additional model integrations (Gemini, Llama)
- Web interface for running evaluations
