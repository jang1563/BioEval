# BioEval Literature Survey: LLM Evaluation Benchmarks for Biology

> Date: 2026-02-24
> Sources: arXiv, bioRxiv, PubMed, GitHub, HuggingFace
> Purpose: Competitive landscape analysis for BioEval improvement

---

## 1. Biology-Specific Benchmarks (Direct Competitors)

### 1.1 LAB-Bench (FutureHouse, Jul 2024)
- **Paper**: [arXiv:2407.10362](https://arxiv.org/abs/2407.10362)
- **GitHub**: https://github.com/Future-House/LAB-Bench (~94 stars)
- **HuggingFace**: https://huggingface.co/datasets/futurehouse/lab-bench
- **Tasks**: 2,400+ MCQs across 8 categories (LitQA2, DbQA, SuppQA, SeqQA, FigQA, TableQA, ProtocolQA, CloningScenarios)
- **Key finding**: All models deeply underperform humans on all tasks. Claude 3.5 Sonnet narrowly exceeds humans only on TableQA.
- **BioEval overlap**: HIGH — practical biology evaluation, but MCQ-only, no causal/adversarial/calibration
- **Borrow**: Contamination detection (private test set), HuggingFace distribution

### 1.2 BixBench (FutureHouse, Feb 2025)
- **Paper**: [arXiv:2503.00096](https://arxiv.org/abs/2503.00096)
- **GitHub**: https://github.com/Future-House/BixBench
- **Tasks**: 53 scenarios, ~300 questions, real-world bioinformatics analysis
- **Key finding**: Frontier models achieve only 17% accuracy on open-answer questions
- **BioEval overlap**: MODERATE — agent-focused (code execution), complementary
- **Borrow**: Using real published notebooks as ground truth, LLM-as-judge for open answers

### 1.3 BioProBench (May 2025)
- **Paper**: [arXiv:2505.07889](https://arxiv.org/abs/2505.07889)
- **GitHub**: https://github.com/YuyangSunshine/bioprotocolbench
- **HuggingFace**: https://huggingface.co/datasets/GreatCaptainNemo/BioProBench
- **Tasks**: 556K structured instances, 1,000 test per task (QA, ordering, error correction, generation, reasoning)
- **Key finding**: General comprehension high, but drops on reasoning, quantitative precision, safety awareness
- **BioEval overlap**: MODERATE — overlaps with ProtoReason specifically
- **Borrow**: Massive scale from automated generation, 5-task decomposition

### 1.4 Genome-Bench (May 2025)
- **Paper**: [arXiv:2505.19501](https://arxiv.org/abs/2505.19501)
- **Tasks**: 3,332 MCQs from 10+ years of CRISPR forum archives
- **Key finding**: RL from scientific discussions improves model by >15%
- **BioEval overlap**: HIGH — troubleshooting and reasoning from real discourse
- **Borrow**: Source questions from real scientific discussions

### 1.5 VCT — Virology Capabilities Test (Apr 2025)
- **Paper**: [arXiv:2504.16137](https://arxiv.org/abs/2504.16137)
- **Tasks**: 322 multimodal MCQs, "Google-proof" tacit knowledge
- **Key finding**: OpenAI o3 achieves 43.8%, outperforming 94% of expert virologists
- **BioEval overlap**: MODERATE — domain-specific but design philosophy relevant
- **Borrow**: "Google-proof" design, tacit knowledge testing

### 1.6 CGBench — Clinical Genetics (Oct 2025, NeurIPS 2025)
- **Paper**: [arXiv:2510.11985](https://arxiv.org/abs/2510.11985)
- **Key finding**: Models hallucinate even when correctly classifying evidence
- **BioEval overlap**: HIGH — evidence interpretation, hallucination detection
- **Borrow**: Correct classification ≠ correct understanding (test mechanism quality)

### 1.7 SciHorizon-Gene (Jan 2026)
- **Paper**: [arXiv:2601.12805](https://arxiv.org/abs/2601.12805)
- **Tasks**: 540K+ questions covering 190K+ human genes
- **Key finding**: Fully automatic evaluation with hallucination metrics
- **Borrow**: Hallucination-specific metrics, fully automatic evaluation

### 1.8 SciGym — Systems Biology Dry Lab (Jul 2025)
- **Paper**: [arXiv:2507.02083](https://arxiv.org/abs/2507.02083)
- **GitHub**: https://github.com/h4duan/SciGym
- **Tasks**: 350 SBML systems, iterative experiment design
- **Key finding**: All models decline significantly with complexity
- **BioEval overlap**: Complementary — simulated experiments vs real data ground truth
- **Borrow**: Complexity scaling analysis, SBML integration

### 1.9 BioAgentBench (Jan 2026)
- **GitHub**: https://github.com/bioagent-bench/bioagent-bench
- **Tasks**: Bioinformatics pipelines with stress tests (corrupted inputs, decoy files, prompt bloat)
- **Borrow**: Perturbation-based robustness testing

---

## 2. Multi-Domain Scientific Benchmarks

### 2.1 ATLAS (Nov 2025)
- **Paper**: [arXiv:2511.14366](https://arxiv.org/abs/2511.14366)
- **Tasks**: ~800 problems across 7 fields, PhD-level, open-ended
- **Borrow**: LLM-as-judge panel, contamination-resistant design

### 2.2 SDE — Scientific Discovery Evaluation (Dec 2025)
- **Paper**: [arXiv:2512.15567](https://arxiv.org/abs/2512.15567)
- **Key finding**: Consistent underperformance vs general benchmarks, diminishing returns from scaling
- **Borrow**: Two-phase (question-level + project-level) evaluation

### 2.3 SciEval (AAAI 2024)
- **GitHub**: https://github.com/OpenDFM/SciEval
- **HuggingFace**: https://huggingface.co/datasets/OpenDFM/SciEval
- **Tasks**: ~18K objective questions + subjective, multi-level
- **Borrow**: Dynamic question generation to prevent data leakage

### 2.4 SciKnowEval
- **GitHub**: https://github.com/HICAI-ZJU/SciKnowEval
- **Tasks**: ~70K problems, 5 progressive levels (memory → application)
- **Borrow**: Progressive difficulty levels

### 2.5 GPQA (Nov 2023)
- **Paper**: [arXiv:2311.12022](https://arxiv.org/abs/2311.12022)
- **GitHub**: https://github.com/idavidrein/gpqa
- **Tasks**: 448 MCQs, "Google-proof"
- **Key finding**: Biology subset being saturated (Justen 2025)
- **Borrow**: Expert calibration baseline

---

## 3. Causal Reasoning, Calibration, Adversarial

### 3.1 CausalProbe (NeurIPS 2024)
- **Paper**: [arXiv:2506.21215](https://arxiv.org/abs/2506.21215)
- **Key finding**: LLMs show only "shallow (level-1) causal reasoning" from parametric knowledge
- **BioEval relevance**: CRITICAL — directly validates BioEval's causal reasoning focus

### 3.2 UQ Benchmark (NeurIPS 2024)
- **Paper**: [arXiv:2401.12794](https://arxiv.org/abs/2401.12794)
- **Key finding**: Higher accuracy models may exhibit LOWER certainty. Instruction fine-tuning increases uncertainty.
- **BioEval relevance**: CRITICAL — counterintuitive calibration patterns

### 3.3 LLM-as-Judge Surveys
- [arXiv:2411.15594](https://arxiv.org/abs/2411.15594) (Nov 2024)
- [arXiv:2412.05579](https://arxiv.org/abs/2412.05579) (Dec 2024)
- **Key concerns**: Prompt template sensitivity, self-bias, positional bias, verbosity bias
- **BioEval relevance**: Must address if using LLM-as-Judge

### 3.4 Justen 2025 Meta-Analysis
- **Paper**: [arXiv:2505.06108](https://arxiv.org/abs/2505.06108)
- **Key finding**: Biology benchmarks being rapidly saturated. Top VCT performance 4x in ~2 years.
- **BioEval relevance**: CRITICAL — BioEval must be designed to resist saturation

---

## 4. Calibration in Biomedical AI (PubMed)

### 4.1 JAMA Meta-Review (Jan 2025)
- **DOI**: [10.1001/jama.2024.21700](https://doi.org/10.1001/jama.2024.21700)
- 519 studies reviewed: Only **1.2% measured calibration**, 84.2% used accuracy only
- **Implication**: BioEval's calibration component addresses a massive gap

### 4.2 Flex-ECE Calibration Study (JAMIA Open, Jul 2025)
- **DOI**: [10.1093/jamiaopen/ooaf058](https://doi.org/10.1093/jamiaopen/ooaf058)
- 9 LLMs across BLURB: Out-of-the-box calibration 24-47% error
- Self-consistency (27.3%) >> Verbal confidence (42.0%)
- **Implication**: BioEval should adopt Flex-ECE, not rely on verbal confidence alone

### 4.3 Inverse Confidence Paradox (JMIR, May 2025)
- **DOI**: [10.2196/66917](https://doi.org/10.2196/66917)
- 12 LLMs: Worse models show HIGHER confidence (r=-0.40, P=.001)
- **Implication**: Calibration testing is essential for reliable biology AI

### 4.4 Gene Set Function Calibration (Nature Methods, Nov 2024)
- **DOI**: [10.1038/s41592-024-02525-x](https://doi.org/10.1038/s41592-024-02525-x)
- GPT-4: 87% correctly zero confidence on random gene sets
- Other LLMs: **Falsely confident** on random/meaningless data
- **Implication**: Directly validates BioEval's calibration approach

### 4.5 CARDBiomedBench (bioRxiv, Jan 2025)
- **DOI**: [10.1101/2025.01.15.633272](https://doi.org/10.1101/2025.01.15.633272)
- 68K+ QA pairs; Claude-3.5 shows **excessive caution** (25% quality, 76% safety)
- GPT-4o shows **poor accuracy AND unsafe behavior** (37% quality, 31% safety)
- **Implication**: BioEval should measure hedging behavior (over-cautious vs reckless)

---

## 5. Context-Dependency and Biological Ambiguity (Key Gap)

### 5.1 CondMedQA (Feb 2025) — Closest Existing Work
- **Paper**: [arXiv:2602.17911](https://arxiv.org/abs/2602.17911)
- First benchmark for conditional multi-hop reasoning in biomedical QA
- 100 curated questions requiring context-gated reasoning
- **Gap**: Clinical focus only, not basic biology

### 5.2 HealthContradict (npj Digital Medicine)
- **DOI**: [10.1038/s41746-025-02336-0](https://doi.org/10.1038/s41746-025-02336-0)
- 920 instances of contradictory biomedical evidence
- **Gap**: Health claims only, not mechanistic biology

### 5.3 ConflictBank (NeurIPS 2024)
- 7.45M claim-evidence pairs, 553K QA pairs
- Three conflict types: misinformation, temporal, semantic
- **Gap**: Not biology-specific

### 5.4 rbio1 (CZI, bioRxiv 2025)
- **Paper**: [bioRxiv:2025.08.18.670981](https://www.biorxiv.org/content/10.1101/2025.08.18.670981v2)
- Uses biological world models as "soft verifiers" during RL training
- Key insight: "In biology, exact rules for formal verification are unavailable"
- **Implication**: BioEval should evaluate whether such training improves contextual reasoning

### 5.5 CONFIRMED GAP: No Existing Benchmark Tests
- Context-dependent gene function (TP53 tumor suppressor vs gain-of-function)
- Negative/null result interpretation (p=0.23 ≠ no effect)
- Conflicting evidence synthesis (autophagy dual role)
- Tissue-specific gene essentiality
- Temporal dynamics of biological function
- Dose-dependent biphasic responses (hormesis)

---

## 6. Competitive Landscape Matrix

| Benchmark | Knowledge | Reasoning | Causal | Calibration | Adversarial | Open-ended | Exp. Data | Context-Dep |
|-----------|:---------:|:---------:|:------:|:-----------:|:-----------:|:----------:|:---------:|:-----------:|
| **BioEval** | **Yes** | **Yes** | **Yes** | **Yes** | **Yes** | **Yes** | **DepMap/CMap** | **Planned** |
| LAB-Bench | Yes | Partial | No | No | No | No | Partial | No |
| BixBench | Yes | Yes | No | No | No | Yes | Real datasets | No |
| BioProBench | Yes | Yes | No | No | No | Partial | No | No |
| Genome-Bench | Yes | Yes | No | No | No | No | No | No |
| VCT | Yes | Partial | No | No | No | No | No | No |
| GPQA-Bio | Yes | Yes | No | No | No | No | No | No |
| ATLAS-Bio | Yes | Yes | No | No | No | Yes | No | No |
| SciGym | No | Yes | Partial | No | No | Yes | Simulated | No |
| CausalProbe | No | No | Yes | No | No | No | No | No |
| CondMedQA | Yes | Yes | No | No | No | No | No | Partial |
| HealthContradict | Yes | No | No | No | No | No | No | Partial |

---

## 7. BioEval's Unique Position (Gaps We Fill)

### Confirmed Unique Contributions:
1. **Experimental ground truth (DepMap/CMap)** — No other benchmark does this
2. **Causal reasoning in biology specifically** — CausalProbe is domain-agnostic
3. **Adversarial robustness for biology** — Only WMDP touches biosecurity, not reasoning robustness
4. **Calibration in biological contexts** — Only 1.2% of existing evaluations measure calibration
5. **Experimental design critique (DesignCheck)** — Completely novel
6. **Biological ambiguity/context-dependency** — Confirmed gap, no existing benchmark
7. **Integrated multi-dimensional evaluation** — No other combines all these

### Areas Where We're Outscaled:
- BioProBench: 556K tasks vs our ~98 (protocol reasoning)
- SciKnowEval: 70K tasks vs our ~98 (general science)
- SciHorizon-Gene: 540K questions (gene knowledge)
- LAB-Bench: 2,400 tasks with private test set

### Strategic Implication:
> BioEval should NOT compete on scale. Compete on **depth, novelty, and experimental grounding**.
> "100 tasks with DepMap ground truth + biological ambiguity evaluation" beats "70K factual recall questions"

---

## 8. Ideas to Adopt

### High Priority
| Idea | Source | Why |
|------|--------|-----|
| Private test set (20%) for contamination detection | LAB-Bench | Benchmarks are being saturated |
| HuggingFace dataset distribution | LAB-Bench, SciEval | Discoverability and standardization |
| Dynamic question generation | SciEval | Prevent data leakage |
| Fully automatic evaluation | SciHorizon-Gene | Reproducibility at scale |
| Flex-ECE calibration metric | JAMIA Open study | Better than standard ECE |
| Condition-gated reasoning framework | CondMedQA | For context-dependency evaluation |

### Medium Priority
| Idea | Source | Why |
|------|--------|-----|
| Complexity scaling analysis | SciGym | Characterize where models break |
| Cross-judge evaluation | LLM-as-Judge surveys | Mitigate judge self-bias |
| Citation frequency correlation | MoBiPlant | Detect training data bias |
| Real scientific discussions as source | Genome-Bench | Ecological validity |
| Perturbation-based stress tests | BioAgentBench | Beyond current adversarial |

### Avoid
| Mistake | Source |
|---------|--------|
| MCQ-only format (saturating quickly) | Justen 2025 |
| Static question banks (leak into training) | All benchmarks |
| Relying on verbal confidence only | Flex-ECE study |
| Scale without depth | SciKnowEval vs quality |
| Assuming CoT always helps | Justen 2025 |

---

## 9. Key References

### Must-Cite Papers
1. Justen 2025 — "LLMs Outperform Experts on Biology Benchmarks" [arXiv:2505.06108](https://arxiv.org/abs/2505.06108)
2. LAB-Bench — Laurent et al. 2024 [arXiv:2407.10362](https://arxiv.org/abs/2407.10362)
3. CausalProbe — Chi et al. 2024 [arXiv:2506.21215](https://arxiv.org/abs/2506.21215)
4. JAMA Meta-Review 2025 [10.1001/jama.2024.21700](https://doi.org/10.1001/jama.2024.21700)
5. Flex-ECE Calibration [10.1093/jamiaopen/ooaf058](https://doi.org/10.1093/jamiaopen/ooaf058)
6. Gene Set Calibration (Nature Methods) [10.1038/s41592-024-02525-x](https://doi.org/10.1038/s41592-024-02525-x)
7. CondMedQA [arXiv:2602.17911](https://arxiv.org/abs/2602.17911)
8. HealthContradict [10.1038/s41746-025-02336-0](https://doi.org/10.1038/s41746-025-02336-0)
9. rbio1 (CZI) [bioRxiv:2025.08.18.670981](https://www.biorxiv.org/content/10.1101/2025.08.18.670981v2)
10. BioProBench [arXiv:2505.07889](https://arxiv.org/abs/2505.07889)
