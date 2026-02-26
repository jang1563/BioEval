"""
Data Interpretation Evaluation Module

Tests whether LLMs can correctly interpret experimental data, perform
quantitative reasoning, and draw appropriate conclusions from biological
datasets. Covers the core analytical skills expected of research scientists.

Evaluates 5 dimensions:
1. qPCR Analysis — ΔΔCt calculations, efficiency, quality assessment
2. Dose-Response — IC50/EC50 estimation, curve interpretation
3. Statistical Test — Test selection, p-value interpretation, multiple comparisons
4. Survival Analysis — Kaplan-Meier, hazard ratios, Cox regression
5. Multi-Assay Integration — Cross-platform data reconciliation

This component is distinct from ProtoReason (procedural calculations) and
CausalBio (mechanism prediction) by focusing on interpreting structured
numerical datasets and applying statistical reasoning.
"""

import re
import math
from dataclasses import dataclass, field
from enum import Enum


class DataInterpType(Enum):
    """Types of data interpretation tasks."""
    QPCR_ANALYSIS = "qpcr_analysis"
    DOSE_RESPONSE = "dose_response"
    STATISTICAL_TEST = "statistical_test"
    SURVIVAL_ANALYSIS = "survival_analysis"
    MULTI_ASSAY = "multi_assay"


@dataclass
class DataInterpTask:
    """Single data interpretation task."""
    id: str
    interp_type: DataInterpType
    scenario: str                           # Context + question
    data_table: str                         # Structured data (text table)
    expected_answer: dict                   # Numerical answers + interpretation
    interpretation_points: list[str]        # Required interpretation elements
    common_mistakes: list[str]              # Mistakes to penalize
    difficulty: str                         # easy, medium, hard
    domain: str


DIFFICULTY_WEIGHTS = {"easy": 1.0, "medium": 1.5, "hard": 2.0}


# =============================================================================
# DATA INTERPRETATION TASKS — 25 tasks, 5 per type
# =============================================================================

