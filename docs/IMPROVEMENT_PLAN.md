# BioEval Improvement Plan

> Version: 2.0
> Last Updated: 2026-02-24
> Status: **Revised after Publication-Quality Review**
> Related: [PRD.md](PRD.md) | [EXPERT_PANEL_REVIEW.md](EXPERT_PANEL_REVIEW.md) | [LITERATURE_SURVEY.md](LITERATURE_SURVEY.md) | [BIOLOGICAL_AMBIGUITY_DESIGN.md](BIOLOGICAL_AMBIGUITY_DESIGN.md) | [PUBLICATION_QUALITY_REVIEW.md](PUBLICATION_QUALITY_REVIEW.md)

---

## 1. Honest Current State Assessment

### What Actually Works Well
| Component | Status | Evidence |
|-----------|--------|----------|
| Async execution + caching | Production-ready | SQLite cache, token bucket rate limiter, semaphore concurrency |
| Prompt enhancement system | Proven | +20.8% adversarial improvement (87.5% enhanced vs 66.7% baseline) |
| Adversarial evaluation | Solid | 44 tasks, real scoring logic, type-specific validation |
| Calibration metrics | Real | ECE, MCE, Brier score, proper statistical bucketing |
| Model abstraction layer | Working | Claude, OpenAI, HuggingFace w/ LoRA + 4-bit quantization |
| DesignCheck task design | High quality | 10 scientifically accurate flawed experiments |

### What's Weak / Placeholder
| Component | Issue | Impact |
|-----------|-------|--------|
| ProtoReason scoring | `kendall_tau: null`, keyword matching only | Ordering tasks produce no real score |
| CausalBio scoring | Keyword matching, no ground truth validation | Can't distinguish good from mediocre answers |
| DesignCheck scoring | Flaw keyword presence check only | Misses explanation quality entirely |
| MultiTurn scoring | Behavior coverage threshold (50%) | Too coarse, 7 dialogues too few |
| Task count claim | "170+" is ~97 unique tasks | Credibility issue |
| Ground truth data | All hardcoded, no DB integration | Not data-driven |
| Test suite | Exists but coverage unknown | Can't verify correctness |
| Extended data modules | Referenced but missing in some components | Import errors possible |

### Actual Task Count (Verified)
```
protoreason:  14 tasks (3 protocols × ordering/missing/safety + 5 calc + 3 troubleshoot)
causalbio:    13 tasks (5 knockout + 3 pathway + 2 drug + 3 epistasis)
designcheck:  10 tasks (10 flawed experiments)
adversarial:  44 tasks (5+5+3+4+2+3+2 across 7 types)
multiturn:     7 dialogues
calibration:  10 tasks
────────────────────────────────
TOTAL:        ~98 unique tasks
```

### Real Evaluation Results (Jan 8-9, 2026, Claude Sonnet 4)
- **Total tasks evaluated**: 36-37 (not all components ran together)
- **Adversarial enhanced**: 87.5% pass rate
- **Adversarial baseline**: 66.7% pass rate
- **Key win**: edge_case 25% → 100%, plausible_nonsense 67% → 100%
- **Key loss**: misleading_context 33% → 0% (regression)

---

## 2. Improvement Strategy

### Philosophy
> Don't inflate. Don't pad. Make ~140 tasks that produce **trustworthy, reproducible, meaningful** scores. Quality over quantity.

### Priority Matrix (Post Expert Panel + Publication Quality Review)

> **Key principle**: "Make it run" → "Make it score" → "Make it credible" → "Make it impressive"

| Phase | Area | Effort | Impact | Driver |
|-------|------|--------|--------|--------|
| **Phase 0** | Make it run — import fixes, 98 tasks executable | Low | **Blocking** | Dr. B |
| **Phase 1** | Make it score — null scores → real metrics | Medium | Critical | Dr. D, Dr. B |
| **Phase 2** | Make it credible — 3-model comparison, stats, ground truth | High | High | Dr. A, Dr. C, Dr. D |
| **Phase 2b** | BioAmbiguity — 45 context-dependency tasks (parallel w/ Phase 2) | High | High | Literature gap |
| **Phase 3** | Make it impressive — demo, README, Key Findings, publication prep | Medium | High | Dr. E |

**Scope guardrail**: Maximum 150 validated tasks, 7 components. No further expansion.

