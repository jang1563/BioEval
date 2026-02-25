# BioEval Post-Phase 0 Comprehensive Review

> Date: 2026-02-24
> Scope: Plans for Phases 1–3, reviewed against Phase 0 baseline reality
> Perspectives: Technical Feasibility, Scientific Rigor, Publication Strategy, Risk Assessment
> Status: **21 issues identified (7 critical, 8 important, 6 minor)**

---

## Executive Summary

Phase 0 revealed a significant gap between planning documents and actual codebase state. The infrastructure (async execution, caching, rate limiting) is production-quality. But the scoring layer — the core of a benchmark — is almost entirely keyword-matching placeholders. The plans describe the RIGHT fixes but underestimate the effort and contain several internal contradictions that Phase 0 did not resolve.

**Bottom line**: The plan is scientifically sound but needs recalibration against Phase 0 findings. Estimated Phase 1 effort is 2x what's documented. BioAmbiguity (Phase 2b) should be deprioritized for first submission.

---

## PERSPECTIVE 1: Plan vs Phase 0 Reality Alignment

### CRITICAL-1: Task Count Inconsistency STILL Not Resolved

Phase 0 found: **80 base, 114 extended, 78 advanced = 272 total tasks**

But the planning documents still say:
- IMPROVEMENT_PLAN §1: "~98 unique tasks" and "adversarial: 44 tasks"
- IMPROVEMENT_PLAN §4: "98 tasks × real numeric scores"
- PRD §3.1: R4 says "~44 tasks (current)"
- PHASE0_BASELINE.md: Correctly says "80 base, 272 total"

**Actual verified counts (Phase 0)**:
```
Base:
  ProtoReason:  17  (3 protocols × 3 + 5 calc + 3 troubleshoot)
  CausalBio:    13  (5 knockout + 3 pathway + 2 drug + 3 epistasis)
  DesignCheck:  10
  Adversarial:  24  (NOT 44 — that includes extended)
  MultiTurn:     6  (NOT 7)
  Calibration:  10
  ─────────────────
  Base total:   80

PRD target counts vs actual base:
  R1 ProtoReason ~25 target:  17 exist (need +8)
  R2 CausalBio   ~25 target:  13 exist (need +12)
  R3 DesignCheck  ~15 target:  10 exist (need +5)
  R4 Adversarial  ~44 target:  24 exist (need +20)
  R5 MultiTurn    ~10 target:   6 exist (need +4)
  R6 Calibration  ~20 target:  10 exist (need +10)
```

**Impact**: Phase 1 plan says "98 tasks × real scores" — the actual number is 80 (base) or 272 (all tiers). Which tier is Phase 1 targeting? This must be decided explicitly.

**Recommendation**: Phase 1 should target **base (80 tasks) only**. Extended/advanced scoring can follow. Update all documents accordingly.

### CRITICAL-2: Scoring Gap Is Much Larger Than Plans Acknowledge

The plans describe scoring fixes as "Medium effort, ~2 weeks." Phase 0 code inspection reveals:

| Component | Plan Says | Actual State | Real Effort |
|-----------|-----------|-------------|-------------|
| ProtoReason ordering | "Kendall's tau null → compute" | `kendall_tau: None`, no response parser exists | **High** — need structured output parser + tau computation |
| ProtoReason calc | "±5% tolerance" | Checks if raw number string exists in response | **Medium** — need numerical extraction + tolerance logic |
| ProtoReason troubleshoot | "LLM-as-Judge fallback" | 4-char keyword matching on cause list | **Medium** — need LLM-Judge integration |
| CausalBio knockout | "Directional accuracy + LLM-Judge" | Checks if "essential"/"non-essential" string appears | **High** — need structured prediction extraction + direction validation |
| CausalBio pathway | "Mechanism quality scoring" | Splits pathway name by "/" and checks word presence | **High** — completely inadequate current scoring |
| CausalBio drug | "Drug response prediction" | Checks if gene name appears (no direction) | **High** — ignores up/down regulation entirely |
| DesignCheck | "Detection rate + FP rate + severity" | Keyword presence in response | **High** — need flaw extraction, severity parsing, FP counting |
| MultiTurn | "Per-turn + context retention" | 50% keyword coverage threshold | **Medium** — need per-turn scoring framework |
| Adversarial | "Already strong" | Regex-based keyword detection | **Medium** — works but brittle; edge cases will fail |
| Calibration | "Add Flex-ECE" | Pattern-based confidence extraction works | **Low** — need Flex-ECE metric + self-consistency method |