DATA_INTERP_TASKS = [
    # ----- qPCR ANALYSIS (5 tasks) -----
    DataInterpTask(
        id="di_qpcr_001",
        interp_type=DataInterpType.QPCR_ANALYSIS,
        scenario=(
            "A researcher treated HeLa cells with Drug X for 24 hours and measured "
            "gene expression of VEGFA by qPCR. GAPDH was used as the reference gene. "
            "Using the ΔΔCt method, calculate the fold-change of VEGFA expression "
            "in treated vs. control cells and interpret the result."
        ),
        data_table=(
            "Sample          | Gene   | Ct (Rep1) | Ct (Rep2) | Ct (Rep3) | Mean Ct\n"
            "Control         | VEGFA  | 25.2      | 25.4      | 25.1      | 25.23\n"
            "Control         | GAPDH  | 18.1      | 18.3      | 18.0      | 18.13\n"
            "Drug X treated  | VEGFA  | 22.1      | 22.3      | 22.0      | 22.13\n"
            "Drug X treated  | GAPDH  | 18.2      | 18.0      | 18.1      | 18.10"
        ),
        expected_answer={
            "delta_ct_control": 7.10,
            "delta_ct_treated": 4.03,
            "delta_delta_ct": -3.07,
            "fold_change": 8.4,
            "direction": "upregulated",
        },
        interpretation_points=[
            "delta ct", "fold change", "upregulated", "2^",
            "gapdh", "reference", "biological replicate",
        ],
        common_mistakes=[
            "forgot to subtract reference gene",
            "used wrong direction for delta delta ct",
            "base 10 instead of base 2",
        ],
        difficulty="easy",
        domain="gene_expression",
    ),
    DataInterpTask(
        id="di_qpcr_002",
        interp_type=DataInterpType.QPCR_ANALYSIS,
        scenario=(
            "You generated a standard curve for a qPCR assay using 5 serial dilutions "
            "of a plasmid template (10-fold each). Calculate the PCR efficiency from "
            "the standard curve slope and assess whether the assay is acceptable."
        ),
        data_table=(
            "Log10(copy number) | Mean Ct\n"
            "7                  | 10.2\n"
            "6                  | 13.5\n"
            "5                  | 16.9\n"
            "4                  | 20.2\n"
            "3                  | 23.6"
        ),
        expected_answer={
            "slope": -3.35,
            "efficiency_pct": 98.8,
            "r_squared_approx": 0.999,
            "acceptable": True,
        },
        interpretation_points=[
            "slope", "efficiency", "10^(-1/slope)", "90%", "110%",
            "linear", "acceptable", "r-squared",
        ],
        common_mistakes=[
            "used wrong efficiency formula",
            "didn't check if efficiency is in 90-110% range",
            "confused slope sign",
        ],
        difficulty="medium",
        domain="gene_expression",
    ),
    DataInterpTask(
        id="di_qpcr_003",
        interp_type=DataInterpType.QPCR_ANALYSIS,
        scenario=(
            "A study used two reference genes (GAPDH and ACTB) for normalization. "
            "The data shows that GAPDH Ct varies between conditions but ACTB is stable. "
            "How should the researcher handle normalization, and what does this imply "
            "about reference gene validation?"
        ),
        data_table=(
            "Condition  | GAPDH Ct | ACTB Ct  | Target (TP53) Ct\n"
            "Control    | 18.5     | 20.1     | 24.3\n"
            "Hypoxia    | 21.2     | 20.3     | 22.1\n"
            "Serum-free | 16.8     | 20.0     | 25.7"
        ),
        expected_answer={
            "stable_reference": "ACTB",
            "unstable_reference": "GAPDH",
            "gapdh_variation": 4.4,
            "actb_variation": 0.3,
        },
        interpretation_points=[
            "gapdh", "unstable", "actb", "stable", "reference gene validation",
            "condition", "normalization", "misleading",
        ],
        common_mistakes=[
            "used gapdh without noting its instability",
            "averaged both reference genes without checking stability",
            "ignored reference gene variation",
        ],
        difficulty="medium",
        domain="gene_expression",
    ),
    DataInterpTask(
        id="di_qpcr_004",
        interp_type=DataInterpType.QPCR_ANALYSIS,
        scenario=(
            "Three biological replicates of control and treated cells were analyzed "
            "by qPCR. Calculate the mean fold-change with standard deviation and "
            "assess whether the difference is likely meaningful given the variability."
        ),
        data_table=(
            "Replicate | Control ΔCt | Treated ΔCt\n"
            "1         | 7.2         | 4.1\n"
            "2         | 6.8         | 5.8\n"
            "3         | 7.5         | 4.4"
        ),
        expected_answer={
            "mean_delta_ct_control": 7.17,
            "mean_delta_ct_treated": 4.77,
            "mean_ddct": -2.4,
            "mean_fold_change": 5.3,
            "variability_concern": True,
        },
        interpretation_points=[
            "fold change", "standard deviation", "variability", "replicate",
            "biological", "statistical", "confidence",
        ],
        common_mistakes=[
            "averaged fold-changes instead of delta ct values",
            "ignored the high variability in treated replicate 2",
            "claimed significant without proper statistical test",
        ],
        difficulty="hard",
        domain="gene_expression",
    ),
    DataInterpTask(
        id="di_qpcr_005",
        interp_type=DataInterpType.QPCR_ANALYSIS,
        scenario=(
            "A qPCR experiment shows the following data quality issues. Identify "
            "all problems and recommend corrective actions."
        ),
        data_table=(
            "Sample       | Target Ct (Rep1) | Target Ct (Rep2) | Target Ct (Rep3) | NTC Ct\n"
            "Control      | 24.5             | 24.8             | 24.3             | 35.2\n"
            "Treatment A  | 21.2             | 28.7             | 21.5             | 35.0\n"
            "Treatment B  | 38.1             | 37.5             | undetermined     | 35.1\n"
            "Notes: Melt curves show single peaks for all samples except Treatment B Rep3."
        ),
        expected_answer={
            "issues": [
                "Treatment A Rep2 is an outlier (>3 Ct from other reps)",
                "Treatment B Ct values near or beyond NTC (non-specific)",
                "Treatment B Rep3 undetermined + abnormal melt curve",
            ],
        },
        interpretation_points=[
            "outlier", "replicate", "ntc", "non-template", "melt curve",
            "non-specific", "primer dimer", "exclude", "repeat",
        ],
        common_mistakes=[
            "failed to notice Treatment A replicate outlier",
            "didn't compare Treatment B Ct to NTC",
            "ignored melt curve warning",
        ],
        difficulty="hard",
        domain="quality_control",
    ),

    # ----- DOSE-RESPONSE (5 tasks) -----
    DataInterpTask(
        id="di_dr_001",
        interp_type=DataInterpType.DOSE_RESPONSE,
        scenario=(
            "A cell viability assay was performed with Drug Y at 6 concentrations. "
            "Estimate the IC50 from this data and describe the dose-response relationship."
        ),
        data_table=(
            "Concentration (μM) | % Cell Viability (mean ± SD)\n"
            "0 (vehicle)        | 100.0 ± 3.2\n"
            "0.01               | 98.5 ± 4.1\n"
            "0.1                | 87.3 ± 5.0\n"
            "1.0                | 52.1 ± 3.8\n"
            "10                 | 18.4 ± 2.9\n"
            "100                | 5.2 ± 1.5"
        ),
        expected_answer={
            "ic50_range": [0.8, 1.5],
            "curve_shape": "sigmoidal",
            "max_inhibition": 94.8,
        },
        interpretation_points=[
            "ic50", "sigmoidal", "dose-response", "log",
            "viability", "inhibition", "concentration",
        ],
        common_mistakes=[
            "reported IC50 on linear scale without noting log relationship",
            "confused viability with inhibition",
        ],
        difficulty="easy",
        domain="pharmacology",
    ),
    DataInterpTask(
        id="di_dr_002",
        interp_type=DataInterpType.DOSE_RESPONSE,
        scenario=(
            "Two kinase inhibitors (Drug A and Drug B) were tested against the same "
            "cell line. Compare their potency and efficacy from the dose-response data."
        ),
        data_table=(
            "Concentration (nM) | Drug A (% inhibition) | Drug B (% inhibition)\n"
            "0                  | 0                     | 0\n"
            "1                  | 5                     | 15\n"
            "10                 | 22                    | 48\n"
            "100                | 55                    | 82\n"
            "1000               | 78                    | 88\n"
            "10000              | 82                    | 90"
        ),
        expected_answer={
            "drug_a_ic50_range": [50, 150],
            "drug_b_ic50_range": [5, 15],
            "more_potent": "Drug B",
            "similar_efficacy": True,
        },
        interpretation_points=[
            "potency", "efficacy", "ic50", "drug b", "more potent",
            "maximum", "plateau", "selectivity",
        ],
        common_mistakes=[
            "confused potency with efficacy",
            "failed to note both drugs reach similar max inhibition",
        ],
        difficulty="medium",
        domain="pharmacology",
    ),
    DataInterpTask(
        id="di_dr_003",
        interp_type=DataInterpType.DOSE_RESPONSE,
        scenario=(
            "The following dose-response data shows an unusual pattern. Identify "
            "the non-standard response and discuss possible explanations."
        ),
        data_table=(
            "Concentration (μM) | % Cell Viability\n"
            "0                  | 100\n"
            "0.001              | 105\n"
            "0.01               | 112\n"
            "0.1                | 118\n"
            "1.0                | 95\n"
            "10                 | 45\n"
            "100                | 12"
        ),
        expected_answer={
            "pattern": "hormesis/biphasic",
            "stimulatory_range": [0.001, 0.1],
            "inhibitory_range": [1.0, 100],
        },
        interpretation_points=[
            "hormesis", "biphasic", "stimulat", "low dose", "high dose",
            "u-shape", "j-shape", "non-monotonic",
        ],
        common_mistakes=[
            "ignored the low-dose stimulation",
            "assumed monotonic dose-response",
            "attributed stimulation to experimental error without justification",
        ],
        difficulty="hard",
        domain="pharmacology",
    ),
    DataInterpTask(
        id="di_dr_004",
        interp_type=DataInterpType.DOSE_RESPONSE,
        scenario=(
            "A candidate drug shows the following activity against cancer cells and "
            "normal cells. Assess the therapeutic index and suitability for further "
            "development."
        ),
        data_table=(
            "Concentration (μM) | Cancer Cell Viability (%) | Normal Cell Viability (%)\n"
            "0                  | 100                       | 100\n"
            "0.1                | 85                        | 98\n"
            "1.0                | 42                        | 92\n"
            "10                 | 8                         | 75\n"
            "100                | 2                         | 35"
        ),
        expected_answer={
            "cancer_ic50_range": [0.8, 2.0],
            "normal_ic50_range": [20, 50],
            "therapeutic_index_range": [10, 50],
            "assessment": "favorable",
        },
        interpretation_points=[
            "therapeutic index", "selectivity", "cancer", "normal",
            "ic50", "window", "safety margin",
        ],
        common_mistakes=[
            "calculated only cancer IC50 without comparing to normal",
            "didn't compute or estimate therapeutic index",
        ],
        difficulty="medium",
        domain="drug_development",
    ),
    DataInterpTask(
        id="di_dr_005",
        interp_type=DataInterpType.DOSE_RESPONSE,
        scenario=(
            "A cancer cell line developed resistance to Drug Z after 3 months of "
            "continuous exposure. Compare the dose-response curves of parental and "
            "resistant lines. Quantify the resistance shift."
        ),
        data_table=(
            "Concentration (nM) | Parental (% viability) | Resistant (% viability)\n"
            "0                  | 100                    | 100\n"
            "10                 | 75                     | 98\n"
            "100                | 35                     | 90\n"
            "1000               | 8                      | 55\n"
            "10000              | 2                      | 20\n"
            "100000             | 1                      | 5"
        ),
        expected_answer={
            "parental_ic50_range": [30, 80],
            "resistant_ic50_range": [800, 2000],
            "resistance_fold": [10, 50],
        },
        interpretation_points=[
            "resistance", "fold", "shift", "rightward", "ic50",
            "mechanism", "efflux", "target mutation", "bypass",
        ],
        common_mistakes=[
            "didn't quantify the fold-change in IC50",
            "failed to suggest resistance mechanisms",
        ],
        difficulty="hard",
        domain="oncology",
    ),

    # ----- STATISTICAL TEST (5 tasks) -----
    DataInterpTask(
        id="di_st_001",
        interp_type=DataInterpType.STATISTICAL_TEST,
        scenario=(
            "A researcher measured tumor volume in two groups of mice (treated vs. "
            "control, n=8 each). The data appears normally distributed with equal "
            "variances. Which statistical test should be used and why? Interpret the "
            "provided result."
        ),
        data_table=(
            "Group   | Mean (mm³) | SD (mm³) | n\n"
            "Control | 450        | 120      | 8\n"
            "Treated | 280        | 105      | 8\n"
            "\n"
            "Statistical output:\n"
            "  Two-sample t-test: t(14) = 3.01, p = 0.0094\n"
            "  95% CI for difference: [48.5, 291.5]"
        ),
        expected_answer={
            "correct_test": "two-sample t-test",
            "p_significant": True,
            "interpretation": "significant reduction",
            "effect_size": 170,
        },
        interpretation_points=[
            "t-test", "normal", "independent", "p < 0.05", "significant",
            "confidence interval", "difference", "reject null",
        ],
        common_mistakes=[
            "used paired t-test for independent groups",
            "reported p-value without interpreting the direction",
            "didn't mention confidence interval",
        ],
        difficulty="easy",
        domain="biostatistics",
    ),
    DataInterpTask(
        id="di_st_002",
        interp_type=DataInterpType.STATISTICAL_TEST,
        scenario=(
            "An experiment tested three drug concentrations (low, medium, high) plus "
            "vehicle control on cell proliferation. ANOVA was performed followed by "
            "post-hoc tests. Interpret the results."
        ),
        data_table=(
            "One-way ANOVA: F(3,20) = 8.42, p = 0.0008\n"
            "\n"
            "Tukey's HSD post-hoc (p-values):\n"
            "                | Vehicle | Low    | Medium | High\n"
            "Vehicle         | -       | 0.82   | 0.015  | 0.0003\n"
            "Low             | 0.82    | -      | 0.045  | 0.001\n"
            "Medium          | 0.015   | 0.045  | -      | 0.31\n"
            "High            | 0.0003  | 0.001  | 0.31   | -"
        ),
        expected_answer={
            "overall_significant": True,
            "vehicle_vs_low": "not significant",
            "vehicle_vs_medium": "significant",
            "vehicle_vs_high": "significant",
            "medium_vs_high": "not significant",
        },
        interpretation_points=[
            "anova", "post-hoc", "tukey", "multiple comparison",
            "pairwise", "dose-dependent", "significant",
        ],
        common_mistakes=[
            "only reported ANOVA without post-hoc interpretation",
            "compared all pairs without correction",
            "didn't note medium and high are not different from each other",
        ],
        difficulty="medium",
        domain="biostatistics",
    ),
    DataInterpTask(
        id="di_st_003",
        interp_type=DataInterpType.STATISTICAL_TEST,
        scenario=(
            "A genomics study tested 20 candidate genes for differential expression "
            "between tumor and normal tissue. The following p-values were obtained. "
            "Assess whether the claimed 'significant' genes are truly significant "
            "after multiple testing correction."
        ),
        data_table=(
            "Gene    | Raw p-value | Claimed significant?\n"
            "GENE1   | 0.001       | Yes\n"
            "GENE2   | 0.012       | Yes\n"
            "GENE3   | 0.023       | Yes\n"
            "GENE4   | 0.038       | Yes\n"
            "GENE5   | 0.047       | Yes\n"
            "GENE6   | 0.062       | No\n"
            "...14 more genes with p > 0.1\n"
            "\n"
            "Bonferroni threshold: 0.05/20 = 0.0025\n"
            "BH (FDR 5%) threshold: ~0.0125"
        ),
        expected_answer={
            "bonferroni_significant": ["GENE1"],
            "bh_significant": ["GENE1"],
            "overclaimed": ["GENE2", "GENE3", "GENE4", "GENE5"],
        },
        interpretation_points=[
            "multiple comparison", "bonferroni", "false discovery", "fdr",
            "correction", "type i error", "inflated",
        ],
        common_mistakes=[
            "accepted all p < 0.05 as significant without correction",
            "didn't explain why correction is needed for 20 tests",
            "confused Bonferroni with BH/FDR",
        ],
        difficulty="medium",
        domain="biostatistics",
    ),
    DataInterpTask(
        id="di_st_004",
        interp_type=DataInterpType.STATISTICAL_TEST,
        scenario=(
            "A study reports a significant correlation between coffee consumption "
            "and cancer incidence in a cohort study. Evaluate the statistical result "
            "and the causal claim."
        ),
        data_table=(
            "Regression output:\n"
            "  Dependent variable: Cancer incidence (per 100,000)\n"
            "  Independent variable: Coffee consumption (cups/day)\n"
            "  Coefficient: 12.3 (SE: 4.1)\n"
            "  p = 0.003\n"
            "  R² = 0.08\n"
            "  N = 5,000\n"
            "\n"
            "Confounders measured but not adjusted:\n"
            "  Smoking status, alcohol use, age, BMI"
        ),
        expected_answer={
            "statistically_significant": True,
            "clinically_meaningful": "questionable",
            "r_squared_low": True,
            "confounders_not_adjusted": True,
            "causal_claim_valid": False,
        },
        interpretation_points=[
            "correlation", "causation", "confounder", "r-squared",
            "variance explained", "smoking", "adjustment",
            "observational", "residual confounding",
        ],
        common_mistakes=[
            "equated statistical significance with causal relationship",
            "ignored the low R-squared value",
            "didn't mention confounders",
        ],
        difficulty="hard",
        domain="epidemiology",
    ),
    DataInterpTask(
        id="di_st_005",
        interp_type=DataInterpType.STATISTICAL_TEST,
        scenario=(
            "A clinical trial is being planned to detect a 15% improvement in "
            "response rate (from 30% to 45%). The trial statistician provides "
            "the following power analysis. Evaluate the sample size and design."
        ),
        data_table=(
            "Power analysis parameters:\n"
            "  Control response rate: 30%\n"
            "  Expected treatment rate: 45%\n"
            "  Alpha: 0.05 (two-sided)\n"
            "  Power: 80%\n"
            "  Required N per arm: 120\n"
            "  Total enrollment: 240\n"
            "\n"
            "Additional considerations:\n"
            "  Expected dropout rate: 15%\n"
            "  Interim analysis planned: Yes (1 interim at 50%)"
        ),
        expected_answer={
            "n_adequate_for_power": True,
            "adjusted_n_for_dropout": 283,
            "interim_affects_alpha": True,
        },
        interpretation_points=[
            "power", "sample size", "dropout", "inflate", "interim",
            "alpha spending", "type i", "effect size",
        ],
        common_mistakes=[
            "didn't adjust sample size for dropouts",
            "ignored interim analysis impact on alpha",
            "confused one-sided with two-sided test",
        ],
        difficulty="hard",
        domain="clinical_trials",
    ),

    # ----- SURVIVAL ANALYSIS (5 tasks) -----
    DataInterpTask(
        id="di_sa_001",
        interp_type=DataInterpType.SURVIVAL_ANALYSIS,
        scenario=(
            "A phase III trial compared overall survival between standard treatment "
            "and a new drug. Interpret the survival data and describe the outcome."
        ),
        data_table=(
            "Arm          | N   | Events | Median OS (months) | 95% CI\n"
            "Standard     | 200 | 150    | 12.3               | [10.8, 14.1]\n"
            "New Drug     | 200 | 125    | 16.8               | [14.2, 19.5]\n"
            "\n"
            "Log-rank test: p = 0.0012\n"
            "Hazard ratio (new vs standard): 0.72 [95% CI: 0.59-0.88]"
        ),
        expected_answer={
            "median_improvement": 4.5,
            "hr": 0.72,
            "hr_significant": True,
            "risk_reduction_pct": 28,
        },
        interpretation_points=[
            "median", "overall survival", "hazard ratio", "0.72",
            "risk reduction", "28%", "significant", "log-rank",
        ],
        common_mistakes=[
            "misinterpreted HR direction (lower = better for treatment)",
            "didn't calculate risk reduction from HR",
        ],
        difficulty="easy",
        domain="oncology",
    ),
    DataInterpTask(
        id="di_sa_002",
        interp_type=DataInterpType.SURVIVAL_ANALYSIS,
        scenario=(
            "Two immunotherapy regimens were compared for progression-free survival. "
            "The survival curves initially overlap but separate after 6 months. "
            "Interpret the results."
        ),
        data_table=(
            "Time (months) | Regimen A (% alive) | Regimen B (% alive)\n"
            "0              | 100                 | 100\n"
            "3              | 78                  | 80\n"
            "6              | 60                  | 58\n"
            "9              | 48                  | 42\n"
            "12             | 42                  | 28\n"
            "18             | 38                  | 15\n"
            "24             | 35                  | 8\n"
            "\n"
            "Log-rank test: p = 0.043\n"
            "Restricted mean survival time (24mo): A=14.2mo, B=11.3mo"
        ),
        expected_answer={
            "curves_cross_or_overlap_early": True,
            "separation_timepoint": "after 6 months",
            "regimen_a_better": True,
            "rmst_difference": 2.9,
        },
        interpretation_points=[
            "delayed separation", "immunotherapy", "late benefit",
            "plateau", "log-rank", "restricted mean",
        ],
        common_mistakes=[
            "ignored the early overlap pattern",
            "didn't mention delayed separation characteristic of immunotherapy",
        ],
        difficulty="medium",
        domain="clinical_trials",
    ),
    DataInterpTask(
        id="di_sa_003",
        interp_type=DataInterpType.SURVIVAL_ANALYSIS,
        scenario=(
            "A multivariable Cox proportional hazards model was fit to predict "
            "overall survival in a lung cancer cohort. Interpret the model output."
        ),
        data_table=(
            "Variable            | HR    | 95% CI        | p-value\n"
            "Age (per 10 years)  | 1.35  | [1.15, 1.58]  | 0.0003\n"
            "Stage III vs I-II   | 2.41  | [1.82, 3.19]  | <0.0001\n"
            "Stage IV vs I-II    | 4.87  | [3.65, 6.50]  | <0.0001\n"
            "EGFR mutation (+)   | 0.68  | [0.49, 0.94]  | 0.019\n"
            "Smoking (current)   | 1.12  | [0.88, 1.43]  | 0.35\n"
            "Treatment (new)     | 0.75  | [0.60, 0.94]  | 0.012"
        ),
        expected_answer={
            "strongest_predictor": "Stage IV",
            "protective_factors": ["EGFR mutation", "new treatment"],
            "not_significant": ["smoking"],
            "treatment_benefit": "25% risk reduction",
        },
        interpretation_points=[
            "hazard ratio", "cox", "proportional hazards", "multivariable",
            "adjusted", "stage", "independent predictor", "protective",
        ],
        common_mistakes=[
            "interpreted HR > 1 as protective",
            "didn't note that smoking is not significant after adjustment",
            "failed to identify strongest predictor",
        ],
        difficulty="hard",
        domain="epidemiology",
    ),
    DataInterpTask(
        id="di_sa_004",
        interp_type=DataInterpType.SURVIVAL_ANALYSIS,
        scenario=(
            "The following survival data shows an unusual pattern where the two "
            "treatment arms cross around 12 months. The log-rank test gives "
            "p = 0.15. Does this mean there is no treatment difference? "
            "Explain the limitation."
        ),
        data_table=(
            "Time (months) | Arm A (% alive) | Arm B (% alive)\n"
            "0              | 100             | 100\n"
            "6              | 85              | 65\n"
            "12             | 55              | 55\n"
            "18             | 35              | 52\n"
            "24             | 20              | 48\n"
            "30             | 12              | 45"
        ),
        expected_answer={
            "curves_cross": True,
            "crossing_time": 12,
            "log_rank_limitation": "non-proportional hazards",
            "arm_b_better_late": True,
        },
        interpretation_points=[
            "crossing", "non-proportional", "log-rank", "limitation",
            "weighted", "landmark", "restricted mean", "hazard",
        ],
        common_mistakes=[
            "concluded no difference based only on log-rank p-value",
            "didn't recognize non-proportional hazards",
            "ignored the crossing pattern",
        ],
        difficulty="hard",
        domain="biostatistics",
    ),
    DataInterpTask(
        id="di_sa_005",
        interp_type=DataInterpType.SURVIVAL_ANALYSIS,
        scenario=(
            "From the following life table data, calculate the 1-year (12-month) "
            "survival rate for patients with newly diagnosed glioblastoma."
        ),
        data_table=(
            "Interval (months) | N at start | Deaths | Withdrawals\n"
            "0-3                | 100        | 15     | 2\n"
            "3-6                | 83         | 12     | 3\n"
            "6-9                | 68         | 10     | 1\n"
            "9-12               | 57         | 8      | 2"
        ),
        expected_answer={
            "survival_0_3": 0.849,
            "survival_3_6": 0.853,
            "survival_6_9": 0.852,
            "survival_9_12": 0.857,
            "cumulative_12mo": 0.528,
        },
        interpretation_points=[
            "life table", "conditional", "cumulative", "product",
            "kaplan-meier", "censored", "withdrawal", "adjusted",
        ],
        common_mistakes=[
            "didn't adjust for withdrawals at risk",
            "added instead of multiplied conditional probabilities",
            "confused deaths with survival",
        ],
        difficulty="medium",
        domain="oncology",
    ),

    # ----- MULTI-ASSAY INTEGRATION (5 tasks) -----
    DataInterpTask(
        id="di_ma_001",
        interp_type=DataInterpType.MULTI_ASSAY,
        scenario=(
            "A study measured p53 expression at both mRNA (qPCR) and protein "
            "(Western blot densitometry) levels after DNA damage. Do the two "
            "assays agree? Explain any discordance."
        ),
        data_table=(
            "Condition    | TP53 mRNA (fold-change) | p53 protein (fold-change)\n"
            "Control      | 1.0                     | 1.0\n"
            "UV 2h        | 1.2                     | 3.5\n"
            "UV 6h        | 1.1                     | 5.8\n"
            "UV 24h       | 0.9                     | 4.2"
        ),
        expected_answer={
            "mrna_change": "minimal",
            "protein_change": "substantial increase",
            "concordant": False,
            "explanation": "post-transcriptional regulation",
        },
        interpretation_points=[
            "discordant", "post-transcriptional", "stabilization",
            "mdm2", "degradation", "protein stability", "half-life",
        ],
        common_mistakes=[
            "assumed mRNA and protein must correlate",
            "didn't explain the biological basis for discordance",
            "concluded the assays are wrong",
        ],
        difficulty="easy",
        domain="molecular_biology",
    ),
    DataInterpTask(
        id="di_ma_002",
        interp_type=DataInterpType.MULTI_ASSAY,
        scenario=(
            "RNA-seq and proteomics were performed on the same tumor samples. "
            "The data shows poor overall correlation. Interpret these findings."
        ),
        data_table=(
            "Gene/Protein | RNA log2FC | Protein log2FC | RNA padj  | Prot padj\n"
            "EGFR         | 2.5        | 1.8            | 0.001     | 0.01\n"
            "MYC          | 3.1        | 0.3            | 0.0001    | 0.45\n"
            "CDH1         | -2.8       | -2.1           | 0.0005    | 0.008\n"
            "PTEN         | -0.2       | -1.9           | 0.72      | 0.003\n"
            "GAPDH        | 0.1        | 0.05           | 0.89      | 0.91\n"
            "\n"
            "Overall Spearman correlation (RNA vs protein): r = 0.42, p = 0.03"
        ),
        expected_answer={
            "concordant_genes": ["EGFR", "CDH1", "GAPDH"],
            "discordant_genes": ["MYC", "PTEN"],
            "overall_correlation": "moderate",
        },
        interpretation_points=[
            "post-transcriptional", "translation", "protein stability",
            "turnover", "correlation", "discordant",
            "multi-omics", "complementary",
        ],
        common_mistakes=[
            "expected perfect RNA-protein correlation",
            "didn't identify specific discordant genes",
            "ignored post-transcriptional regulation",
        ],
        difficulty="medium",
        domain="multi_omics",
    ),
    DataInterpTask(
        id="di_ma_003",
        interp_type=DataInterpType.MULTI_ASSAY,
        scenario=(
            "Drug W shows potent activity in vitro but the in vivo results are "
            "less impressive. Integrate the data and assess translational potential."
        ),
        data_table=(
            "In vitro data:\n"
            "  IC50 (A549 cells): 50 nM\n"
            "  IC50 (H1975 cells): 35 nM\n"
            "  Selectivity (normal BEAS-2B): IC50 = 2.5 μM (50-fold window)\n"
            "\n"
            "In vivo data (A549 xenograft, 30 mg/kg daily):\n"
            "  Tumor growth inhibition: 35%\n"
            "  PK: Cmax = 200 nM, AUC = 800 nM·h, t1/2 = 2.1 h\n"
            "  Free fraction in plasma: 5%\n"
            "  Effective free Cmax: 10 nM"
        ),
        expected_answer={
            "in_vitro_potent": True,
            "in_vivo_modest": True,
            "gap_explanation": "insufficient free drug exposure",
            "free_cmax_below_ic50": True,
        },
        interpretation_points=[
            "free fraction", "exposure", "pharmacokinetic", "cmax",
            "ic50", "coverage", "protein binding", "translation",
        ],
        common_mistakes=[
            "compared total plasma concentration to in vitro IC50",
            "didn't calculate free drug concentration",
            "concluded drug doesn't work without PK explanation",
        ],
        difficulty="hard",
        domain="translational",
    ),
    DataInterpTask(
        id="di_ma_004",
        interp_type=DataInterpType.MULTI_ASSAY,
        scenario=(
            "Flow cytometry and gene expression data were collected from tumor-"
            "infiltrating lymphocytes (TILs). Integrate the results to characterize "
            "the immune microenvironment."
        ),
        data_table=(
            "Flow cytometry (% of CD45+ cells):\n"
            "  CD8+ T cells: 25%\n"
            "  CD4+ T cells: 35%\n"
            "  Tregs (CD4+FoxP3+): 18% of CD4+\n"
            "  PD-1+ (of CD8+): 65%\n"
            "\n"
            "Gene expression (TPM, tumor vs normal fold-change):\n"
            "  CD8A: 3.2x   | PDCD1 (PD-1): 4.5x   | LAG3: 2.8x\n"
            "  FOXP3: 2.1x  | IFNG: 1.8x            | GZMB: 2.5x\n"
            "  CD274 (PD-L1): 3.8x | CTLA4: 2.2x"
        ),
        expected_answer={
            "immune_phenotype": "inflamed/hot",
            "exhaustion_markers": ["PD-1", "LAG3"],
            "treg_concern": True,
            "immunotherapy_candidate": True,
        },
        interpretation_points=[
            "inflamed", "exhaustion", "pd-1", "checkpoint",
            "treg", "immunotherapy", "cd8", "response",
        ],
        common_mistakes=[
            "only analyzed flow or gene expression, not both",
            "missed the exhaustion signature",
            "didn't consider Tregs as immunosuppressive",
        ],
        difficulty="medium",
        domain="immunology",
    ),
    DataInterpTask(
        id="di_ma_005",
        interp_type=DataInterpType.MULTI_ASSAY,
        scenario=(
            "Metabolomics and transcriptomics data from liver tissue of obese "
            "vs. lean mice were integrated using pathway analysis. Interpret the "
            "converging evidence."
        ),
        data_table=(
            "Pathway                  | Transcriptomics p | Metabolomics p | Direction\n"
            "Fatty acid oxidation     | 0.002             | 0.008          | Down in obese\n"
            "De novo lipogenesis      | 0.001             | 0.003          | Up in obese\n"
            "Gluconeogenesis          | 0.015             | 0.042          | Up in obese\n"
            "TCA cycle                | 0.34              | 0.012          | Down (metab only)\n"
            "Amino acid catabolism    | 0.008             | 0.56           | Down (RNA only)\n"
            "Oxidative stress (Nrf2)  | 0.003             | 0.005          | Up in obese"
        ),
        expected_answer={
            "converging_pathways": ["fatty acid oxidation", "de novo lipogenesis",
                                     "gluconeogenesis", "oxidative stress"],
            "discordant_pathways": ["TCA cycle", "amino acid catabolism"],
            "metabolic_phenotype": "lipogenic shift with oxidative stress",
        },
        interpretation_points=[
            "converging", "multi-omics", "pathway", "lipogenesis",
            "oxidative stress", "metabolic", "integration",
            "discordant", "complementary",
        ],
        common_mistakes=[
            "only reported one omics layer",
            "treated discordant pathways as errors",
            "didn't synthesize into overall metabolic phenotype",
        ],
        difficulty="hard",
        domain="systems_biology",
    ),
]


