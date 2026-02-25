# BioEval New Component: Biological Ambiguity & Context-Dependency (BioAmbiguity)

> Date: 2026-02-24
> Status: Design Phase (Revised after Publication-Quality Review)
> Literature basis: See [LITERATURE_SURVEY.md](LITERATURE_SURVEY.md)
> Ground truth strategy: Revised — multi-dimensional rubric approach

---

## 1. Motivation

Biology is not a closed system. The same gene, same drug, and same pathway can produce entirely different outcomes depending on context. Current LLM benchmarks systematically avoid this problem:
- **GPQA**: Intentionally removes questions where experts disagree
- **MedQA**: Uses only multiple-choice questions with a single correct answer
- **LAB-Bench**: Measures factual accuracy only

**Confirmed gap (literature survey result)**: No existing benchmark systematically evaluates context-dependent biological reasoning.

Closest existing work:
- **CondMedQA** (Feb 2025): Conditional reasoning in clinical QA, 100 questions — clinical focus, not basic biology
- **HealthContradict**: Contradictory health claims — no mechanistic reasoning
- **ConflictBank** (NeurIPS 2024): General knowledge conflicts — not biology-specific

---

## 2. Component Architecture: 6 Evaluation Axes

### AXIS 1: ContextSwitch — Context-Dependent Gene Function

**Evaluates**: Whether the model gives a single context-free answer to "What does gene X do?" or appropriately considers biological context.

**Example task**:
```
Q: "A tumor harboring the TP53 R248W missense mutation shows high, stable
    expression of the protein. Is this consistent with loss-of-function?"
Expected: Must recognize gain-of-function possibility.
  Specific hotspot mutations (R248W, R273H) acquire neomorphic oncogenic activity.
  Simply answering "TP53 mutation = loss of tumor suppression" → FAIL.
```