**The fundamental problem**: Almost every evaluator uses naive keyword matching. "Fixing scoring" means building a response parsing layer that doesn't exist at all. This is not a tweak — it's a new subsystem.

**Recommendation**: Phase 1 needs a **Response Parser** module before individual scorer fixes. Budget 3-4 weeks, not 2.

### IMPORTANT-3: LLM-Judge Exists But Is Disconnected

`bioeval/scoring/llm_judge.py` (516 lines) is fully implemented with:
- Task-specific rubrics (4-6 dimensions per task type)
- Weighted scoring (1-5 per dimension)
- Structured JSON output
- Claude API integration

BUT: **No evaluator actually calls it.** Each evaluator has its own inline keyword-matching scorer. The LLM-Judge module is orphaned code.

**Impact**: The plan says "LLM-as-Judge fallback for free-text tasks." In reality, the integration work hasn't started. The judge rubrics may also not align with the scoring dimensions described in the plan.

**Recommendation**: Phase 1 Step 0 should be: wire LLM-Judge into the evaluation pipeline as an optional scorer (`--use-judge` flag). Then fix individual scorers.

### IMPORTANT-4: Phase 1 Exit Criteria Need Revision

Current exit criteria:
```
- [ ] Zero null scores across all tasks
- [ ] Each scoring function has unit tests with known inputs/outputs
- [ ] Full suite regression test passes
- [ ] API cost per run updated
```

Missing:
- No criterion for scoring QUALITY (avoiding keyword-only scoring)
- No correlation check between old vs new scores (regression detection)
- No criterion for LLM-Judge integration
- No criterion for response parsing reliability

**Recommendation**: Add:
```
- [ ] ProtoReason ordering: Kendall's tau computable on ≥90% of responses
- [ ] CausalBio: directional accuracy measurable (not just keyword hit)
- [ ] DesignCheck: precision AND recall computable (not just recall)
- [ ] LLM-Judge callable for ≥1 component with validated rubric
- [ ] Response parsing success rate documented per component
```

---

## PERSPECTIVE 2: Scientific Rigor

### CRITICAL-3: The MedQA Gap Analysis Is Underspecified

The plan's central argument is "Figure 1: MedQA 90%+ → GPQA-Bio → BioEval X%." But:

1. **MedQA subset selection**: Which MedQA questions? The full 12,723-question test set? A biology-relevant subset? Running full MedQA is expensive and includes many non-biology questions (cardiology, nephrology, etc.).

2. **GPQA-Bio access**: GPQA has only 448 questions total, of which the biology subset is ~198. These are multiple-choice. How do you compare MCQ performance on GPQA-Bio with open-ended BioEval performance?

3. **Statistical comparison**: You can't run a paired statistical test between MedQA and BioEval — they're different tasks on different formats. The "gap" is descriptive, not statistically testable.

4. **Confound**: The plan acknowledges format confound but doesn't resolve it. A reviewer will say: "You're comparing MCQ (25% baseline) with open-ended (0% baseline). Of course the score drops."

**Recommendation**:
- Create a BioEval MCQ subset (20-30 tasks converted to 4-option MCQ) to enable format-controlled comparison
- Use GPQA-Bio as reference, not as direct comparison
- Frame Figure 1 as "illustrative" not "proof" — the real evidence comes from BioEval's internal component analysis
- Consider dropping MedQA comparison entirely and focusing on within-BioEval findings (simpler, more defensible)

### CRITICAL-4: Judge Validation Design Has a Bootstrapping Problem

The plan requires:
- "50 tasks × 2 annotators" for judge validation
- "κ ≥ 0.5 for judge acceptance"

But Phase 1 needs the judge to produce scores. If you don't validate the judge until Phase 2, you're building Phase 1 scores on an unvalidated judge. Then if the judge fails validation in Phase 2, all Phase 1 scores are invalid.

**Recommendation**: Split judge validation into two stages:
1. **Phase 1 mini-validation**: 10 tasks × 1 expert annotator (yourself). Enough to confirm the judge is directionally correct.
2. **Phase 2 full validation**: 50 tasks × 2 external annotators. Formal κ computation.

This prevents building on an unvalidated foundation.

