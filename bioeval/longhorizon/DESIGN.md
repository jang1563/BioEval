# LongHorizon Component: Design Document

## Overview

BioEval Component 10: Multi-step scientific reasoning evaluation.

Tests whether LLMs can sustain coherent reasoning across multi-step
experimental workflows. Unlike `multiturn` (dialogue refinement) or
`protoreason` (single-protocol step ordering), `longhorizon` evaluates
the model's ability to **maintain state, enforce constraints, and adapt
plans across an entire experimental campaign** spanning multiple stages.

### Motivation

From 243 AI-assisted research sessions (Cognitive Bottleneck paper, accepted):
- AI production rate exceeds scientist verification rate
- Models lose track of constraints after ~5 planning stages
- Prior Long-Horizon prototype found: 34% constraint violations after stage 5,
  62% sample-availability tracking failures

From Anthropic Life Sciences JD:
- "Develop approaches to address long-horizon task completion and complex
  reasoning challenges essential for scientific discovery"

### Differentiation from Existing Components

| Component | What it tests | Horizon |
|---|---|---|
| protoreason | Single protocol step ordering/troubleshooting | Short (1 protocol) |
| multiturn | Dialogue refinement across turns | Medium (3-5 turns) |
| causalbio | Single causal inference question | Short (1 question) |
| **longhorizon** | **Multi-stage experimental campaign with state/constraints** | **Long (6-10 stages)** |

---

## Task Types (5 types, target 30 tasks total)

### 1. `constraint_tracking` (6 tasks)

Model receives a multi-stage experiment plan and must identify constraint
violations introduced at later stages that conflict with earlier decisions.

**Example scenario**: RNA-seq experiment across 4 conditions x 3 timepoints.
- Stage 1: Define experimental design (conditions, replicates, timepoints)
- Stage 2: Sample collection protocol (volume, storage, processing timeline)
- Stage 3: Library preparation (kit selection, input requirements)
- Stage 4: Sequencing plan (depth, read length, multiplexing)
- Stage 5: Analysis pipeline (alignment, normalization, DE analysis)
- **Test**: At stage 4, the multiplexing plan requires more samples than
  available from stage 2's collection protocol. Does the model detect this?

**Ground truth**: Programmatic. Each task has embedded constraint violations
with known locations. Scoring: binary (detected/missed) per violation.

**Biological domains**:
- Transcriptomics (RNA-seq, scRNA-seq)
- Proteomics (mass spec, sample prep constraints)
- Clinical trial design (enrollment, endpoint, timeline)
- Drug screening (compound library, assay compatibility)
- Multi-omics integration (sample splitting, processing order)

### 2. `state_accumulation` (6 tasks)

Model receives results from each stage sequentially and must make decisions
at later stages that correctly incorporate ALL prior results.

**Example scenario**: Drug target validation campaign.
- Stage 1: Literature review identifies 5 candidate targets (genes A-E)
- Stage 2: Expression analysis eliminates gene C (not expressed in tissue)
- Stage 3: CRISPR knockout shows gene A and D have phenotype
- Stage 4: Dose-response for compounds against A and D
- Stage 5: Selectivity profiling eliminates compound against D (off-target)
- **Test**: At stage 6, model must correctly state that only gene A with its
  specific compound remains viable, citing all elimination reasons.

**Ground truth**: State vector at each checkpoint. The correct accumulated
state is deterministic. Scoring: Jaccard similarity between model's stated
active candidates and ground truth active set at each checkpoint.

### 3. `error_propagation` (6 tasks)

Model is given a completed multi-stage plan, then told that an intermediate
result was wrong. Must correctly identify all downstream consequences.

**Example scenario**: Spaceflight gene expression study.
- Stage 1-4 completed with assumed housekeeping gene GAPDH stability
- Reveal: GAPDH is actually differentially expressed in microgravity
- **Test**: Model must identify which downstream conclusions are invalidated
  (DE analysis, pathway enrichment, biomarker candidates) and which survive
  (raw data quality, sample processing, library metrics).

**Ground truth**: Curated list of affected vs. unaffected downstream steps.
Scoring: Precision/recall on affected step identification.

**Biological relevance**: This directly mirrors real research failures where
an early assumption (reference gene stability, antibody specificity, cell
line identity) turns out to be wrong.

### 4. `resource_management` (6 tasks)

Model must allocate limited resources (samples, budget, time, equipment)
across a multi-stage experiment while satisfying all constraints.

**Example scenario**: Biobank sample allocation.
- 12 plasma aliquots per patient, 8 patients
- Need: metabolomics (2 aliquots), proteomics (3 aliquots), cfDNA (2 aliquots),
  cytokine panel (1 aliquot), backup storage (2 aliquots minimum)
- Additional constraint: some assays require fresh-frozen, others tolerate 1 F/T cycle
- **Test**: Stage 5 proposes adding a lipidome panel (2 aliquots). Model must
  determine whether this is feasible and what tradeoffs are needed.

**Ground truth**: Programmatic constraint satisfaction. Each scenario has a
known feasibility answer and optimal/suboptimal allocation strategies.
Scoring: Feasibility correct (binary) + allocation quality (constraint
violations counted).

**Biological relevance**: Directly from CAMbank experience. Real biobank
allocation is a constraint satisfaction problem.

### 5. `adaptive_replanning` (6 tasks)

Model receives unexpected intermediate results and must revise the
experimental plan while preserving valid prior work.

