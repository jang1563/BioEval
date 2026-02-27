"""
Debate-specific biomedical tasks for multi-agent evaluation.

25 tasks across 5 categories, each designed for structured debate:
- Variant Interpretation (5): ACMG/ClinVar variant classification
- Differential Diagnosis (5): clinical scenario-based diagnosis
- Experimental Critique (5): experimental design attack/defense
- Evidence Synthesis (5): conflicting study reconciliation
- Mechanism Dispute (5): competing biological mechanism debate
"""

from dataclasses import dataclass, field
from enum import Enum


class DebateTaskType(Enum):
    VARIANT_INTERPRETATION = "variant_interpretation"
    DIFFERENTIAL_DIAGNOSIS = "differential_diagnosis"
    EXPERIMENTAL_CRITIQUE = "experimental_critique"
    EVIDENCE_SYNTHESIS = "evidence_synthesis"
    MECHANISM_DISPUTE = "mechanism_dispute"


DIFFICULTY_WEIGHTS = {"easy": 1.0, "medium": 1.5, "hard": 2.0}


@dataclass
class DebateTask:
    """A biomedical scenario designed for multi-agent debate."""

    id: str
    task_type: DebateTaskType
    scenario: str
    context: str
    answer_options: list[str]
    ground_truth: dict
    difficulty: str
    domain: str
    adversarial_positions: list[str] = field(default_factory=list)


# =============================================================================
# VARIANT INTERPRETATION (5 tasks)
# =============================================================================

_VARIANT_TASKS = [
    DebateTask(
        id="debate_vi_001",
        task_type=DebateTaskType.VARIANT_INTERPRETATION,
        scenario=(
            "A 45-year-old woman with family history of breast cancer has genetic testing "
            "revealing BRCA2 c.7397T>C (p.Val2466Ala). ClinVar has conflicting interpretations. "
            "The variant is in the DNA-binding domain, allele frequency 0.0003 in gnomAD, "
            "computational predictors split (SIFT: tolerated; PolyPhen-2: possibly damaging; "
            "CADD: 22.5). Functional assays are unavailable. "
            "Classify this variant using ACMG/AMP criteria."
        ),
        context="ACMG/AMP 5-tier classification: pathogenic, likely pathogenic, VUS, likely benign, benign.",
        answer_options=["pathogenic", "likely_pathogenic", "VUS", "likely_benign", "benign"],
        ground_truth={
            "classification": "VUS",
            "reasoning": (
                "PM2 (rare in population) and PP3 (some computational support) favor pathogenicity, "
                "but BP4 (SIFT tolerated) and absence of functional data or segregation data "
                "prevent stronger classification. Insufficient criteria met for either "
                "pathogenic or benign."
            ),
            "key_criteria": ["PM2", "PP3", "BP4", "insufficient", "VUS", "functional"],
        },
        difficulty="hard",
        domain="genetics",
        adversarial_positions=["pathogenic", "likely_benign"],
    ),
    DebateTask(
        id="debate_vi_002",
        task_type=DebateTaskType.VARIANT_INTERPRETATION,
        scenario=(
            "A pediatric patient with developmental delay has whole exome sequencing showing "
            "a de novo MECP2 c.473C>T (p.Thr158Met) variant. This variant is absent from "
            "gnomAD, is recurrent in Rett syndrome databases (>50 affected individuals), "
            "and has been functionally validated to impair MeCP2 binding to methylated DNA. "
            "Classify this variant."
        ),
        context="ACMG/AMP criteria. De novo status confirmed by trio sequencing.",
        answer_options=["pathogenic", "likely_pathogenic", "VUS", "likely_benign", "benign"],
        ground_truth={
            "classification": "pathogenic",
            "reasoning": (
                "PS2 (de novo, confirmed), PS4 (recurrent in >50 affected), "
                "PM2 (absent from controls), PP3 (computational), PS3 (functional evidence). "
                "Multiple strong/moderate criteria met for pathogenic."
            ),
            "key_criteria": ["PS2", "de novo", "PS4", "recurrent", "PM2", "PS3", "functional", "pathogenic"],
        },
        difficulty="easy",
        domain="genetics",
        adversarial_positions=["likely_pathogenic", "VUS"],
    ),
    DebateTask(
        id="debate_vi_003",
        task_type=DebateTaskType.VARIANT_INTERPRETATION,
        scenario=(
            "Targeted sequencing in a healthy 30-year-old identifies TP53 c.743G>A "
            "(p.Arg248Gln) — a known Li-Fraumeni hotspot mutation. However, the VAF "
            "is only 2%, suggesting possible clonal hematopoiesis of indeterminate "
            "potential (CHIP). Does this finding represent a germline pathogenic variant "
            "or somatic CHIP? What clinical management is appropriate?"
        ),
        context=(
            "TP53 R248Q is a well-characterized gain-of-function mutation. "
            "CHIP prevalence increases with age but is unusual at age 30."
        ),
        answer_options=[
            "germline_pathogenic",
            "somatic_CHIP",
            "needs_confirmation",
        ],
        ground_truth={
            "classification": "needs_confirmation",
            "reasoning": (
                "Low VAF (2%) is atypical for germline but possible if mosaic. "
                "Age 30 is unusual for CHIP. Requires skin fibroblast or buccal "
                "confirmation to distinguish germline vs somatic. Clinical significance "
                "differs dramatically between germline Li-Fraumeni and somatic CHIP."
            ),
            "key_criteria": [
                "VAF",
                "mosaic",
                "CHIP",
                "germline",
                "confirmation",
                "fibroblast",
                "buccal",
                "Li-Fraumeni",
            ],
        },
        difficulty="hard",
        domain="genetics",
        adversarial_positions=["germline_pathogenic", "somatic_CHIP"],
    ),
    DebateTask(
        id="debate_vi_004",
        task_type=DebateTaskType.VARIANT_INTERPRETATION,
        scenario=(
            "A pharmacogenomics panel reveals CYP2D6 *4/*10 genotype in a patient "
            "starting tamoxifen for ER+ breast cancer. CYP2D6*4 is a null allele and "
            "*10 has reduced function. The patient asks whether to switch to an "
            "aromatase inhibitor. How should this pharmacogenomic result be interpreted?"
        ),
        context=(
            "CPIC guidelines classify CYP2D6 metabolizer status based on activity score. "
            "*4 = 0.0, *10 = 0.25-0.5. Activity score <1.0 indicates intermediate metabolizer."
        ),
        answer_options=[
            "switch_to_AI",
            "continue_tamoxifen",
            "intermediate_metabolizer_consider_switch",
        ],
        ground_truth={
            "classification": "intermediate_metabolizer_consider_switch",
            "reasoning": (
                "Activity score 0.25-0.5 (intermediate metabolizer). CPIC recommends "
                "considering alternative endocrine therapy for intermediate/poor metabolizers. "
                "Not an absolute contraindication but reduced endoxifen levels expected."
            ),
            "key_criteria": [
                "activity score",
                "intermediate metabolizer",
                "endoxifen",
                "CPIC",
                "alternative",
                "aromatase inhibitor",
            ],
        },
        difficulty="medium",
        domain="pharmacogenomics",
        adversarial_positions=["switch_to_AI", "continue_tamoxifen"],
    ),
    DebateTask(
        id="debate_vi_005",
        task_type=DebateTaskType.VARIANT_INTERPRETATION,
        scenario=(
            "Trio exome identifies a hemizygous ATRX c.6253A>G (p.Ile2085Val) variant "
            "in a boy with intellectual disability and alpha-thalassemia. The variant is "
            "absent from gnomAD males, REVEL score 0.72, and the mother is a carrier. "
            "A similarly affected maternal uncle was never tested. Classify this variant."
        ),
        context="X-linked gene. ATRX syndrome features intellectual disability with alpha-thalassemia.",
        answer_options=["pathogenic", "likely_pathogenic", "VUS", "likely_benign", "benign"],
        ground_truth={
            "classification": "likely_pathogenic",
            "reasoning": (
                "PM2 (absent from gnomAD males), PP3 (REVEL 0.72), PP1 (co-segregation: "
                "carrier mother, potentially affected uncle), PP4 (phenotype highly specific "
                "for ATRX). Combined moderate + supporting criteria reach likely pathogenic."
            ),
            "key_criteria": [
                "PM2",
                "PP3",
                "PP1",
                "co-segregation",
                "PP4",
                "X-linked",
                "hemizygous",
                "likely_pathogenic",
            ],
        },
        difficulty="medium",
        domain="genetics",
        adversarial_positions=["pathogenic", "VUS"],
    ),
]