---

## 3. Phase 0: Make It Run (~1 week)

### Objective
Every existing task executes without errors and produces output (even if scoring is placeholder).

### Tasks
1. Fix all import errors (extended_data, taxonomy modules)
2. Verify all 98 existing tasks execute end-to-end
3. Run existing test suite and record baseline results
4. Document API cost per full run
5. Create `bioeval run --all` CLI entry point that exits cleanly

### Deliverable
`bioeval run --all` exits with code 0, baseline results recorded for all 98 tasks.

### Exit Criteria
- [ ] Zero import errors
- [ ] 98/98 tasks produce output (null scores acceptable at this stage)
- [ ] Test suite results documented
- [ ] API cost per run documented

---

## 4. Phase 1: Make It Score (~2 weeks)

### Objective
Replace all placeholder/keyword scoring with real metrics. Zero null scores.

### 4.1 ProtoReason Scoring Fix
**Current**: `kendall_tau: null`, `requires_manual_parsing: true`

**Fix** — Hybrid scoring approach:
1. **Structured extraction**: Parse LLM response into structured format (step numbers, values)
2. **Metric computation**: Kendall's tau for ordering, numerical distance for calculations (±5% tolerance)
3. **LLM-as-Judge fallback**: For free-text responses that resist parsing (troubleshooting, safety tasks)

For missing steps: compare identified steps against ground truth step list (set intersection score).
For troubleshooting: score against ranked cause list.

### 4.2 CausalBio Scoring Fix
**Current**: Keyword matching (`"effect" in response`)

**Fix**:
- **Directional accuracy**: Does the model predict the correct direction? (lethal/viable/impaired)
- **Mechanism quality**: LLM-as-Judge with rubric for mechanistic explanation
- **Ground truth linkage**: Compare predictions against DepMap CRISPR scores where available (binary: essential vs non-essential)

### 4.3 DesignCheck Scoring Fix
**Current**: Flaw keyword presence check only

**Fix**:
- **Flaw detection rate** (recall): How many of the annotated flaws were identified?
- **False positive rate** (precision): Did the model hallucinate non-existent flaws?
- **Severity accuracy**: Did the model correctly assess severity (critical vs minor)?
- **Fix quality**: LLM-as-Judge on proposed fixes

### 4.4 MultiTurn Scoring Fix
**Current**: 50% behavior coverage threshold

**Fix**:
- **Per-turn evaluation**: Score each turn independently
- **Context retention**: Test if model references earlier turns correctly
- **Progression quality**: Does reasoning improve across turns?

### Development Process
- **Preserve existing file structure** — modify scorer logic within existing evaluator files (Dr. B recommendation)
- Fix one component at a time, test after each fix
- Run full suite after all fixes to verify no regressions

### Deliverable
98 tasks × real numeric scores, zero null scores.

### Exit Criteria
- [ ] Zero null scores across all tasks
- [ ] Each scoring function has unit tests with known inputs/outputs
- [ ] Full suite regression test passes
- [ ] API cost per run updated

---

## 5. Phase 2: Make It Credible (~2-3 weeks)

### Objective
Produce the evidence needed for a credible publication: multi-model comparison, statistical rigor, experimental ground truth, and judge validation.

### 5.1 Three-Model Comparison
- **Models**: Claude Sonnet 4, GPT-4o, open-source 7B (via API if no GPU)
- **Tasks**: All existing components, same task set
- **Statistics**: Per-component appropriate test (McNemar for binary, Wilcoxon for ordinal/continuous), bootstrap 95% CI
- **Deliverable**: Comparison table with per-component scores and statistical significance

### 5.2 MedQA Gap Analysis
- Run same model on MedQA (subset or full) to establish baseline
- Compare: MedQA score (MCQ) → GPQA-Bio score (hard MCQ) → BioEval score (open-ended)
- **Format confound**: Acknowledge in limitations; GPQA-Bio serves as intermediate comparison
- **Deliverable**: "Figure 1" — MedQA 90%+ vs BioEval X% performance gradient