# =============================================================================
# SCORING
# =============================================================================

_DEPTH_INDICATORS = [
    "furthermore", "additionally", "importantly", "specifically",
    "in particular", "for example", "such as", "including",
    "moreover", "it is critical", "it is essential", "notably",
]


def _extract_numbers(text: str) -> list[float]:
    """Extract all numerical values from text."""
    patterns = [
        r'[-+]?\d+\.?\d*(?:[eE][-+]?\d+)?',
    ]
    numbers = []
    for pat in patterns:
        for match in re.findall(pat, text):
            try:
                numbers.append(float(match))
            except ValueError:
                pass
    return numbers


def _count_interp_matches(points: list[str], text: str) -> tuple[int, list[str]]:
    """Count how many interpretation points are found in response."""
    text_lower = text.lower()
    found = []
    for point in points:
        words = point.lower().split()
        if len(words) == 1:
            if words[0] in text_lower:
                found.append(point)
        else:
            if all(w in text_lower for w in words):
                found.append(point)
    return len(found), found


def _count_mistakes(mistakes: list[str], text: str) -> tuple[int, list[str]]:
    """Check if response exhibits common mistakes.

    Uses keyword overlap BUT requires the response to NOT contain negation
    or correction language near the matching keywords.  This prevents
    penalising a model that *addresses* a mistake topic correctly.
    """
    text_lower = text.lower()
    _correction_signals = [
        "correctly", "appropriately", "properly", "as expected",
        "should be", "need to", "must ", "important to", "adjusted for",
        "accounted for", "accounting for", "after correction",
        "applying", "applied", "using bonferroni", "using bh",
        "after adjusting", "we adjust", "i adjust",
    ]
    detected = []
    for mistake in mistakes:
        keywords = [w for w in mistake.lower().split() if len(w) > 3]
        if len(keywords) >= 3:
            match_count = sum(1 for kw in keywords if kw in text_lower)
            if match_count >= len(keywords) * 0.6:
                # Check if keywords appear in a correction/negation context
                # Find where each keyword appears and check surrounding text
                addressed_correctly = False
                for kw in keywords:
                    if kw not in text_lower:
                        continue
                    idx = text_lower.find(kw)
                    window = text_lower[max(0, idx - 80):min(len(text_lower), idx + 80)]
                    if any(sig in window for sig in _correction_signals):
                        addressed_correctly = True
                        break
                if not addressed_correctly:
                    detected.append(mistake)
    return len(detected), detected