### IMPORTANT-5: BioAmbiguity Task Quality Is Unverifiable by Solo Developer

The plan requires:
- "Each task created by PhD-level biologist, verified by second expert"
- "IAA κ ≥ 0.7 required for inclusion"

For a solo developer, this means:
- You create all 45 tasks yourself
- You need to find at least 1 external expert to validate them
- If that expert disagrees on 30% of tasks, you drop to 31 tasks (below the 35 minimum)

**More critically**: The plan never specifies WHO the second expert is. Without a concrete name or recruitment plan, this is a blocker.

**Recommendation**:
- Reduce initial BioAmbiguity scope to 20 high-confidence tasks (enough for a pilot)
- Use 2 validation strategies: (a) literature citation for each ground truth element, (b) 1 external reviewer for 20 tasks
- Scale to 45 only if publication submission is imminent and resources allow

### IMPORTANT-6: Statistical Framework Needs Minimum Sample Size Analysis

The plan specifies tests (McNemar, Wilcoxon, etc.) but never asks: "With N tasks per component, do we have enough statistical power?"

Power analysis for key comparisons:
```
Adversarial (24 tasks, binary):
  McNemar: detectable effect size at 80% power, α=0.05
  → Need ≥25% discordant pairs (~6 tasks where models disagree)
  → With 24 tasks and 3 models: MARGINAL power

ProtoReason (17 tasks, continuous tau):
  Paired t-test: detectable d at 80% power, α=0.05
  → 17 observations: can detect d ≥ 0.72 (large effect only)
  → INSUFFICIENT for moderate effects

CausalBio (13 tasks):
  → Can only detect very large effects (d ≥ 0.83)
  → INSUFFICIENT for publishable claims

Calibration (10 tasks):
  → Practically no power for statistical tests
```

**Impact**: With base task counts, most per-component comparisons will be underpowered. You can detect large effects in Adversarial, but almost nothing else will reach significance.

**Recommendation**:
- Option A: Use extended data (194 tasks) for statistical comparisons, not base (80)
- Option B: Report effect sizes and CIs without significance claims for small components
- Option C: Aggregate across components for overall comparison (increases N but loses component-level insight)
- Must be transparent about power limitations in the paper

### IMPORTANT-7: Calibration Component Needs Redesign

Current calibration has 10 tasks. The plan says expand to 20 (HIGH: 5, MEDIUM: 10, LOW: 5).

But the confidence extraction method is fragile:
- Pattern-based: counts "might/could/possibly" vs "definitely/certainly/always"
- Base score 0.5, adjusted by density difference × 0.1
- Range clipped to 0.1-0.95

**Problems**:
1. Extracting a float from a natural language response is inherently unreliable
2. The plan says "self-consistency method (5 samples)" — this 5x the API cost
3. Flex-ECE requires binned predictions — with 10-20 tasks, you get 1-2 per bin

**Recommendation**:
- Use structured prompting: force model to output a confidence number (e.g., "Output your confidence as a percentage 0-100% on a separate line")
- Self-consistency is valuable but expensive — implement it as optional mode
- With 20 tasks and 5 bins, you get ~4 tasks per bin — report this limitation
- Consider whether calibration should use extended data (more tasks = better binning)

---

## PERSPECTIVE 3: Technical Feasibility

### CRITICAL-5: Phase 1 Needs a Response Parser Before Scorer Fixes

The fundamental missing piece in the codebase is a **structured response parser**. Every evaluator tries to extract information from free-text LLM responses via keyword matching. Phase 1 needs:

```python
class ResponseParser:
    """Extract structured answers from LLM free-text responses."""

    def extract_step_ordering(self, response: str) -> list[int]
    def extract_numerical_value(self, response: str, unit: str) -> float
    def extract_direction(self, response: str) -> Literal["up", "down", "no_change", "unclear"]
    def extract_flaw_list(self, response: str) -> list[dict]
    def extract_confidence(self, response: str) -> float
```

**Two approaches**:
1. **Regex + heuristics**: Fast, free, brittle. Fails on creative model responses.
2. **LLM-based extraction**: Reliable, expensive (extra API call per task). Could use a cheap model (Haiku) for parsing.

**Recommendation**: Use structured prompting (force specific output format) + LLM-based extraction as fallback. This is a prerequisite module that should be built first in Phase 1.

### CRITICAL-6: GPU/Open-Source Model Strategy Is Undefined

