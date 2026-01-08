# BioEval: Multi-dimensional Evaluation of LLMs for Biological Research

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

## Overview

BioEval is an evaluation framework that tests whether large language models can *do* biology, not just *know* biology. While existing benchmarks test factual recall (e.g., "What does TP53 encode?"), BioEval tests the reasoning capabilities scientists actually need: executing protocols, predicting experimental outcomes, and identifying methodological flaws.

### Key Insight

> Current LLM benchmarks for biology measure whether models have *learned about* biology from text. BioEval measures whether models have *learned biology*—the causal reasoning that predicts what happens when you perturb a system.

## Example Results

BioEval includes **prompt enhancement strategies** that significantly improve model performance on adversarial tasks:

### Enhanced vs Baseline Comparison

| Test Type | Baseline | Enhanced | Improvement |
|-----------|----------|----------|-------------|
| **False Premise** | 60% | 100% | +40% |
| **Plausible Nonsense** | 67% | 100% | +33% |
| **Edge Case** | 75% | 100% | +25% |
| **Hallucination Trap** | 80% | 100% | +20% |
| **Overall Pass Rate** | 62.5% | 83.3% | **+20.8%** |

These improvements are achieved through targeted prompt engineering that addresses specific failure modes identified during evaluation.

## Components

| Component | What it tests | Tasks | Ground truth |
|-----------|--------------|-------|--------------|
| **ProtoReason** | Protocol execution & troubleshooting | 70+ | Expert annotation |
| **CausalBio** | Perturbation outcome prediction | 44 | Experimental data (DepMap, CMap) |
| **DesignCheck** | Experimental design critique | 10 designs | Annotated flaws |
| **Adversarial** | Robustness to trick questions | 24 | Trap detection |
| **MultiTurn** | Scientific dialogue coherence | 6 dialogues | Conversation flow |
| **Calibration** | Confidence calibration | 10 | "I don't know" tests |

**Total: 170+ evaluation tasks across 6 components**

## Quick Start

```bash
# Clone repository
git clone https://github.com/jang1563/BioEval.git
cd BioEval

# Install dependencies
pip install -e .

# Set API key
export ANTHROPIC_API_KEY="your-key-here"

# Run basic evaluation
python scripts/run_evaluation.py --model claude-sonnet-4-20250514 --component all

# Run comparison test (enhanced vs baseline prompts)
python scripts/run_comparison.py
```

## Features

### 🎯 Prompt Enhancement System

BioEval includes a sophisticated prompt enhancement system that improves model performance by addressing specific failure modes:

#### 1. Calibration Enhancement
Reduces overconfidence by requiring explicit evidence listing before stating confidence levels.
```python
from bioeval.prompts import add_calibration_instructions
enhanced_prompt = add_calibration_instructions(original_prompt)
```

#### 2. Context Defense
Filters misleading/irrelevant information by forcing explicit relevance analysis.
```python
from bioeval.prompts import add_context_defense
enhanced_prompt = add_context_defense(original_prompt)
```

#### 3. Edge Case Recognition
Catches boundary conditions by forcing explicit consideration of unusual scenarios.
```python
from bioeval.prompts import add_edge_case_check
enhanced_prompt = add_edge_case_check(original_prompt)
```

#### 4. Nonsense Detection
Catches hallucination traps by requiring verification of biological entities.
```python
from bioeval.prompts import add_nonsense_detection
enhanced_prompt = add_nonsense_detection(original_prompt)
```

#### 5. Chain-of-Thought for Causal Reasoning
Structured 6-step reasoning for causal biology questions.
```python
from bioeval.prompts import add_chain_of_thought
enhanced_prompt = add_chain_of_thought(original_prompt)
```

#### Composite Enhancement
Apply all enhancements at once:
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

### 🔄 Automated Comparison Testing

Run head-to-head comparisons between enhanced and baseline prompts:

```bash
# Run comparison with default settings
python scripts/run_comparison.py

# Output includes:
# - results/enhanced_TIMESTAMP.json
# - results/baseline_TIMESTAMP.json
# - results/comparison_TIMESTAMP.json
# - results/comparison_report_TIMESTAMP.html
```

### 🚀 Async Execution (10x faster)
Run evaluations in parallel with automatic rate limiting:
```bash
python scripts/run_enhanced.py --max-concurrent 10
```