def _check_numerical_accuracy(task: DataInterpTask, response: str) -> float:
    """Check if key numerical values from expected_answer appear in response."""
    response_numbers = _extract_numbers(response)
    if not response_numbers:
        return 0.0

    expected = task.expected_answer
    checks_passed = 0
    checks_total = 0

    for key, val in expected.items():
        # Skip booleans — isinstance(True, int) is True in Python but
        # booleans should not be checked as numeric values
        if isinstance(val, bool):
            continue
        if isinstance(val, (int, float)):
            checks_total += 1
            for rn in response_numbers:
                if val == 0:
                    if abs(rn) < 0.1:
                        checks_passed += 1
                        break
                elif abs(rn - val) / max(abs(val), 0.001) < 0.15:
                    checks_passed += 1
                    break
        elif isinstance(val, list) and len(val) == 2 and all(isinstance(v, (int, float)) for v in val):
            # Range check [lo, hi] — any response number in range counts
            checks_total += 1
            lo, hi = val
            for rn in response_numbers:
                if lo <= rn <= hi:
                    checks_passed += 1
                    break

    # When expected_answer has no numeric fields, return 1.0 (nothing to fail)
    # rather than 0.0 which would unfairly penalize 40% of the score
    return checks_passed / checks_total if checks_total > 0 else 1.0


