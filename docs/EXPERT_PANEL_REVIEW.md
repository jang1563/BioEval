# BioEval Expert Panel Review

> Date: 2026-02-24
> Documents Reviewed: IMPROVEMENT_PLAN.md, PRD.md
> Format: 5-member expert panel simulation
> Purpose: Validate BioEval improvement plan for execution feasibility, scientific rigor, and portfolio value

---

## Panel Composition

| # | Role | Perspective | Focus |
|---|------|-------------|-------|
| 1 | **Dr. A** — Benchmark Publication Expert | NeurIPS Datasets & Benchmarks, Nature Methods experience | Completeness as a benchmark paper |
| 2 | **Dr. B** — ML Systems Engineer | 10 years production AI systems | Code architecture, scalability, execution feasibility |
| 3 | **Dr. C** — Computational Biologist | DepMap/CMap data researcher | Scientific validity of biological tasks |
| 4 | **Dr. D** — AI Evaluation Methodology | LLM-as-Judge, calibration research | Statistical rigor of scoring methodology |
| 5 | **Dr. E** — Hiring Manager / Portfolio Reviewer | BioAI startup CTO | Portfolio impact and differentiation |

---

## Panel Member 1: Dr. A — Benchmark Publication Expert

### Overall Assessment: B+ (Good concept, execution gaps)

### Strengths
1. **Clear positioning**: "BioEval tests whether LLMs can 'do' biology, not just 'know' it." This framing is strong and resonates with NeurIPS D&B reviewers.
2. **Anti-hallucination system**: A benchmark that guarantees its own data integrity is very rare. This could be a standalone contribution.
3. **Honest current state**: Correcting "170+ tasks" to ~98 and admitting 60% placeholder scoring — this honesty builds plan credibility.

### Critical Concerns

**CC-A1: No quantitative comparison with existing benchmarks**
> The PRD describes differentiation from MedQA/PubMedQA/BioASQ qualitatively only. For a paper:
> - Evaluate the same model (Claude Sonnet 4) on both MedQA and BioEval simultaneously
> - "A model scoring 90% on MedQA scores only 62% on BioEval causal reasoning" — this gap IS the core contribution
> - Without this gap data, the "why do we need a new benchmark?" argument is weak

**Recommendation**: Acquire MedQA/PubMedQA baseline in parallel with Phase 0-1. This becomes Figure 1 of the paper.

**CC-A2: Missing leaderboard / reproducibility package**
> Good benchmark papers always include:
> - Public leaderboard (GitHub Pages is sufficient)
> - Docker/conda environment for one-command reproducibility
> - Minimum 3-model comparison (GPT-4, Claude, open-source 7B)

**Recommendation**: Add "3-model comparison table" to Phase 2 deliverables.

**CC-A3: 250-task target is risky**
> Phase 3 originally targeted 250 tasks, which risks scope creep.
> MMLU has 14,000+ questions but they're auto-scored MCQ.
> BioEval uses free-response + LLM-as-Judge, so 100 high-quality tasks > 250 mediocre ones.

**Recommendation**: Revise target to **100-120 fully validated tasks**. Strengthen per-task ground truth depth instead.

---

## Panel Member 2: Dr. B — ML Systems Engineer

### Overall Assessment: B (Architecture sound, execution plan too vague)

### Strengths
1. **Async/caching infrastructure**: Token bucket rate limiter, SQLite cache, semaphore concurrency — genuinely production-quality. Most academic benchmarks ignore this.
2. **Hybrid scoring pipeline**: Structured extraction → metric → LLM-as-Judge fallback. This 3-stage design balances cost and accuracy well.
3. **CLI design** (`bioeval run/compare/report`): Follows Unix philosophy. Easy to integrate into pipelines.

### Critical Concerns

**CC-B1: Refactoring scope is excessive**
> The PRD's architecture (Section 6) proposes splitting each component into 3 files (evaluator, data, scorer).
> 6 components × 3 files = 18 files refactored, plus ~10 new files for integrity/, reporting/, data/.
>
> **Risk**: Large-scale refactoring of "working" code introduces regressions. Refactoring is not the goal — meaningful results are.

**Recommendation**: Minimize refactoring. **Preserve existing file structure** and modify scorer logic in-place.

**CC-B2: No LLM-as-Judge cost modeling**
> PRD says "LLM-as-Judge only for free-text tasks" but doesn't estimate:
> - How many of 98 tasks are free-text?
> - Token count per Judge call
> - Total API cost per full evaluation run

**Recommendation**: Add cost model.
```
98 tasks × avg 2000 input + 500 output tokens
Claude Sonnet 4: ~$1.50 (eval) + ~$0.75 (judge) = ~$2.25/run
Development budget (20 runs): ~$45
```

