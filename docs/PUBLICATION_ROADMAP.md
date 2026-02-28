# BioEval Publication Roadmap

> Last updated: 2026-02-28 | Version: 0.3.1
> Phase 1: COMPLETE (incl. expert review hardening) | Phase 2: NEXT
> Current readiness: ~75% (expert review done, scoring hardened, awaiting multi-model eval)

## Current System State (Verified 2026-02-27)

### Task Inventory (Actual, Code-Verified)

| Component | Base | Extended-only | Advanced-only | Unique Total |
|-----------|:----:|:------------:|:------------:|:------------:|
| ProtoReason | 14 | 45 | 0* | 59 |
| CausalBio | 13 | 34 | 0* | 47 |
| DesignCheck | 10 | 20 | 0* | 30 |
| Adversarial | 30 | — | — | 30 |
| MultiTurn | 6 | 24 | — | 30 |
| Calibration | 30 | — | — | 30 |
| BioSafety | 25 | — | — | 25 |
| DataInterp | 25 | — | — | 25 |
| Debate | 25 | — | — | 25 |
| **Total** | **178** | **123** | **0** | **301** |

\* Advanced tiers return identical task IDs as base (same prompts, no unique additions).

### Evaluation Results (Claude Sonnet 4, seed=42) — Phase 2.0 Re-run

| Component | Tasks | Scored | Mean | Primary Metric | Rating | vs Old |
|-----------|:-----:|:------:|:----:|----------------|:------:|:------:|
| ProtoReason | 14 | 10/14 | 0.978 | apa / recall / num_acc / cause_cov | Strong | +0.068 |
| Adversarial | 30 | 30/30 | 0.923 | score | Strong | +0.112 |
| BioSafety | 25 | 25/25 | 0.829 | score (top-level) | Strong | -0.028 |
| CausalBio | 13 | 11/13 | 0.798 | effect_correct / combined / mechanism | Good | +0.083 |
| MultiTurn | 6 | 6/6 | 0.772 | overall_score | Good | -0.139 |
| DataInterp | 25 | 25/25 | 0.720 | score (top-level) | Good | +0.096 |
| Calibration | 30 | 30/30 | 0.690 | 1 − calibration_error | Good | -0.030 |
| DesignCheck | 10 | 10/10 | 0.535 | F1 | Fair | **+0.217** |
| Debate | 25 | 25/25 | 0.377 | composite_score | Weak | **-0.076** |
| **Weighted Mean** | **178** | **172/178** | **0.727** | | | +0.022 |

**Phase 2.0 notes:**
- 6 tasks failed due to API connection errors (4 ProtoReason, 2 CausalBio). Retry pending.
- **DesignCheck** improved from 0.318 to 0.535 (+68%) — alias matching fix validated.
- **Debate** dropped from 0.453 to 0.377 as predicted — honest score reflecting 16% outcome accuracy.
- Overall weighted mean improved from 0.705 to 0.727 despite Debate drop.

**Score field structure varies by component** (see `docs/SCORE_FIELD_MAPPING.md`):
- ProtoReason: 4 task types × 4 different metric names inside `scores{}`
- BioSafety, DataInterp: `score` at result top-level, `scores{}` is empty
- All others: metrics inside `scores{}`

### Infrastructure

| Item | Status |
|------|--------|
| Version | 0.3.1 |
| Tests | 365 passing |
| CLI | `bioeval run / inventory / compare / judge-pack / adapt / validate-adapter / demo` |
| Seed support | `--seed 42 --temperature 0.0 --judge-temperature 0.0` |
| Caching | SQLite-based (timeout=10s, write-resilient) |
| Adapters | LAB-Bench, BioProBench, BioLP-Bench |
| Statistical | Bootstrap CI, Wilcoxon, permutation test, Bonferroni/BH correction |
| Contamination | 80/20 public/private split + 3 canary tasks |
| Provenance | EvalTask.source / .validator fields |

---

## Competitive Landscape (as of 2026-02)

| Benchmark | Scale | Focus | BioEval Differentiator |
|-----------|-------|-------|----------------------|
| BioProBench (2025) | 556K tasks | Protocol QA only | BioEval: 9-dimensional, not just protocols |
| BixBench (2025) | 50 scenarios | Agentic code execution | BioEval: reasoning, not code execution |
| BioLP-Bench (2025) | ~100 protocols | Protocol error detection | BioEval: broader (causal, design, safety, debate) |
| LAB-Bench (2024) | 2,457 MCQ | Factual recall | BioEval: open-ended reasoning, not MCQ |
| CauSciBench (2025) | — | Causal inference (general) | BioEval: biology-specific causal reasoning |