# =============================================================================
# DIFFERENTIAL DIAGNOSIS (5 tasks)
# =============================================================================

_DIAGNOSIS_TASKS = [
    DebateTask(
        id="debate_dd_001",
        task_type=DebateTaskType.DIFFERENTIAL_DIAGNOSIS,
        scenario=(
            "A 55-year-old male presents with fatigue, splenomegaly, and WBC 85,000/uL. "
            "Peripheral smear shows left shift with all stages of myeloid maturation, "
            "2% blasts, basophilia (5%). No Auer rods. LDH elevated. "
            "Molecular testing pending. Most likely diagnosis?"
        ),
        context="Key differentials: CML, CMML, atypical CML, MPN with leukocytosis.",
        answer_options=["CML", "CMML", "atypical_CML", "AML"],
        ground_truth={
            "classification": "CML",
            "reasoning": (
                "Classic CML presentation: extreme leukocytosis with full myeloid "
                "maturation, low blast percentage, basophilia, splenomegaly. "
                "BCR-ABL1 testing would confirm. CMML typically has monocytosis, "
                "atypical CML lacks basophilia, and AML requires >=20% blasts."
            ),
            "key_criteria": [
                "BCR-ABL1",
                "basophilia",
                "myeloid maturation",
                "blasts",
                "splenomegaly",
                "CML",
            ],
        },
        difficulty="easy",
        domain="hematology",
        adversarial_positions=["CMML", "atypical_CML"],
    ),
    DebateTask(
        id="debate_dd_002",
        task_type=DebateTaskType.DIFFERENTIAL_DIAGNOSIS,
        scenario=(
            "A 28-year-old woman presents with bilateral hilar lymphadenopathy, "
            "erythema nodosum, and non-caseating granulomas on transbronchial biopsy. "
            "ACE level elevated. However, she also has hypercalcemia (Ca 11.5) and "
            "recent travel to the Ohio River Valley. TB skin test negative. "
            "Most likely diagnosis?"
        ),
        context=(
            "Key differentials: sarcoidosis, histoplasmosis, tuberculosis, lymphoma. "
            "Ohio River Valley is endemic for Histoplasma capsulatum."
        ),
        answer_options=["sarcoidosis", "histoplasmosis", "tuberculosis", "lymphoma"],
        ground_truth={
            "classification": "sarcoidosis",
            "reasoning": (
                "Classic triad: bilateral hilar LAD + erythema nodosum + non-caseating "
                "granulomas with elevated ACE. Hypercalcemia occurs in sarcoidosis via "
                "1-alpha-hydroxylase in granulomas. While histoplasmosis can cause "
                "granulomas and hilar LAD, erythema nodosum + elevated ACE + "
                "non-caseating (not necrotic) granulomas favor sarcoidosis."
            ),
            "key_criteria": [
                "non-caseating",
                "ACE",
                "erythema nodosum",
                "bilateral hilar",
                "hypercalcemia",
                "1-alpha-hydroxylase",
                "sarcoidosis",
            ],
        },
        difficulty="medium",
        domain="pulmonology",
        adversarial_positions=["histoplasmosis", "lymphoma"],
    ),
    DebateTask(
        id="debate_dd_003",
        task_type=DebateTaskType.DIFFERENTIAL_DIAGNOSIS,
        scenario=(
            "A 65-year-old presents with progressive symmetric polyarthritis of small "
            "joints (MCP, PIP), morning stiffness >1 hour, RF positive (titer 1:160), "
            "anti-CCP positive. However, X-rays show erosions AND tophi-like deposits. "
            "Serum uric acid is 9.2 mg/dL. Is this RA, gout, or coexistent disease?"
        ),
        context="Both RA and gout can coexist. Dual-energy CT can distinguish tophi from erosions.",
        answer_options=["rheumatoid_arthritis", "gout", "coexistent_RA_and_gout"],
        ground_truth={
            "classification": "coexistent_RA_and_gout",
            "reasoning": (
                "Strong serologic evidence for RA (high-titer RF + anti-CCP). "
                "However, tophi-like deposits with elevated uric acid suggest "
                "concurrent tophaceous gout. Coexistence is underdiagnosed. "
                "DECT would confirm urate crystal deposits."
            ),
            "key_criteria": [
                "anti-CCP",
                "RF",
                "tophi",
                "uric acid",
                "coexistent",
                "DECT",
                "dual-energy",
                "both",
            ],
        },
        difficulty="hard",
        domain="rheumatology",
        adversarial_positions=["rheumatoid_arthritis", "gout"],
    ),
    DebateTask(
        id="debate_dd_004",
        task_type=DebateTaskType.DIFFERENTIAL_DIAGNOSIS,
        scenario=(
            "A 40-year-old man with sudden onset severe headache (thunderclap), "
            "neck stiffness, photophobia, and normal head CT obtained 8 hours after onset. "
            "Lumbar puncture shows xanthochromia and elevated RBC count (consistent across "
            "tubes). Should this be managed as subarachnoid hemorrhage despite negative CT?"
        ),
        context=(
            "CT sensitivity for SAH decreases with time: ~98% at 6h, ~93% at 12h. "
            "LP with xanthochromia is considered confirmatory when CT is negative."
        ),
        answer_options=["SAH_confirmed", "traumatic_tap", "further_imaging_needed"],
        ground_truth={
            "classification": "SAH_confirmed",
            "reasoning": (
                "Thunderclap headache + meningismus + xanthochromia + consistent RBC "
                "across tubes = SAH until proven otherwise. CT sensitivity drops after "
                "6 hours. Xanthochromia distinguishes SAH from traumatic tap. "
                "CTA/DSA should follow to identify aneurysm."
            ),
            "key_criteria": [
                "xanthochromia",
                "thunderclap",
                "consistent RBC",
                "CT sensitivity",
                "CTA",
                "aneurysm",
                "SAH",
            ],
        },
        difficulty="medium",
        domain="neurology",
        adversarial_positions=["traumatic_tap", "further_imaging_needed"],
    ),
    DebateTask(
        id="debate_dd_005",
        task_type=DebateTaskType.DIFFERENTIAL_DIAGNOSIS,
        scenario=(
            "A 3-year-old with recurrent sinopulmonary infections, low IgG and IgA, "
            "normal IgM, absent isohemagglutinins, and <2% CD19+ B cells on flow cytometry. "
            "Genetic testing shows BTK mutation. However, the patient has tonsillar tissue "
            "visible on exam. Does this exclude X-linked agammaglobulinemia (XLA)?"
        ),
        context=(
            "Classic XLA features absent/near-absent B cells and absent lymphoid tissue. "
            "BTK mutations have variable expressivity."
        ),
        answer_options=["XLA_confirmed", "not_XLA_due_to_tonsils", "hypomorphic_XLA"],
        ground_truth={
            "classification": "hypomorphic_XLA",
            "reasoning": (
                "BTK mutation is definitive for XLA diagnosis regardless of tonsil presence. "
                "Hypomorphic BTK mutations allow residual B cell development and some "
                "lymphoid tissue. Absent isohemagglutinins and very low B cells confirm "
                "functional XLA. Tonsil presence does not exclude diagnosis."
            ),
            "key_criteria": [
                "BTK",
                "hypomorphic",
                "residual",
                "isohemagglutinins",
                "CD19",
                "B cells",
                "XLA",
            ],
        },
        difficulty="hard",
        domain="immunology",
        adversarial_positions=["XLA_confirmed", "not_XLA_due_to_tonsils"],
    ),
]