def _compute_depth_score(text: str) -> float:
    """Compute depth/specificity bonus."""
    text_lower = text.lower()
    depth_count = sum(1 for ind in _DEPTH_INDICATORS if ind in text_lower)
    length_bonus = min(0.1, len(text) / 5000)
    indicator_bonus = min(0.2, depth_count * 0.04)
    return round(length_bonus + indicator_bonus, 4)


def score_datainterp_response(task: DataInterpTask, response: str) -> dict:
    """Score a response to a data interpretation task.

    Scoring combines:
    1. Numerical accuracy (0-0.4): correct values within tolerance
    2. Interpretation coverage (0-0.4): interpretation points matched
    3. Mistake penalty (0-0.2): deduction for common mistakes
    4. Depth bonus (0-0.2): reward for thorough responses

    Returns:
        Dict with score (0-1), passed (bool), and detailed breakdown.
    """
    if response is not None and not isinstance(response, str):
        response = str(response)
    if not response or not response.strip():
        return {
            "task_id": task.id,
            "interp_type": task.interp_type.value,
            "score": 0.0,
            "passed": False,
            "numerical_accuracy": 0.0,
            "interpretation_coverage": 0.0,
            "mistake_penalty": 0.0,
            "depth_score": 0.0,
            "points_found": [],
            "mistakes_detected": [],
            "difficulty": task.difficulty,
            "domain": task.domain,
            "response_length": 0,
        }

    # 1. Numerical accuracy (0-0.4)
    num_acc = _check_numerical_accuracy(task, response)
    numerical_score = num_acc * 0.4

    # 2. Interpretation coverage (0-0.4)
    n_points = len(task.interpretation_points)
    n_found, points_found = _count_interp_matches(task.interpretation_points, response)
    interp_coverage = n_found / n_points if n_points > 0 else 0.0
    interp_score = interp_coverage * 0.4

    # 3. Mistake penalty (0-0.2)
    n_mistakes, mistakes_detected = _count_mistakes(task.common_mistakes, response)
    mistake_penalty = min(0.2, n_mistakes * 0.07)

    # 4. Depth bonus (0-0.2)
    depth = _compute_depth_score(response)
    depth_score = min(0.2, depth)

    # Final score
    score = max(0.0, min(1.0, numerical_score + interp_score + depth_score - mistake_penalty))
    passed = score >= 0.5

    return {
        "task_id": task.id,
        "interp_type": task.interp_type.value,
        "score": round(score, 4),
        "passed": passed,
        "numerical_accuracy": round(num_acc, 4),
        "interpretation_coverage": round(interp_coverage, 4),
        "mistake_penalty": round(mistake_penalty, 4),
        "depth_score": round(depth_score, 4),
        "points_found": points_found,
        "mistakes_detected": mistakes_detected,
        "difficulty": task.difficulty,
        "difficulty_weight": DIFFICULTY_WEIGHTS.get(task.difficulty, 1.0),
        "domain": task.domain,
        "response_length": len(response),
    }


