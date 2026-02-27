# BioEval — Product Requirements Document (PRD)

> NOTE (Canonical Status): This PRD includes historical phase-planning targets.  
> For current runtime counts/version/contracts, see [STATUS.md](STATUS.md) and [README.md](../README.md).

> Version: 3.0
> Author: JangKeun Kim
> Last Updated: 2026-02-24
> Status: **Revised after Phase 0 completion + Post-Phase 0 Review**
> Related: [IMPROVEMENT_PLAN.md](IMPROVEMENT_PLAN.md) | [EXPERT_PANEL_REVIEW.md](EXPERT_PANEL_REVIEW.md) | [LITERATURE_SURVEY.md](LITERATURE_SURVEY.md) | [BIOLOGICAL_AMBIGUITY_DESIGN.md](BIOLOGICAL_AMBIGUITY_DESIGN.md) | [PUBLICATION_QUALITY_REVIEW.md](PUBLICATION_QUALITY_REVIEW.md) | [POST_PHASE0_REVIEW.md](POST_PHASE0_REVIEW.md)

---

## 1. Product Vision

**BioEval** is a benchmark framework that evaluates whether LLMs can **"do" biology**, not just **"know" it**.

While existing benchmarks (MedQA, PubMedQA, BioASQ) measure factual recall through multiple-choice questions, BioEval measures **causal reasoning, protocol execution, experimental design critique, adversarial robustness, context-dependent reasoning, and confidence calibration** through open-ended evaluation.

### Unique Contributions (Confirmed via Literature Survey of 30+ benchmarks)
1. **Experimental ground truth** — DepMap CRISPR scores and CMap drug responses as verifiable answers (no other benchmark does this)
2. **Open-ended evaluation** — Free-response format with hybrid scoring, resistant to MCQ saturation (Justen 2025)
3. **Biology-specific adversarial robustness** — False premises, hallucination traps, misleading context in biology (unique)
4. **Confidence calibration** — Only 1.2% of biomedical AI evaluations measure calibration (JAMA 2025)
5. **Experimental design critique** — Identifying flaws in experimental designs (completely novel)
6. **Biological ambiguity & context-dependency (BioAmbiguity)** — First benchmark for context-dependent biological reasoning across 6 axes; no existing benchmark tests this (confirmed gap)
7. **Integrated multi-dimensional evaluation** — All dimensions in a single framework with data integrity guarantees

### Publication-Level Positioning
```
Dimensions tested by BioEval that NO existing benchmark covers:
  ✓ Experimental ground truth (DepMap/CMap)
  ✓ Causal reasoning in biology specifically (CausalProbe is domain-agnostic)
  ✓ Biological context-dependency (6 axes, BioAmbiguity)
  ✓ Negative/null result interpretation
  ✓ Dose-response reasoning (hormesis, biphasic)
  ✓ Experimental design critique
  ✓ Integrated multi-dimensional evaluation

Key competitors/reference benchmarks:
  LAB-Bench (2,400 MCQ, practical biology)  →  BioEval tests deeper reasoning
  BioProBench (556K protocol instances)     →  BioEval is broader (causal + adversarial + ambiguity)
  GPQA-Bio (saturating per Justen 2025)     →  BioEval has saturation-resistant design
```

---

## 2. Target Users

| User | Use Case |
|------|----------|
| AI researchers | Quantitative evaluation of LLM biological reasoning capabilities |
| Biotech companies | Domain capability verification before LLM deployment |
| Fine-tuning teams | Pre/post-training performance comparison, iterative improvement |
| Portfolio reviewers | Benchmark design competence, scientific rigor assessment |

---

## 3. Core Requirements

### 3.1 Evaluation Components

#### First Submission: 6 Components (Phase 1-3)

#### R1: ProtoReason — Protocol Reasoning
| Requirement | Specification |
|-------------|---------------|
| Task types | Step ordering, missing step detection, calculations, troubleshooting, safety |
| Data source | protocols.io API (CC BY 4.0) + curated protocols (citation>10 or journal-linked, 8-20 steps) |
| Ground truth | Published protocol step sequences with critical ordering constraints annotated |
| Scoring | Kendall's tau (ordering), numerical tolerance ±5% (calc), LLM-as-Judge (troubleshoot) |
| Verified count | **17 base**, 70 extended, 49 advanced (136 total available) |
| Validation | Each protocol verified against original publication |

#### R2: CausalBio — Causal Biological Reasoning
| Requirement | Specification |
|-------------|---------------|
| Task types | Knockout prediction, pathway reasoning, drug response, epistasis |
| Data source | DepMap CRISPR scores (CC BY 4.0, release 24Q4, version-pinned), Connectivity Map (CC BY 4.0) |
| Ground truth | Experimental CRISPR fitness scores (binary: essential <-0.5, non-essential >-0.3, ambiguous zone excluded) |
| Cell line context | Every knockout task MUST specify the cell line (e.g., "In A549 cells, what happens when TP53 is knocked out?") |
| Scoring | Directional accuracy + LLM-as-Judge for mechanism quality (Wilcoxon signed-rank for comparisons) |
| Verified count | **13 base**, 44 extended, 19 advanced (76 total available) |
| Validation | Ground truth values verified against pinned DepMap release with SHA256 hash |