# =============================================================================
# EXPERIMENTAL CRITIQUE (5 tasks)
# =============================================================================

_CRITIQUE_TASKS = [
    DebateTask(
        id="debate_ec_001",
        task_type=DebateTaskType.EXPERIMENTAL_CRITIQUE,
        scenario=(
            "A CRISPR knockout study claims gene X is essential for tumor growth based on: "
            "1) 90% growth reduction in KO vs WT in vitro (n=3), "
            "2) single sgRNA targeting exon 3, "
            "3) no rescue experiment, "
            "4) Western blot showing protein loss. "
            "Is this sufficient evidence for essentiality?"
        ),
        context="CRISPR KO standards: multiple sgRNAs, rescue experiments, off-target analysis.",
        answer_options=["sufficient", "insufficient", "partially_sufficient"],
        ground_truth={
            "classification": "insufficient",
            "reasoning": (
                "Major flaws: single sgRNA (off-target effects not controlled), "
                "no rescue experiment (cannot prove specificity), n=3 is minimal, "
                "no in vivo validation. Need >=2 independent sgRNAs, rescue with "
                "sgRNA-resistant cDNA, and off-target analysis."
            ),
            "key_criteria": [
                "single sgRNA",
                "off-target",
                "rescue",
                "specificity",
                "multiple sgRNAs",
                "in vivo",
                "insufficient",
            ],
        },
        difficulty="easy",
        domain="molecular_biology",
        adversarial_positions=["sufficient", "partially_sufficient"],
    ),
    DebateTask(
        id="debate_ec_002",
        task_type=DebateTaskType.EXPERIMENTAL_CRITIQUE,
        scenario=(
            "An RCT reports a new antibiotic reduces mortality by 30% (p=0.04) in sepsis "
            "patients. However: 1) the trial was stopped early for benefit at interim analysis, "
            "2) the control arm used an outdated standard of care, "
            "3) the primary endpoint was changed mid-trial from 28-day to 14-day mortality, "
            "4) the sponsor funded the study. Should this trial change clinical practice?"
        ),
        context="CONSORT guidelines for RCT reporting. Early stopping inflates treatment effect.",
        answer_options=["practice_changing", "not_practice_changing", "needs_confirmation"],
        ground_truth={
            "classification": "not_practice_changing",
            "reasoning": (
                "Multiple red flags: early stopping inflates effect size (Bayesian correction "
                "needed), endpoint change is a major integrity concern, outdated comparator "
                "makes efficacy non-comparative to current practice. Sponsor bias risk. "
                "Needs independent confirmatory trial with current standard of care."
            ),
            "key_criteria": [
                "early stopping",
                "inflated effect",
                "endpoint change",
                "outdated comparator",
                "sponsor bias",
                "confirmatory trial",
            ],
        },
        difficulty="medium",
        domain="clinical_trials",
        adversarial_positions=["practice_changing", "needs_confirmation"],
    ),
    DebateTask(
        id="debate_ec_003",
        task_type=DebateTaskType.EXPERIMENTAL_CRITIQUE,
        scenario=(
            "A scRNA-seq study claims to identify a novel immune cell subtype based on: "
            "1) a distinct cluster in UMAP, "
            "2) 50 differentially expressed genes, "
            "3) no validation by flow cytometry or FISH, "
            "4) data from a single donor, "
            "5) 3,000 cells sequenced. "
            "Is this a genuine novel cell type?"
        ),
        context=(
            "scRNA-seq clustering can produce artifacts from technical variation, "
            "batch effects, and doublets. Validation with orthogonal methods is standard."
        ),
        answer_options=["genuine_novel_type", "likely_artifact", "needs_validation"],
        ground_truth={
            "classification": "needs_validation",
            "reasoning": (
                "UMAP clusters can be artifacts of resolution parameter, doublets, or "
                "ambient RNA. Single donor prevents generalizability assessment. "
                "No orthogonal validation (flow, FISH, spatial transcriptomics). "
                "50 DE genes is meaningful but not proof without protein-level confirmation. "
                "Must validate in multiple donors with independent methods."
            ),
            "key_criteria": [
                "UMAP artifact",
                "doublets",
                "single donor",
                "orthogonal validation",
                "flow cytometry",
                "resolution",
                "generalizability",
            ],
        },
        difficulty="medium",
        domain="genomics",
        adversarial_positions=["genuine_novel_type", "likely_artifact"],
    ),
    DebateTask(
        id="debate_ec_004",
        task_type=DebateTaskType.EXPERIMENTAL_CRITIQUE,
        scenario=(
            "A drug company reports their CAR-T therapy achieves 85% complete response rate "
            "in relapsed DLBCL. The study: 1) enrolled 40 patients, 2) 8 patients died before "
            "response assessment and were excluded from analysis, 3) median follow-up 6 months, "
            "4) no intention-to-treat analysis presented. "
            "Is the 85% CR rate reliable?"
        ),
        context="FDA guidance requires intention-to-treat analysis. Excluding deaths inflates response rates.",
        answer_options=["reliable", "inflated", "needs_ITT_reanalysis"],
        ground_truth={
            "classification": "inflated",
            "reasoning": (
                "Excluding 8/40 (20%) deaths from denominator inflates CR rate. "
                "ITT analysis: 34/40 = 85% becomes at best 34/40 with 8 non-responders = "
                "worst case ~65% CR. Treatment-related mortality must be included. "
                "6-month follow-up is insufficient for durability assessment."
            ),
            "key_criteria": [
                "ITT",
                "intention-to-treat",
                "excluded deaths",
                "inflated",
                "denominator",
                "treatment-related mortality",
                "durability",
            ],
        },
        difficulty="medium",
        domain="oncology",
        adversarial_positions=["reliable", "needs_ITT_reanalysis"],
    ),
    DebateTask(
        id="debate_ec_005",
        task_type=DebateTaskType.EXPERIMENTAL_CRITIQUE,
        scenario=(
            "A microbiome study associates Bacteroides fragilis abundance with colorectal "
            "cancer risk (OR=3.2, p<0.001). Study design: cross-sectional, 200 CRC patients "
            "vs 200 healthy controls. Samples collected at diagnosis. Diet and antibiotic "
            "use not controlled. 16S rRNA V4 region used. "
            "Does this establish B. fragilis as a causal factor in CRC?"
        ),
        context="Microbiome studies: reverse causation, confounding by diet/medications, compositional bias.",
        answer_options=["causal_evidence", "association_only", "flawed_study"],
        ground_truth={
            "classification": "association_only",
            "reasoning": (
                "Cross-sectional design cannot establish causation (reverse causation "
                "possible — tumor may alter microbiome). No control for diet or antibiotics "
                "(major confounders). Sampling at diagnosis introduces disease-state bias. "
                "16S V4 has limited species resolution. Need longitudinal/prospective design "
                "with pre-diagnostic samples."
            ),
            "key_criteria": [
                "cross-sectional",
                "reverse causation",
                "confounders",
                "diet",
                "antibiotics",
                "longitudinal",
                "association",
            ],
        },
        difficulty="easy",
        domain="microbiology",
        adversarial_positions=["causal_evidence", "flawed_study"],
    ),
]