# =============================================================================
# EVALUATOR CLASS
# =============================================================================

class DataInterpEvaluator:
    """Evaluator for data interpretation tasks."""

    def __init__(self, model_name: str = "claude-sonnet-4-20250514"):
        self.model_name = model_name
        self._client = None

    @property
    def client(self):
        if self._client is None:
            import anthropic
            self._client = anthropic.Anthropic()
        return self._client

    def load_tasks(self) -> list[DataInterpTask]:
        """Load all data interpretation tasks."""
        return list(DATA_INTERP_TASKS)

    def evaluate_task(self, task: DataInterpTask) -> dict:
        """Evaluate a single task via API call."""
        system_prompt = (
            "You are a biostatistics and data analysis expert. Interpret "
            "experimental data accurately. Show your calculations, state "
            "assumptions, and provide biological context for your conclusions. "
            "Be precise with numbers and honest about limitations."
        )

        user_content = f"{task.scenario}\n\nData:\n{task.data_table}"

        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=2000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}],
        )
        response_text = response.content[0].text

        scores = score_datainterp_response(task, response_text)
        scores["response"] = response_text
        return scores

    def run_evaluation(self) -> dict:
        """Run all data interpretation tasks and aggregate results."""
        results = []
        for task in DATA_INTERP_TASKS:
            try:
                result = self.evaluate_task(task)
                results.append(result)
            except Exception as e:
                results.append({"task_id": task.id, "error": str(e)})

        by_type = {}
        for r in results:
            if "error" in r and "score" not in r:
                continue
            it = r.get("interp_type", "unknown")
            if it not in by_type:
                by_type[it] = {"scores": [], "passed": 0, "total": 0}
            by_type[it]["scores"].append(r["score"])
            by_type[it]["total"] += 1
            if r.get("passed"):
                by_type[it]["passed"] += 1

        for it, data in by_type.items():
            data["mean"] = round(sum(data["scores"]) / len(data["scores"]), 4) if data["scores"] else 0
            data["pass_rate"] = round(data["passed"] / data["total"], 4) if data["total"] else 0

        scored = [r for r in results if "score" in r]
        mean_score = sum(r["score"] for r in scored) / len(scored) if scored else 0

        return {
            "model": self.model_name,
            "component": "datainterp",
            "total_tasks": len(results),
            "mean_score": round(mean_score, 4),
            "by_type": by_type,
            "results": results,
        }