#### R3: DesignCheck — Experimental Design Critique
| Requirement | Specification |
|-------------|---------------|
| Task types | Flaw detection across 5 categories (controls, statistics, confounders, technical, interpretation) |
| Data source | Expert-curated flawed designs, retraction case studies |
| Ground truth | Annotated flaws with category, severity, explanation |
| Scoring | Detection rate (recall), false positive rate (precision), severity accuracy, LLM-as-Judge for fix quality |
| Verified count | **10 base**, 10 advanced (20 total available) |
| Validation | Each design reviewed by domain expert |

#### R4: Adversarial — Adversarial Robustness
| Requirement | Specification |
|-------------|---------------|
| Task types | 7 types: false premise, hallucination trap, misleading context, edge case, contradictory, plausible nonsense, overly specific |
| Difficulty tiers | Basic (~8), Intermediate (~10), Expert (~6) — to be classified in Phase 2 |
| Scoring | Binary pass/fail with type-specific validation logic (McNemar test for model comparisons) |
| Verified count | **24 base** |
| Proven results | Enhanced prompts: 87.5% vs baseline 66.7% (+20.8%) — measured with keyword scorer, needs re-validation |

#### R5: MultiTurn — Scientific Dialogue
| Requirement | Specification |
|-------------|---------------|
| Task types | Hypothesis refinement, experimental design iteration, troubleshooting, data interpretation, peer review |
| Scoring | Per-turn evaluation + context retention + progression quality |
| Verified count | **6 base** |

#### R6: Calibration — Confidence Calibration
| Requirement | Specification |
|-------------|---------------|
| Metrics | ECE, MCE, Brier score, **Flex-ECE** (per JAMIA Open recommendation), overconfidence rate, reliability diagram |
| Confidence extraction | (1) Structured prompt requiring numerical 0-100% confidence, AND (2) self-consistency method (5 samples, optional — 5x cost) |
| Task balance | Current: 10 tasks. Target: HIGH 5, MEDIUM 10, LOW/IDK 5 |
| Scoring | Confidence extraction → bucket accuracy comparison |
| Verified count | **10 base** |
| Power limitation | With 10-20 tasks and 5 bins, ~2-4 tasks per bin — report this limitation explicitly |

#### Deferred: R7: BioAmbiguity — Biological Context-Dependency
| Requirement | Specification |
|-------------|---------------|
| Status | **Deferred to post-first-submission** (separate paper or revision) |
| Rationale | Solo developer cannot build + validate 45 tasks while completing Phases 2-3 for NeurIPS deadline |
| Phase 1 work | Create skeleton directory + 5 pilot tasks as proof-of-concept |
| Full design | See [BIOLOGICAL_AMBIGUITY_DESIGN.md](BIOLOGICAL_AMBIGUITY_DESIGN.md) |
| Evaluation axes | ContextSwitch (10), NullSense (8), ConflictResolve (8), TissueContext (8), TemporalBiology (6), DoseLogic (5) |
| Target count | ~45 tasks (when fully built) |

### Task Count Summary (Phase 0 Verified)
```
FIRST SUBMISSION (6 components):
                    Base    Extended   Advanced   Total Available
R1 ProtoReason:      17        70         49          136
R2 CausalBio:        13        44         19           76
R3 DesignCheck:      10         —         10           20
R4 Adversarial:      24         —          —           24
R5 MultiTurn:         6         —          —            6
R6 Calibration:      10         —          —           10
─────────────────────────────────────────────────────────────
TOTAL:               80       114         78          272

Phase 1 target:     80 base tasks with real scoring
Phase 2 target:    194 tasks (base + extended) for statistical power
```

---

### 3.2 Scoring System

#### R8: Hybrid Scoring Pipeline
```
LLM Response
  │
  ├─→ [Response Parser] → Structured extraction (NEW: Phase 1 prerequisite)
  │     ├─→ Step ordering → list[int]
  │     ├─→ Numerical value → float
  │     ├─→ Direction prediction → up/down/unchanged
  │     ├─→ Flaw list → list[dict]
  │     └─→ Confidence → float (0-100%)
  │
  ├─→ [Metric Computation] → Kendall's tau, directional accuracy, precision/recall, Flex-ECE
  │
  └─→ [LLM-as-Judge] → Rubric-based evaluation (for free-text tasks only)
        └─→ 1-5 scale per dimension (accuracy, mechanism, reasoning, completeness, uncertainty)
```

**Response Parser** (`bioeval/scoring/response_parser.py`): NEW module — Phase 1 prerequisite.
- **Primary method**: Structured prompting (force LLM to output parseable format)
- **Fallback**: LLM-based extraction using Haiku (~$0.001/call) for ambiguous responses
- **Target**: ≥85% extraction success rate per component

