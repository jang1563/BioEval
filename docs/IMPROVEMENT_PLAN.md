# BioEval Improvement Plan

> Version: 3.0
> Last Updated: 2026-02-24
> Status: **Revised after Phase 0 completion + Post-Phase 0 Review**
> Related: [PRD.md](PRD.md) | [EXPERT_PANEL_REVIEW.md](EXPERT_PANEL_REVIEW.md) | [LITERATURE_SURVEY.md](LITERATURE_SURVEY.md) | [BIOLOGICAL_AMBIGUITY_DESIGN.md](BIOLOGICAL_AMBIGUITY_DESIGN.md) | [PUBLICATION_QUALITY_REVIEW.md](PUBLICATION_QUALITY_REVIEW.md) | [POST_PHASE0_REVIEW.md](POST_PHASE0_REVIEW.md) | [PHASE0_BASELINE.md](PHASE0_BASELINE.md)

---

## 1. Current State (Post Phase 0 — Verified)

### What Works Well
| Component | Status | Evidence |
|-----------|--------|----------|
| All imports | Working | 6 evaluators load without errors (conda bioeval env, Python 3.11.14 arm64) |
| Test suite | Passing | 27/27 tests pass in 0.92s |
| Async execution + caching | Production-ready | SQLite cache, token bucket rate limiter, semaphore concurrency |
| Prompt enhancement system | Proven | +20.8% adversarial improvement (87.5% enhanced vs 66.7% baseline) — measured with keyword scorer, needs re-validation |
| Model abstraction layer | Working | Claude, OpenAI, HuggingFace w/ LoRA + 4-bit quantization |
| CLI entry point | Working | `bioeval run/inventory/compare/demo` (v0.2.0) |
| LLM-as-Judge module | Implemented | 516 lines, task-specific rubrics, structured JSON output — but NOT wired into evaluators |

### What's Weak / Placeholder
| Component | Actual Scoring Method | Impact |
|-----------|----------------------|--------|
| ProtoReason ordering | `kendall_tau: None` — completely unimplemented | No score produced |
| ProtoReason calculation | Checks if raw number string appears in response | Doesn't verify correctness |
| ProtoReason troubleshooting | 4-char keyword matching on cause list | No semantic understanding |
| CausalBio knockout | Checks if "essential"/"non-essential" string appears | No directional validation |
| CausalBio pathway | Splits pathway name by "/" and checks word presence | Extremely brittle |
| CausalBio drug response | Checks if gene name appears (ignores up/down direction) | Missing critical dimension |
| DesignCheck | Keyword presence from flaw explanation | No false positive detection, no severity assessment |
| MultiTurn | 50% keyword coverage threshold | No per-turn scoring, no context retention check |
| Adversarial | Regex-based keyword detection | Works but brittle; surface-level |
| Calibration | Pattern-based confidence extraction (density of hedging words) | Fragile, not structured |

**Critical missing module**: No Response Parser exists. All evaluators extract information from free-text via naive keyword matching.

### Verified Task Count (Phase 0)
```
BASE (default):
  ProtoReason:  17  (3 protocols × 3 + 5 calc + 3 troubleshoot)
  CausalBio:    13  (5 knockout + 3 pathway + 2 drug + 3 epistasis)
  DesignCheck:  10  (10 flawed experiments)
  Adversarial:  24  (5 false_premise + 5 hallucination + 3 misleading + 4 edge + 2 contradictory + 3 nonsense + 2 specific)
  MultiTurn:     6  (6 dialogues)
  Calibration:  10  (10 calibration test tasks)
  ─────────────────
  Base total:   80

EXTENDED:
  ProtoReason:  70  (13 protocols × 3 + 16 calc + 10 troubleshoot + 5 safety)
  CausalBio:    44  (18 knockout + 10 pathway + 8 drug + 8 epistasis)
  ─────────────────
  Extended total: 114

ADVANCED:
  ProtoReason:  49  (12 protocols × 3 + 8 calc + 5 troubleshoot)
  CausalBio:    19  (5 biomarker + 6 combination + 4 multi-omic + 4 resistance)
  DesignCheck:  10  (3 animal + 3 clinical + 1 multicenter + 3 sequencing)
  ─────────────────
  Advanced total: 78

GRAND TOTAL: 272 tasks (80 base + 114 extended + 78 advanced)
```

