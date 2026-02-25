# BioEval: Multi-dimensional Evaluation of LLMs for Biological Research

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.2.0-green.svg)](https://github.com/jang1563/BioEval)
[![Tests](https://img.shields.io/badge/tests-27%2F27%20passing-brightgreen.svg)](#testing)

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

BioEval fills this gap with **procedural reasoning**, **causal grounding** from experimental data, **design critique**, and **adversarial robustness** testing.

## Evaluation Components

| Component | What It Tests | Base Tasks | Ground Truth |
|-----------|--------------|:----------:|--------------|
| **ProtoReason** | Protocol execution, calculation, troubleshooting | 17 | Expert annotation |
| **CausalBio** | Perturbation outcome prediction | 13 | Experimental data (DepMap, CMap) |
| **DesignCheck** | Experimental design critique | 10 | Annotated flaws |
| **Adversarial** | Robustness to trick questions | 24 | Trap detection |
| **MultiTurn** | Scientific dialogue coherence | 6 | Conversation flow |
| **Calibration** | Confidence calibration | 10 | "I don't know" tests |

### Task Inventory

| Tier | Tasks | Description |
|------|:-----:|-------------|
| **Base** | 80 | Core evaluation tasks across all 6 components |
| **Extended** | 114 | Additional ProtoReason (70) and CausalBio (44) tasks |
| **Advanced** | 78 | Advanced ProtoReason (49), CausalBio (19), DesignCheck (10) |
| **Total** | **272** | Full benchmark suite |

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
bioeval run --all --model claude-sonnet-4-20250514

# Run specific component
bioeval run -c adversarial -m claude-sonnet-4-20250514

# Run with extended data tier
bioeval run --all --data-tier extended

# Compare two result files
bioeval compare results_a.json results_b.json

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

### Enhanced vs Baseline Prompt Comparison (Claude Sonnet 4)

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
│   │   ├── evaluator.py         # Base tasks (17)
│   │   ├── extended_data.py     # Extended tasks (70)
│   │   └── advanced_data.py     # Advanced tasks (49)
│   ├── causalbio/               # Causal biology component
│   │   ├── evaluator.py         # Base tasks (13)
│   │   ├── extended_data.py     # Extended tasks (44)
│   │   └── advanced_data.py     # Advanced tasks (19)
│   ├── designcheck/             # Experimental design critique
│   │   ├── evaluator.py         # Base tasks (10)
│   │   └── advanced_data.py     # Advanced tasks (10)
│   ├── adversarial/             # Adversarial robustness (24 tasks)
│   ├── multiturn/               # Multi-turn dialogues (6 scenarios)
│   ├── scoring/                 # Scoring & calibration
│   └── calibration/             # Calibration tests (10 tasks)
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
├── tests/                       # Test suite (27 tests)
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
- 13+ protocols with 235+ steps (sources: protocols.io, Nature Protocols, STAR Protocols)
- 44+ causal biology tasks with experimental ground truth
- 10 flawed experimental designs with 30 annotated flaws
- 24 adversarial robustness tests across 7 categories
- 6 multi-turn dialogue scenarios

### External Data Sources (Optional)

| Source | License | Used For |
|--------|---------|----------|
| [DepMap](https://depmap.org/) | CC BY 4.0 | Gene essentiality ground truth |
| [Connectivity Map](https://clue.io/) | CC BY 4.0 | Drug response signatures |
| [protocols.io](https://www.protocols.io/) | Various | Additional protocols |
| [GEO](https://www.ncbi.nlm.nih.gov/geo/) | Public | Expression data |

## Testing

```bash
# Run full test suite
pytest tests/ -v

# Expected output: 27 passed in ~1s
```

Test coverage includes:
- Data loading for all 6 components
- Task structure validation
- Confidence extraction
- Adversarial scoring
- Calibration metrics
- Response caching
- Statistics functions

## API Cost Estimates

| Tier | Tasks | Cost per Run (Claude) |
|------|:-----:|-----------------:|
| Base | 80 | ~$1.40 |
| Base + Judge | 80 | ~$1.80 |
| Extended + Judge | 194 | ~$3.50 |

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