**LLM-as-Judge** (`bioeval/scoring/llm_judge.py`): EXISTS (516 lines) but currently disconnected from evaluators. Must be wired in during Phase 1.

#### R9: Scoring Requirements
| Requirement | Specification |
|-------------|---------------|
| No null scores | Every task MUST produce a numeric score |
| Reproducibility | Same input → same score (cache-based, temperature=0) |
| Cost control | LLM-as-Judge only for free-text tasks, not for parseable answers |
| Rubric transparency | Every score explainable by referencing rubric criteria |
| Judge validation | Two-stage: (1) 10-task mini-validation in Phase 1, (2) 30-50 task formal validation in Phase 2 |
| Judge acceptance | LLM-as-Judge accepted only for components where Human-Judge κ ≥ 0.5 |
| Score reporting | Per-component independent reporting (no single composite score) |
| Parser reliability | Response parser success rate ≥ 85% per component (documented) |

#### R10: Statistical Comparison Framework
| Score Type | Appropriate Test | Effect Size | Components |
|-----------|-----------------|-------------|------------|
| Binary (pass/fail) | McNemar's test | Odds ratio | Adversarial |
| Ordinal (1-5) | Wilcoxon signed-rank | Rank-biserial correlation | CausalBio, MultiTurn |
| Continuous (-1 to 1, 0-1) | Paired t-test or Wilcoxon | Cohen's d | ProtoReason (tau), Calibration (ECE), DesignCheck (F1) |
| All comparisons | Bootstrap 95% CI (1000 iterations) | — | All |

**Power limitation**: With base task counts (6-24 per component), only large effects (d ≥ 0.7) are detectable. Use extended data (194 tasks) for Phase 2 comparisons to improve power.

---

### 3.3 Infrastructure

#### R11: Execution Engine
| Requirement | Specification |
|-------------|---------------|
| Async execution | Configurable concurrency (default 5, max 20) |
| Rate limiting | Token bucket algorithm, configurable RPM/TPM |
| Caching | SQLite, SHA256 keyed, prevents redundant API calls |
| Resumability | JSON progress files, resumable from any point |
| CLI interface | `bioeval run`, `bioeval compare`, `bioeval report`, `bioeval demo` |

#### R12: Model Support
| Backend | Requirements | Status |
|---------|--------------|--------|
| Anthropic | Claude Sonnet 4, Claude Opus 4, Claude Haiku | Working |
| OpenAI | GPT-4o, GPT-4-turbo | Working |
| HuggingFace | Any causal LM, LoRA adapter support, 4-bit quantization | Implemented, untested |
| **API-based open-source** | **together.ai, Groq for Llama-3-8B / Mistral-7B** | **Phase 2 (primary strategy for 3-model comparison)** |
| Custom | BaseModel interface for any backend | Available |

**Decision (Post-Phase 0)**: Use API-based open-source models for 3-model comparison, NOT local inference. Apple Silicon Macs cannot run `bitsandbytes` 4-bit quantization (CUDA-only). CPU inference (~60s/response) is too slow. together.ai/Groq provides fast, cheap access (~$0.20/M tokens).

#### R13: Reporting
| Feature | Specification |
|---------|---------------|
| JSON results | Standardized schema, one file per run |
| HTML dashboard | Component breakdown, task-level drill-down, charts |
| Comparison mode | A/B testing with per-component statistical significance |
| CI integration | Exit code 0/1, machine-readable summary |
| Transparency report | Auto-generated data provenance and integrity report per run |

---

## 4. Data Integrity & Anti-Hallucination System

> **Design Principle**: BioEval itself measures hallucination, so hallucination in the benchmark's own data would undermine all credibility. Data integrity is a core requirement, not an add-on.

### 4.1 Data Provenance Tracking

All task data must include source metadata:

```python
@dataclass
class TaskProvenance:
    source_type: Literal["experimental_db", "publication", "expert_curated", "synthetic"]
    source_id: str          # DOI, DepMap release ID, protocols.io URL
    source_version: str     # Database version or access date
    retrieval_date: str     # When data was fetched
    validation_status: Literal["verified", "peer_reviewed", "unverified"]
    validator: str          # Who/what validated (expert name, automated check)
    license: str            # Data license (CC BY 4.0, etc.)
```

**Rules**:
- `source_type: "synthetic"` tasks are separately labeled and limited to ≤20% of total
- `validation_status: "unverified"` tasks are excluded from final benchmark scores
- All `source_id` values must be verifiable URLs/DOIs

### 4.2 Ground Truth Verification Pipeline