### Pre-Existing Results (Jan 8-9, 2026, Claude Sonnet 4)
- Adversarial enhanced: 87.5% pass rate (keyword scorer)
- Adversarial baseline: 66.7% pass rate (keyword scorer)
- Note: These results used the old keyword-based scorer. Must re-validate after Phase 1 scoring fixes.

---

## 2. Improvement Strategy (Revised)

### Philosophy
> Don't inflate. Don't pad. Make **80 base tasks** produce **trustworthy, reproducible, meaningful** scores. Then extend to 194 tasks for statistical power. Quality over quantity.

### Key Principle
> "Make it run" → "Make it score" → "Make it credible" → "Make it publishable"

### Priority Matrix (Post Phase 0 Review)

| Phase | Area | Effort | Impact | Status |
|-------|------|--------|--------|--------|
| **Phase 0** | Make it run — imports, tests, CLI, baseline | Low | Blocking | **COMPLETE** |
| **Phase 1** | Make it score — response parser + real metrics | **High** | Critical | Next |
| **Phase 2** | Make it credible — multi-model comparison, stats, judge validation | High | High | Planned |
| **Phase 3** | Make it publishable — paper, datasheet, demo, distribution | Medium | High | Planned |

### Key Changes from v2.0
1. **Phase 1 estimate: 2 weeks → 3-4 weeks** — scoring gap is much larger than originally assessed
2. **BioAmbiguity deferred** — removed from first NeurIPS submission; separate paper or revision
3. **Response Parser added** — new prerequisite module for Phase 1
4. **Extended data strategy** — use 194 tasks (base + extended) for statistical power
5. **MVP defined** — minimum viable publication scope for NeurIPS D&B
6. **Open-source model via API** — not local inference (Apple Silicon incompatible with bitsandbytes)

### Scope Guardrails
- Phase 1 targets: **80 base tasks** with real scoring
- Phase 2 extends to: **194 tasks** (base + extended) for statistical power
- Maximum components: **6** for first submission (BioAmbiguity deferred)
- API cost cap: **$120** total development budget

---

## 3. Phase 0: Make It Run — COMPLETE

> Completed 2026-02-24. See [PHASE0_BASELINE.md](PHASE0_BASELINE.md) for full report.

### Exit Criteria — All Met
- [x] Zero import errors (all 6 evaluators load)
- [x] All base tasks loadable (80 tasks verified)
- [x] Extended + advanced data loadable (272 total)
- [x] Test suite passes (27/27)
- [x] CLI entry point working (4 commands)
- [x] Dry-run completes successfully
- [x] API cost documented
- [x] Environment setup documented

---

## 4. Phase 1: Make It Score (~3-4 weeks)

### Objective
Replace all keyword-matching/placeholder scoring with real metrics. Build the response parsing infrastructure that the entire benchmark depends on.

### 4.0 Foundation: Response Parser Module (Week 1)

**Problem**: Every evaluator tries to extract structured information from free-text LLM responses via keyword matching. This fundamental missing piece must be built first.

**Implementation**: `bioeval/scoring/response_parser.py`
```python
class ResponseParser:
    """Extract structured answers from LLM free-text responses."""

    def extract_step_ordering(self, response: str, num_steps: int) -> list[int]
    def extract_numerical_value(self, response: str, expected_unit: str) -> float | None
    def extract_direction(self, response: str) -> Literal["up", "down", "no_change", "unclear"]
    def extract_flaw_list(self, response: str) -> list[dict]
    def extract_confidence(self, response: str) -> float
    def extract_yes_no(self, response: str) -> bool | None
```