**Example scenario**: scRNA-seq experiment pivot.
- Original plan: Compare spaceflight vs. ground control in 4 cell types
- Stage 3 result: One cell type shows unexpected batch effect, data unusable
- **Test**: Model must propose revised analysis that (a) drops affected cell
  type, (b) adjusts statistical power calculations, (c) preserves valid
  comparisons, (d) does NOT restart from scratch.

**Ground truth**: Structured rubric with required elements (drop affected,
adjust power, preserve valid) and prohibited elements (restart entirely,
ignore the problem, proceed without adjustment).
Scoring: LLM-judge with structured rubric + programmatic constraint check.

---

## Architecture

### File Structure

```
bioeval/longhorizon/
    __init__.py
    DESIGN.md           # This file
    evaluator.py        # LongHorizonEvaluator class
    tasks.py            # Task definitions (30 tasks across 5 types)
    scenarios/          # Complex scenario data (JSON)
        constraint_tracking.json
        state_accumulation.json
        error_propagation.json
        resource_management.json
        adaptive_replanning.json
    scoring.py          # Component-specific scoring logic
```

### Evaluator Pattern

Follows BioEval convention:

```python
class LongHorizonEvaluator(BaseEvaluator):
    def load_tasks(self, data_tier="base") -> list[EvalTask]:
        ...
    def evaluate_single(self, task, response) -> EvalResult:
        ...
```

### Scoring Strategy

Mixed scoring (following existing BioEval patterns):

| Task Type | Primary Scoring | Secondary |
|---|---|---|
| constraint_tracking | Programmatic (violation detection) | None |
| state_accumulation | Programmatic (state vector match) | None |
| error_propagation | Programmatic (affected step P/R) | LLM-judge (reasoning quality) |
| resource_management | Programmatic (constraint satisfaction) | None |
| adaptive_replanning | LLM-judge (structured rubric) | Programmatic (constraint check) |

### Registry Entry

```python
"longhorizon": ComponentInfo(
    name="longhorizon",
    description="Long-horizon scientific reasoning: constraint tracking, "
                "state accumulation, error propagation, resource management, "
                "adaptive replanning across multi-stage experiments",
    evaluator_module="bioeval.longhorizon.evaluator",
    evaluator_class="LongHorizonEvaluator",
    task_data_module="bioeval.longhorizon.tasks",
    task_types=[
        "constraint_tracking",
        "state_accumulation",
        "error_propagation",
        "resource_management",
        "adaptive_replanning",
    ],
    supports_data_tiers=["base"],
    normalizer_name="normalize_longhorizon",
    judge_rubric_types=["adaptive_replanning", "error_propagation_reasoning"],
),
```

---

## Implementation Plan

### Phase 1: Scaffold + constraint_tracking (3-4 hours)
1. Create `evaluator.py` with LongHorizonEvaluator skeleton
2. Create `tasks.py` with 6 constraint_tracking tasks
3. Create `scoring.py` with constraint violation detection
4. Register in registry.py
5. Add to __init__.py exports
6. Write tests

### Phase 2: state_accumulation + error_propagation (3-4 hours)
1. Design 6 state_accumulation scenarios with checkpoint state vectors
2. Design 6 error_propagation scenarios with affected/unaffected step lists
3. Implement programmatic scoring for both
4. Tests

### Phase 3: resource_management + adaptive_replanning (3-4 hours)
1. Design 6 resource_management scenarios with constraint matrices
2. Design 6 adaptive_replanning scenarios with structured rubrics
3. Implement LLM-judge rubrics for adaptive_replanning
4. Tests

### Phase 4: Integration + Evaluation Run (2-3 hours)
1. Run against Claude Sonnet, Opus, GPT-4o
2. Collect baseline metrics
3. Update BioEval README with component 10
4. Update HuggingFace dataset

### Total: ~12-15 hours across 2-3 sessions

---

## Task Count Impact

Current BioEval: 301 tasks across 9 components
After longhorizon: **331 tasks across 10 components** (+30)
Updated CV claim: "490+ tasks" → with SpaceOmicsBench 138 + bioreview-bench + GeneLab 25 + CAMELOT 27 = still 490+ (BioEval internal count goes to 331)

---

## Grounding in Real Experience

Each task type maps to actual research experience:

| Task Type | Real Experience Source |
|---|---|
| constraint_tracking | SOMA protocol standardization across 100+ institutions |
| state_accumulation | Multi-mission spaceflight data integration (I4, PD, Fram2, etc.) |
| error_propagation | scGPT GO/NO-GO assessment (reference gene instability in microgravity) |
| resource_management | CAMbank biospecimen allocation (8 protocols, limited aliquots) |
| adaptive_replanning | scGPT pivot from ML to biology paper (Nature Comms, in prep) |

---

## Key Design Decisions

1. **30 tasks, not more**: Quality over quantity. Each task is a complex
   multi-stage scenario requiring careful curation. BioEval's other
   components range from 14-30 tasks.

2. **Programmatic scoring where possible**: Reduces LLM-judge dependency.
   constraint_tracking, state_accumulation, and resource_management are
   fully programmatic. Only adaptive_replanning needs LLM-judge.

3. **Biologically grounded scenarios**: Every scenario maps to a real
   experimental workflow. No synthetic/artificial constraint puzzles.

4. **Stage-by-stage presentation**: Unlike protoreason (all steps at once),
   longhorizon feeds information stage by stage, testing whether the model
   maintains coherent state across sequential inputs.

5. **Compatible with BioEval CLI**: `bioeval run longhorizon` should work
   with existing infrastructure. Uses same EvalTask/EvalResult dataclasses.