Phase 2 requires 3 models: Claude Sonnet 4, GPT-4o, open-source 7B.

The `HuggingFaceModel` class exists in `base.py` but:
- Requires `torch`, `transformers`, `bitsandbytes`, `peft` — heavy dependencies
- Untested — no tests exist for the HuggingFace path
- On Apple Silicon (M-series Mac): `bitsandbytes` 4-bit quantization typically doesn't work (CUDA-only)
- CPU inference for 7B model: ~30-60 seconds per response × 80 tasks = ~40-80 minutes minimum

**Recommendation**:
- Do NOT use local inference on M-series Mac
- Use together.ai or Groq API for Llama-3-8B or Mistral-7B (~$0.20/M tokens)
- Add `TogetherAIModel` and `GroqModel` to `base.py` (simple API wrappers)
- Test this BEFORE Phase 2, not during

### IMPORTANT-8: Prompt Enhancement System Is Not Tested Against New Scoring

The existing prompt enhancement system (+20.8% on adversarial) was measured against the OLD keyword-based scorer. When Phase 1 replaces scoring with real metrics, the enhancement effect may:
- **Increase**: If the old scorer missed improvements the enhancements caused
- **Decrease**: If the old scorer gave false-positive "improvements"
- **Disappear**: If enhancements helped game keyword detection, not actual reasoning

**Recommendation**: After Phase 1 scoring fixes, re-run the enhanced vs baseline comparison. Update the +20.8% claim or flag it as "preliminary, pre-scoring-fix."

---

## PERSPECTIVE 4: Publication Strategy

### CRITICAL-7: Minimum Viable Publication (MVP) Is Not Defined

The plan describes a maximal vision (7 components, 45 BioAmbiguity tasks, 3-model comparison, MedQA gap, judge validation, Flex-ECE, etc.). But no "minimum viable publication" is defined for the case where time runs out.

**Question**: If you can only submit to NeurIPS D&B by June deadline, what is the MINIMUM scope?

**Recommended MVP**:
```
MUST HAVE (for any submission):
  ✓ 6 existing components with real scoring (Phase 1)
  ✓ 2-model comparison (Claude + GPT-4o) — drop open-source if needed
  ✓ Basic statistical tests with CIs
  ✓ Honest task counts and limitations
  ✓ Reproducibility (seed, caching, version pinning)

SHOULD HAVE (strengthens the paper):
  ✓ LLM-Judge validation (10-20 tasks, mini-study)
  ✓ Adversarial tier classification
  ✓ Flex-ECE calibration
  ✓ 3-model comparison (add open-source)
  ✓ Datasheet + Ethics statement

NICE TO HAVE (for strongest possible paper):
  ✓ BioAmbiguity component (even 15-20 pilot tasks)
  ✓ Full MedQA gap analysis
  ✓ 50-task judge validation with 2 annotators
  ✓ DepMap integration
  ✓ HuggingFace distribution
```

**Recommendation**: Define the MVP explicitly. BioAmbiguity should be "nice to have" for the first submission — it can be a follow-up paper if needed.

### IMPORTANT-9: NeurIPS D&B Deadline Feasibility

NeurIPS 2026 Datasets & Benchmarks deadline is typically early-mid June.

From today (Feb 24) to June = ~15 weeks.

Required work:
```
Phase 1 (scoring fixes):     3-4 weeks (revised from 2)
Phase 2 (credibility):       3-4 weeks
Phase 2b (BioAmbiguity):     3-4 weeks (if included)
Phase 3 (publication prep):  2-3 weeks
Paper writing:                2-3 weeks
───────────────────────────────────────
Total with BioAmbiguity:     13-18 weeks ← exceeds 15 weeks
Total WITHOUT BioAmbiguity:  10-14 weeks ← feasible (barely)
```

**Recommendation**:
- Target NeurIPS WITHOUT BioAmbiguity for the first submission
- Submit BioAmbiguity as a separate paper to Nature Methods or Bioinformatics
- Or: include 10-15 pilot BioAmbiguity tasks as "preliminary results" appendix

### IMPORTANT-10: Paper Narrative Needs Sharpening

Current narrative: "BioEval tests whether LLMs can DO biology" — this is broad.

For NeurIPS D&B, the reviewer wants ONE clear contribution. Competing narratives:
1. "First multi-dimensional biology benchmark with experimental ground truth"
2. "First context-dependency benchmark for biology (BioAmbiguity)"
3. "First calibration + adversarial analysis of LLMs in biology"
4. "Integrated benchmark revealing the knows-vs-reasons gap"