**Strategy**: Two-tier extraction:
1. **Primary**: Structured prompting — force LLM to output in parseable format (e.g., "Output your answer as: DIRECTION: [up/down/unchanged]")
2. **Fallback**: LLM-based extraction — use Haiku to parse ambiguous responses (cheap, ~$0.001/call)

**Also in Week 1**:
- Wire existing LLM-Judge module into evaluation pipeline (`--use-judge` flag)
- Fix CLI `--data-tier` flag (currently not passed to `_run_component()`)
- Mini-judge validation: score 10 tasks yourself to confirm judge is directionally correct

### 4.1 ProtoReason Scoring Fix (Week 2)

**Current state**: `kendall_tau: None`, no response parser

**Fixes**:
| Task Type | Current | Fix |
|-----------|---------|-----|
| Step ordering | Null | Structured prompt → extract step numbers → Kendall's tau |
| Missing step | 4-char keyword matching | Set intersection on extracted step descriptions → recall |
| Calculation | Raw number string presence | Numerical extraction → ±5% tolerance comparison |
| Troubleshooting | 4-char keyword matching | LLM-as-Judge with ranked cause rubric |
| Safety | Keyword matching | LLM-as-Judge with safety criteria rubric |

**Key metric**: Kendall's tau for ordering (the headline ProtoReason metric)

### 4.2 CausalBio Scoring Fix (Week 2)

**Current state**: Checks if "essential"/"non-essential" string appears; ignores direction for drug responses

**Fixes**:
| Task Type | Current | Fix |
|-----------|---------|-----|
| Knockout | String presence of label | Extract direction → binary accuracy (essential/non-essential) |
| Pathway | Split pathway by "/" | Extract mentioned pathways → set coverage + LLM-Judge for mechanism |
| Drug response | Gene name presence (no direction) | Extract up/down per gene → directional accuracy |
| Epistasis | String presence of interaction type | Extract interaction type → accuracy + LLM-Judge for mechanism |

**Key metric**: Directional accuracy (binary: correct/incorrect prediction direction)

### 4.3 DesignCheck Scoring Fix (Week 3)

**Current state**: Keyword presence from flaw explanation text

**Fixes**:
- **Flaw detection rate (recall)**: Extract list of identified flaws → match against ground truth
- **False positive rate (precision)**: Count hallucinated flaws not in ground truth
- **Severity accuracy**: Extract severity assessment → compare against annotated severity
- **Fix quality**: LLM-as-Judge on proposed fixes (optional, for judge-scored tasks)

**Key metrics**: Precision, recall, F1 for flaw detection

### 4.4 MultiTurn Scoring Fix (Week 3)

**Current state**: 50% keyword coverage threshold, binary pass/fail

**Fixes**:
- **Per-turn evaluation**: Score each turn independently (not just aggregate)
- **Context retention**: Check if model references earlier turns appropriately
- **Progression quality**: Does reasoning build across turns?

**Key metric**: Per-turn behavior score + continuity bonus

### 4.5 Adversarial Scoring Hardening (Week 3)

**Current state**: Regex-based keyword detection — works but surface-level

**Fixes**:
- Review and add missing edge cases to detection patterns
- Add structured output extraction for clearer pass/fail determination
- Classify tasks into difficulty tiers (Basic/Intermediate/Expert)

**Key metric**: Binary pass/fail (keep, but with more robust detection)

### 4.6 Calibration Improvements (Week 3)

**Current state**: Pattern-based confidence density estimation

**Fixes**:
- **Structured confidence extraction**: Force model to output explicit 0-100% confidence number
- **Flex-ECE metric**: Implement per JAMIA Open study recommendation
- **Self-consistency (optional)**: 5 samples, agreement rate → more reliable confidence (expensive: 5x API cost)

