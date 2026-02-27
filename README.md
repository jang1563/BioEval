# BioEval: Multi-dimensional Evaluation of LLMs for Biological Research

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.3.0-green.svg)](https://github.com/jang1563/BioEval)
[![Tests](https://img.shields.io/badge/tests-299%2F299%20passing-brightgreen.svg)](#testing)

Canonical status note: for version/task-count/reproducibility contract, see [docs/STATUS.md](docs/STATUS.md).

## Overview

BioEval is a benchmark framework that evaluates whether large language models can **reason about biology**, not just recall biological facts. While existing benchmarks test factual knowledge (e.g., "What does TP53 encode?"), BioEval tests the reasoning capabilities scientists actually need: executing protocols, predicting experimental outcomes, identifying methodological flaws, and handling adversarial scenarios.

### Key Insight

> Current LLM benchmarks for biology measure whether models have *learned about* biology from text. BioEval measures whether models have *learned biology* — the causal reasoning that predicts what happens when you perturb a biological system.

### Why Existing Benchmarks Are Insufficient

| Benchmark | Limitation |
|-----------|------------|
| MedQA, MedMCQA | Multiple choice, knowledge retrieval only |
| GPQA | Intentionally removes questions where experts disagree |
| PubMedQA | Yes/no questions on abstracts |
| BioASQ | Question answering, not reasoning |
| LAB-Bench | Factual accuracy only |

BioEval fills this gap with **procedural reasoning**, **causal perturbation reasoning**, **design critique**, and **adversarial robustness** testing.

## Evaluation Components

| Component | What It Tests | Base Tasks | Ground Truth |
|-----------|--------------|:----------:|--------------|
| **ProtoReason** | Protocol execution, calculation, troubleshooting | 14 | Expert annotation |
| **CausalBio** | Perturbation outcome prediction | 13 | Curated benchmark ground truth (optional external loader) |
| **DesignCheck** | Experimental design critique | 10 | Annotated flaws |
| **Adversarial** | Robustness to trick questions | 30 | Trap detection |
| **MultiTurn** | Scientific dialogue coherence | 6 | Conversation flow |
| **Calibration** | Confidence calibration | 30 | Confidence-behavior alignment tasks |
| **BioSafety** | Biosafety and dual-use risk judgment | 25 | Safety rubric |
| **DataInterp** | Biological data interpretation | 25 | Quant/interpretation rubric |
| **Debate** | Multi-agent debate reliability | 25 | Debate outcome/process rubric |

### Task Inventory

| Tier | Tasks | Description |
|------|:-----:|-------------|
| **Base** | 178 | Base tasks across 9 components |
| **Extended** | 123 | Additional ProtoReason (+45), CausalBio (+34), DesignCheck (+20), MultiTurn (+24) |
| **Total Unique** | **301** | Full benchmark suite |

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/jang1563/BioEval.git
cd BioEval

# Option 1: pip install
pip install -e .

# Option 2: conda (recommended for Apple Silicon)
conda create -n bioeval python=3.11
conda activate bioeval
pip install -e .
```

### CLI Usage

```bash
# Show complete task inventory (no API key needed)
bioeval inventory

# Dry run — shows what would be evaluated without API calls
bioeval run --all --dry-run

# Run full evaluation
export ANTHROPIC_API_KEY="your-key-here"
bioeval run --all --model claude-sonnet-4-20250514 --seed 42

# Run specific component
bioeval run -c adversarial -m claude-sonnet-4-20250514

# Run with extended data tier
bioeval run --all --data-tier extended

# Compare two result files
bioeval compare results_a.json results_b.json

# Generate human validation pack for judge reliability study
bioeval judge-pack results.json --sample-size 50 --seed 42

# Convert external benchmark outputs into BioEval canonical schema
bioeval adapt lab-bench /path/to/labbench_results.json -o results/labbench_adapted.json
bioeval adapt bioprobench /path/to/bioprobench_results.json -o results/bioprobench_adapted.json
bioeval adapt biolp-bench /path/to/biolp_results.json -o results/biolp_adapted.json

# Validate external benchmark JSON before conversion
bioeval validate-adapter lab-bench /path/to/labbench_results.json
bioeval validate-adapter bioprobench /path/to/bioprobench_results.json --json
bioeval validate-adapter biolp-bench /path/to/biolp_results.json

# Run bundled JSON Schema validation
bioeval validate-adapter lab-bench /path/to/labbench_results.json --schema-check

# Strict mode: warnings also fail (non-zero exit code)
bioeval validate-adapter lab-bench /path/to/labbench_results.json --schema-check --strict

# Show pre-cached results (no API key needed)
bioeval demo
```

### Python API

```python
from bioeval.protoreason.evaluator import ProtoReasonEvaluator
from bioeval.causalbio.evaluator import CausalBioEvaluator
from bioeval.adversarial.tasks import AdversarialEvaluator

# Run individual components
evaluator = ProtoReasonEvaluator(model_name="claude-sonnet-4-20250514")
results = evaluator.run_evaluation()

# With enhanced prompts (adversarial)
evaluator = AdversarialEvaluator(use_enhanced_prompts=True)
results = evaluator.run_evaluation()
```

## Preliminary Results

### 9-Component Evaluation (Claude Sonnet 4, seed=42)

| Component | Tasks | Mean Score | Primary Metric |
|-----------|:-----:|:----------:|----------------|
| ProtoReason | 14 | **0.978** | Step ordering / calculation / troubleshooting accuracy |
| Adversarial | 30 | **0.923** | Robustness against hallucination traps |
| BioSafety | 25 | **0.829** | Safety judgment & dual-use risk identification |
| CausalBio | 13 | **0.798** | Perturbation prediction accuracy |
| MultiTurn | 6 | **0.772** | Dialogue coherence & context retention |
| DataInterp | 25 | **0.720** | Quantitative data interpretation |
| Calibration | 30 | **0.690** | 1 − calibration error |
| DesignCheck | 10 | **0.535** | Flaw detection F1 |
| Debate | 25 | **0.377** | Multi-agent debate composite score |
| **Overall** | **178** | **0.727** | Weighted mean across all components |

### Enhanced vs Baseline Prompt Comparison (Adversarial subset)

| Test Type | Baseline | Enhanced | Improvement |
|-----------|:--------:|:--------:|:-----------:|
| False Premise | 60% | 100% | +40% |
| Plausible Nonsense | 67% | 100% | +33% |
| Edge Case | 75% | 100% | +25% |
| Hallucination Trap | 80% | 100% | +20% |
| **Overall Pass Rate** | **62.5%** | **83.3%** | **+20.8%** |

## Features

### Prompt Enhancement System

BioEval includes targeted prompt engineering strategies that address specific failure modes:

- **Calibration Enhancement** — Reduces overconfidence by requiring explicit evidence listing
- **Context Defense** — Filters misleading/irrelevant information via relevance analysis
- **Edge Case Recognition** — Forces explicit consideration of boundary conditions
- **Nonsense Detection** — Catches hallucination traps by requiring entity verification
- **Chain-of-Thought** — Structured 6-step reasoning for causal biology questions

```python
from bioeval.prompts import enhance_prompt, PromptEnhancementConfig

config = PromptEnhancementConfig(
    calibration=True,
    context_defense=True,
    edge_case=True,
    nonsense_detection=True,
    chain_of_thought=True
)
enhanced = enhance_prompt(original_prompt, config)
```

### Model Support

| Provider | Models | Method |
|----------|--------|--------|
| Anthropic | Claude Sonnet 4, Claude Opus 4 | API |
| OpenAI | GPT-4o, GPT-4-turbo | API |
| HuggingFace | Mistral, Llama, etc. | Local (with LoRA support) |

### Additional Features

- **Async Execution** — Parallel evaluation with rate limiting (`scripts/run_enhanced.py`)
- **Response Caching** — SQLite-based caching to avoid redundant API calls
- **LLM-as-Judge** — Semantic evaluation using structured rubrics
- **Confidence Calibration** — ECE, overconfidence rates, reliability diagrams
- **Multi-Turn Dialogue** — Hypothesis refinement, iterative design, troubleshooting

## Project Structure

```
BioEval/
├── bioeval/
│   ├── __init__.py              # Package exports
│   ├── cli.py                   # Unified CLI entry point
│   ├── config.py                # Configuration settings
│   ├── models/
│   │   └── base.py              # Model wrappers (Claude, OpenAI, HuggingFace)
│   ├── prompts/
│   │   └── prompt_templates.py  # Enhancement templates
│   ├── protoreason/             # Protocol reasoning component
│   │   ├── evaluator.py         # Base tasks (14)
│   │   ├── extended_data.py     # Extended tasks (+45)
│   │   └── advanced_data.py     # Advanced tier
│   ├── causalbio/               # Causal biology component
│   │   ├── evaluator.py         # Base tasks (13)
│   │   ├── extended_data.py     # Extended tasks (+34)
│   │   └── advanced_data.py     # Advanced tier
│   ├── designcheck/             # Experimental design critique
│   │   ├── evaluator.py         # Base tasks (10)
│   │   ├── extended_data.py     # Extended tasks (+20)
│   │   └── advanced_data.py     # Advanced tier
│   ├── adversarial/             # Adversarial robustness (30 tasks)
│   ├── multiturn/               # Multi-turn dialogues (6 scenarios)
│   ├── biosafety/               # Biosafety evaluation (25 tasks)
│   ├── datainterp/              # Data interpretation (25 tasks)
│   ├── debate/                  # Multi-agent debate (25 tasks)
│   └── scoring/                 # Scoring & calibration
├── scripts/
│   ├── run_evaluation.py        # Basic evaluation runner
│   ├── run_enhanced.py          # Full-featured async runner
│   ├── run_comparison.py        # Enhanced vs baseline comparison
│   └── visualize_results.py     # Results visualization
├── docs/                        # Project documentation
│   ├── PRD.md                   # Product Requirements Document
│   ├── IMPROVEMENT_PLAN.md      # Development roadmap
│   ├── BIOLOGICAL_AMBIGUITY_DESIGN.md  # BioAmbiguity component design
│   ├── LITERATURE_SURVEY.md     # Related work survey
│   ├── EXPERT_PANEL_REVIEW.md   # Expert panel feedback
│   ├── PUBLICATION_QUALITY_REVIEW.md   # Quality review
│   └── PHASE0_BASELINE.md      # Phase 0 baseline report
├── results/                     # Evaluation outputs
├── tests/                       # Test suite (299 tests currently passing)
├── notebooks/                   # Analysis notebooks
├── setup.py
├── requirements.txt
└── README.md
```

## Development Roadmap

| Phase | Goal | Status |
|-------|------|--------|
| **Phase 0** | Make It Run — imports, tests, CLI, baseline | **COMPLETE** |
| **Phase 1** | Make It Score — real metrics (Kendall's tau, directional accuracy, detection rate) | Planned |
| **Phase 2** | Make It Credible — 3-model comparison, statistical tests, judge validation | Planned |
| **Phase 2b** | BioAmbiguity — novel component for context-dependent biological reasoning (45 tasks) | Planned |
| **Phase 3** | Make It Impressive — dashboard, publication prep, HuggingFace distribution | Planned |

Publication target: **NeurIPS Datasets & Benchmarks** / **Nature Methods**

## Data Sources

### Built-in Data

BioEval includes expert-curated evaluation tasks that work out of the box:
- 14 ProtoReason tasks: step ordering, missing step detection, calculation, troubleshooting
- 13 CausalBio tasks (+ 34 extended): knockout, pathway, epistasis, drug response
- 10 DesignCheck tasks (+ 20 extended) with annotated flaw taxonomy (30 flaw types)
- 30 adversarial robustness tests across 8 categories
- 6 multi-turn dialogue scenarios (+ 24 extended)
- 30 calibration tasks including overconfidence traps
- 25 biosafety dual-use risk judgment tasks
- 25 data interpretation tasks
- 25 multi-agent debate tasks

### External Data Sources (Optional, Not Required for Base Run)

| Source | License | Used For |
|--------|---------|----------|
| [DepMap](https://depmap.org/) | CC BY 4.0 | Gene essentiality ground truth |
| [Connectivity Map](https://clue.io/) | CC BY 4.0 | Drug response signatures |
| [protocols.io](https://www.protocols.io/) | Various | Additional protocols |
| [GEO](https://www.ncbi.nlm.nih.gov/geo/) | Public | Expression data |

Current release note: base CausalBio tasks are bundled curated tasks. External loaders are optional and intended for expanded/production pipelines.

## Testing

```bash
# Run full test suite
pytest tests/ -v

# Expected: 299 passed

# Format + lint checks (publication-grade hygiene)
black --check bioeval/ scripts/ tests/
ruff check bioeval/ scripts/ tests/

# Optional: install git hooks
pre-commit install
pre-commit run --all-files

# One-shot local quality suite (pytest + release checks + optional lint/type tools)
python scripts/run_quality_checks.py
# CI-like strict mode (fails if black/ruff/mypy missing)
python scripts/run_quality_checks.py --require-tools
```

CI note: GitHub Actions uses `python scripts/run_quality_checks.py --require-tools` as the primary quality gate.

Test coverage includes:
- Data loading for all components
- Task structure validation
- Confidence extraction
- Adversarial scoring
- Calibration metrics
- Response caching
- Statistics functions

Release consistency:

```bash
python scripts/check_release_consistency.py
```

Cross-benchmark adapter output uses the same top-level schema as native runs:
- `metadata` (includes `source_benchmark`, `adapter_version`, `adapter_schema`)
- `summary` (`total_tasks`, `by_component`)
- `results` (per-component task rows with `task_id`, `task_type`, `prompt`, `response`, `score`, `passed`)

Input template JSON files are provided in:
- `examples/adapters/lab-bench_input_template.json`
- `examples/adapters/bioprobench_input_template.json`
- `examples/adapters/biolp-bench_input_template.json`

Companion JSON Schema references are provided in:
- `examples/adapters/schemas/lab-bench_input.schema.json`
- `examples/adapters/schemas/bioprobench_input.schema.json`
- `examples/adapters/schemas/biolp-bench_input.schema.json`

## API Cost Estimates

| Tier | Tasks | Cost per Run (Claude) |
|------|:-----:|-----------------:|
| Base (all components) | 178 | Environment/model-dependent |
| Base + Judge | 178 | Environment/model-dependent |
| Extended + Judge | 301 | Environment/model-dependent |

## Citation

```bibtex
@software{bioeval2026,
  author = {JangKeun Kim},
  title = {BioEval: Multi-dimensional Evaluation of LLMs for Biological Research},
  year = {2026},
  url = {https://github.com/jang1563/BioEval}
}
```

## License

MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments

- DepMap project for CRISPR screening data
- Connectivity Map for drug perturbation signatures
- protocols.io community for open protocols