**Problem**: Trying to do all 4 dilutes each one. With 80-140 tasks, you don't have enough scale to support all 4 claims with statistical power.

**Recommendation**: Pick ONE primary contribution:
- **Best option**: #4 "Integrated benchmark revealing the knows-vs-reasons gap" — uses all components as evidence for a single story
- Frame: "We find that frontier LLMs score 90%+ on factual biology but show systematic failures in [causal reasoning / experimental design / adversarial robustness / calibration]"
- Each component contributes ONE finding to this story
- BioAmbiguity strengthens this narrative but isn't required for it

---

## PERSPECTIVE 5: Risk Assessment

### IMPORTANT-11: Phase Dependency Chain Creates Cascading Delay Risk

```
Phase 1 (scoring) → Phase 2 (comparison) → Phase 3 (publication)
                  ↗ Phase 2b (BioAmbiguity)
```

If Phase 1 takes 4 weeks instead of 2:
- Phase 2 starts late
- Phase 2b either starts in parallel (solo developer can't) or gets squeezed
- Phase 3 gets compressed
- Deadline pressure → quality drops

**Recommendation**: Build in 1-week buffer between phases. Better to start Phase 2 on week 5 than rush Phase 1 completion.

### IMPORTANT-12: Expert Annotator Recruitment Is Unresolved

The plan requires external expert annotators for:
- Judge validation (Phase 2): 50 tasks × 2 annotators
- BioAmbiguity validation (Phase 2b): 45 tasks × 2 annotators

No annotator has been identified. No budget is allocated.

**Realistic options**:
1. Lab collaborator (free, but their time is limited)
2. PhD student in biology (could exchange co-authorship for annotation work)
3. Prolific/Surge ($15-30/hr, ~$500-1000 for full annotation)
4. Self + 1 colleague (minimum viable)

**Recommendation**: Identify annotator(s) NOW, not during Phase 2. Offer co-authorship to a biology PhD student who can validate 50-70 tasks.

### MINOR-13: API Cost Budget May Be Insufficient

Budget: ~$100-125 total.

Phase 1 development runs (debugging scoring): ~20 runs × $1.40 = $28
Phase 2 three-model comparison: 3 models × 3 runs × $3 = $27
Judge scoring: 80 tasks × $0.03 × 10 runs = $24
Self-consistency calibration: 20 tasks × 5 samples × $0.02 × 5 runs = $10
BioAmbiguity evaluation: 45 tasks × 3 models × $0.03 = $4
Miscellaneous/debugging: ~$20

**Total realistic estimate**: $113 — within budget but tight.

**Recommendation**: Track costs from day 1 of Phase 1. If hitting $60 before Phase 2 starts, reassess.

---

## PERSPECTIVE 6: Missed Opportunities and Improvements

### MINOR-14: Extended Data Is Under-Utilized

272 tasks exist (80 base + 114 extended + 78 advanced), but the plan only targets 80 base + 45 BioAmbiguity ≈ 125 tasks.

The extended/advanced data already exists and is loadable. Using it:
- Increases statistical power dramatically (194 tasks vs 80)
- Requires no new task creation
- ProtoReason goes from 17 → 87 tasks, CausalBio from 13 → 57

**Risk**: Extended data may not have the same quality as base data.

**Recommendation**:
- Phase 1: Fix scoring for base tasks first
- Phase 1.5: Apply same scoring to extended data, spot-check quality
- Phase 2: Use extended data for statistical comparisons where base is underpowered
- Report base vs extended separately

### MINOR-15: No Error Analysis Framework Planned

The plan mentions error taxonomy but doesn't operationalize it. A systematic error analysis would be a significant publication contribution:

```
For each wrong response, classify:
  - Knowledge error (hallucination, outdated, domain confusion)
  - Reasoning error (causal reversal, pathway truncation)
  - Format error (correct knowledge, wrong output format)
  - Confidence error (correct answer, wrong confidence)
```

This distinguishes "doesn't know" from "knows but reasons poorly" — directly supporting the paper's thesis.

**Recommendation**: Add lightweight error classification to Phase 2 analysis. Even a manual classification of 30-50 error responses would strengthen the paper significantly.

### MINOR-16: Prompt Enhancement Strategy Not Integrated Into Plan

The existing +20.8% enhancement result is mentioned but not systematically leveraged in the Phase plan. Options:

1. **Phase 1**: Apply enhancements to all components (not just adversarial)
2. **Phase 2**: Report enhanced vs baseline for ALL components (not just adversarial)
3. **Publication**: "BioEval also provides prompt engineering strategies that improve performance by X%"

**Recommendation**: Integrate enhancement evaluation into Phase 2 as a secondary analysis dimension.

### MINOR-17: No Version Control Strategy for Task Data

The plan mentions "version freeze at submission" but doesn't address ongoing development. As scoring changes, task definitions may need modification (e.g., adjusting ground truth, fixing incorrect answers found during testing).

**Recommendation**:
- Tag current state as `v0.2.0-phase0` (done)
- Tag Phase 1 completion as `v0.3.0-phase1`
- Tag submission version as `v1.0.0-submission`
- Use semantic versioning for data changes

### MINOR-18: CLI Doesn't Support Extended/Advanced Data Properly

`bioeval/cli.py` has `--data-tier` flag but `_run_component()` doesn't actually use it — it always loads base tasks.

**Recommendation**: Fix in Phase 1 as part of scoring work. Low effort, high utility.

### MINOR-19: BioAmbiguity Integration Path Is Unclear

The plan says BioAmbiguity is Phase 2b, parallel with Phase 2. But:
- CLI doesn't include "bioambiguity" in COMPONENTS list
- No `bioambiguity/` directory exists yet
- No evaluator class template
- No data format defined

Starting BioAmbiguity from scratch in Phase 2b while simultaneously running Phase 2 is unrealistic for a solo developer.

**Recommendation**:
- Create `bioambiguity/` directory skeleton in Phase 1 (empty evaluator + data format)
- Create 5 pilot tasks in Phase 1 as proof-of-concept
- Full task creation deferred to Phase 2b or separate paper

---

## Summary: Issue Priority Matrix

| ID | Issue | Severity | Phase | Action Required |
|----|-------|----------|-------|----------------|
| C1 | Task count still inconsistent across docs | Critical | Now | Update IMPROVEMENT_PLAN with Phase 0 actual counts |
| C2 | Scoring gap much larger than planned | Critical | Phase 1 | Revise Phase 1 estimate to 3-4 weeks; build response parser first |
| C3 | MedQA gap analysis underspecified | Critical | Phase 2 | Define subset, format-control strategy, or drop from MVP |
| C4 | Judge validation bootstrapping problem | Critical | Phase 1-2 | Add mini-validation (10 tasks) to Phase 1 |
| C5 | No response parser exists | Critical | Phase 1 | Build structured parsing module as Phase 1 prerequisite |
| C6 | GPU/open-source model strategy undefined | Critical | Phase 2 | Choose API-based approach now; test before Phase 2 |
| C7 | No MVP defined | Critical | Now | Define minimum viable publication scope |
| I3 | LLM-Judge exists but disconnected | Important | Phase 1 | Wire judge into pipeline first |
| I4 | Phase 1 exit criteria incomplete | Important | Now | Add quality criteria, not just "no nulls" |
| I5 | BioAmbiguity unverifiable solo | Important | Phase 2b | Reduce scope to 20 pilot tasks |
| I6 | Underpowered statistical tests | Important | Phase 2 | Use extended data or report limitations |
| I7 | Calibration extraction fragile | Important | Phase 1 | Use structured prompting |
| I8 | Enhancement claims untested with new scoring | Important | Phase 2 | Re-measure after scoring fix |
| I9 | NeurIPS deadline tight | Important | Now | Drop BioAmbiguity from first submission |
| I10 | Paper narrative too broad | Important | Phase 3 | Pick ONE primary contribution |
| I11 | Cascading delay risk | Important | Now | Add 1-week buffer between phases |
| I12 | No annotator recruited | Important | Now | Start recruitment immediately |
| m13 | API budget tight | Minor | Ongoing | Track from Phase 1 start |
| m14 | Extended data under-utilized | Minor | Phase 1.5 | Apply scoring to extended after base |
| m15 | No error analysis framework | Minor | Phase 2 | Add manual error classification |
| m16 | Enhancement not systematically integrated | Minor | Phase 2 | Test enhancements on all components |
| m17 | No version control strategy for data | Minor | Phase 1 | Use git tags |
| m18 | CLI doesn't use data-tier flag | Minor | Phase 1 | Fix during scoring work |
| m19 | BioAmbiguity integration path unclear | Minor | Phase 1 | Create skeleton + 5 pilot tasks |

---

## Recommended Revised Phase Plan

### Phase 1: Make It Score (3-4 weeks)

**Week 1**: Foundation
- Build response parser module (structured extraction + LLM-based fallback)
- Wire LLM-Judge into evaluation pipeline (`--use-judge` flag)
- Fix CLI data-tier support
- Mini-judge validation: 10 tasks self-scored

**Week 2**: Core scoring fixes
- ProtoReason: implement Kendall's tau + numerical extraction
- CausalBio: implement directional accuracy + mechanism quality
- DesignCheck: implement flaw detection rate + false positive rate

**Week 3**: Remaining fixes + validation
- MultiTurn: per-turn evaluation + context retention
- Calibration: structured confidence extraction + Flex-ECE
- Adversarial: review and harden scoring logic
- Unit tests for all new scoring functions

**Week 4**: Integration + baseline
- Run full evaluation on base tasks (80 tasks × Claude)
- Document all scores, identify any remaining nulls
- Run enhanced vs baseline comparison with new scoring
- Update Phase 0 baseline document

**Exit criteria (revised)**:
- [ ] Zero null scores on base tasks
- [ ] Response parser success rate ≥ 85% per component
- [ ] Kendall's tau computable on ≥ 90% of ordering tasks
- [ ] Directional accuracy measurable for all CausalBio tasks
- [ ] LLM-Judge integrated and callable
- [ ] 10-task mini-judge validation completed
- [ ] Unit tests for all scoring functions
- [ ] Enhanced vs baseline re-measured with new scoring

### Phase 2: Make It Credible (3-4 weeks)

**Week 5**: Multi-model evaluation
- Set up together.ai/Groq API for open-source model
- Run 3-model evaluation on base tasks
- Compute per-component statistics

**Week 6**: Validation + analysis
- Run on extended data (194 tasks) for statistical power
- Judge validation: 30-50 tasks × 2 annotators (if recruited)
- Adversarial tier classification
- Error analysis: classify 50 wrong responses

**Week 7**: Statistical analysis + figures
- Statistical tests with CIs
- Generate comparison tables and figures
- Calibration analysis with Flex-ECE
- Identify 3-5 Key Findings

**Exit criteria**:
- [ ] 3 models evaluated
- [ ] Statistical tests with CIs for all comparisons
- [ ] Judge validation κ reported (even if only 30 tasks)
- [ ] Key Findings documented
- [ ] Error analysis completed

### Phase 3: Make It Publishable (3 weeks)

**Week 8-9**: Paper writing
- Draft paper following outline
- Create figures and tables
- Write Datasheet, Ethics, Reproducibility sections

**Week 10**: Polish + submission
- Internal review and revision
- Demo mode finalization
- README update
- HuggingFace upload (if time allows)

### BioAmbiguity (Separate Track)
- Phase 1: Create skeleton + 5 pilot tasks (during Phase 1, 2-3 days)
- Post-submission: Full 45-task development for follow-up paper or revision

### Revised Timeline
```
Week 1-4:   Phase 1 (scoring)
Week 5-7:   Phase 2 (credibility)
Week 8-10:  Phase 3 (publication)
───────────────────────────────────
Total: 10 weeks → NeurIPS deadline ~June = feasible
Buffer: 5 weeks before typical June deadline
```

---

## Appendix: Documents That Need Updates

| Document | What Needs Changing |
|----------|-------------------|
| IMPROVEMENT_PLAN.md §1 | Task count: "~98" → "80 base (272 total)" |
| IMPROVEMENT_PLAN.md §4 | Phase 1 estimate: "2 weeks" → "3-4 weeks" |
| IMPROVEMENT_PLAN.md §4 | Add response parser as Phase 1 prerequisite |
| IMPROVEMENT_PLAN.md §10 | Timeline: recalibrate to 10-week plan |
| PRD.md R4 | Adversarial: "~44 tasks (current)" → "24 base tasks" |
| PRD.md R6 | Calibration: specify structured confidence extraction |
| PRD.md §9 | Add MVP definition |
| PUBLICATION_QUALITY_REVIEW.md | Mark resolved issues from Phase 0 |