# =============================================================================
# EVIDENCE SYNTHESIS (5 tasks)
# =============================================================================

_SYNTHESIS_TASKS = [
    DebateTask(
        id="debate_es_001",
        task_type=DebateTaskType.EVIDENCE_SYNTHESIS,
        scenario=(
            "Two large meta-analyses on vitamin D supplementation and COVID-19 outcomes "
            "reach opposite conclusions:\n"
            "Study A (25 RCTs, n=10,000): 'No significant effect on hospitalization or "
            "mortality (RR=0.95, 95% CI: 0.82-1.10)'\n"
            "Study B (30 RCTs, n=12,000): 'Significant reduction in ICU admission "
            "(RR=0.65, 95% CI: 0.48-0.87)'\n"
            "How should clinicians interpret these conflicting results?"
        ),
        context="Meta-analyses differ in: included studies, outcome definitions, statistical methods.",
        answer_options=[
            "vitamin_D_beneficial",
            "vitamin_D_not_beneficial",
            "outcome_dependent",
        ],
        ground_truth={
            "classification": "outcome_dependent",
            "reasoning": (
                "Apparent conflict resolves when noting different outcomes: Study A assessed "
                "overall hospitalization/mortality, Study B focused on ICU admission. "
                "Vitamin D may reduce severity (ICU) without affecting overall mortality. "
                "Also note different study inclusion criteria. Both findings can be true. "
                "Recommend vitamin D for deficient patients, insufficient evidence for routine "
                "supplementation in replete individuals."
            ),
            "key_criteria": [
                "different outcomes",
                "ICU",
                "mortality",
                "deficient",
                "inclusion criteria",
                "severity",
                "both true",
            ],
        },
        difficulty="medium",
        domain="epidemiology",
        adversarial_positions=["vitamin_D_beneficial", "vitamin_D_not_beneficial"],
    ),
    DebateTask(
        id="debate_es_002",
        task_type=DebateTaskType.EVIDENCE_SYNTHESIS,
        scenario=(
            "Conflicting evidence on statin use in elderly (>75 years):\n"
            "ALLHAT-LLT subgroup: No benefit in >75 (HR=1.08 for all-cause mortality)\n"
            "PROSPER trial: Modest benefit in 70-82 year olds (HR=0.85 for CV events)\n"
            "CTT meta-analysis: Consistent benefit across all ages per mmol/L LDL reduction\n"
            "Recent observational study (n=300,000): Statin discontinuation in >75 associated "
            "with 33% increased MI risk.\n"
            "Should statins be prescribed for primary prevention in healthy 78-year-olds?"
        ),
        context="Frailty, polypharmacy, and remaining life expectancy affect risk-benefit.",
        answer_options=["prescribe", "do_not_prescribe", "individualize"],
        ground_truth={
            "classification": "individualize",
            "reasoning": (
                "Evidence is genuinely conflicting for primary prevention in >75. "
                "RCT evidence is limited (ALLHAT negative, PROSPER positive but mixed ages). "
                "CTT supports benefit but lumps primary/secondary prevention. "
                "Must individualize based on: life expectancy, frailty index, "
                "polypharmacy risk, patient preferences, and CV risk factors."
            ),
            "key_criteria": [
                "individualize",
                "life expectancy",
                "frailty",
                "polypharmacy",
                "primary prevention",
                "risk-benefit",
                "patient preferences",
            ],
        },
        difficulty="hard",
        domain="cardiology",
        adversarial_positions=["prescribe", "do_not_prescribe"],
    ),
    DebateTask(
        id="debate_es_003",
        task_type=DebateTaskType.EVIDENCE_SYNTHESIS,
        scenario=(
            "Two studies on CRISPR base editing for sickle cell disease conflict:\n"
            "Study A (Nature, 2024): BCL11A enhancer editing in CD34+ cells achieves "
            "95% HbF induction, 0.01% off-target rate, durable at 12 months.\n"
            "Study B (Cell, 2024): Similar editing strategy shows 80% HbF induction but "
            "reports 0.5% off-target rate at a TP53-adjacent locus with potential "
            "oncogenic concern.\n"
            "Is BCL11A base editing safe for clinical translation?"
        ),
        context="Off-target editing rates depend on: assay sensitivity, cell type, delivery method.",
        answer_options=["safe_for_translation", "unsafe_needs_more_data", "conditionally_safe"],
        ground_truth={
            "classification": "conditionally_safe",
            "reasoning": (
                "Discrepancy likely due to different off-target detection methods "
                "(Study A: GUIDE-seq; Study B: CIRCLE-seq, more sensitive). "
                "TP53-adjacent off-target is a legitimate concern requiring long-term "
                "monitoring. Conditionally safe: proceed with enhanced monitoring, "
                "improved guide RNA design, and long-term follow-up protocols."
            ),
            "key_criteria": [
                "off-target detection",
                "GUIDE-seq",
                "CIRCLE-seq",
                "sensitivity",
                "TP53",
                "monitoring",
                "conditionally",
                "long-term",
            ],
        },
        difficulty="hard",
        domain="gene_therapy",
        adversarial_positions=["safe_for_translation", "unsafe_needs_more_data"],
    ),
    DebateTask(
        id="debate_es_004",
        task_type=DebateTaskType.EVIDENCE_SYNTHESIS,
        scenario=(
            "Conflicting evidence on aspirin for primary prevention of cardiovascular disease:\n"
            "ARRIVE (2018, n=12,546): No significant reduction in CV events (HR=0.96), "
            "increased GI bleeding\n"
            "ASCEND (2018, n=15,480, diabetics): 12% reduction in CV events offset by "
            "29% increase in major bleeding\n"
            "ASPREE (2018, n=19,114, elderly): No CV benefit, higher mortality (unexpected)\n"
            "Should aspirin be used for primary CV prevention in a 60-year-old diabetic "
            "with 10-year ASCVD risk of 15%?"
        ),
        context="AHA/ACC 2019 guidelines give aspirin a weak recommendation for select patients.",
        answer_options=["recommend_aspirin", "do_not_recommend", "shared_decision_making"],
        ground_truth={
            "classification": "shared_decision_making",
            "reasoning": (
                "For this specific patient: moderate CV risk (15%) and diabetes suggest "
                "potential benefit, but bleeding risk must be weighed. All three trials "
                "show marginal or no net benefit. AHA/ACC recommend shared decision-making "
                "for ages 40-70 with higher ASCVD risk. Contraindicated if bleeding risk "
                "factors present. Must discuss with patient."
            ),
            "key_criteria": [
                "shared decision",
                "bleeding risk",
                "net benefit",
                "ASCVD risk",
                "diabetes",
                "AHA",
                "individualize",
            ],
        },
        difficulty="medium",
        domain="cardiology",
        adversarial_positions=["recommend_aspirin", "do_not_recommend"],
    ),
    DebateTask(
        id="debate_es_005",
        task_type=DebateTaskType.EVIDENCE_SYNTHESIS,
        scenario=(
            "Debate on liquid biopsy (ctDNA) for early cancer detection:\n"
            "PATHFINDER study: Multi-cancer early detection test detected 1.4% of "
            "asymptomatic participants with cancer. PPV 38%, but 62% were stage I-III.\n"
            "Critics argue: lead-time bias, overdiagnosis, high false positive burden, "
            "cost-effectiveness not demonstrated.\n"
            "Supporters argue: mortality reduction potential, early stage detection "
            "enables curative treatment.\n"
            "Is population-level ctDNA screening justified?"
        ),
        context="Screening criteria: Wilson-Jungner principles, NNT/NNS considerations.",
        answer_options=["justified_now", "not_justified", "justified_for_high_risk_only"],
        ground_truth={
            "classification": "justified_for_high_risk_only",
            "reasoning": (
                "General population screening premature: PPV 38% means 62% false positives "
                "leading to unnecessary workup. No mortality reduction data yet (RCT ongoing). "
                "However, high-risk populations (strong family history, cancer predisposition "
                "syndromes) have higher pre-test probability, improving PPV. "
                "Need RCT mortality data before population-level implementation."
            ),
            "key_criteria": [
                "PPV",
                "false positive",
                "overdiagnosis",
                "mortality reduction",
                "high-risk",
                "pre-test probability",
                "RCT",
                "Wilson-Jungner",
            ],
        },
        difficulty="hard",
        domain="oncology",
        adversarial_positions=["justified_now", "not_justified"],
    ),
]