### 5.3 DepMap Integration
- Download DepMap CRISPR gene effect scores (release 24Q4, version-pinned)
- Every knockout task specifies cell line (e.g., "In A549 cells, TP53 KO → ?")
- Binary ground truth: essential (score < -0.5), non-essential (score > -0.3)
- Ambiguous zone (-0.5 to -0.3): excluded from binary scoring, potential BioAmbiguity tasks
- **Deliverable**: CausalBio tasks with verifiable DepMap ground truth

### 5.4 Judge Validation Study
- **Sample**: 50 tasks stratified across all components (~7 per component)
- **Annotators**: Minimum 2 independent annotators (PhD-level biology)
- **Training**: 10 calibration tasks scored together, rubric discussion
- **Metrics**: Cohen's κ (inter-annotator), ICC (ordinal), LLM-Judge vs Human-Consensus
- **Cross-judge**: Claude-as-judge vs GPT-4o-as-judge agreement
- **Threshold**: κ ≥ 0.5 for judge acceptance per component
- **Deliverable**: Judge validation report with per-component κ values

### 5.5 Statistical Significance Framework
- Implement per-component appropriate tests (see PRD R10)
- Bootstrap 95% CI for all comparisons (1000 iterations)
- Effect size reporting (odds ratio for binary, Cohen's d for continuous)
- **Deliverable**: `bioeval compare` outputs statistical report automatically

### 5.6 Adversarial Tier Classification
- Classify existing 44 tasks into: Basic (~20), Intermediate (~15), Expert (~10)
- Report failure rates per tier per model
- **Deliverable**: Tier-stratified adversarial results

### 5.7 Calibration Task Balance
- Reorganize calibration tasks: HIGH confidence (5), MEDIUM confidence (10), LOW/IDK (5)
- Add Flex-ECE metric (per JAMIA Open study recommendation)
- Implement self-consistency confidence extraction (5 samples, agreement rate)
- **Deliverable**: Balanced calibration with Flex-ECE + verbal confidence comparison

### Deliverable
"3-5 Key Findings" with statistical backing, ready for publication.

### Exit Criteria
- [ ] 3 models evaluated on all components
- [ ] MedQA baseline established
- [ ] DepMap ground truth integrated
- [ ] Judge validation κ ≥ 0.5 for all judge-scored components
- [ ] All comparisons have p-values and CIs
- [ ] Adversarial tasks classified by tier

---

## 6. Phase 2b: BioAmbiguity Component (~2-3 weeks, parallel with Phase 2)

### Objective
Build the novel BioAmbiguity component: 45 context-dependent biological reasoning tasks across 6 axes.

### 6.1 Task Creation
- **ContextSwitch** (10 tasks): Context-dependent gene function
- **NullSense** (8 tasks): Negative/null result interpretation
- **ConflictResolve** (8 tasks): Contradictory evidence synthesis
- **TissueContext** (8 tasks): Cell line/tissue specificity
- **TemporalBiology** (6 tasks): Temporal dynamics
- **DoseLogic** (5 tasks): Dose-response reasoning

### 6.2 Ground Truth Strategy (Revised)
Each task has a multi-dimensional rubric instead of a single score:
1. **Context Recognition** (0/1): Does the response acknowledge context-dependency?
2. **Variable Identification** (0-N checklist): How many relevant context variables are named?
3. **Mechanism Quality** (LLM-Judge 1-5): Quality of mechanistic explanation
4. **Epistemic Calibration** (0/1): Does the response appropriately hedge?

Ground truth = expert-annotated rubric with:
- Required context variables (checklist, must-identify)
- Acceptable mechanism explanations (set of valid answers)
- Unacceptable oversimplifications (explicit exclusion list)

### 6.3 Validation
- Each task: PhD-level biologist creates, second expert validates
- Inter-annotator agreement: κ ≥ 0.7 required for inclusion
- Human validation subset: minimum 20 tasks with expert scores (to validate LLM-Judge on ambiguity tasks)
- If LLM-Judge κ < 0.5 on BioAmbiguity: fall back to structured rubric (checklist) scoring only

### 6.4 Cross-Cutting Scoring Dimensions
- **Epistemic Humility**: Use of hedging language, uncertainty acknowledgment
- **Contextual Specificity**: Mentions of cell type, organism, disease stage, dose range
- **Reasoning Transparency**: Mechanistic explanation of WHY context matters

### Deliverable
45 validated ambiguity tasks with multi-dimensional rubrics, first context-dependency benchmark in biology.

### Exit Criteria
- [ ] 45 tasks created with provenance metadata
- [ ] ≥ 35 tasks pass IAA threshold (κ ≥ 0.7)
- [ ] 20-task human validation subset scored
- [ ] LLM-Judge validation on BioAmbiguity reported
- [ ] All tasks have TaskProvenance metadata

---

## 7. Phase 3: Make It Impressive (~2 weeks)

### Objective
Prepare the project for portfolio presentation and publication submission.

### 7.1 Demo Mode
- `bioeval demo` command using pre-cached results
- HTML dashboard with all components, charts, Key Findings
- No API key required — portfolio reviewer can see results in 5 minutes

### 7.2 README Overhaul
- One-line summary + 3 key differentiators
- Quick results table (already available: 87.5% vs 66.7%, etc.)
- Architecture diagram (Mermaid)
- `pip install bioeval && bioeval demo` one-liner
- Key Findings section (3-5 bullet points)
- Ecosystem context ("Part of BioAI-Ecosystem")
- Limitations section (honest)

### 7.3 Publication Preparation
- **Paper outline** following structure in PUBLICATION_QUALITY_REVIEW.md §3.5
- **Datasheet for Datasets** (Gebru et al. 2021 template)
- **Ethics & Broader Impact statement**
- **Reproducibility checklist** (NeurIPS format)
- **REPRODUCE.md** in repository
- **Supplementary materials**: Full task list, judge validation details, statistical details

### 7.4 Distribution
- HuggingFace dataset publication (following LAB-Bench model)
- Private test set (20%) for contamination detection
- Public test set (80%) for community use
- Git tag + SHA256 manifest for version freeze

### 7.5 Additional Enhancements (if time permits)
- Expand epistasis tasks (3 → 10+, synthetic lethality data)
- Ecosystem integration documentation
- Cross-benchmark correlation analysis

### Deliverable
Portfolio-ready project with 5-minute demo and publication-ready manuscript draft.

### Exit Criteria
- [ ] `bioeval demo` works without API key
- [ ] README reflects actual state with Key Findings
- [ ] Paper draft complete
- [ ] Datasheet for Datasets complete
- [ ] Ethics statement complete
- [ ] Reproducibility checklist filled
- [ ] HuggingFace dataset uploaded (public portion)

---

## 8. Ground Truth Data Sources

### 8.1 DepMap Integration (CausalBio + TissueContext)
- **Source**: DepMap CRISPR gene effect scores (public, CC BY 4.0)
- **Release**: 24Q4 (version-pinned, SHA256 verified)
- **Data**: ~18,000 genes × ~1,000 cell lines
- **Usage**: Knockout prediction tasks specify cell line; binary scoring (essential/non-essential)
- **Ambiguous zone**: Scores between -0.5 and -0.3 excluded from binary scoring; used for BioAmbiguity TissueContext tasks

### 8.2 Protocols.io Integration (ProtoReason)
- **Source**: protocols.io API (CC BY 4.0)
- **Quality filter**: citation count > 10 OR journal-linked only
- **Step constraint**: 8-20 steps per protocol
- **Annotation**: Critical ordering constraints manually annotated per protocol
- **Goal**: 10+ high-quality protocols (currently 3)

### 8.3 Published Experimental Results (DesignCheck)
- **Source**: Retracted papers (PubMed retraction database), reproducibility studies
- **Usage**: Flawed designs from retractions, correct designs from high-impact reproducibility work
- **Goal**: 15+ designs (currently 10)

---

## 9. BioAI-Ecosystem Integration Points

### Current Integration
- BioEval contributes 40% of Ecosystem Score
- Shared model interface (`bioai_models/`)
- Failure analysis feeds into BioRLHF training
- Iterative improvement pipeline runs BioEval as one of 3 benchmarks

### Improvements Needed
1. **Standardize result format** across BioEval, SpaceOmicsBench, CAMELOT
2. **Unified failure taxonomy** (BioEval's taxonomy → ecosystem-wide)
3. **Cross-benchmark correlation** analysis
4. **Single CLI** that runs all 3 benchmarks and produces ecosystem score

---

## 10. Timeline

### Phase 0: "Make it Run" (~1 week)
- Fix import errors, missing modules
- Verify all 98 tasks execute
- Run existing test suite, record baseline
- Document API cost model
- **Deliverable**: `bioeval run --all` exits cleanly, baseline recorded

### Phase 1: "Make it Score" (~2 weeks)
- Replace null/keyword scoring with real metrics (ProtoReason, CausalBio, DesignCheck, MultiTurn)
- Preserve existing file structure; modify scorer logic in-place (minimal refactoring)
- Score normalization: per-component independent reporting (no forced composite)
- **Deliverable**: 98 tasks × real numeric scores

### Phase 2: "Make it Credible" (~2-3 weeks)
- 3-model comparison (Claude Sonnet 4, GPT-4o, open-source 7B)
- MedQA/PubMedQA → GPQA-Bio → BioEval gap analysis (Figure 1)
- DepMap integration (cell line context, binary ground truth)
- Judge validation study (50 tasks × 2 annotators)
- Statistical significance framework (per-component appropriate tests)
- Adversarial tier classification (Basic/Intermediate/Expert)
- Calibration balance (HIGH 5 / MEDIUM 10 / LOW 5) + Flex-ECE
- **Deliverable**: "3-5 Key Findings" with statistical backing

### Phase 2b: "BioAmbiguity Component" (~2-3 weeks, parallel with Phase 2)
- 45 context-dependency tasks across 6 axes
- Multi-dimensional rubric scoring with ground truth checklist
- Expert validation (IAA κ ≥ 0.7)
- Human validation subset (20 tasks) for LLM-Judge calibration
- **Deliverable**: 45 validated ambiguity tasks, first context-dependency benchmark in biology

### Phase 3: "Make it Impressive" (~2 weeks)
- Demo mode (pre-cached results → HTML report, no API key)
- README overhaul (accurate counts, Key Findings, architecture diagram)
- Publication preparation (paper draft, datasheet, ethics statement, reproducibility checklist)
- HuggingFace dataset distribution + private test set (20%)
- **Deliverable**: Portfolio-ready project with 5-min demo and publication draft

### Realistic Timeline Estimate
| Scenario | Total Duration |
|----------|---------------|
| Full-time, solo developer | 7-9 weeks |
| Part-time, solo developer | 11-15 weeks |
| Full-time, with 1 collaborator | 5-7 weeks |

### Target Total: ~140 validated tasks (98 existing improved + ~45 BioAmbiguity - quality filtering)

### Publication Target
- **Primary venue**: NeurIPS Datasets & Benchmarks Track
- **Secondary venue**: Nature Methods (focus BioAmbiguity as biological contribution)
- **Core contribution**: First context-dependent biological reasoning benchmark with experimental ground truth
- **Figure 1**: MedQA 90%+ → GPQA-Bio → BioEval causal → BioAmbiguity 40-60% performance gradient

---

## 11. Guardrails Summary

All guardrails are defined in detail in PRD §5. Key guardrails:

| Category | Key Rule |
|----------|----------|
| Scope | Max 150 tasks, 7 components, no further expansion |
| Quality | IAA κ ≥ 0.7 for task inclusion, Judge κ ≥ 0.5 for acceptance |
| Anti-hallucination | Gene/drug name validation, DepMap hash verification, provenance required |
| Development | Preserve file structure, one component at a time, test before refactor |
| Publication | No inflated claims, negative results reported, pre-registered hypotheses |
| Budget | API cost cap at $120, tracked per call |

---

## Appendix: Key File Locations

```
bioeval/
├── config.py                    # Global settings — needs version bump
├── models/base.py               # Model wrappers — solid, keep as-is
├── prompts/prompt_templates.py  # Enhancement system — strong, keep
├── protoreason/evaluator.py     # Scoring needs fix (in-place update)
├── causalbio/evaluator.py       # Scoring needs fix (in-place update)
├── designcheck/evaluator.py     # Scoring needs fix (tasks are good)
├── adversarial/tasks.py         # Best component — enhance, don't rewrite
├── scoring/llm_judge.py         # Needs validation + cost optimization
├── scoring/calibration.py       # Solid — add Flex-ECE
├── execution/async_runner.py    # Production-ready — keep as-is
├── multiturn/dialogues.py       # Needs more scenarios + better scoring
├── bioambiguity/                # NEW: Context-dependency component
└── taxonomy/                    # Verify existence, complete if needed
```