**Data sources**:
- Gain-of-function mutation literature ([Nature Comms 2023](https://www.nature.com/articles/s41467-023-44239-2))
- DepMap tissue-specific essentiality
- ClinVar context-dependent annotations

**Task count**: 10 | **Difficulty**: Mixed

---

### AXIS 2: NullSense — Negative/Null Result Interpretation

**Evaluates**: Whether the model commits the error of equating "not statistically significant" with "no effect."

**Example task 1**:
```
Q: "Drug X was tested for inhibition of cell line Y proliferation. Result: p=0.23
    (n=3, t-test). Authors conclude: 'Drug X has no effect on cell line Y
    proliferation.' Is this conclusion valid?"
Expected: Must identify the logical error.
  - Non-significance ≠ evidence of no effect
  - Underpowered study (n=3) — low statistical power
  - Effect size and confidence intervals should be discussed
  - "Evidence of absence vs absence of evidence" distinction
```

**Example task 2**:
```
Q: "RNA-seq comparing WT vs KO: 0 DEGs at FDR<0.05.
    Can we conclude this gene has no transcriptional targets?"
Expected: Cannot draw this conclusion.
  - Sequencing depth and replicate count considerations
  - Post-transcriptional effects possible
  - Compensatory mechanisms
  - Condition-specific effects
```

**Task count**: 8 | **Difficulty**: Mixed

---

### AXIS 3: ConflictResolve — Contradictory Evidence Synthesis

**Evaluates**: Whether the model can identify contextual variables that explain apparently contradictory published findings.

**Example task**:
```
Q: "Paper A: Autophagy promotes tumor survival in established pancreatic cancer.
    Paper B: Autophagy deficiency accelerates tumor formation in a liver cancer mouse model.
    Are these results contradictory? Explain."
Expected: Recognize autophagy's dual role:
  - Early: Maintains genomic stability, limits oxidative stress → tumor suppression
  - Late: Metabolic adaptation, treatment resistance → tumor promotion
  Key variables: cancer stage, cancer type, genetic context
```

**Data sources**:
- Autophagy dual role ([FEBS Letters](https://febs.onlinelibrary.wiley.com/doi/10.1002/1873-3468.70060))
- Caveolin-1 ambiguity ([Mol Cancer 2025](https://doi.org/10.1186/s12943-025-02297-8))
- ROS in cancer (signaling vs damage)
- Wnt signaling in stem cells vs cancer

**Task count**: 8 | **Difficulty**: Hard

---

### AXIS 4: TissueContext — Cell Line/Tissue Specificity

**Evaluates**: Whether the model over-generalizes results from one experimental system to different biological contexts.

**Example task**:
```
Q: "Gene X was identified as essential in K562 (CML) CRISPR screen.
    A researcher wants to pursue it as a breast cancer therapeutic target.
    What should they consider?"
Expected:
  - Tissue-of-origin differences
  - Lineage dependency (BCR-ABL in K562)
  - Need for independent validation in breast cancer cell lines
  - DepMap lineage-specific essentiality differences
```

**Data sources**: DepMap (gene essentiality across 1,000+ cell lines), GDSC drug sensitivity, GTEx tissue expression

**Task count**: 8 | **Difficulty**: Medium-Hard

---

### AXIS 5: TemporalBiology — Temporal Dynamics

**Evaluates**: Understanding that biological functions change over development, disease progression, and treatment course.

**Example task**:
```
Q: "A tumor initially responsive to EGFR inhibitor progresses after 8 months.
    Biopsy shows the EGFR mutation is still present. Interpretation?"
Expected:
  - Acquired resistance mechanisms (T790M, MET amplification, histological transformation)
  - Tumor heterogeneity and evolution under selective pressure
  - "The drug stopped working on EGFR" is an inaccurate conclusion
```

**Task count**: 6 | **Difficulty**: Hard

---

### AXIS 6: DoseLogic — Dose-Dependency and Non-Linear Responses

**Evaluates**: Reasoning about biphasic responses, hormesis, and non-linear dose-response relationships.

**Example task 1**:
```
Q: "Low-dose methotrexate is an immunosuppressant for rheumatoid arthritis.
    High-dose methotrexate is a cytotoxic chemotherapy agent.
    How can the same drug serve opposite purposes?"
Expected:
  - Low dose: adenosine release, anti-inflammatory effect
  - High dose: folate antagonism, anti-proliferative effect
  - Biphasic pharmacology understanding
```

**Example task 2**:
```
Q: "0.1 Gy radiation shows reduced cancer incidence in some epidemiological studies.
    2 Gy clearly increases cancer risk. Evaluate."
Expected:
  - Discuss radiation hormesis hypothesis
  - LNT model vs hormetic model
  - Adaptive response mechanisms
  - Acknowledge scientific uncertainty (critically evaluate both sides)
```

**Data sources**: Hormesis literature ([PMC5354598](https://pmc.ncbi.nlm.nih.gov/articles/PMC5354598/)), pharmacology dose-response data

**Task count**: 5 | **Difficulty**: Medium-Hard

---

## 3. Scoring Strategy (Revised after Publication-Quality Review)

### Problem with Single-Score Approach
BioAmbiguity tasks are inherently ambiguous — there may not be a single "correct" answer. Using a single 0-3 score creates ground truth paradox: if the question is genuinely ambiguous, who decides the correct answer?

### Solution: Multi-Dimensional Rubric Scoring

For each BioAmbiguity task, score across 4 independent dimensions:

| Dimension | Scale | Method | Description |
|-----------|-------|--------|-------------|
| **Context Recognition** | 0/1 (binary) | Automated keyword check | Does the response acknowledge context-dependency? |
| **Variable Identification** | 0-N (checklist) | Automated set matching | How many of the required context variables are named? |
| **Mechanism Quality** | 1-5 (ordinal) | LLM-as-Judge with rubric | Quality of the mechanistic explanation |
| **Epistemic Calibration** | 0/1 (binary) | Automated pattern check | Does the response appropriately hedge/qualify? |

### Ground Truth Definition Per Task
```python
@dataclass
class BioAmbiguityGroundTruth:
    # Dimension 1: Context Recognition
    context_dependency_acknowledged: bool  # Must the response say "it depends"?

    # Dimension 2: Variable Identification (checklist)
    required_variables: list[str]  # Must-identify context variables
    optional_variables: list[str]  # Nice-to-have context variables
    minimum_required: int          # Minimum required variables to score >0

    # Dimension 3: Mechanism Quality (rubric)
    acceptable_mechanisms: list[str]     # Set of valid mechanism explanations
    unacceptable_simplifications: list[str]  # Explicit wrong answers

    # Dimension 4: Epistemic Calibration
    should_hedge: bool                   # Should the response qualify claims?
    overconfidence_patterns: list[str]   # Patterns that indicate overconfidence
```

### Example Ground Truth (TP53 R248W Task)
```python
BioAmbiguityGroundTruth(
    context_dependency_acknowledged=True,
    required_variables=[
        "specific mutation type (hotspot vs non-hotspot)",
        "protein stability/expression level",
        "gain-of-function vs loss-of-function distinction",
    ],
    optional_variables=[
        "dominant-negative effect",
        "tissue type",
        "co-occurring mutations",
    ],
    minimum_required=2,
    acceptable_mechanisms=[
        "R248W is a contact mutant that acquires neomorphic oncogenic activity",
        "Hotspot TP53 mutations can gain new protein-protein interactions",
        "Stabilized mutant p53 can activate transcription of oncogenic targets",
    ],
    unacceptable_simplifications=[
        "TP53 mutation means loss of tumor suppression",
        "All TP53 mutations are loss-of-function",
    ],
    should_hedge=True,
    overconfidence_patterns=[
        "always", "never", "all TP53 mutations", "definitely loss-of-function"
    ],
)
```

### Addressing the Judge Circularity Problem

**Problem**: BioAmbiguity evaluates whether LLMs can reason about context-dependency. If LLMs fail at this, how can they judge it?

**Solution**: Tiered scoring approach:
1. **Dimensions 1, 2, 4** (Context Recognition, Variable Identification, Epistemic Calibration): Scored via automated methods (keyword/pattern matching, set intersection) — NO LLM-as-Judge needed
2. **Dimension 3** (Mechanism Quality): LLM-as-Judge, BUT with mandatory human validation:
   - Minimum 20 tasks scored by both LLM-Judge and human expert
   - If LLM-Judge κ < 0.5 on BioAmbiguity: fall back to automated scoring only
   - Use stronger model as judge (e.g., Claude Opus 4) when evaluating weaker models

---

## 4. Cross-Cutting Scoring Dimensions

Applied to all axis responses as meta-evaluations:

### A. Epistemic Humility Score
- Does the response use "always/never" vs "in most studies/generally"?
- Does it distinguish epistemic uncertainty (model's ignorance) from aleatoric uncertainty (inherent biological variability)?
- Does it differentiate strength and quality of evidence?

### B. Contextual Specificity Score
- Does the response specify cell type, organism, disease stage, dose range, etc.?
- Does it voluntarily present relevant caveats without being prompted?

### C. Reasoning Transparency Score
- Does the response explain the **cause** of context-dependency mechanistically?
- Does it identify the key variables that determine the outcome?

---

## 5. Task Design Principles

### Format Mix
- **MCQ with "It depends" option**: Tests whether the model appropriately selects context-dependency
- **Free-response**: Rubric-based evaluation using multi-dimensional scoring
- **"Identify the error"**: Spot oversimplifications in given statements
- **Scenario-based**: Reason within a specified experimental context

### Expert Validation (Adapted from GPQA Model)
- Each task: created by PhD-level biologist, verified by second expert
- **Critical distinction from GPQA**: GPQA removes tasks where experts disagree; BioAmbiguity **preserves them** (expert disagreement signals genuine ambiguity)
- **IAA requirement**: κ ≥ 0.7 on the variable checklist and unacceptable simplification list
- Tasks with low IAA are revised, not silently included

### Contamination Prevention
- Source from recent literature (LiveBench strategy)
- Novel combinations of existing knowledge
- Private test set (20%) maintained

---

## 6. Target Task Count

| Axis | Tasks | Difficulty |
|------|-------|-----------|
| ContextSwitch | 10 | Mixed |
| NullSense | 8 | Mixed |
| ConflictResolve | 8 | Hard |
| TissueContext | 8 | Medium-Hard |
| TemporalBiology | 6 | Hard |
| DoseLogic | 5 | Medium-Hard |
| **Total** | **45** | |

After quality filtering (IAA, validation): expect ~35-45 tasks in final benchmark.

---

## 7. Implementation Priority

This component is built in **Phase 2b** (parallel with Phase 2 "Make it Credible"):
1. Phases 0-1: Stabilize existing components first
2. Phase 2b: Design and validate BioAmbiguity tasks
3. Phase 3: Analyze results and derive Key Findings

### Expected Key Finding (Pre-Registered Hypothesis):
> "Frontier LLMs achieve 85%+ on factual biology (MedQA), but drop to 40-60%
> when the same biological concepts require context-dependent reasoning.
> The gap is largest on ConflictResolve (synthesizing contradictory evidence)
> and NullSense (interpreting negative results)."

**Publication guardrail**: If this finding is NOT confirmed, report the actual result honestly. Negative results are still publishable as they characterize LLM capabilities.

---

## 8. Related Work Positioning

```
Existing benchmarks:
  CondMedQA (clinical context, 100Q)  →  BioAmbiguity goes deeper (basic biology, 6 axes)
  HealthContradict (health claims)     →  BioAmbiguity tests mechanistic reasoning
  ConflictBank (general knowledge)     →  BioAmbiguity is domain-specific with expert ground truth
  GPQA (removes ambiguity)             →  BioAmbiguity embraces it

Novel contributions:
  1. First benchmark for context-dependent BIOLOGICAL (not clinical) reasoning
  2. First systematic evaluation of null/negative result interpretation by LLMs
  3. First benchmark that tests dose-response reasoning (hormesis, biphasic)
  4. Epistemic vs aleatoric uncertainty distinction in biology evaluation
  5. Multi-dimensional rubric scoring that handles inherent ambiguity without forcing single correct answer
```

---

## 9. Limitations (Pre-Identified)

1. **Expert dependency**: Task quality depends on the expertise of creators and validators. Limited annotator pool may introduce bias.
2. **Cultural/linguistic scope**: All tasks in English, reflecting primarily Western biomedical literature.
3. **Evolving science**: Some "ambiguous" findings may become resolved as new research emerges. Version pinning mitigates but doesn't eliminate.
4. **LLM-Judge limitations**: Mechanism Quality scoring may not capture all nuances of expert evaluation. Human validation subset provides calibration but not elimination of judge bias.
5. **Small scale**: 45 tasks provides signal but limits statistical power for fine-grained subgroup analyses across all 6 axes.