```
[Raw Data Source]
    │
    ├─→ [Automated Fetch] ─→ DepMap API, protocols.io API
    │       └─→ Version-pinned, reproducible
    │
    ├─→ [Cross-Reference Check]
    │       └─→ 2+ independent sources for critical facts
    │       └─→ DepMap score ↔ published literature concordance
    │
    ├─→ [Boundary Validation]
    │       └─→ Numerical values within biologically plausible ranges
    │       └─→ Gene names validated against HGNC database
    │       └─→ Drug names validated against ChEMBL/DrugBank
    │
    └─→ [Expert Review Flag]
            └─→ Tasks flagged for expert review if:
                - Ground truth contradicts common textbook knowledge
                - Numerical values are extreme outliers
                - Task involves controversial/evolving science
```

### 4.3 Anti-Simulation Safeguards

#### Rule 1: No Fabricated Experimental Values
```python
class GroundTruthValidator:
    """All ground truth values must be traceable to their source."""

    def validate_crispr_score(self, gene: str, cell_line: str, score: float) -> bool:
        """Verify against actual DepMap query."""
        depmap_score = self.depmap_client.get_gene_effect(gene, cell_line)
        if depmap_score is None:
            raise DataIntegrityError(f"Gene {gene} in {cell_line} not found in DepMap")
        if abs(score - depmap_score) > TOLERANCE:
            raise DataIntegrityError(
                f"Claimed score {score} != DepMap score {depmap_score}"
            )
        return True

    def validate_gene_name(self, gene: str) -> bool:
        """Verify valid gene symbol via HGNC."""
        return self.hgnc_client.is_valid_symbol(gene)

    def validate_drug_name(self, drug: str) -> bool:
        """Verify real drug via ChEMBL/DrugBank."""
        return self.chembl_client.exists(drug)
```

#### Rule 2: Synthetic Data Segregation
```python
class TaskFactory:
    def create_task(self, ..., source_type: str):
        if source_type == "synthetic":
            task.metadata["synthetic"] = True
            task.metadata["synthetic_method"] = "template_based"
            # Synthetic tasks reported in a separate section
        elif source_type == "experimental_db":
            assert self.validator.verify_source(task.source_id)
```

#### Rule 3: Version Pinning
```python
DATA_SOURCES = {
    "depmap": {
        "version": "24Q4",
        "url": "https://depmap.org/portal/download/...",
        "sha256": "abc123...",  # File hash verification
    },
    "protocols_io": {
        "protocol_ids": ["p123", "p456", ...],
        "access_date": "2026-02-24",
    }
}
```

### 4.4 Runtime Integrity Checks

```python
class IntegrityChecker:
    """Automated data integrity verification before every run."""

    def pre_run_checks(self):
        checks = [
            self._check_task_count(),        # Expected task count matches
            self._check_ground_truth_hash(), # Ground truth tamper detection
            self._check_gene_names(),        # Gene name validity
            self._check_numerical_ranges(),  # Numerical plausibility
            self._check_provenance(),        # Source metadata completeness
            self._check_no_duplicate_ids(),  # No duplicate task IDs
        ]
        failures = [c for c in checks if not c.passed]
        if failures:
            raise IntegrityError(f"{len(failures)} checks failed: {failures}")
```

### 4.5 Transparency Report (Auto-generated per run)

```
═══ BioEval Integrity Report ═══
Run ID: bioeval_20260224_143000
Model: claude-sonnet-4-20250514

DATA PROVENANCE:
  experimental_db: 65 tasks (46.4%)  ← DepMap, CMap
  publication:     18 tasks (12.9%)  ← protocols.io, papers
  expert_curated:  52 tasks (37.1%)  ← manually created, expert verified
  synthetic:        5 tasks  (3.6%)  ← template-generated variants

INTEGRITY CHECKS: 6/6 PASSED ✓
  ✓ task_count: 140 (expected 140)
  ✓ ground_truth_hash: a1b2c3... matches manifest
  ✓ gene_names: 45/45 valid HGNC symbols
  ✓ numerical_ranges: all within plausible bounds
  ✓ provenance: 140/140 tasks have source metadata
  ✓ no_duplicates: 140 unique task IDs

SCORING COVERAGE:
  metric_scored:     95 tasks (67.9%)  ← automated metric
  llm_judge_scored:  45 tasks (32.1%)  ← rubric-based
  null_scores:        0 tasks  (0.0%)  ← ZERO null scores ✓
```

---

## 5. Project Guardrails

### 5.1 Scope Guardrails

| Guardrail | Rule | Trigger |
|-----------|------|---------|
| Task count cap | Maximum 150 validated tasks total | Stop adding tasks at 150 |
| Component cap | 7 components maximum (R1-R7) | Reject proposals for 8th component |
| Scoring completeness gate | No task enters benchmark without a working non-null scorer | Task review checklist |
| Provenance gate | No task enters benchmark without completed TaskProvenance metadata | Automated pre-commit check |
| Phase gate | Each phase must produce its defined deliverable before next phase begins | Phase exit criteria review |

### 5.2 Quality Guardrails