# =============================================================================
# MECHANISM DISPUTE (5 tasks)
# =============================================================================

_MECHANISM_TASKS = [
    DebateTask(
        id="debate_md_001",
        task_type=DebateTaskType.MECHANISM_DISPUTE,
        scenario=(
            "Two competing hypotheses for metformin's anti-cancer effects:\n"
            "Hypothesis A: Direct AMPK activation reduces mTOR signaling and inhibits "
            "cell proliferation.\n"
            "Hypothesis B: Indirect effect via reduced circulating insulin levels "
            "(insulin is a mitogen for cancer cells).\n"
            "Which mechanism is more likely to be clinically relevant?"
        ),
        context=(
            "Metformin achieves ~10-40 uM plasma concentration. AMPK activation in vitro "
            "requires ~1-5 mM. Epidemiological studies show ~30% cancer risk reduction in diabetics."
        ),
        answer_options=["direct_AMPK", "indirect_insulin", "both_mechanisms"],
        ground_truth={
            "classification": "indirect_insulin",
            "reasoning": (
                "Critical pharmacokinetic argument: therapeutic metformin levels (10-40 uM) "
                "are 50-100x lower than concentrations needed for AMPK activation in vitro "
                "(1-5 mM). In vivo AMPK activation may occur in hepatocytes (portal vein "
                "concentrations higher) but not in peripheral tumors. Insulin reduction at "
                "therapeutic doses is well-documented. Epidemiological benefit more consistent "
                "with systemic insulin reduction than direct tumor effect."
            ),
            "key_criteria": [
                "pharmacokinetic",
                "concentration",
                "uM",
                "mM",
                "insulin",
                "mitogen",
                "portal vein",
                "hepatocyte",
            ],
        },
        difficulty="medium",
        domain="pharmacology",
        adversarial_positions=["direct_AMPK", "both_mechanisms"],
    ),
    DebateTask(
        id="debate_md_002",
        task_type=DebateTaskType.MECHANISM_DISPUTE,
        scenario=(
            "Debate on the primary mechanism of immune checkpoint inhibitor (ICI) resistance "
            "in microsatellite-stable (MSS) colorectal cancer:\n"
            "Hypothesis A: Low tumor mutational burden (TMB) produces insufficient neoantigens.\n"
            "Hypothesis B: Immunosuppressive tumor microenvironment (TME) with TGF-beta-driven "
            "exclusion prevents T cell infiltration.\n"
            "Which mechanism is the better therapeutic target?"
        ),
        context=("MSS CRC has TMB ~4 mut/Mb vs MSI-H ~40 mut/Mb. " "Some MSS tumors with high TMB still resist ICI."),
        answer_options=["low_TMB", "immunosuppressive_TME", "TME_is_better_target"],
        ground_truth={
            "classification": "TME_is_better_target",
            "reasoning": (
                "While low TMB contributes, TME is the more actionable target because: "
                "1) some MSS tumors have adequate neoantigens but still resist ICI, "
                "2) TGF-beta inhibition in preclinical models converts cold to hot tumors, "
                "3) TMB cannot be therapeutically increased but TME can be remodeled. "
                "Combination strategies targeting TME (anti-TGF-beta, anti-VEGF) show promise."
            ),
            "key_criteria": [
                "TME",
                "TGF-beta",
                "T cell exclusion",
                "cold tumor",
                "neoantigen",
                "actionable",
                "combination",
                "remodel",
            ],
        },
        difficulty="hard",
        domain="immuno_oncology",
        adversarial_positions=["low_TMB", "immunosuppressive_TME"],
    ),
    DebateTask(
        id="debate_md_003",
        task_type=DebateTaskType.MECHANISM_DISPUTE,
        scenario=(
            "Two models for Alzheimer's disease pathogenesis:\n"
            "Model A: Amyloid cascade — A-beta accumulation triggers tau pathology and "
            "neurodegeneration. Supported by genetics (APP, PSEN1/2 mutations).\n"
            "Model B: Neuroinflammation-first — Microglial dysregulation (TREM2, CD33 risk "
            "alleles) drives neurodegeneration, with amyloid as a secondary marker.\n"
            "Given recent anti-amyloid drug trial results (lecanemab: 27% slowing, "
            "aducanumab: controversial), which model better explains the disease?"
        ),
        context="Genetic evidence supports both: APP mutations (amyloid), TREM2/CD33 (inflammation).",
        answer_options=["amyloid_cascade", "neuroinflammation_first", "integrated_model"],
        ground_truth={
            "classification": "integrated_model",
            "reasoning": (
                "Neither model alone explains all evidence. Lecanemab shows amyloid removal "
                "slows decline (supports amyloid involvement) but 27% is modest (amyloid is "
                "not the whole story). TREM2 risk alleles and microglial dysfunction are "
                "independent risk factors. Integrated model: amyloid initiates, "
                "neuroinflammation amplifies, tau spreads. Both are therapeutic targets."
            ),
            "key_criteria": [
                "integrated",
                "amyloid",
                "TREM2",
                "microglia",
                "tau",
                "lecanemab",
                "modest",
                "both targets",
            ],
        },
        difficulty="medium",
        domain="neuroscience",
        adversarial_positions=["amyloid_cascade", "neuroinflammation_first"],
    ),
    DebateTask(
        id="debate_md_004",
        task_type=DebateTaskType.MECHANISM_DISPUTE,
        scenario=(
            "Debate on ferroptosis vs apoptosis as the primary cell death mechanism in "
            "ischemia-reperfusion injury of the kidney:\n"
            "Evidence for ferroptosis: GPX4 knockout sensitizes to renal IRI, "
            "lipid peroxidation markers elevated, ferrostatin-1 is protective.\n"
            "Evidence for apoptosis: caspase activation detected, Bcl-2 overexpression "
            "is protective, TUNEL staining positive.\n"
            "Which cell death pathway is the primary therapeutic target?"
        ),
        context=(
            "Ferroptosis and apoptosis can occur simultaneously. "
            "TUNEL staining is not specific to apoptosis (also marks other forms of DNA damage)."
        ),
        answer_options=["ferroptosis_primary", "apoptosis_primary", "both_pathways"],
        ground_truth={
            "classification": "ferroptosis_primary",
            "reasoning": (
                "In renal IRI specifically, ferroptosis appears dominant: "
                "1) ferrostatin-1 provides more robust protection than caspase inhibitors "
                "in multiple models, 2) GPX4 is the critical determinant, "
                "3) TUNEL positivity is non-specific and can indicate ferroptotic DNA damage, "
                "4) lipid peroxidation is the early initiating event. "
                "Apoptosis may be secondary. Ferroptosis inhibition is the better target."
            ),
            "key_criteria": [
                "ferroptosis",
                "GPX4",
                "ferrostatin",
                "lipid peroxidation",
                "TUNEL non-specific",
                "more protective",
                "primary",
            ],
        },
        difficulty="hard",
        domain="nephrology",
        adversarial_positions=["apoptosis_primary", "both_pathways"],
    ),
    DebateTask(
        id="debate_md_005",
        task_type=DebateTaskType.MECHANISM_DISPUTE,
        scenario=(
            "Mechanism of GLP-1 receptor agonist (semaglutide) weight loss:\n"
            "Hypothesis A: Central appetite suppression via hypothalamic GLP-1R activation.\n"
            "Hypothesis B: Delayed gastric emptying reduces food intake mechanically.\n"
            "Hypothesis C: Direct effect on reward circuits (nucleus accumbens) reducing "
            "food-seeking behavior.\n"
            "Which mechanism is most important for the observed 15-20% weight loss?"
        ),
        context=(
            "Semaglutide crosses BBB. Weight loss exceeds what gastric emptying alone "
            "would predict. Brain imaging shows reduced food-cue reactivity."
        ),
        answer_options=["central_appetite", "gastric_emptying", "reward_circuits", "all_three"],
        ground_truth={
            "classification": "central_appetite",
            "reasoning": (
                "Central hypothalamic appetite suppression is the dominant mechanism: "
                "1) weight loss magnitude (15-20%) far exceeds gastric emptying effect "
                "(which attenuates over time due to adaptation), "
                "2) semaglutide crosses BBB and activates hypothalamic POMC/CART neurons, "
                "3) brain-restricted GLP-1R KO ablates weight loss in animal models. "
                "Reward circuit effects contribute but are downstream of hypothalamic signaling. "
                "Gastric emptying is an early, transient effect."
            ),
            "key_criteria": [
                "hypothalamic",
                "POMC",
                "BBB",
                "central",
                "gastric emptying attenuates",
                "brain-restricted KO",
                "dominant",
                "appetite suppression",
            ],
        },
        difficulty="medium",
        domain="endocrinology",
        adversarial_positions=["gastric_emptying", "reward_circuits"],
    ),
]