**BioEval's confirmed unique contributions:**
1. Multi-dimensional (9 components) biology LLM evaluation
2. Experimental design critique (DesignCheck) — no other benchmark
3. Biology-specific adversarial robustness
4. Calibration in biological context (only 1.2% of biomedical AI evaluations measure this — JAMA 2025)
5. Multi-agent debate for biology
6. Integrated open-ended + quantitative scoring

**Key reference:** MIT Media Lab (2025) showed LLMs now exceed expert performance on factual biology benchmarks → validates the shift to reasoning-based evaluation.

---

## Publication Venues

| Venue | Format | Deadline | Fit |
|-------|--------|----------|-----|
| **NeurIPS 2026 D&B** | 9 pages + unlimited refs | ~May 2026 | Best fit. Requires HF + Croissant |
| **KDD 2026 D&B** | New track + AI for Sciences | Early 2026 | Good fit, first year = more receptive |
| **Bioinformatics (Oxford)** | Application Note, 4 pages | Rolling | Fast priority claim |
| **Nature Methods** | Registered Report or Article | Rolling | Prestige, slow review |
| **ISMB 2026** | Proceedings | ~Feb 2026 | Bioinformatics community |

**Recommended strategy:** Bioinformatics Application Note (fast, 4-6 weeks) + NeurIPS 2026 D&B full paper (3-4 months).

---

## Roadmap

### Phase 1: Accuracy First (1 week) — COMPLETE

**Goal:** All public-facing numbers match code reality. Weak components diagnosed.

| # | Task | Status | Result |
|---|------|:------:|--------|
| 1.1 | Fix task counts | DONE | README/STATUS.md/HTML/consistency-check all corrected to 178 base, 301 unique |
| 1.2 | DesignCheck precision | DONE | **Root cause: scoring bug.** Precision matching too strict (exact type match required). Fix: added flaw-type alias map + lowered term threshold 2→1. Needs re-evaluation to see impact. |
| 1.3 | Debate composite | DONE | **Root cause: 70% genuine model weakness (16% outcome accuracy) + 30% scoring bug.** `dissent_preservation` always 1.0 (zero variance, no minority agents). Fix: replaced with `reasoning_quality` in composite formula. New estimated mean: 0.380. |
| 1.4 | Score field unification | DONE | `docs/SCORE_FIELD_MAPPING.md` created. BioSafety/DataInterp store score at top-level (not in `scores{}`). ProtoReason has 4 different metrics by task type. |

**Phase 1 side-findings:**
- ProtoReason raw data has 17 items (3 protocols × 3 types) but only 2 types implemented (ordering + missing_step). 3rd type never coded. Technical debt, not blocking.
- `check_release_consistency.py` rewritten to use `load_tasks()` counts instead of raw data arithmetic.
- All existing results (`sonnet_all_9components.json`) use old scoring. Must re-run in Phase 2.

### Phase 1.5: Expert Review Hardening (2026-02-28) — COMPLETE

**Goal:** Address issues from 4-perspective expert review (statistical, biological, SW, benchmark design).

| # | Task | Status | Result |
|---|------|:------:|--------|
| 1.5.1 | Python 3.9 compat | DONE | `from __future__ import annotations` in 32 files |
| 1.5.2 | LLM Judge error handling | DONE | score=None on parse failure, timeout, XML delimiters |
| 1.5.3 | CLI temperature flags | DONE | `--temperature`, `--judge-temperature` with metadata recording |
| 1.5.4 | SQLite resilience | DONE | timeout=10s, cache write try-except |
| 1.5.5 | Statistical corrections | DONE | permutation zero-diff guard, Bonferroni/BH correction |
| 1.5.6 | Per-component weighting | DONE | `overall_per_component` equal-weighted aggregation |
| 1.5.7 | Calibration hallucination | DONE | Fabricated entity detection, partial_knowledge hardening |
| 1.5.8 | Canary contamination | DONE | 3 fingerprint tasks + `check_canary_contamination()` |
| 1.5.9 | EvalTask provenance | DONE | `source`, `validator` fields |
| 1.5.10 | Sensitivity analysis | DONE | `scripts/sensitivity_analysis.py` |
| 1.5.11 | Reproduction manifest | DONE | `docs/REPRODUCTION_MANIFEST.md` |
| 1.5.12 | Test coverage | DONE | 299→365 tests (+66) |