| Guardrail | Rule | Enforcement |
|-----------|------|-------------|
| Ground truth verification | Every experimental-data task must be verifiable by re-querying source DB | Automated integration test |
| No fabricated data | Zero tolerance for made-up experimental values | Code review + provenance check |
| Judge agreement threshold | LLM-as-Judge accepted only for components where Human-Judge κ ≥ 0.5 | Judge validation study |
| Statistical significance | No performance claim without p < 0.05 and 95% CI | Automated report generation |
| Minimum effect size | Don't report differences smaller than Cohen's d = 0.3 as "findings" | Analysis review |
| Inter-annotator agreement | Tasks included only if IAA κ ≥ 0.7 between creators and validators | Annotation protocol |

### 5.3 Anti-Hallucination Guardrails

| Guardrail | Rule | Implementation |
|-----------|------|----------------|
| Gene name validation | Every gene in tasks must be valid HGNC symbol | HGNC API check at task creation |
| Drug name validation | Every drug must exist in ChEMBL or DrugBank | ChEMBL API check |
| DepMap score verification | CRISPR scores must match pinned DepMap release | SHA256 hash + spot-check queries |
| Protocol verification | Step sequences must match source protocols.io entry | URL verification + step count |
| Training data overlap check | Check for verbatim overlap with known LLM training data | N-gram overlap check |
| Version freeze at submission | Lock all tasks, scoring logic, and ground truth | Git tag + SHA256 manifest |

### 5.4 Development Process Guardrails

| Guardrail | Rule | Why |
|-----------|------|-----|
| Test before refactor | Run existing test suite before ANY code change | Prevent unknown regressions |
| Minimal refactoring | Modify scorer logic within existing files; no directory reorganization until Phase 3 | Panel recommendation (Dr. B) |
| One component at a time | Complete scoring fix for one component before starting next | Prevent scattered half-fixes |
| Atomic commits | Each discrete change gets its own git commit | Traceability |
| API cost tracking | Log every API call with cost; halt if cumulative cost exceeds $120 | Budget protection |
| Weekly checkpoint | Weekly progress review against timeline; adjust scope if behind | Timeline discipline |

### 5.5 Publication Guardrails

| Guardrail | Rule | Why |
|-----------|------|-----|
| No inflated claims | Report exact task counts, model names, dates | Credibility |
| Honest limitations | Every document includes a Limitations section | Reviewer trust |
| Reproducibility | All results reproducible with `bioeval run --all --seed 42` | NeurIPS requirement |
| Pre-registered hypotheses | State expected findings before experiments | Scientific integrity |
| Negative results reported | If expected gap doesn't appear, report honestly | Scientific integrity |
| No cherry-picking | Report ALL component scores | Reviewer trust |

### 5.6 Code Quality Guardrails

| Guardrail | Rule | Implementation |
|-----------|------|----------------|
| Type hints | All new functions must have type annotations | mypy |
| Docstrings for public API | All evaluator classes and scoring functions | pydocstyle |
| No hardcoded API keys | All credentials via environment variables | Pre-commit hook |
| Test coverage for scorers | New scoring logic ≥ 80% coverage | pytest-cov |
| No silent failures | Scoring functions raise exceptions, never return None | Type checker + tests |

---

## 6. Non-Functional Requirements

### R14: Performance
| Metric | Target |
|--------|--------|
| Full evaluation (Claude, API) | < 30 minutes (async, 10 concurrent) |
| Full evaluation (local 7B) | < 2 hours |
| Cache hit rate | > 90% on re-runs |
| Memory usage | < 4GB (excluding local models) |

### R15: Reproducibility
| Requirement | Implementation |
|-------------|---------------|
| Deterministic scoring | temperature=0, cached responses |
| Version-pinned data | SHA256 hash verification |
| Environment capture | Python version, package versions recorded in results |
| Seed control | Fixed random seeds for any stochastic elements |
| Reproducibility checklist | REPRODUCE.md in repository (NeurIPS requirement) |

### R16: Extensibility
| Requirement | Implementation |
|-------------|---------------|
| New components | `BaseEvaluator` interface + register in config |
| New models | `BaseModel` interface |
| New scoring rubrics | Add to `llm_judge.py` rubric dict |
| New task types | Add to component evaluator + update config |

---

## 7. Architecture