**Key metric**: Flex-ECE (replaces standard ECE as primary calibration metric)

### 4.7 Integration, Testing, Baseline (Week 4)

- Run full evaluation on 80 base tasks with Claude Sonnet 4
- Document all scores — verify zero null scores
- Re-run enhanced vs baseline comparison with new scoring (update +20.8% claim)
- Apply scoring to extended data (114 tasks) — spot-check quality
- Write unit tests for all new scoring functions
- Update API cost estimate

### Development Process
- **Preserve existing file structure** — modify scorer logic within existing evaluator files
- **One component at a time**, test after each fix
- **Response parser first** — all scorer fixes depend on it
- **Run full suite after all fixes** to verify no regressions

### Deliverables
- 80 base tasks × real numeric scores, zero null scores
- Response parser module with ≥85% extraction success rate
- LLM-Judge wired into pipeline
- Enhanced vs baseline re-measured with real scoring
- Extended data (114 tasks) scoring validated

### Exit Criteria
- [ ] Zero null scores on 80 base tasks
- [ ] Response parser success rate ≥ 85% per component
- [ ] Kendall's tau computable on ≥ 90% of ordering tasks
- [ ] Directional accuracy measurable for all CausalBio tasks
- [ ] DesignCheck precision AND recall computable
- [ ] LLM-Judge integrated and callable (`--use-judge` flag works)
- [ ] 10-task mini-judge validation completed (self-scored)
- [ ] Unit tests for all scoring functions
- [ ] Enhanced vs baseline re-measured with new scoring
- [ ] Extended data scoring spot-checked
- [ ] Full test suite passes (27+ tests)
- [ ] API cost per run updated

---

## 5. Phase 2: Make It Credible (~3-4 weeks)

### Objective
Produce the evidence needed for a credible NeurIPS D&B submission: multi-model comparison, statistical rigor, judge validation, and key findings.

### 5.1 Open-Source Model Setup (Week 5, first)

**Decision**: Use API-based open-source models, NOT local inference.
- Apple Silicon Mac: `bitsandbytes` 4-bit quantization is CUDA-only
- CPU inference: ~30-60s per response × 80 tasks = too slow
- **Solution**: together.ai or Groq API for Llama-3-8B or Mistral-7B-Instruct (~$0.20/M tokens)

**Implementation**: Add `TogetherAIModel` / `GroqModel` wrapper to `bioeval/models/base.py`

Test with 5 tasks before full evaluation.

### 5.2 Three-Model Comparison (Week 5)

**Models**: Claude Sonnet 4, GPT-4o, Llama-3-8B (via together.ai)

**Task set**: 194 tasks (base 80 + extended 114) for statistical power

**Why extended**: Power analysis shows base-only counts (13-24 per component) are insufficient for most statistical tests. Extended data brings ProtoReason to 87 tasks and CausalBio to 57 tasks — adequate for moderate effect sizes.

**Statistics**: Per-component appropriate test (see PRD R10):
| Component | Score Type | Test | Effect Size |
|-----------|-----------|------|-------------|
| Adversarial | Binary | McNemar | Odds ratio |
| CausalBio | Ordinal | Wilcoxon signed-rank | Rank-biserial |
| ProtoReason | Continuous (tau) | Paired t-test / Wilcoxon | Cohen's d |
| DesignCheck | Continuous (F1) | Paired t-test / Wilcoxon | Cohen's d |
| Calibration | Continuous (ECE) | Paired t-test | Cohen's d |
| MultiTurn | Ordinal | Wilcoxon signed-rank | Rank-biserial |
| All | — | Bootstrap 95% CI (1000 iterations) | — |

**Deliverable**: Comparison table with per-component scores, effect sizes, CIs, p-values

### 5.3 Judge Validation Study (Week 6)

**Two-stage design** (solving the bootstrapping problem):
1. **Phase 1 mini-validation** (already done): 10 tasks × self-scored → confirms judge is directionally correct
2. **Phase 2 full validation**: 30-50 tasks × 2 annotators → formal κ computation