### Phase 2: Credibility (3–4 weeks)

**Goal:** Multi-model comparison, statistical rigor, judge validation.

**Prerequisite:** Phase 1 + 1.5 hardening complete. Claude re-run with fixed scoring done. New scoring includes calibration hallucination defense, per-component weighting, and multiple comparison correction.

| # | Task | Detail | Deliverable |
|---|------|--------|-------------|
| 2.0 | Claude re-run (seed 42) | **DONE.** Results: `results/phase2_claude_sonnet4_seed42.json`. 172/178 scored. Overall: 0.727. | Updated baseline JSON ✓ |
| 2.1 | GPT-4o evaluation | Run seeds 42, 123, 456. OpenAI API key available (`~/.api_keys`). | 3 result JSON files |
| 2.2 | Open-source model | DeepSeek or Llama 3 70B via API. Keys available (`~/.api_keys`). 3 seeds. | 3 result JSON files |
| 2.3 | Claude 3× repeat | Seeds 123, 456 (seed 42 done in 2.0). | 2 additional result JSON files |
| 2.4 | Statistical analysis | Module **DONE** (bootstrap CI, Wilcoxon, permutation, Cohen's d, Hedges' g, Bonferroni/BH). Integrate with CLI `compare` command. | Statistics table + significance |
| 2.5 | Judge validation | `bioeval judge-pack` CLI working. 2+ domain experts. Cohen's κ ≥ 0.5 target. | Judge validation report |
| 2.6 | 3-model comparison table | Component × Model with CIs + per-component weighting. Radar chart. | Main results table for paper |

**Post-2.0 note:** After re-run, expect DesignCheck F1 to improve (alias matching); Debate composite to drop to ~0.380 (honest score). README and HTML Preliminary Results table should be updated with 2.0 results, but final update deferred to 3.7.

**Debate framing strategy:** Mean ~0.38 is a legitimate finding. Frame as: "Multi-agent debate does not reliably improve outcome accuracy for biology reasoning tasks (16% correct), despite high reasoning quality in individual arguments. This challenges assumptions about debate-as-evaluation." This is a publishable negative result.

### Phase 3: Publishable (2–3 weeks)

**Goal:** Meet all venue-specific requirements.

| # | Task | Detail | Deliverable |
|---|------|--------|-------------|
| 3.1 | HuggingFace dataset | Upload tasks + results to HF. Include dataset card. Use `bioeval inventory --json` output as base. | HF dataset URL |
| 3.2 | Croissant metadata | Generate Croissant JSON-LD (required for NeurIPS 2026 D&B). Tools: `mlcroissant` Python package. | croissant.json |
| 3.3 | Datasheet for Datasets | Gebru et al. template: motivation, composition, collection, preprocessing, uses, distribution, maintenance | datasheet.md |
| 3.4 | Ethics statement | Dual-use risk (BioSafety component tests safety *judgment*, not bypass capabilities). Data provenance. LLM judge limitations. | ethics section |
| 3.5 | Reproducibility checklist | NeurIPS reproducibility checklist filled | checklist.md |
| 3.6 | Data contamination | Analyze whether benchmark tasks appear in model training data. Methods: canary strings, membership inference, novelty analysis. Note: expert-curated tasks (not scraped from web) reduce contamination risk. | contamination report |
| 3.7 | Demo + README + HTML final | Update README results table with Phase 2 re-run scores. Update HTML `bioeval_overview.html` results section with 3-model comparison. Update hero stats if needed. | Final README + HTML |

**Note on score field consistency:** BioSafety and DataInterp currently store `score` at result top-level instead of inside `scores{}`. Consider unifying before HF upload (Phase 3.1) for cleaner schema. See `docs/SCORE_FIELD_MAPPING.md`.

### Phase 4 (Optional): BioAmbiguity Component

**Goal:** Novel contribution — context-dependent biological reasoning (45 planned tasks).