**CC-B3: `bioeval run --all` doesn't currently work**
> The end-to-end pipeline is listed as Phase 2, but it should be Phase 0.
> Import errors exist, missing modules exist, only 36/98 tasks have run successfully.
> Scoring fixes are meaningless if execution fails.

**Recommendation**: Reorder priorities: **Run first → Score second → Ground truth third.**

**CC-B4: Test strategy is "nice-to-have" level**
> Phase 3 test strategy lists "Unit tests, Integration tests, Regression tests, Validation tests" without specifying the first test to write.
> Existing `tests/test_bioeval.py` should be run first to establish a baseline.

**Recommendation**: Make "run existing test suite" the first action in Phase 0.

---

## Panel Member 3: Dr. C — Computational Biologist

### Overall Assessment: B+ (Biologically sound, but ground truth strategy needs work)

### Strengths
1. **Biological task validity**: TP53/KRAS/BRCA1 knockout, EGFR pathway, epistasis — these are real research questions, not toy problems.
2. **DesignCheck flaw taxonomy**: Controls, statistics, confounders, technical, interpretation — maps exactly to common peer review issues.
3. **DepMap/CMap integration plan**: Using experimental data as ground truth distinguishes BioEval from all other LLM benchmarks.

### Critical Concerns

**CC-C1: DepMap integration is not simple**
> 1. **Cell line specificity**: TP53 knockout effects differ entirely between A549 (KRAS mutant) and MCF7 (ER+). "What happens when you knock out TP53?" is unanswerable without cell line context.
> 2. **CRISPR score interpretation**: Gene effect score -1.0 = "essential" (growth), 0 = "no effect" — but this only reflects growth phenotype. The model might answer about DNA repair function loss, which doesn't map directly to fitness scores.
> 3. **Context-dependent essentiality**: BRCA1 is non-essential in most cell lines but synthetic lethal in BRCA2-mutant backgrounds.

**Recommendation**: DepMap integration principles:
```
1. Specify cell line in every task: "In A549 cells, what happens when TP53 is knocked out?"
2. Use binary ground truth only: essential (<-0.5) vs non-essential (>-0.3)
3. Ambiguous zone (-0.5 to -0.3): exclude from binary scoring, use for BioAmbiguity tasks
4. Separate "cell line context awareness" as an evaluation dimension
```

**CC-C2: Protocols.io data quality concern**
> Protocols.io is user-generated content with high quality variance.
> Mechanically importing 30 protocols risks "garbage in, garbage out."

**Recommendation**:
```
1. Use only protocols with citation count > 10 OR journal-linked
2. Prioritize Nature Protocols, STAR Protocols, Current Protocols
3. Constrain to 8-20 steps per protocol
4. Manually annotate "critical ordering constraints" for each protocol
```

**CC-C3: Adversarial tasks need more biological depth**
> Current adversarial tasks are mostly undergraduate-level.
> Expert-level adversarial examples needed, e.g.:
> - "PLK4 inhibition causes mitotic catastrophe in all cell types" (false — only in tetraploid cells)
> - "BET inhibitors like JQ1 downregulate MYC in all cancers" (false — BET-independent MYC regulation exists)

**Recommendation**: Classify adversarial tasks into 3 tiers:
```
Tier 1 (Basic): Textbook-level error detection (~20)
Tier 2 (Intermediate): Common but subtle misconceptions (~15)
Tier 3 (Expert): Recent literature nuance required (~10)
```

**CC-C4: Epistasis tasks too few (only 3)**
> Epistasis (genetic interactions) is BioEval's most unique evaluation area.
> 3 tasks (KRAS-STK11, BRCA1-53BP1, RB1-TP53) is insufficient.

**Recommendation**: Add 5-10 epistasis pairs from SyntheticLethal.com and DepMap synthetic lethality data. Include:
- Synthetic lethality (therapeutically relevant, e.g., BRCA-PARP)
- Suppressor interactions (e.g., TP53 loss causing MDM2 inhibitor resistance)
- Buffering interactions (paralog redundancy)

---

## Panel Member 4: Dr. D — AI Evaluation Methodology Expert

### Overall Assessment: B (Methodology has potential, statistical rigor lacking)

### Strengths
1. **Hybrid scoring approach**: Structured extraction + LLM-as-Judge is the right combination. Many benchmarks rely on only one method.
2. **Calibration component**: Directly measuring ECE and Brier score is rare in LLM benchmarks. This is a real contribution.
3. **Prompt enhancement A/B test**: Systematic enhanced vs baseline comparison with existing results (87.5% vs 66.7%) is good.