**Annotator recruitment** (start NOW, not during Phase 2):
- Option A: Biology PhD student collaborator (offer co-authorship)
- Option B: Lab colleague with biology expertise
- Minimum viable: self + 1 expert → 30 tasks × 2 annotators

**Metrics to report**:
- Cohen's κ (inter-annotator agreement)
- ICC (intra-class correlation for ordinal scores)
- LLM-Judge vs Human-Consensus correlation
- Per-component judge accuracy

**Threshold**: κ ≥ 0.5 (moderate agreement) for judge acceptance
**Fallback**: If κ < 0.5 for any component, use automated scoring only for that component

### 5.4 MedQA Gap Analysis (Week 6 — Simplified)

**Revised approach**: The MedQA comparison is illustrative, not the core finding.

**Simplified design**:
- Use published MedQA scores from literature (Claude Sonnet ~90%, GPT-4o ~88%) — no need to re-run
- Run GPQA-Bio subset (198 questions, MCQ) on same models as intermediate point
- BioEval scores provide the third data point
- Frame as "illustrative gradient" not "statistical proof"

**Alternative if time is short**: Drop MedQA comparison entirely. Focus on within-BioEval cross-component analysis as the primary finding.

### 5.5 Error Analysis (Week 7)

Systematic classification of wrong responses — a significant publication contribution:
```
For 50 wrong responses, classify:
  - Knowledge error: hallucination, outdated, domain confusion
  - Reasoning error: causal reversal, pathway truncation, scale confusion
  - Format error: correct knowledge, wrong output format
  - Confidence error: correct answer, wrong confidence
```

This directly supports the paper's thesis: "Models KNOW biology but can't REASON about it."

### 5.6 Adversarial Tier Classification (Week 7)

Classify 24 base adversarial tasks into:
- Basic (~8): straightforward traps
- Intermediate (~10): requires domain knowledge to detect
- Expert (~6): requires deep biological reasoning

Report failure rates per tier per model.

### 5.7 Calibration Analysis (Week 7)

- Run Flex-ECE on all 3 models
- Compare verbal confidence vs self-consistency (if budget allows)
- Report overconfidence rate on "should NOT be confident" tasks
- With 10 base + extended calibration tasks, report power limitations

### Deliverables
- 3-model comparison table with statistical backing
- Judge validation report with κ values
- Error analysis taxonomy (50 classified errors)
- 3-5 Key Findings with evidence
- Adversarial tier-stratified results
- Calibration analysis with Flex-ECE

### Exit Criteria
- [ ] 3 models evaluated on 194 tasks (base + extended)
- [ ] Statistical tests with CIs for all pairwise comparisons
- [ ] Judge validation completed (≥ 30 tasks × 2 annotators)
- [ ] Judge κ ≥ 0.5 for all judge-scored components (or fallback documented)
- [ ] Error analysis completed (50 classified errors)
- [ ] 3-5 Key Findings documented with supporting evidence
- [ ] Adversarial tasks classified by tier, results reported per tier
- [ ] Flex-ECE calibration results reported

---

## 6. Phase 3: Make It Publishable (~3 weeks)

### Objective
Write the paper, prepare supplementary materials, create demo mode, and submit.

### 6.1 Paper Writing (Week 8-9)

**Primary narrative**: "Integrated benchmark revealing the knows-vs-reasons gap"
- Frame: "Frontier LLMs score 90%+ on factual biology but show systematic failures in causal reasoning, experimental design, adversarial robustness, and calibration."
- Each component contributes ONE finding to this unified story.