### 💾 Response Caching
Avoid redundant API calls with SQLite-based caching:
```bash
# Check cache stats
python scripts/run_enhanced.py --cache-stats

# Clear cache
python scripts/run_enhanced.py --clear-cache
```

### 🧑‍⚖️ LLM-as-Judge Scoring
Semantic evaluation using structured rubrics:
```bash
python scripts/run_enhanced.py --use-judge
```

### 📊 Confidence Calibration
Measure if models know what they don't know:
- Expected Calibration Error (ECE)
- Overconfidence/underconfidence rates
- Reliability diagrams

### 🎯 Adversarial Robustness
Test resistance to common failure modes:
```bash
python scripts/run_enhanced.py --component adversarial
```
Includes:
- False premise detection (correcting wrong assumptions)
- Hallucination traps (made-up genes, drugs, papers)
- Misleading context (ignoring irrelevant information)
- Edge cases and contradictions

### 💬 Multi-Turn Dialogue
Test scientific conversation coherence:
```python
from bioeval.multiturn.dialogues import MultiTurnEvaluator
evaluator = MultiTurnEvaluator()
results = evaluator.run_all_dialogues()
```
Scenarios include:
- Hypothesis refinement through discussion
- Iterative experimental design
- Troubleshooting with follow-up questions
- Peer review response

## Installation

### Using pip

```bash
pip install -e .
```

### Using conda

```bash
conda create -n bioeval python=3.10
conda activate bioeval
pip install -e .
```

### Required API keys

Set as environment variables:
- `ANTHROPIC_API_KEY` for Claude models
- `OPENAI_API_KEY` for GPT models (optional, for comparison)

## Evaluation Components

### 1. ProtoReason: Protocol Procedural Reasoning

Tests whether LLMs can correctly execute, troubleshoot, and reason about experimental protocols.

**Task types:**
- Step ordering (shuffled protocol reconstruction)
- Missing step detection
- Safety-critical reasoning
- Calculation tasks (dilutions, concentrations)
- Troubleshooting (differential diagnosis)

**Data sources:** protocols.io, Nature Protocols, STAR Protocols

```python
from bioeval.protoreason.evaluator import ProtoReasonEvaluator

evaluator = ProtoReasonEvaluator()
results = evaluator.run_evaluation()
```

### 2. CausalBio: Causal Perturbation Prediction

Tests causal biological reasoning using experimental perturbation data as ground truth.

**Task types:**
- Gene knockout phenotype prediction
- Pathway reasoning (downstream effects)
- Drug response prediction
- Epistasis reasoning (genetic interactions)

**Data sources:** DepMap, Connectivity Map, LINCS L1000, public Perturb-seq

```python
from bioeval.causalbio.evaluator import CausalBioEvaluator

# With enhanced prompts (default)
evaluator = CausalBioEvaluator(use_enhanced_prompts=True)
results = evaluator.run_evaluation()

# Without enhancements (baseline)
evaluator = CausalBioEvaluator(use_enhanced_prompts=False)
results = evaluator.run_evaluation()
```

### 3. DesignCheck: Experimental Design Critique

Tests whether LLMs can identify flaws in experimental designs.

**Flaw categories:**
- Missing/inappropriate controls
- Statistical issues (power, test selection, pseudoreplication)
- Confounders (batch effects, technical variables)
- Interpretation errors

```python
from bioeval.designcheck.evaluator import DesignCheckEvaluator

evaluator = DesignCheckEvaluator()
results = evaluator.run_evaluation()
```

### 4. Adversarial Robustness

Tests model resistance to various adversarial scenarios:

| Type | Description | Example |
|------|-------------|---------|
| `false_premise` | Questions with incorrect assumptions | "Why does TP53 promote cancer?" (it doesn't) |
| `hallucination_trap` | Made-up biological entities | "What pathway does ONCORIX regulate?" |
| `misleading_context` | Irrelevant details mixed in | Extra information that shouldn't affect the answer |
| `plausible_nonsense` | Realistic-sounding but false claims | Plausible but incorrect mechanisms |
| `edge_case` | Boundary conditions | Unusual cell types or extreme conditions |
| `contradictory` | Self-contradicting statements | Logically inconsistent scenarios |

```python
from bioeval.adversarial.tasks import AdversarialEvaluator

# With enhanced prompts
evaluator = AdversarialEvaluator(use_enhanced_prompts=True)
results = evaluator.run_evaluation()
```

### 5. Error Taxonomy

Systematic categorization of how LLMs fail in biological reasoning.

**Error categories:**
- Knowledge errors (hallucination, outdated info, domain confusion)
- Reasoning errors (causal reversal, pathway truncation, scale confusion)
- Procedural errors (step omission/hallucination, reagent confusion)
- Uncertainty errors (overconfidence, false hedging)

## Configuration

Configure prompt enhancements in `bioeval/config.py`:

```python
# Enable/disable prompt enhancements globally
PROMPT_ENHANCEMENTS_ENABLED = True

# Individual enhancements
ENHANCEMENT_CALIBRATION = True
ENHANCEMENT_CONTEXT_DEFENSE = True
ENHANCEMENT_EDGE_CASE = True
ENHANCEMENT_NONSENSE_DETECTION = True
ENHANCEMENT_CHAIN_OF_THOUGHT = True

# Fine-tuning
CALIBRATION_MIN_EVIDENCE = 2  # Min evidence pieces for high confidence
```

## Project Structure

```
BioEval/
├── bioeval/
│   ├── __init__.py
│   ├── config.py              # Configuration settings
│   ├── models/
│   │   └── base.py            # Model wrappers (Claude, OpenAI)
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── prompt_templates.py # Enhancement templates
│   ├── protoreason/           # Protocol reasoning
│   ├── causalbio/             # Causal biology
│   ├── designcheck/           # Experimental design
│   ├── adversarial/           # Adversarial tests
│   ├── multiturn/             # Multi-turn dialogues
│   └── calibration/           # Confidence calibration
├── scripts/
│   ├── run_evaluation.py      # Basic evaluation runner
│   ├── run_enhanced.py        # Enhanced evaluation with all features
│   ├── run_comparison.py      # Compare enhanced vs baseline
│   └── visualize_results.py   # Results visualization
├── results/                   # Evaluation outputs
├── notebooks/                 # Analysis notebooks
├── tests/                     # Unit tests
├── setup.py
├── requirements.txt
└── README.md
```

## Data

### Built-in data

BioEval includes curated evaluation tasks that work out of the box:
- 13 protocols with 235 steps
- 44 causal biology tasks with DepMap/CMap ground truth
- 10 flawed experimental designs with 30 annotated flaws
- 24 adversarial robustness tests
- 6 multi-turn dialogue scenarios

### External data sources (optional)

For extended evaluation with live data:

| Source | URL | License | Used for |
|--------|-----|---------|----------|
| DepMap | https://depmap.org/ | CC BY 4.0 | Gene essentiality ground truth |
| Connectivity Map | https://clue.io/ | CC BY 4.0 | Drug response signatures |
| protocols.io | https://www.protocols.io/ | Various | Additional protocols |
| GEO | https://www.ncbi.nlm.nih.gov/geo/ | Public | Expression data |

## Methodology

### Why existing benchmarks are insufficient

| Benchmark | Limitation |
|-----------|------------|
| MedQA, MedMCQA | Multiple choice, knowledge retrieval |
| PubMedQA | Yes/no questions on abstracts |
| BioASQ | Question answering, not reasoning |

### BioEval's approach

1. **Procedural reasoning**: Can the model execute a protocol, not just describe it?
2. **Causal grounding**: Use experimental data as ground truth, not text-derived answers
3. **Design thinking**: Test scientific judgment, not fact recall
4. **Error analysis**: Understand *how* models fail to guide improvement
5. **Prompt engineering**: Provide tools to improve model performance

## Contributing

Contributions welcome! Please open an issue or pull request.

Priority areas:
- Additional protocol tasks
- New perturbation datasets
- Error annotation
- Multi-language support
- Additional model integrations

## Citation

```bibtex
@software{bioeval2025,
  author = {JangKeun Kim},
  title = {BioEval: Multi-dimensional Evaluation of LLMs for Biological Research},
  year = {2025},
  url = {https://github.com/jang1563/BioEval}
}
```

## License

MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments

- DepMap project for CRISPR screening data
- Connectivity Map for drug perturbation signatures
- protocols.io community for open protocols