# =============================================================================
# COMBINED TASK LIST
# =============================================================================

DEBATE_TASKS: list[DebateTask] = _VARIANT_TASKS + _DIAGNOSIS_TASKS + _CRITIQUE_TASKS + _SYNTHESIS_TASKS + _MECHANISM_TASKS


# =============================================================================
# TASK-LEVEL OUTCOME SCORING
# =============================================================================


def score_debate_task_outcome(task: DebateTask, final_position: str, final_answer: str = "") -> dict:
    """Score the outcome of a debate against ground truth.

    Returns a dict with:
      - position_correct: bool
      - accuracy: float (0-1, with partial credit)
      - reasoning_quality: float (0-1, key_criteria coverage)
      - difficulty_weight: float
    """
    gt = task.ground_truth
    gt_classification = gt.get("classification", "")
    key_criteria = gt.get("key_criteria", [])

    # Position matching (case-insensitive)
    pos_lower = (final_position or "").lower().strip()
    gt_lower = gt_classification.lower().strip()

    position_correct = pos_lower == gt_lower

    # Partial credit for near-matches
    if position_correct:
        accuracy = 1.0
    else:
        accuracy = _partial_credit_map(pos_lower, gt_lower, task.answer_options)

    # Reasoning quality: check key_criteria in final_answer
    text = (final_answer or "").lower()
    if key_criteria:
        matched = sum(1 for kc in key_criteria if kc.lower() in text)
        reasoning_quality = matched / len(key_criteria)
    else:
        reasoning_quality = 0.0

    return {
        "position_correct": position_correct,
        "accuracy": round(accuracy, 3),
        "reasoning_quality": round(reasoning_quality, 3),
        "difficulty_weight": DIFFICULTY_WEIGHTS.get(task.difficulty, 1.0),
    }


def _partial_credit_map(pos: str, gt: str, options: list[str]) -> float:
    """Give partial credit for close-but-wrong answers."""
    # Adjacency in ordered classifications
    _ordered_groups = [
        ["pathogenic", "likely_pathogenic", "vus", "likely_benign", "benign"],
    ]
    for group in _ordered_groups:
        group_lower = [o.lower() for o in group]
        if gt in group_lower and pos in group_lower:
            distance = abs(group_lower.index(gt) - group_lower.index(pos))
            if distance == 1:
                return 0.5
            if distance == 2:
                return 0.25
            return 0.0
    return 0.0