```
bioeval/
├── cli.py                    # NEW: Unified CLI entry point
├── config.py                 # Settings and constants
├── integrity/                # NEW: Data integrity system
│   ├── provenance.py         #   Data source tracking
│   ├── validator.py          #   Ground truth verification
│   └── checker.py            #   Runtime integrity checks
├── models/
│   └── base.py               # Model wrappers (Claude, OpenAI, HF, API-based)
├── protoreason/
│   └── evaluator.py          # Protocol reasoning (scorer updated in-place)
├── causalbio/
│   └── evaluator.py          # Causal biology (scorer updated in-place)
├── designcheck/
│   └── evaluator.py          # Design critique (scorer updated in-place)
├── adversarial/
│   └── tasks.py              # Adversarial robustness (already strong)
├── multiturn/
│   └── dialogues.py          # Multi-turn dialogue
├── calibration/
│   └── evaluator.py          # Confidence calibration
├── bioambiguity/             # NEW: Biological context-dependency
│   ├── evaluator.py          #   6-axis evaluation
│   ├── tasks.py              #   Task definitions with provenance
│   └── scorer.py             #   Multi-dimensional rubric scoring
├── scoring/
│   ├── llm_judge.py          # Rubric-based LLM evaluation
│   ├── calibration.py        # Confidence calibration metrics (+ Flex-ECE)
│   ├── metrics.py            # NEW: Unified metric computation
│   └── statistics.py         # NEW: Statistical comparison framework
├── prompts/
│   └── prompt_templates.py   # Enhancement system (keep as-is)
├── execution/
│   └── async_runner.py       # Async engine (keep as-is)
├── reporting/                # NEW: Result reporting
│   ├── html_report.py        #   Dashboard generation
│   ├── comparison.py         #   A/B comparison with statistics
│   ├── transparency.py       #   Integrity report generation
│   └── templates/            #   Jinja2 HTML templates
└── data/                     # NEW: External data management
    ├── depmap/               #   Cached DepMap downloads (version-pinned)
    ├── protocols/            #   Cached protocol data
    └── manifest.json         #   Data version + hash manifest
```

**Note**: Existing component file structure (protoreason/, causalbio/, etc.) is preserved per Dr. B's recommendation. Scorer logic is updated in-place within existing evaluator files. New files created only for genuinely new functionality (bioambiguity/, integrity/, reporting/, statistics).

---

## 8. BioAI-Ecosystem Integration

### 8.1 Role Within Ecosystem
```
BioAI-Ecosystem
  ├── SpaceOmicsBench (30%) — Multi-modal spaceflight data integration
  ├── CAMELOT (30%) — Deep scientific reasoning on transcriptomics
  └── BioEval (40%) — Practical biology skills + robustness + context-dependency
        ├── Causal reasoning (DepMap ground truth)
        ├── Protocol execution (protocols.io ground truth)
        ├── Adversarial defense
        ├── Confidence calibration
        └── Biological ambiguity (BioAmbiguity)
```

### 8.2 Integration Requirements
| Requirement | Specification |
|-------------|---------------|
| Shared model interface | `bioai_models.get_model()` works for all 3 benchmarks |
| Unified result schema | Common JSON format for cross-benchmark analysis |
| Failure taxonomy | BioEval taxonomy extended to ecosystem-wide |
| Single pipeline | `bioai evaluate --all` runs all 3 benchmarks |
| Ecosystem score | Weighted aggregation with per-component breakdown |

### 8.3 Cross-Benchmark Analysis
```python
class BioEvalEcosystemAdapter:
    def get_ecosystem_metrics(self) -> dict:
        return {
            "bioeval_score": self.overall_score,
            "component_scores": {
                "causal_reasoning": self.causalbio_score,
                "protocol_execution": self.protoreason_score,
                "design_critique": self.designcheck_score,
                "adversarial_robustness": self.adversarial_score,
                "calibration": self.calibration_score,
                "context_dependency": self.bioambiguity_score,
            },
            "failure_patterns": self.get_failure_taxonomy(),
            "training_recommendations": self.generate_training_data(),
        }
```

---

## 9. Minimum Viable Publication (MVP)

### MUST HAVE (required for any submission)
| Deliverable | Metric | Phase |
|-------------|--------|-------|
| 6 components with real scoring | Zero null scores, ≥85% parser success | Phase 1 |
| 2-model comparison minimum | Claude Sonnet 4 + GPT-4o results table | Phase 2 |
| Basic statistical tests with CIs | Bootstrap 95% CI for all comparisons | Phase 2 |
| Honest task counts and limitations | Verified counts in all docs | Phase 0 ✓ |
| Reproducibility | seed, caching, version pinning | Phase 1 |

### SHOULD HAVE (strengthens the paper significantly)
| Deliverable | Metric | Phase |
|-------------|--------|-------|
| 3-model comparison | Add open-source via API (Llama-3-8B) | Phase 2 |
| LLM-Judge validation | ≥30 tasks, κ reported | Phase 2 |
| Error analysis | 50 classified wrong responses | Phase 2 |
| Flex-ECE calibration | Reported for all models | Phase 2 |
| Adversarial tier classification | Basic/Intermediate/Expert failure rates | Phase 2 |
| Datasheet + Ethics statement | NeurIPS format | Phase 3 |

### NICE TO HAVE (for the strongest possible paper)
| Deliverable | Metric | Phase |
|-------------|--------|-------|
| BioAmbiguity pilot | 15-20 tasks in appendix | Post-submission |
| Full MedQA gap analysis | Re-run MedQA on same models | Phase 2 |
| 50-task judge validation with 2 external annotators | κ with formal protocol | Phase 2 |
| DepMap live integration | API query at runtime | Phase 2 |
| HuggingFace distribution | Public 80% / private 20% | Phase 3 |
| HTML dashboard demo | `bioeval demo` with charts | Phase 3 |

