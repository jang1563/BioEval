# BioEval Publication-Quality Review

> Date: 2026-02-24
> Reviewer scope: All 5 planning documents
> Target venues: NeurIPS Datasets & Benchmarks Track, Nature Methods
> Verdict: **Strong concept with 17 critical issues to resolve before submission**

---

## Executive Summary

BioEval has a genuinely novel positioning: evaluating whether LLMs can "do" biology, not just "know" it. The BioAmbiguity component addresses a confirmed gap in the literature. However, the current planning documents contain **internal inconsistencies, methodological gaps, and missing elements** that would result in desk rejection at target venues.

This review identifies issues in 6 categories:
1. Cross-document inconsistencies (4 issues)
2. Scientific methodology gaps (6 issues)
3. Publication-specific missing elements (5 issues)
4. Feasibility concerns (3 issues)
5. Guardrails and safety considerations (new section)
6. Language standardization (all documents need English conversion)

---

## 1. Cross-Document Inconsistencies

### ISSUE 1.1: Task Count Targets Are Self-Contradictory

**Problem**: Three different task count targets appear across documents.

| Source | Stated Target |
|--------|--------------|
| IMPROVEMENT_PLAN §2 | "target 100-120 validated tasks" |
| IMPROVEMENT_PLAN §8 | "~139 validated tasks" |
| IMPROVEMENT_PLAN §10 | "~143 validated tasks (98 + 45)" |
| PRD R1-R6 individual targets | 80+50+25+60+15+20 = **250+** tasks |

The PRD component-level requirements (R1: 80+, R2: 50+, etc.) sum to 250+, which **directly contradicts** the panel's consensus of 100-120 validated tasks and the plan's own rejection of the 250-task target.

**Fix**: Reconcile all counts. Recommended approach:
```
R1 ProtoReason:  ~25 tasks (not 80+)
R2 CausalBio:    ~25 tasks (not 50+)
R3 DesignCheck:   ~15 tasks (not 25+)
R4 Adversarial:  ~44 tasks (keep, + tier classification)
R5 MultiTurn:    ~10 dialogues (not 15+)
R6 Calibration:  ~20 tasks (keep)
R7 BioAmbiguity: ~45 tasks (new, add as R7)
─────────────────────────────────
TOTAL:           ~184 → realistically ~140 validated
```

### ISSUE 1.2: Phase Numbering Mismatch Between Sections

**Problem**: IMPROVEMENT_PLAN uses two different numbering schemes:

| §3-8 Labels | §10 Timeline Labels | Actual Content |
|-------------|--------------------| --------------|
| P0 | Phase 1 | Fix Scoring |
| P1 | Phase 2 | Ground Truth |
| P2 | Phase 0 | End-to-End Pipeline (import fixes) |
| P3 | -- | Test Coverage |
| P4 | -- | Documentation |
| P5 | -- | Task Expansion |

The §3-8 section numbers (P0-P5) do NOT map to the Phase 0-3 timeline in §10. After the expert panel review, the timeline was correctly reordered (Run → Score → Credible → Impressive), but §3-8 still reflect the OLD priority order.

**Fix**: Renumber §3-8 to match the revised Phase 0-3 timeline, or restructure to eliminate dual numbering.

### ISSUE 1.3: BioAmbiguity Not Integrated into PRD Requirements