**Paper outline**:
```
Title: "BioEval: Evaluating Whether LLMs Can Reason About Biology, Not Just Recall It"

Abstract

1. Introduction
   - Motivation: MedQA 90%+ but can models reason?
   - Figure 1: Performance gradient across task types
   - Contributions: (1) multi-dimensional benchmark with experimental ground truth,
     (2) 3-model comparison revealing systematic reasoning gaps,
     (3) error analysis distinguishing knowledge from reasoning failures

2. Related Work
   - Table 1: Competitive landscape matrix (from LITERATURE_SURVEY.md §6)
   - Position against LAB-Bench, GPQA, BioProBench

3. BioEval Framework
   - 3.1 Task Design (6 components, 194 tasks)
   - 3.2 Scoring System (hybrid: structured extraction + LLM-Judge)
   - 3.3 Data Integrity System

4. Experimental Setup
   - Models: Claude Sonnet 4, GPT-4o, Llama-3-8B
   - Evaluation protocol, statistical tests
   - Judge validation study results

5. Results
   - 5.1 Overall performance comparison (Table 2)
   - 5.2 Component-level analysis (the reasoning gap story)
   - 5.3 Error analysis: knowledge vs reasoning failures
   - 5.4 Calibration analysis
   - 5.5 Adversarial robustness by difficulty tier
   - 5.6 Prompt enhancement effects

6. Discussion
   - Key Finding 1: Models know biology but can't reason about it
   - Key Finding 2: Causal reasoning is the hardest dimension
   - Key Finding 3: Calibration paradoxes
   - Limitations

7. Conclusion & Future Work (BioAmbiguity teased)

Supplementary:
   - Datasheet for Datasets
   - Full task list with provenance
   - Judge validation details
   - Statistical test details
   - Reproducibility checklist
```

### 6.2 Publication Materials (Week 9)

- **Datasheet for Datasets** (Gebru et al. 2021 template)
- **Ethics & Broader Impact statement**
- **Reproducibility checklist** (NeurIPS format)
- **REPRODUCE.md** in repository

### 6.3 Demo Mode (Week 10)

- `bioeval demo` command using pre-cached results from Phase 2
- HTML dashboard with component breakdown, charts, Key Findings
- No API key required — reviewer can see results in 5 minutes

### 6.4 Distribution (Week 10)

- HuggingFace dataset publication (public 80% / private 20%)
- Git tag `v1.0.0-submission` + SHA256 manifest
- README final update with Key Findings

### Deliverables
- Complete paper draft (NeurIPS D&B format, 9 pages + references)
- Supplementary materials (datasheet, ethics, reproducibility)
- Demo mode working
- HuggingFace upload (if time allows)

### Exit Criteria
- [ ] Paper draft complete and internally reviewed
- [ ] Datasheet for Datasets complete
- [ ] Ethics statement complete
- [ ] Reproducibility checklist filled
- [ ] `bioeval demo` works without API key
- [ ] README reflects Key Findings
- [ ] Git tagged as submission version

---

## 7. BioAmbiguity: Deferred Track

### Rationale for Deferral
1. Solo developer cannot build 45 validated tasks in parallel with Phase 2
2. Expert validation (IAA κ ≥ 0.7) requires external annotators not yet recruited
3. NeurIPS deadline (~June) is achievable without BioAmbiguity
4. BioAmbiguity is strong enough for a separate paper (Nature Methods)

### Minimal Phase 1 Work (2-3 days during Phase 1)
- Create `bioambiguity/` directory skeleton (empty evaluator + data format)
- Create 5 pilot tasks as proof-of-concept
- Register in CLI as optional component

### Post-First-Submission Plan
- Option A: Add 15-20 pilot BioAmbiguity tasks during NeurIPS revision period
- Option B: Submit BioAmbiguity as separate paper to Nature Methods / Bioinformatics
- Option C: Expand to full 45 tasks for second submission cycle

### Design documents preserved:
- [BIOLOGICAL_AMBIGUITY_DESIGN.md](BIOLOGICAL_AMBIGUITY_DESIGN.md) — full 6-axis design
- See IMPROVEMENT_PLAN v2.0 §6 for original Phase 2b plan