**Decision point**: At end of Phase 2, evaluate which NICE-TO-HAVEs are achievable before deadline.

---

## 10. Success Criteria (Revised)

### Key Findings to Demonstrate
1. **Cross-model comparison** — Performance differences between Claude, GPT-4o, and open-source on 194 tasks
2. **Component-level reasoning gaps** — "Models score differently across task types: causal reasoning vs design critique vs adversarial"
3. **Error analysis** — "Knowledge errors (X%) vs reasoning errors (Y%) — models KNOW biology but can't REASON about it"
4. **Prompt enhancement effect** — Baseline vs enhanced with statistical significance (re-measured with real scoring)
5. **Adversarial difficulty tiers** — Basic vs Intermediate vs Expert failure rates
6. **Calibration analysis** — Overconfidence patterns, Flex-ECE across models

### API Cost Budget (Revised)
```
Phase 1 development (20 debugging runs × $1.40):     ~$28
Phase 2 three-model comparison (3 × 3 × $3.00):      ~$27
Phase 2 judge scoring (194 tasks × $0.03 × 5 runs):  ~$29
Phase 2 extended data runs:                           ~$15
Self-consistency calibration (optional):              ~$10
Miscellaneous/debugging:                              ~$15
──────────────────────────────────────────────────────────
Total estimated:                                     ~$124
Budget cap:                                          $120 (track from Phase 1 start)
```

---

## 10. Requirements from Panel Review

### R17: 3-Model Comparison (Dr. A, Dr. E)
| Requirement | Specification |
|-------------|---------------|
| Models | Claude Sonnet 4, GPT-4o, open-source 7B (via API or local) |
| Tasks | All 7 components, same task set |
| Output | Comparison table with per-component scores |
| Statistics | Per-component appropriate test (see R10), bootstrap 95% CI |

### R18: MedQA Gap Analysis (Dr. A)
| Requirement | Specification |
|-------------|---------------|
| Purpose | Quantify "knows vs can do" gap |
| Method | Same model on MedQA (MCQ) + BioEval (open-ended) |
| Format confound mitigation | Include GPQA-Bio subset as intermediate comparison; discuss format as limitation |
| Output | Figure 1: MedQA → GPQA-Bio → BioEval performance gradient |

### R19: Judge Validation Study (Dr. D)
| Requirement | Specification |
|-------------|---------------|
| Annotators | Minimum 2 independent annotators per task (PhD or advanced graduate in biology) |
| Sample | 50 tasks stratified across 7 components (~7 per component) |
| Training | 10 calibration tasks scored together, rubric discussed |
| Metrics | Cohen's κ (inter-annotator), ICC (ordinal scores), LLM-Judge vs Human-Consensus |
| Cross-judge | Claude-as-judge vs GPT-4o-as-judge agreement |
| Threshold | κ ≥ 0.5 (moderate agreement) for judge acceptance |

### R20: Demo Mode (Dr. E)
| Requirement | Specification |
|-------------|---------------|
| Command | `bioeval demo` or `bioeval report --demo` |
| Behavior | Uses pre-cached results, no API key required |
| Output | HTML dashboard with all components, charts, findings |
| Purpose | Portfolio reviewer can see results in 5 minutes |

### R21: Datasheet for Datasets (NeurIPS Requirement)
| Requirement | Specification |
|-------------|---------------|
| Template | Gebru et al. (2021) Datasheets for Datasets |
| Contents | Motivation, Composition, Collection, Uses, Distribution, Maintenance |
| Location | `docs/DATASHEET.md` and supplementary materials |

### R22: Ethics & Broader Impact Statement
| Requirement | Specification |
|-------------|---------------|
| Biosecurity | Confirm no dangerous capability testing |
| Dual-use | Adversarial tasks test robustness to misinformation, not generation |
| Data licensing | All external data under open licenses |
| IRB | Not applicable (no human subjects) |

---

## 11. Risks and Mitigations

