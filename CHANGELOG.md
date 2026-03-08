# Changelog

All notable changes to BioEval will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2026-03-08

### Added

- **LongHorizon component** — 30 QA-based tasks for multi-step scientific reasoning
  - 5 task types: constraint tracking (6), state accumulation (6), error propagation (6), resource management (6), adaptive replanning (6)
  - Tests sustained reasoning across multi-stage experimental workflows without code execution
  - Programmatic scoring via `phrase_match()` with task-type-specific rubrics
  - Composite scoring: violation recall, target/elimination recall, affected/unaffected identification, infeasibility detection, required/prohibited element checking

- **Agentic component** — 24 pseudo-agentic multi-turn tasks with milestone-based progress scoring
  - 4 categories × 6 tasks: experimental design, bioinformatics pipeline, literature research, troubleshooting
  - Multi-step workflow: model receives scenario → step-by-step prompts → milestone scoring per step
  - Progress rate metric (milestones_achieved / total) inspired by AgentBoard (NeurIPS 2024)
  - No code execution required — evaluates reasoning quality, not tool-use success
  - Offline `score_response()` for batch evaluation without API calls

- Simulation generators for longhorizon and agentic in `bioeval simulate`
- Benchmark statistics coverage for all 11 components
- 26 new tests for agentic component (data loading, milestone scoring, progress rate, offline scoring, registry, normalizer)
- Longhorizon and agentic in `bioeval export`, `bioeval inventory`, and `bioeval run` CLI commands

### Changed

- Total components: 9 → **11**
- Base tasks: 197 → **251** (+30 longhorizon, +24 agentic)
- Total unique tasks: 301 → **355**
- Tests: 433 → **482**
- Version: 0.4.1 → 0.5.0
- Updated `check_release_consistency.py` to validate all 11 components
- Updated reproducibility framework expected components (9 → 11)

### Fixed

- **ag_lr_006**: Corrected factual error — "gut microbes consume ~95% of dietary tryptophan" → "~95% of the body's serotonin is produced in the gut"
- **ag_ts_004**: Fixed TMT11-plex arithmetic — "3 TMT sets × 40 samples" → "12 plexes total, 4 plexes per batch"
- **ag_lr_003**: CA 19-9 sensitivity clarified — added "(~79% overall, but only 40-65% for stage I-II)"
- **ag_bp_005**: H3K27ac peak calling mode — changed from "broad peak" to "peak calling (narrow per ENCODE or broad for super-enhancer analysis)"
- Removed dead code `AgenticTaskScore` dataclass from `agentic/scoring.py`

## [0.4.1] - 2026-03-02

### Fixed

- `load_tasks("extended")` in ProtoReason and CausalBio now correctly merges base + extended tasks (previously replaced base, dropping 5 tasks)

### Added

- `bioeval export` CLI command for JSONL data generation (HuggingFace-compatible)
- 20 new tests: data tier consistency (base⊆extended), baselines, datasheet, export validation

## [0.4.0] - 2026-03-02

### Changed

- DesignCheck base tier: 10 → 20 tasks (promoted design_011–design_020 from extended)
- MultiTurn base tier: 6 → 15 dialogues (promoted 9 domain-diverse dialogues from extended)
- Total base tasks: 178 → 197 (total unique remains 301)
- Fixed load_tasks() docstrings with correct extended counts
- README roadmap: Phase 1-2 marked COMPLETE

## [0.3.2] - 2026-03-01

### Added

- Auto-apply Benjamini-Hochberg multiple comparison correction when comparing >1 component
- `--correction` flag for `bioeval compare` (choices: auto, bh, bonferroni, none)
- Gemini token fairness transparency: constant, logging, `--equalize-tokens` flag
- `docs/FAIRNESS.md` documenting token budget asymmetry
- Weight sensitivity analysis framework (`bioeval sensitivity` CLI)
- Random and naive baseline computations (`bioeval/reporting/baselines.py`)
- LLM-as-Judge metadata (`get_judge_metadata()`), rubric versioning, and score validation (clamping to [1,5])
- Judge self-consistency measurement (`compute_judge_self_consistency()`)
- `docs/JUDGE_VALIDATION.md` — judge reliability protocol
- `docs/LIMITATIONS.md` — 8 key limitations documented
- `bioeval baselines` CLI command for random/naive baseline display

### Changed

- Migrated remaining substring matching to `phrase_match()` in debate, biosafety, datainterp
- Updated datasheet to cover all 9 components with limitations section
- Normalized judge score scale (1-5 → 0-1) in agreement analysis for correct `weighted_kappa`
- README: added Limitations and Documentation sections
- Version synchronized across version.py, STATUS.md, README.md

### Fixed

- `print_comparison()` displays corrected p-values when correction applied
- Significance stars now use corrected (not raw) p-values
- `analyze_agreement()` judge_passed threshold fixed from 0.5 to normalized midpoint

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
- Web interface for running evaluations