**Problem**: BioAmbiguity is described as a major new component (contribution #6 in PRD §1), but:
- No R-number assigned (R1-R6 cover only the original 6 components)
- Not listed in PRD §3.1 "Evaluation Components (6)"
- Architecture diagram in PRD §6 does not include a `bioambiguity/` directory
- Scoring scale (0-3) conflicts with PRD R7's LLM-as-Judge scale (1-5)

**Fix**: Add R7 for BioAmbiguity in PRD §3.1, update component count to 7, add to architecture diagram, and reconcile scoring scales.

### ISSUE 1.4: Scoring Scale Inconsistencies

**Problem**: Five different scoring scales are in use with no normalization strategy decided:

| Component | Scale | Direction |
|-----------|-------|-----------|
| Adversarial | Binary 0/1 | Higher = better |
| Calibration (ECE) | 0-1 continuous | **Lower** = better |
| CausalBio (LLM-Judge) | 1-5 ordinal | Higher = better |
| ProtoReason (Kendall's tau) | -1 to +1 | Higher = better |
| BioAmbiguity | 0-3 ordinal | Higher = better |
| DesignCheck (detection rate) | 0-1 continuous | Higher = better |

The expert panel recommended "Option A: Component-level independent reporting" but this is not formally adopted in the PRD.

**Fix**: Formally adopt per-component independent reporting in PRD. For any composite score, define the normalization strategy explicitly.

---

## 2. Scientific Methodology Gaps

### ISSUE 2.1: BioAmbiguity Ground Truth Paradox

**Problem**: BioAmbiguity tests whether LLMs handle genuinely ambiguous questions. But a benchmark requires ground truth. If a question is genuinely ambiguous, what IS the correct answer?

The design says "PhD-level biologist creates, second expert validates" and notes that "expert disagreement is itself a signal of genuine ambiguity." This is philosophically interesting but operationally problematic:

- If experts disagree, which expert's scoring rubric is "correct"?
- A 0-3 rubric where 3 = "explains mechanism of context-dependency" presupposes a specific correct mechanism
- For ConflictResolve tasks (synthesizing contradictory evidence), the "correct synthesis" may itself be contested

**Fix**: Adopt a **rubric-based, multi-dimensional scoring** approach instead of a single 0-3 score:
```
For each BioAmbiguity task:
  1. Context Recognition Score (0/1): Does the response acknowledge context-dependency?
  2. Variable Identification Score (0-N): How many relevant context variables are named?
  3. Mechanism Quality Score (LLM-Judge 1-5): Quality of mechanistic explanation
  4. Epistemic Calibration (0/1): Does the response appropriately hedge?

Ground truth = expert-annotated rubric with:
  - Required context variables (checklist)
  - Acceptable mechanism explanations (set of valid answers)
  - Unacceptable oversimplifications (explicit exclusion list)
```

This makes scoring more objective while preserving the ambiguity-testing purpose.

### ISSUE 2.2: Circular Dependency in LLM-as-Judge for BioAmbiguity

**Problem**: BioAmbiguity evaluates whether LLMs can handle context-dependent biological reasoning. If LLMs fail at this (the hypothesis), then using an LLM as judge for BioAmbiguity scoring is circular — the judge may have the same blind spots as the evaluated model.

**Fix**:
1. BioAmbiguity MUST have a human validation subset (minimum 20 tasks with expert scores)
2. Report LLM-Judge vs Human-Expert agreement specifically for BioAmbiguity tasks
3. If agreement is low (κ < 0.5), BioAmbiguity scoring must rely on structured rubric checking (variable checklist) rather than LLM-Judge free-form evaluation
4. Consider using a stronger model as judge (e.g., Claude Opus 4) when evaluating weaker models

### ISSUE 2.3: Statistical Test Selection Mismatch

**Problem**: The plan recommends McNemar's test and Cohen's d for all comparisons, but these are only appropriate for specific score types:

| Score Type | Appropriate Test | Currently Proposed |
|-----------|-----------------|-------------------|
| Binary (Adversarial pass/fail) | McNemar's test | McNemar ✓ |
| Ordinal (Judge 1-5, Ambiguity 0-3) | Wilcoxon signed-rank | Not mentioned |
| Continuous (Kendall's tau, ECE) | Paired t-test or Wilcoxon | Not mentioned |
| Effect size (binary) | Odds ratio | Cohen's d ✗ |
| Effect size (continuous) | Cohen's d | ✓ but only for continuous |

**Fix**: Specify statistical tests per component type:
```
Adversarial (binary):     McNemar's test, odds ratio, 95% CI
CausalBio (ordinal 1-5):  Wilcoxon signed-rank, rank-biserial correlation
ProtoReason (continuous):  Paired t-test (if normal) or Wilcoxon, Cohen's d
Calibration (continuous):  Paired t-test on ECE differences
BioAmbiguity (ordinal):   Wilcoxon signed-rank
All comparisons:           Bootstrap 95% CI (1000 iterations)
```

### ISSUE 2.4: MedQA Gap Analysis Is Apples-to-Oranges

**Problem**: PRD R16 proposes comparing MedQA scores (MCQ, percentage correct) with BioEval scores (open-ended, multi-dimensional). This comparison is central to the paper's argument ("Figure 1") but methodologically problematic:

- MedQA: 4-option MCQ, chance = 25%, max = 100%
- BioEval CausalBio: 1-5 rubric score, chance ≈ 2-3/5, max = 5/5
- BioEval Adversarial: Binary, chance depends on task type

Showing "90% on MedQA vs 62% on BioEval" conflates format difficulty with reasoning difficulty.

**Fix**:
1. **Primary comparison**: Use same MCQ format for a subset of BioEval tasks (e.g., calibration tasks with known answers) to enable apples-to-apples format comparison
2. **Secondary comparison**: Show the open-ended format gap separately, acknowledging format as a confound
3. **Best approach**: Include GPQA-Bio subset (also MCQ, but harder) as an intermediate comparison point: MedQA (easy MCQ) → GPQA-Bio (hard MCQ) → BioEval (open-ended reasoning)
4. Explicitly discuss format confound in the paper's limitations section

### ISSUE 2.5: Judge Validation Study Design Is Incomplete

**Problem**: PRD R17 calls for "50 tasks with expert manual scoring" and Cohen's κ ≥ 0.6, but:

- Who are the expert annotators? If the developer is the sole annotator, κ cannot be computed (need ≥2)
- How will expert disagreements be resolved?
- No mention of annotator training/calibration procedure
- No stratification plan (should include tasks from each component, not just easy ones)
- No plan for measuring intra-rater reliability (same person scoring twice)

**Fix**: Define a concrete annotation protocol:
```
Annotator recruitment:
  - Minimum 2 independent annotators (ideally 3) per task
  - Qualifications: PhD or advanced graduate student in biology/bioinformatics
  - Annotator training: Score 10 calibration tasks together, discuss rubric

Annotation design:
  - 50 tasks stratified: ~8 per component (7 components × ~7 tasks)
  - Each task scored by 2 annotators independently
  - Disagreements resolved by third annotator or discussion

Metrics to report:
  - Cohen's κ (inter-annotator agreement)
  - ICC (intra-class correlation for ordinal scores)
  - LLM-Judge vs Human-Consensus correlation
  - Per-component breakdown of judge accuracy
```

### ISSUE 2.6: Flex-ECE Not Integrated Despite Literature Recommendation

**Problem**: The Literature Survey (§4.2) specifically recommends adopting Flex-ECE over standard ECE, citing evidence that self-consistency (27.3% error) vastly outperforms verbal confidence (42.0% error). However, this finding is not reflected in the PRD or IMPROVEMENT_PLAN:

- PRD R6 still says "ECE, MCE, Brier score" without mentioning Flex-ECE
- No plan to implement self-consistency-based confidence estimation
- Calibration component design doesn't specify HOW confidence is extracted from LLM responses

**Fix**:
1. Add Flex-ECE to calibration metrics in PRD R6
2. Specify confidence extraction method: structured prompt requiring numerical confidence (e.g., "Rate your confidence 0-100%") AND self-consistency method (5 samples, agreement rate)
3. Report both methods and compare, as the literature suggests self-consistency is more reliable

---

## 3. Publication-Specific Missing Elements

### ISSUE 3.1: No Datasheet for Datasets

**Problem**: NeurIPS Datasets & Benchmarks track strongly encourages (and increasingly requires) a Datasheet for Datasets (Gebru et al., 2021). Nature Methods also expects thorough data documentation. The current plan has no mention of creating one.

**Required elements**:
- Motivation (why was this benchmark created?)
- Composition (what does the dataset consist of?)
- Collection process (how was each task created/sourced?)
- Preprocessing/cleaning (quality filters applied?)
- Uses (intended use cases, out-of-scope uses)
- Distribution (license, access method)
- Maintenance (who maintains, update schedule, deprecation policy)

**Fix**: Add a deliverable in Phase 3: "Create Datasheet for Datasets following Gebru et al. (2021) template." This is a straightforward document (~3-5 pages) but reviewers specifically check for it.

### ISSUE 3.2: No Ethics Statement or Biosecurity Considerations

**Problem**: Biology benchmarks increasingly face scrutiny about dual-use potential. BioEval's adversarial component tests whether models can be tricked about biology — a reviewer could ask: "Could this benchmark be used to identify which models are most susceptible to generating dangerous biological information?"

Additionally:
- No IRB/ethics consideration mentioned (even if not applicable, should be stated)
- No discussion of potential misuse of the benchmark itself
- Adversarial "false premise" tasks could inadvertently train models to be better at recognizing misinformation tricks (dual-use)

**Fix**: Add an Ethics & Broader Impact section to the paper plan:
```
1. Biosecurity: BioEval does not test or evaluate dangerous capabilities
   (bioweapons synthesis, pathogen enhancement). All tasks involve standard
   academic biology (cancer biology, molecular biology, genetics).
2. Dual-use: Adversarial tasks test robustness to misinformation, not
   generation of misinformation. Publishing the adversarial methodology
   helps defend against, not enable, misuse.
3. IRB: Not applicable — no human subjects data collected.
4. Data licensing: All external data (DepMap, protocols.io) used under
   their respective open licenses (CC BY 4.0).
```

### ISSUE 3.3: No Reproducibility Checklist

**Problem**: NeurIPS requires a reproducibility checklist. The plan mentions reproducibility (version pinning, caching) but doesn't formally address:

- Exact software versions and environment specification
- Random seed specification for all stochastic elements
- Compute requirements (what GPU, how much time, how much cost)
- Code availability and license
- Data availability and access instructions

**Fix**: Create a reproducibility checklist as part of Phase 3 deliverables. Include a `REPRODUCE.md` in the repository.

### ISSUE 3.4: No Inter-Annotator Agreement for Task Creation

**Problem**: Publication-quality benchmarks report IAA for the task creation process itself. GPQA reports annotator agreement metrics. BioEval's plan has no IAA for task validation.

Questions a reviewer will ask:
- "How do you know your 'correct' answers are actually correct?"
- "What is the agreement rate between the task creator and the validator?"
- "For BioAmbiguity tasks where ambiguity is expected, how do you distinguish intentional ambiguity from task design errors?"

**Fix**: For each component, report:
```
- Task creation IAA: % of tasks where 2 independent reviewers agree on the correct answer/rubric
- For BioAmbiguity: % of tasks where reviewers agree on the SET of acceptable context variables
- Minimum IAA threshold: κ ≥ 0.7 for inclusion in the benchmark
- Tasks with low IAA are flagged for revision, not silently included
```

### ISSUE 3.5: No Paper Outline or Contribution Statement

**Problem**: The planning documents describe what to build but not what to write. A publication-quality plan should include a paper outline showing how the work maps to manuscript sections.

**Fix**: Add a paper outline:
```
Title: "BioEval: Evaluating Whether LLMs Can Do Biology, Not Just Know It"

Abstract: [BioEval tests practical biology skills... BioAmbiguity is first context-dependency benchmark...]

1. Introduction
   - Motivation: MedQA 90%+ but can models actually reason about biology?
   - Figure 1: MedQA vs GPQA-Bio vs BioEval performance gap
   - Contributions: (1) multi-dimensional benchmark, (2) experimental ground truth,
     (3) BioAmbiguity component, (4) 3-model comparison findings

2. Related Work
   - Table 1: Competitive landscape matrix (from LITERATURE_SURVEY.md §6)
   - Position against LAB-Bench, GPQA, BioProBench, CondMedQA

3. BioEval Framework
   - 3.1 Task Design (7 components, ~140 tasks)
   - 3.2 Scoring System (hybrid: structured + LLM-Judge)
   - 3.3 Data Integrity System
   - 3.4 BioAmbiguity: Context-Dependent Reasoning (6 axes)

4. Experimental Setup
   - Models: Claude Sonnet 4, GPT-4o, Mistral-7B
   - Evaluation protocol, statistical tests
   - Judge validation study results

5. Results
   - 5.1 Overall performance comparison (Table 2)
   - 5.2 Component-level analysis
   - 5.3 BioAmbiguity findings (the "key gap" result)
   - 5.4 Calibration analysis
   - 5.5 Adversarial robustness by tier

6. Analysis & Discussion
   - Key Finding 1: MedQA vs BioEval gap
   - Key Finding 2: Context-dependency is the hardest dimension
   - Key Finding 3: Calibration paradoxes
   - Limitations

7. Conclusion & Future Work

Supplementary:
   - Datasheet for Datasets
   - Full task list with provenance
   - Judge validation details
   - Statistical test details
```

---

## 4. Feasibility Concerns

### ISSUE 4.1: Expert Annotation Sourcing

**Problem**: The plan requires expert annotations at multiple points:
- Judge validation study: 50 tasks × 2-3 annotators
- BioAmbiguity task creation: 45 tasks created by PhD biologists
- BioAmbiguity validation: second expert verification

For a single developer, sourcing qualified annotators is non-trivial. No budget, recruitment plan, or alternative is described.

**Realistic options**:
1. Collaborate with biology PhD students (free but slow)
2. Use Prolific/Surge with domain-expert filters ($15-30/hour)
3. Leverage existing lab connections
4. Self-annotate + one additional expert (minimum viable)

**Fix**: Add an annotation sourcing plan with budget estimate. If budget is zero, design the minimum viable annotation protocol (developer + 1 expert collaborator).

### ISSUE 4.2: GPU Availability for Local Model Evaluation

**Problem**: The 3-model comparison requires running Mistral-7B (or similar open-source model). This requires:
- Minimum: 16GB VRAM GPU (for 4-bit quantization)
- Recommended: 24GB+ VRAM

The plan mentions "LoRA + 4-bit quantization" support in the model layer, but doesn't confirm GPU availability or provide a fallback plan.

**Fix**:
1. Confirm available hardware (local GPU, cloud GPU budget)
2. If no GPU: use HuggingFace Inference API or together.ai API as fallback for open-source models
3. Alternative: Replace Mistral-7B with a model accessible via API (e.g., Mixtral via together.ai, or Llama via Groq)

### ISSUE 4.3: Timeline Realism for Solo Developer

**Problem**: Total estimated timeline: 9-11 weeks
- Phase 0: 1 week
- Phase 1: 2 weeks
- Phase 2: 2-3 weeks
- Phase 2b: 2-3 weeks (parallel)
- Phase 3: 2 weeks

"Parallel" execution of Phase 2 and 2b assumes either multiple developers or the ability to context-switch effectively. For a solo developer, phases that are labeled "parallel" typically take 1.5x the longer phase, not the same time.

**Realistic estimate**: 11-15 weeks for a solo developer working part-time, or 7-9 weeks full-time.

**Fix**: Provide realistic timeline with two scenarios (full-time vs part-time) and identify the minimum viable publication package (what can be cut without losing the core story).

---

## 5. Project Guardrails

### 5.1 Scope Guardrails

| Guardrail | Rule | Trigger |
|-----------|------|---------|
| **Task count cap** | Maximum 150 validated tasks total | Stop adding tasks when total reaches 150 |
| **No new components** | 7 components maximum (current 6 + BioAmbiguity) | Reject any proposal for 8th component |
| **Scoring completeness gate** | No task enters the benchmark without a working scorer that produces a non-null numeric score | Task review checklist item |
| **Provenance gate** | No task enters the benchmark without completed TaskProvenance metadata | Automated pre-commit check |
| **Phase gate** | Each phase must produce its defined deliverable before the next phase begins | Phase exit criteria review |

### 5.2 Quality Guardrails

| Guardrail | Rule | Enforcement |
|-----------|------|-------------|
| **Ground truth verification** | Every task with experimental ground truth must be verifiable by re-querying the source database | Automated integration test |
| **No fabricated data** | Zero tolerance for made-up experimental values. All values must trace to a DOI or database version | Code review + provenance check |
| **Judge agreement threshold** | LLM-as-Judge scoring is only accepted for components where Human-Judge κ ≥ 0.5 | Judge validation study result |
| **Statistical significance** | No performance claim without p-value < 0.05 and 95% CI | Automated report generation |
| **Minimum effect size** | Don't report differences smaller than Cohen's d = 0.3 as "findings" | Analysis review |

### 5.3 Anti-Hallucination Guardrails (Expanded)

| Guardrail | Rule | Implementation |
|-----------|------|----------------|
| **Gene name validation** | Every gene mentioned in tasks must be a valid HGNC symbol | HGNC API check at task creation |
| **Drug name validation** | Every drug must exist in ChEMBL or DrugBank | ChEMBL API check at task creation |
| **DepMap score verification** | Every CRISPR score used as ground truth must match the pinned DepMap release | SHA256 hash of data file + spot-check queries |
| **Protocol verification** | Every protocol step sequence must match the source protocols.io entry | URL verification + step count check |
| **No training data in test set** | Check for verbatim overlap between task text and known LLM training datasets | N-gram overlap check against Common Crawl subset |
| **Version freeze before publication** | Lock all task content, scoring logic, and ground truth data at submission time | Git tag + SHA256 manifest |

### 5.4 Development Process Guardrails

| Guardrail | Rule | Why |
|-----------|------|-----|
| **Test before refactor** | Run existing test suite before ANY code change | Prevent unknown regressions |
| **Minimal refactoring** | Modify scorer logic within existing file structure; do not reorganize directories until Phase 3 | Dr. B panel recommendation |
| **One component at a time** | Complete scoring fix for one component before starting the next | Prevent scattered half-fixes |
| **Git commit per task** | Each discrete change (fix one scorer, add one task) gets its own commit | Traceability |
| **API cost tracking** | Log every API call with cost; halt if cumulative cost exceeds $120 | Budget protection |
| **Weekly checkpoint** | Weekly review of progress against timeline; adjust scope if behind schedule | Timeline discipline |

### 5.5 Publication Guardrails

| Guardrail | Rule | Why |
|-----------|------|-----|
| **No inflated claims** | Report exact task counts, exact model names, exact dates | Credibility |
| **Honest limitations** | Every document must include a "Limitations" section | Reviewer trust |
| **Reproducibility commitment** | All results reproducible with `bioeval run --all --seed 42` | NeurIPS requirement |
| **Pre-registration of hypotheses** | State expected findings BEFORE running experiments (already done in BioAmbiguity design) | Scientific integrity |
| **Negative results reported** | If BioAmbiguity does NOT show the expected gap, report that finding honestly | Scientific integrity |
| **No cherry-picking** | Report ALL component scores, not just the ones that look good | Reviewer trust |

### 5.6 Code Quality Guardrails

| Guardrail | Rule | Implementation |
|-----------|------|----------------|
| **Type hints required** | All new functions must have type annotations | Linting (mypy) |
| **Docstrings for public API** | All evaluator classes and scoring functions must have docstrings | Linting (pydocstyle) |
| **No hardcoded API keys** | All credentials via environment variables | Pre-commit hook grep check |
| **Test coverage for scorers** | New scoring logic must have ≥ 80% test coverage | pytest-cov threshold |
| **No silent failures** | Scoring functions must raise exceptions, never return None silently | Type checker + tests |

---

## 6. Language Standardization

### Current State: All 5 documents contain mixed Korean/English

Per user's explicit instruction: "Files and explanations must all be written in English."

**Files requiring full English conversion**:
1. `IMPROVEMENT_PLAN.md` — Timeline section (§10) is mostly Korean
2. `PRD.md` — Sections 1, 2, 4, 7, 8, 9 contain Korean
3. `BIOLOGICAL_AMBIGUITY_DESIGN.md` — Sections 1-6 contain Korean
4. `EXPERT_PANEL_REVIEW.md` — Extensive Korean throughout
5. `LITERATURE_SURVEY.md` — Minimal Korean (cleanest document)

**Priority**: Convert PRD and IMPROVEMENT_PLAN first (these are the primary reference documents), then BioAmbiguity design, then Expert Panel Review.

---

## 7. Venue-Specific Recommendations

### If targeting NeurIPS Datasets & Benchmarks:
- **Deadline**: Typically June (check 2026 schedule)
- **Page limit**: 9 pages + unlimited references + supplementary
- **Required**: Reproducibility checklist, datasheet encouraged
- **Reviewer focus**: Novelty of benchmark design, community utility, rigorous evaluation
- **Strengths to emphasize**: BioAmbiguity novelty, experimental ground truth, multi-dimensional evaluation
- **Weakness to address**: Small task count (140 vs LAB-Bench 2400) — argue quality over quantity

### If targeting Nature Methods:
- **Typical timeline**: 3-6 month review cycle
- **Format**: Article (up to 3000 words main text) or Brief Communication
- **Reviewer focus**: Biological validity, practical utility for biology researchers, comparison with existing tools
- **Strengths to emphasize**: DepMap integration, practical biology tasks, BioAmbiguity for real research questions
- **Weakness to address**: Computational evaluation methodology may be less familiar to biology reviewers

### Recommendation: Target NeurIPS D&B as primary, Nature Methods as secondary/follow-up with a different framing (focus on BioAmbiguity alone as a biology contribution).

---

## 8. Priority Action Items (Ordered)

### Immediate (before any coding):
1. **Reconcile task counts** across all documents (Issue 1.1)
2. **Fix phase numbering** in IMPROVEMENT_PLAN (Issue 1.2)
3. **Add BioAmbiguity as R7** in PRD (Issue 1.3)
4. **Convert all documents to English** (Issue 6)

### Before Phase 1 (scoring fixes):
5. **Define BioAmbiguity ground truth strategy** (Issue 2.1)
6. **Specify statistical tests per component** (Issue 2.3)
7. **Define annotation sourcing plan** (Issue 4.1)
8. **Confirm GPU availability** for 3-model comparison (Issue 4.2)

### Before Phase 2 (credibility):
9. **Design MedQA comparison methodology** with format confound discussion (Issue 2.4)
10. **Create Judge validation protocol** (Issue 2.5)
11. **Add Flex-ECE to calibration plan** (Issue 2.6)
12. **Implement all guardrails** from Section 5

### Before submission:
13. **Create Datasheet for Datasets** (Issue 3.1)
14. **Write Ethics & Broader Impact statement** (Issue 3.2)
15. **Complete reproducibility checklist** (Issue 3.3)
16. **Report inter-annotator agreement** (Issue 3.4)
17. **Write paper following outline** (Issue 3.5)

---

## 9. Summary Verdict

| Dimension | Current State | Publication Ready? | Fix Effort |
|-----------|--------------|-------------------|------------|
| Novelty | Strong — BioAmbiguity confirmed gap | Yes | None needed |
| Positioning | Strong — "know vs do" framing | Yes | None needed |
| Methodology | Moderate — gaps in stats, judge validation | No | Medium |
| Consistency | Weak — contradictions across documents | No | Low |
| Completeness | Weak — missing datasheet, ethics, IAA | No | Medium |
| Feasibility | Moderate — timeline and annotation sourcing unclear | Needs revision | Low |
| Language | Not ready — Korean/English mixed | No | Medium |
| Guardrails | Not defined until this review | Now defined | Implementation needed |

**Bottom line**: The core idea and competitive positioning are publication-worthy. The execution plan needs the 17 fixes above to reach submission quality. Estimated effort for fixes: ~1-2 weeks of planning work before coding begins.