---

## 8. Minimum Viable Publication (MVP)

### MUST HAVE (required for any submission)
- [ ] 6 components with real scoring (Phase 1)
- [ ] 2-model comparison minimum (Claude + GPT-4o)
- [ ] Basic statistical tests with CIs
- [ ] Honest task counts and limitations
- [ ] Reproducibility (seed, caching, version pinning)

### SHOULD HAVE (strengthens the paper significantly)
- [ ] 3-model comparison (add open-source via API)
- [ ] LLM-Judge validation (≥30 tasks, κ reported)
- [ ] Error analysis (50 classified wrong responses)
- [ ] Flex-ECE calibration
- [ ] Adversarial tier classification
- [ ] Datasheet + Ethics statement

### NICE TO HAVE (for the strongest possible paper)
- [ ] BioAmbiguity pilot (15-20 tasks)
- [ ] Full MedQA gap analysis (re-run MedQA on same models)
- [ ] 50-task judge validation with 2 external annotators
- [ ] DepMap live integration (API query at runtime)
- [ ] HuggingFace distribution
- [ ] HTML dashboard demo

### Decision point: At end of Phase 2, evaluate which NICE-TO-HAVEs are achievable before deadline.

---

## 9. Ground Truth Data Sources

### 9.1 DepMap Integration (CausalBio)
- **Source**: DepMap CRISPR gene effect scores (public, CC BY 4.0)
- **Release**: 24Q4 (version-pinned, SHA256 verified)
- **Data**: ~18,000 genes × ~1,000 cell lines
- **Usage**: Knockout prediction tasks specify cell line; binary scoring (essential/non-essential)
- **Ambiguous zone**: Scores between -0.5 and -0.3 excluded from binary scoring
- **Phase 2 integration**: Download and cross-validate existing task ground truth

### 9.2 Protocols.io Integration (ProtoReason)
- **Source**: protocols.io API (CC BY 4.0)
- **Quality filter**: citation count > 10 OR journal-linked only
- **Step constraint**: 8-20 steps per protocol
- **Current**: 3 base protocols, 13 extended, 12 advanced
- **Phase 2 goal**: Verify all protocols against source

### 9.3 Published Experimental Results (DesignCheck)
- **Source**: Retracted papers (PubMed retraction database), reproducibility studies
- **Current**: 10 base designs, 10 advanced
- **Phase 2 goal**: Verify flaw annotations against published retractions

---

## 10. Timeline (Revised)

### 10-Week Plan to NeurIPS D&B Submission

```
Week 1:   Phase 1 — Response parser, LLM-Judge wiring, CLI fix
Week 2:   Phase 1 — ProtoReason + CausalBio scoring fixes
Week 3:   Phase 1 — DesignCheck + MultiTurn + Adversarial + Calibration
Week 4:   Phase 1 — Integration, testing, baseline run, enhanced vs baseline
          ─── Phase 1 COMPLETE ───
Week 5:   Phase 2 — Open-source model setup, 3-model evaluation
Week 6:   Phase 2 — Judge validation, MedQA analysis (simplified)
Week 7:   Phase 2 — Error analysis, adversarial tiers, Flex-ECE, Key Findings
          ─── Phase 2 COMPLETE ───
Week 8:   Phase 3 — Paper writing (introduction, methods, results)
Week 9:   Phase 3 — Paper completion (discussion, supplementary materials)
Week 10:  Phase 3 — Polish, demo mode, README, submission prep
          ─── SUBMISSION ───
```

### Buffer
- NeurIPS D&B deadline typically early-mid June
- 10 weeks from Feb 24 = early May → **5-week buffer** before June deadline
- Buffer absorbs: Phase 1 overruns, annotator recruitment delays, revision cycles

### Realistic Timeline Estimate
| Scenario | Duration |
|----------|----------|
| Full-time, solo developer | 10-12 weeks |
| Part-time (50%), solo developer | 16-20 weeks |
| Full-time, with 1 collaborator for annotations | 8-10 weeks |