| # | Task | Detail |
|---|------|--------|
| 4.1 | Task design | 6 axes: tissue-specificity, developmental stage, dose-response, genetic background, environmental context, temporal dynamics |
| 4.2 | Ground truth | Multi-dimensional rubric (not binary) |
| 4.3 | Implementation | Evaluator + scorer + tests |
| 4.4 | Evaluation | Run on 3 models, integrate into comparison |

---

## Critical Path

```
Phase 1 (Week 1) ✓ COMPLETE
  ├── 1.1 Fix counts ✓
  ├── 1.2 DesignCheck scoring fix ✓
  ├── 1.3 Debate scoring fix ✓
  └── 1.4 Score field mapping ✓
                                                        │
Phase 2 (Weeks 2–5)                                     ▼
  ├── 2.0 Claude re-run seed=42 (fixed scoring) ──────┐ FIRST
  │                                                     ▼
  ├── 2.1 GPT-4o runs (3 seeds) ──────────────────────┐
  ├── 2.2 Open-source runs (3 seeds) ─────────────────│ parallel
  ├── 2.3 Claude seeds 123, 456 ─────────────────────│
  │                                                     ▼
  ├── 2.4 Statistical analysis ────────────────────────┐
  ├── 2.5 Judge validation (start recruiting NOW) ─────│ after runs
  └── 2.6 Comparison table + score updates ───────────┘
                                                        │
Phase 3 (Weeks 6–8)                                     ▼
  ├── 3.1–3.2 HuggingFace + Croissant ───────────────┐
  ├── 3.3–3.5 Datasheet + Ethics + Checklist ─────────│ parallel
  ├── 3.6 Contamination analysis ─────────────────────│
  └── 3.7 Final README + HTML (with 3-model data) ───┘
                                                        │
                                                        ▼
                                              Submit (Week 9–10)
```

**Bottlenecks:**
1. Phase 2.0 must complete before 2.1–2.3 to establish fixed-scoring baseline
2. Phase 2.5 (judge validation) requires external expert time — start recruiting immediately
3. Phase 3.7 depends on all Phase 2 results being finalized

---

## Reviewer Expectations (2025–2026 standards)

| Requirement | Standard | BioEval Status |
|-------------|----------|:--------------:|
| Multi-model (3+ families) | Claude + GPT + open-source | Planned (Phase 2) |
| Statistical significance | Bootstrap CI + Wilcoxon + Bonferroni/BH | **Module done** (Phase 1.5), apply in Phase 2 |
| Judge validation | Cohen's κ ≥ 0.5 | Planned (Phase 2) |
| Multiple runs | ≥ 3 seeds per model | Planned (Phase 2) |
| Persistent hosting | HuggingFace | Planned (Phase 3) |
| Croissant metadata | Required for NeurIPS | Planned (Phase 3) |
| Datasheet | Gebru et al. | Planned (Phase 3) |
| Ethics statement | Dual-use, limitations | Planned (Phase 3) |
| Data contamination | Canary tasks + novelty analysis | **Canary done** (Phase 1.5), analysis in Phase 3 |
| Reproducibility | Seed, model pins, CLI, temperature | **Done** (Phase 1.5, `REPRODUCTION_MANIFEST.md`) |
| Sensitivity analysis | Weight perturbation, threshold sweep | **Done** (Phase 1.5, `scripts/sensitivity_analysis.py`) |
| Cost transparency | Per-run estimates | Done |
| Score field documentation | Per-component metric mapping | Done (Phase 1) |
| Release consistency | Automated count verification | Done (Phase 1) |
| Python 3.9-3.12 compat | CI green across versions | **Done** (Phase 1.5, 32 files) |

---

## References

- Anthropic Bloom (2025.12): Open-source behavioral evaluation framework. Spearman 0.86 with human scores.
- Anthropic RSP v3.0 (2026.02): CBRN capability thresholds updated.
- BioProBench (2025.05): 556K protocol tasks, arXiv:2505.07889.
- BixBench (2025.03): Agentic biology evaluation, arXiv:2503.00096.
- MIT Media Lab (2025): LLMs outperform experts on biology benchmarks.
- JAMA (2025): Only 1.2% of biomedical AI evaluations measure calibration.
- NeurIPS 2025 D&B: Croissant metadata required, 25% acceptance rate.
- KDD 2026: New D&B track + AI for Sciences track, Jeju, August 2026.