### Critical Concerns

**CC-D1: LLM-as-Judge reliability not validated**
> Three critical issues with using LLM-as-Judge:
>
> 1. **Judge-Human Agreement**: Never measured. Need ≥50 tasks with human expert annotation, then report Cohen's kappa.
> 2. **Judge Consistency**: Same response scored 3 times — how much variance? Need to report inter-rater reliability (ICC).
> 3. **Judge Bias**: Claude judging Claude creates self-bias (Zheng et al., 2023). Need cross-judge evaluation (Claude judge + GPT-4 judge).

**Recommendation**: Add "Judge Validation Study" to Phase 2:
```
1. 50 tasks with manual scoring by 3 expert annotators
2. LLM Judge (Claude) vs Human Expert: Cohen's kappa
3. LLM Judge (Claude) vs LLM Judge (GPT-4): Cross-judge agreement
4. Same-response 3x repeated scoring: Judge consistency (ICC)
```

**CC-D2: No statistical significance framework**
> "87.5% vs 66.7%" — is this difference statistically significant?
> - McNemar's test (paired binary outcomes) is appropriate for adversarial
> - 95% confidence interval with bootstrap
> - Effect size (Cohen's d or odds ratio)
> - Without p-values, comparisons lack rigor

**Recommendation**: Add statistical reporting to `bioeval compare`:
```python
def compute_significance(enhanced_results, baseline_results):
    return {
        "mcnemar_p_value": mcnemar_test(enhanced, baseline),
        "bootstrap_ci_95": bootstrap_confidence_interval(enhanced, baseline, n=1000),
        "effect_size": cohens_d_or_odds_ratio(enhanced, baseline),
    }
```

**CC-D3: Calibration task composition bias**
> Current calibration tasks split into "made-up entities" (model doesn't know) and "known facts" (model knows).
> Missing: "partially known" — the hardest and most informative calibration test.
> Example: "Prognostic significance of ARID1A mutation" — context-dependent, should elicit MEDIUM confidence.

**Recommendation**: Balance calibration tasks:
```
Expected HIGH confidence: 5 tasks (well-established facts)
Expected MEDIUM confidence: 10 tasks (context-dependent, evolving)
Expected LOW/IDK confidence: 5 tasks (unknown entities, insufficient data)
```
MEDIUM category is the true test of calibration.

**CC-D4: Score normalization undefined**
> Different components use different scales: Binary 0/1, ECE 0-1 (lower=better), Judge 1-5, Kendall's tau -1 to +1.
> How to combine into a single "BioEval score"?

**Recommendation**: Three options (recommend Option A):
```
Option A (Recommended): Independent per-component reporting, no composite score
Option B: Percentile-based normalization within model pool
Option C: Threshold-based binary (pass/fail per component)
```

---

## Panel Member 5: Dr. E — Hiring Manager / Portfolio Reviewer

### Overall Assessment: B+ (Strong concept, needs sharper demo story)

### Strengths
1. **Shareable problem definition**: "LLMs think they 'know' biology but we don't know if they can 'do' it" — this one-liner works for non-experts. The most important portfolio element.
2. **Real results exist**: 87.5% vs 66.7% — actual data, not just plans. Most portfolio projects are plans without results.
3. **BioAI-Ecosystem connection**: Shows systems thinking — BioEval is part of a larger architecture.

### Critical Concerns

**CC-E1: No 5-minute demo exists**
> Portfolio reviewers need: **30-second hook + 5-minute demo**.
> Current state requires: README → setup → API key → run → interpret (30+ minutes, possible import errors).
> Needed: `bioeval demo` with pre-cached results → HTML report.

**Recommendation**: Add Demo Mode as Phase 3 deliverable.

**CC-E2: README doesn't reflect current state**
> Portfolio reviewers see the README first. If it claims "170+ tasks" when the reality is ~98, credibility is immediately lost.
> README needs:
> 1. One-line summary + 3 key differentiators
> 2. Quick results table
> 3. Architecture diagram
> 4. One-command demo
> 5. Limitations section

**CC-E3: "So what?" story is underdeveloped**
> Reviewer question: "What did this benchmark actually discover?"
>
> Currently answerable:
> - "Claude is tricked 33% of the time by adversarial biology" — good
> - "Prompt engineering improves by 20.8%" — very good
>
> Not yet answerable:
> - "How does GPT-4 compare to Claude?" — no data
> - "How does a fine-tuned 7B compare?" — no data
> - "What type of mistakes are most dangerous?" — qualitative only

**Recommendation**: Create a "Key Findings" section with 3-5 concrete discoveries backed by data.

**CC-E4: Ecosystem story absent from BioEval README**
> BioAI-Ecosystem relationship is only in the PRD. Portfolio reviewers looking at BioEval alone see a standalone project. Adding one paragraph about the ecosystem context demonstrates systems thinking.

---

## Cross-Panel Consensus: Top 10 Action Items

### Tier 1: Immediate (Without these, nothing else matters)

| # | Action | Who raised | Why critical |
|---|--------|-----------|-------------|
| 1 | **Make it run** — fix import errors, verify 98 tasks execute | Dr. B (CC-B3) | Nothing works if it doesn't run |
| 2 | **Remove null scores** — every task must produce a real numeric score | Dr. D, Dr. B | Without scoring, it's not a benchmark |
| 3 | **Run existing test suite** — record current baseline before any changes | Dr. B (CC-B4) | Must know current state before fixing |

### Tier 2: Credibility (Without these, results aren't trustworthy)

| # | Action | Who raised | Why critical |
|---|--------|-----------|-------------|
| 4 | **3-model comparison** — Claude, GPT-4, open-source 7B results | Dr. A, Dr. E | Findings require multi-model evidence |
| 5 | **MedQA gap quantification** — "why do we need a new benchmark?" | Dr. A (CC-A1) | Core motivation requires data |
| 6 | **Judge validation study** — human vs judge agreement metrics | Dr. D (CC-D1) | Using a judge requires proving the judge works |
| 7 | **Cell line context in DepMap tasks** — no context-free knockout questions | Dr. C (CC-C1) | Wrong ground truth = wrong benchmark |

### Tier 3: Portfolio Impact (Without these, good work goes unnoticed)

| # | Action | Who raised | Why critical |
|---|--------|-----------|-------------|
| 8 | **Demo mode** — API-key-free result visualization | Dr. E (CC-E1) | Reviewers need 5-minute experience |
| 9 | **README update** — accurate counts, Key Findings, architecture | Dr. E (CC-E2, E3) | First impression determines everything |
| 10 | **Statistical significance** — p-values and CIs on all comparisons | Dr. D (CC-D2) | Numbers without statistics aren't science |

---

## Revised Priority Matrix (Post-Panel)

```
Phase 0: "Make it Run" (1 week)
  ├── Fix import errors, missing modules
  ├── Verify all 98 tasks execute
  ├── Run existing test suite, record baseline
  └── Deliverable: `bioeval run --all` exits cleanly

Phase 1: "Make it Score" (2 weeks)
  ├── Remove null scores (ProtoReason, CausalBio, DesignCheck, MultiTurn)
  ├── Preserve file structure, update scorer logic in-place (minimize refactoring)
  ├── Document API cost model
  └── Deliverable: 98 tasks × real numeric scores

Phase 2: "Make it Credible" (2-3 weeks)
  ├── 3-model comparison (Claude Sonnet 4, GPT-4o, open-source 7B)
  ├── MedQA baseline → BioEval gap analysis
  ├── DepMap integration (cell line context, binary ground truth)
  ├── Judge validation study (50 tasks × expert annotation)
  ├── Statistical significance framework (McNemar, bootstrap CI)
  └── Deliverable: "3-5 Key Findings" with statistical backing

Phase 3: "Make it Impressive" (2 weeks)
  ├── Demo mode (pre-cached results → HTML report)
  ├── Full README update
  ├── Adversarial tier classification (Basic/Intermediate/Expert)
  ├── Calibration task balance (HIGH/MEDIUM/LOW)
  ├── Ecosystem documentation
  └── Deliverable: Portfolio-ready project with 5-min demo
```

---

## Panel Closing Remarks

**Dr. A**: "BioEval's core value is its framing. The 'knows vs can do' distinction could be a paper title. But that framing needs quantitative evidence. Once the MedQA gap data is secured, this becomes a strong paper."

**Dr. B**: "The infrastructure is good. The problem is the logic sitting on top of it. Resist the refactoring urge — modify scorers in existing files. Working code beats perfect architecture."

**Dr. C**: "The biological task selection is strong. If DepMap integration is done properly, this benchmark is in a different league. But without cell line context, 'What happens when TP53 is knocked out?' is an unanswerable question. Always specify context."

**Dr. D**: "Evaluation methodology is the biggest weakness. If you use LLM-as-Judge, you must validate the judge. Without statistical significance, '87.5% vs 66.7%' is just two numbers, not a finding."

**Dr. E**: "Good project, but the presentation is lacking. A 5-minute demo, clean README, and 3 Key Findings — these three things determine 95% of portfolio impact. Code quality matters in interviews, but you need to get to the interview first."