### Version Tags
- `v0.2.0-phase0` — current (Phase 0 complete)
- `v0.3.0-phase1` — after Phase 1
- `v0.4.0-phase2` — after Phase 2
- `v1.0.0-submission` — submission version

---

## 11. Immediate Action Items (Before Phase 1 Coding)

| # | Action | Priority | Status |
|---|--------|----------|--------|
| 1 | Recruit 1 expert annotator for judge validation (offer co-authorship) | Critical | Not started |
| 2 | Set up together.ai or Groq account for open-source model access | Important | Not started |
| 3 | Confirm NeurIPS D&B 2026 deadline | Important | Not started |
| 4 | Update PRD with Phase 0 actuals | Important | This session |

---

## 12. Guardrails Summary

All guardrails defined in detail in PRD §5. Key guardrails:

| Category | Key Rule |
|----------|----------|
| Scope | 6 components for first submission, 194 tasks max (base + extended) |
| Quality | Judge κ ≥ 0.5 for acceptance, IAA κ ≥ 0.7 for new tasks |
| Anti-hallucination | Gene/drug name validation, DepMap hash verification, provenance required |
| Development | Response parser first, then scorers. One component at a time. Test before refactor |
| Publication | No inflated claims, negative results reported, pre-registered hypotheses |
| Budget | API cost cap at $120, tracked per call |
| MVP | If time runs out, submit with 2-model comparison (MUST HAVE tier only) |

---

## 13. Publication Target

- **Primary venue**: NeurIPS Datasets & Benchmarks Track (deadline ~June 2026)
- **Submission**: 6-component benchmark (BioAmbiguity deferred)
- **Core contribution**: First integrated benchmark for biological reasoning with experimental ground truth, revealing systematic "knows-vs-reasons" gap
- **Secondary venue (later)**: Nature Methods — BioAmbiguity as biology contribution
- **Key differentiators**: DepMap ground truth, adversarial robustness, calibration, error analysis

---

## Appendix: Key File Locations

```
bioeval/
├── cli.py                       # CLI entry point (v0.2.0) — fix data-tier in Phase 1
├── config.py                    # Global settings
├── models/base.py               # Model wrappers — add TogetherAI/Groq in Phase 2
├── prompts/prompt_templates.py  # Enhancement system — keep, re-validate after Phase 1
├── scoring/
│   ├── response_parser.py       # NEW Phase 1: structured response extraction
│   ├── llm_judge.py             # Exists but disconnected — wire in Phase 1
│   ├── calibration.py           # Add Flex-ECE in Phase 1
│   ├── metrics.py               # NEW Phase 2: unified metric computation
│   └── statistics.py            # NEW Phase 2: statistical comparison framework
├── protoreason/evaluator.py     # Scoring fix in Phase 1 Week 2
├── causalbio/evaluator.py       # Scoring fix in Phase 1 Week 2
├── designcheck/evaluator.py     # Scoring fix in Phase 1 Week 3
├── adversarial/tasks.py         # Harden in Phase 1 Week 3
├── multiturn/dialogues.py       # Scoring fix in Phase 1 Week 3
├── execution/async_runner.py    # Production-ready — keep as-is
├── bioambiguity/                # Skeleton in Phase 1, full build deferred
└── integrity/                   # NEW Phase 2: data integrity system
```

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2026-02-24 | 1.0 | Initial plan |
| 2026-02-24 | 2.0 | Post-publication-quality review: English conversion, BioAmbiguity integration, guardrails |
| 2026-02-24 | 3.0 | **Post-Phase 0 review**: Task counts corrected (80 base, 272 total), Phase 1 estimate revised (2→3-4 weeks), BioAmbiguity deferred, MVP defined, response parser added as prerequisite, open-source model strategy decided (API-based), extended data strategy added, 10-week timeline |
