# Changelog

All notable changes to BioEval will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