| Risk | Impact | Mitigation | Source |
|------|--------|------------|--------|
| LLM-as-Judge cost | 2x API cost | Automated scoring for parseable answers; Judge only for free-text | Dr. B |
| LLM-as-Judge reliability | Scoring distrust | Judge validation study: Human vs Judge κ ≥ 0.5 | Dr. D |
| Judge self-bias | Claude judges Claude favorably | Cross-judge eval: Claude judge + GPT-4o judge comparison | Dr. D |
| BioAmbiguity judge circularity | Judge has same blind spots as evaluated model | Human validation subset (20 tasks); structured rubric fallback | Review |
| DepMap cell line ambiguity | Wrong ground truth | All knockout tasks specify cell line; binary scoring; ambiguous zone excluded | Dr. C |
| DepMap data changes | Ground truth drift | Version pinning + SHA256 hash verification | Original |
| Protocols.io quality variance | Low-quality tasks | citation>10 or journal-linked only; 8-20 steps; manual annotation | Dr. C |
| Scoring irreproducibility | Credibility loss | temperature=0, caching, seed control | Original |
| Refactoring regression | Breaking existing code | Preserve file structure; update scorers in-place | Dr. B |
| Scope creep | Never finishes | 150-task cap; 7-component cap; phase gates | Panel |
| "So what?" absence | No portfolio impact | MedQA gap + 3-model comparison + Key Findings | Dr. E |
| MedQA comparison confound | Format ≠ reasoning difference | Include GPQA-Bio intermediate; discuss in limitations | Review |
| Expert annotator sourcing | Can't validate tasks | Plan recruitment early; minimum viable: 2 annotators | Review |
| GPU unavailability | Can't run 3-model comparison | API-based fallback for open-source models | Review |

---

## 12. Limitations (Pre-Identified)

To be included in the paper's Limitations section:

1. **Task count**: 194 tasks (base + extended) is small compared to LAB-Bench (2,400) or BioProBench (556K). We prioritize depth and experimental grounding over scale.
2. **Statistical power**: Per-component task counts (6-24 base, 13-87 with extended) limit detection of small effects. We report effect sizes and CIs, noting power limitations.
3. **LLM-as-Judge**: Despite validation, LLM judges may have systematic biases not captured by κ agreement metrics.
4. **Response parser reliability**: Structured extraction from free-text responses may fail on creative or unexpected response formats. Parser success rates documented per component.
5. **Format confound**: The MedQA vs BioEval gap partially reflects format difficulty (MCQ vs open-ended), not purely reasoning difficulty.
6. **English-only**: All tasks and evaluation in English. Multilingual biology reasoning is not assessed.
7. **Domain scope**: Focused on molecular/cellular biology and cancer biology. Does not cover ecology, evolutionary biology, or computational biology workflows.
8. **Temporal validity**: Biology knowledge evolves. Tasks based on current literature may become outdated. Version-pinned data mitigates but does not eliminate this.
9. **Prompt enhancement claims**: The +20.8% adversarial improvement was measured with keyword-based scoring. Effect may change with real scoring (re-validated in Phase 1).

---

## 13. Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2026-02-24 | 1.0 | Initial PRD creation |
| | | Anti-hallucination/data integrity system design |
| | | Honest task count (~98, not 170+) |
| 2026-02-24 | 1.1 | Expert Panel Review incorporated |
| | | Added R15-R20 (3-model comparison, MedQA gap, Judge validation, Demo mode, Adversarial tiers, Calibration balance) |
| | | Task target: 250 → 100-120 validated |
| 2026-02-24 | 1.2 | Literature Survey + BioAmbiguity Design |
| | | Confirmed 7 unique contributions |
| | | Added BioAmbiguity component (6 axes, 45 tasks) |
| | | Publication target: NeurIPS D&B or Nature Methods |
| 2026-02-24 | 2.0 | **Publication-Quality Review (17 issues addressed)** |
| | | Full English conversion (all Korean text removed) |
| | | Added R7 BioAmbiguity as formal requirement with reconciled task counts |
| | | Added R10 Statistical Comparison Framework (per-component test selection) |
| | | Added R21 Datasheet for Datasets, R22 Ethics Statement |
| | | Added Section 5: Project Guardrails (scope, quality, anti-hallucination, development, publication, code) |
| | | Added Section 12: Pre-identified Limitations |
| | | Fixed task count inconsistency (R1-R6 targets now match 140-150 total, not 250+) |
| | | Added Flex-ECE to calibration metrics (R6) |
| | | Added BioAmbiguity ground truth strategy (multi-dimensional rubric) |
| | | Added judge circularity risk for BioAmbiguity |
| | | Added format confound mitigation for MedQA comparison |
| | | Architecture preserves existing file structure per Dr. B recommendation |
| | | Added API-based fallback for open-source models |
| 2026-02-24 | 3.0 | **Post-Phase 0 Review (21 issues addressed)** |
| | | Phase 0 verified task counts: 80 base, 114 extended, 78 advanced, 272 total |
| | | R1-R6 counts updated to verified actuals (e.g., R4 Adversarial: 44 → 24 base) |
| | | R7 BioAmbiguity deferred to post-first-submission |
| | | Added R8 Response Parser as Phase 1 prerequisite |
| | | R9 updated: two-stage judge validation (mini + full) |
| | | R10 power limitation noted; extended data strategy for Phase 2 |
| | | R12 updated: API-based open-source as primary strategy (Apple Silicon incompatible) |
| | | Added Section 9: Minimum Viable Publication (MVP) definition |
| | | Section 10 success criteria revised (BioAmbiguity removed, error analysis added) |
| | | Section 12 limitations expanded (statistical power, parser reliability, prompt claim caveat) |
| | | API cost budget revised with per-phase breakdown |
