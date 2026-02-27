"""
DesignCheck: Experimental Design Critique Evaluation

Tests whether LLMs can identify flaws in experimental designs—a key skill
for scientific reasoning and peer review.
"""

import json
from typing import Optional
from dataclasses import dataclass

from bioeval.models.base import BaseEvaluator, EvalTask


# =============================================================================
# FLAW TAXONOMY
# =============================================================================

FLAW_CATEGORIES = {
    "controls": {
        "missing_negative_control": "No untreated or vehicle control included",
        "missing_positive_control": "No positive control to validate assay works",
        "inappropriate_control": "Control doesn't match experimental conditions",
        "missing_isotype_control": "Antibody experiments without isotype control",
    },
    "statistics": {
        "underpowered": "Sample size too small to detect expected effect",
        "pseudoreplication": "Technical replicates treated as biological",
        "wrong_test": "Statistical test doesn't match data distribution",
        "multiple_testing": "No correction for multiple comparisons",
        "p_hacking": "Selective reporting or analysis",
    },
    "confounders": {
        "batch_effect": "Conditions processed in different batches",
        "time_confound": "Samples collected at different times",
        "passage_number": "Cells at different passage numbers compared",
        "operator_effect": "Different people performing conditions",
    },
    "technical": {
        "wrong_antibody": "Antibody species mismatch or wrong application",
        "incompatible_buffers": "Buffer conditions inappropriate for assay",
        "wrong_cell_line": "Cell line doesn't model biology of interest",
        "insufficient_replicates": "Only 1-2 replicates per condition",
    },
    "interpretation": {
        "correlation_causation": "Correlation interpreted as causation",
        "overstatement": "Conclusions exceed what data supports",
        "cherry_picking": "Selective presentation of data",
        "confirmation_bias": "Ignoring contradictory evidence",
    },
}


# =============================================================================
# FLAWED EXPERIMENTAL DESIGNS
# =============================================================================

FLAWED_DESIGNS = [
    # -------------------------------------------------------------------------
    # CONTROL ISSUES
    # -------------------------------------------------------------------------
    {
        "id": "design_001",
        "title": "Drug Response Experiment",
        "description": """
        We tested whether Drug X inhibits cancer cell proliferation.
        
        Methods:
        - A549 cells were seeded in 96-well plates (5000 cells/well)
        - Cells were treated with Drug X at 1, 5, 10, 25 μM for 72 hours
        - Cell viability was measured using MTT assay
        - Experiment performed in triplicate (3 wells per concentration)
        
        Results:
        - Cell viability decreased with increasing Drug X concentration
        - IC50 was calculated as 8.5 μM
        
        Conclusion: Drug X is a potent inhibitor of A549 cell proliferation.
        """,
        "flaws": [
            {
                "category": "controls",
                "type": "missing_negative_control",
                "severity": "critical",
                "explanation": "No vehicle (DMSO) control to account for solvent effects",
                "fix": "Include DMSO-only control at highest concentration used",
            },
            {
                "category": "statistics",
                "type": "pseudoreplication",
                "severity": "critical",
                "explanation": "3 wells are technical replicates, not biological replicates",
                "fix": "Repeat experiment on 3 different days or with 3 different cell passages",
            },
            {
                "category": "controls",
                "type": "missing_positive_control",
                "severity": "major",
                "explanation": "No known cytotoxic drug to validate assay performance",
                "fix": "Include a known cytotoxic agent like staurosporine",
            },
        ],
    },
    {
        "id": "design_002",
        "title": "Knockout Phenotype Study",
        "description": """
        We generated CRISPR knockout cells to study Gene X function.
        
        Methods:
        - Transfected HeLa cells with Cas9 and sgRNA targeting Gene X
        - Selected with puromycin for 1 week
        - Picked single clones and verified by Western blot
        - Compared knockout clone to parental HeLa cells
        
        Results:
        - Gene X protein was absent in knockout cells
        - Knockout cells showed slower proliferation
        - RNA-seq revealed 500 differentially expressed genes
        
        Conclusion: Gene X is required for normal cell proliferation and 
        regulates 500 downstream genes.
        """,
        "flaws": [
            {
                "category": "controls",
                "type": "inappropriate_control",
                "severity": "critical",
                "explanation": "Parental cells didn't undergo same selection process - could be selection effects",
                "fix": "Use non-targeting sgRNA control that underwent same selection",
            },
            {
                "category": "technical",
                "type": "insufficient_replicates",
                "severity": "critical",
                "explanation": "Only one knockout clone - could be clonal effects unrelated to Gene X",
                "fix": "Test 2-3 independent knockout clones with different sgRNAs",
            },
            {
                "category": "interpretation",
                "type": "overstatement",
                "severity": "major",
                "explanation": "500 DEGs doesn't mean Gene X 'regulates' them - many are indirect effects",
                "fix": "Distinguish direct vs indirect targets, validate key targets",
            },
        ],
    },
    {
        "id": "design_003",
        "title": "Western Blot Quantification",
        "description": """
        We measured protein X levels after drug treatment.
        
        Methods:
        - HEK293 cells were treated with Drug Y or DMSO for 24 hours
        - Cells were lysed and 30 μg protein loaded per lane
        - Western blot for protein X and β-actin (loading control)
        - Bands were quantified using ImageJ
        
        Results:
        - Drug Y treated: Protein X band intensity = 5000
        - DMSO control: Protein X band intensity = 10000
        - β-actin was similar between samples
        - Conclusion: Drug Y reduces protein X levels by 50%
        
        Statistics: n=1, single experiment
        """,
        "flaws": [
            {
                "category": "technical",
                "type": "insufficient_replicates",
                "severity": "critical",
                "explanation": "n=1 provides no statistical power - result could be noise",
                "fix": "Perform at least n=3 biological replicates",
            },
            {
                "category": "statistics",
                "type": "wrong_test",
                "severity": "critical",
                "explanation": "No statistical test performed - can't claim 50% reduction",
                "fix": "Perform t-test or equivalent on normalized values from replicates",
            },
            {
                "category": "technical",
                "type": "incompatible_buffers",
                "severity": "minor",
                "explanation": "Didn't specify if bands are in linear range of detection",
                "fix": "Include loading curve to verify linear range",
            },
        ],
    },
    # -------------------------------------------------------------------------
    # STATISTICAL ISSUES
    # -------------------------------------------------------------------------
    {
        "id": "design_004",
        "title": "Gene Expression Time Course",
        "description": """
        We studied gene expression changes after cytokine stimulation.
        
        Methods:
        - Macrophages stimulated with LPS
        - RNA collected at 0, 1, 2, 4, 8, 24 hours
        - qPCR for 50 inflammatory genes
        - Each time point done in triplicate
        
        Results:
        - 35 genes showed significant changes (p < 0.05) at some time point
        - Peak expression was at 4 hours for most genes
        
        Statistics: t-test comparing each time point to time 0
        """,
        "flaws": [
            {
                "category": "statistics",
                "type": "multiple_testing",
                "severity": "critical",
                "explanation": "300 comparisons (50 genes × 6 time points) with no correction",
                "fix": "Apply Bonferroni or FDR correction; expect ~15 false positives at p<0.05",
            },
            {
                "category": "statistics",
                "type": "wrong_test",
                "severity": "major",
                "explanation": "Multiple t-tests for time course - should use ANOVA or longitudinal model",
                "fix": "Use repeated measures ANOVA or mixed effects model",
            },
            {
                "category": "confounders",
                "type": "batch_effect",
                "severity": "major",
                "explanation": "Not stated whether time points were collected in same batch",
                "fix": "Collect all time points from same stimulation or include batch in model",
            },
        ],
    },
    {
        "id": "design_005",
        "title": "Clinical Biomarker Study",
        "description": """
        We identified biomarkers for disease progression.
        
        Methods:
        - Collected serum from 20 patients with disease and 20 healthy controls
        - Measured 1000 proteins using mass spectrometry
        - Identified proteins different between groups (p < 0.05)
        - Built classifier using top 50 differential proteins
        - Classifier accuracy: 95% on study cohort
        
        Conclusion: Our 50-protein signature accurately predicts disease.
        """,
        "flaws": [
            {
                "category": "statistics",
                "type": "multiple_testing",
                "severity": "critical",
                "explanation": "1000 tests expect 50 false positives at p<0.05",
                "fix": "Apply FDR correction or permutation testing",
            },
            {
                "category": "statistics",
                "type": "p_hacking",
                "severity": "critical",
                "explanation": "Classifier tested on same data used for feature selection (overfitting)",
                "fix": "Use independent validation cohort or proper cross-validation",
            },
            {
                "category": "statistics",
                "type": "underpowered",
                "severity": "major",
                "explanation": "n=40 for 1000 features is severely underpowered",
                "fix": "Larger sample size or dimensionality reduction before testing",
            },
        ],
    },
    # -------------------------------------------------------------------------
    # CONFOUNDER ISSUES
    # -------------------------------------------------------------------------
    {
        "id": "design_006",
        "title": "Treatment Effect Comparison",
        "description": """
        We compared two cancer treatments in cell lines.
        
        Methods:
        - Treatment A tested on Monday using cells at passage 15
        - Treatment B tested on Friday using cells at passage 22
        - Both used same cell viability assay
        - Treatment A: 60% cell death; Treatment B: 40% cell death
        
        Conclusion: Treatment A is more effective than Treatment B.
        """,
        "flaws": [
            {
                "category": "confounders",
                "type": "time_confound",
                "severity": "critical",
                "explanation": "Treatments tested on different days - day-to-day variation not controlled",
                "fix": "Test both treatments in parallel on same day",
            },
            {
                "category": "confounders",
                "type": "passage_number",
                "severity": "critical",
                "explanation": "7 passages difference can significantly change drug sensitivity",
                "fix": "Use cells within 2-3 passages for comparison",
            },
            {
                "category": "technical",
                "type": "insufficient_replicates",
                "severity": "major",
                "explanation": "No indication of replicates or statistics",
                "fix": "Include biological replicates and statistical comparison",
            },
        ],
    },
    {
        "id": "design_007",
        "title": "Single-cell RNA-seq Analysis",
        "description": """
        We compared tumor microenvironment between responders and non-responders.
        
        Methods:
        - Collected tumors from 3 responders and 3 non-responders to immunotherapy
        - Processed samples for 10X single-cell RNA-seq
        - Responders processed in batch 1, non-responders in batch 2
        - Identified cell types and compared proportions
        
        Results:
        - Responders had 2x more CD8+ T cells in tumors
        - Non-responders had more exhausted T cell signature
        
        Conclusion: T cell infiltration predicts immunotherapy response.
        """,
        "flaws": [
            {
                "category": "confounders",
                "type": "batch_effect",
                "severity": "critical",
                "explanation": "Response status perfectly confounded with batch - differences could be technical",
                "fix": "Balance batches across conditions or include in model",
            },
            {
                "category": "statistics",
                "type": "underpowered",
                "severity": "major",
                "explanation": "n=3 per group insufficient for robust clinical conclusions",
                "fix": "Larger cohort or validation in independent dataset",
            },
            {
                "category": "interpretation",
                "type": "correlation_causation",
                "severity": "major",
                "explanation": "Association doesn't prove T cells cause response",
                "fix": "More careful language about association vs causation",
            },
        ],
    },
    # -------------------------------------------------------------------------
    # INTERPRETATION ISSUES
    # -------------------------------------------------------------------------
    {
        "id": "design_008",
        "title": "Drug Mechanism Study",
        "description": """
        We identified the mechanism of action for new compound Z.
        
        Methods:
        - Treated cancer cells with compound Z
        - Performed RNA-seq at 24 hours
        - Gene set enrichment showed downregulation of E2F targets
        - Compound Z reduced cyclin E protein levels (Western blot)
        
        Conclusion: Compound Z is a cyclin E inhibitor that blocks cell cycle progression.
        """,
        "flaws": [
            {
                "category": "interpretation",
                "type": "correlation_causation",
                "severity": "critical",
                "explanation": "Reduced cyclin E could be effect, not cause (cells dying lose cyclin E)",
                "fix": "Test direct binding, early time points, cyclin E overexpression rescue",
            },
            {
                "category": "controls",
                "type": "missing_positive_control",
                "severity": "major",
                "explanation": "No comparison to known cyclin E/CDK2 inhibitor",
                "fix": "Include CDK inhibitor as positive control for comparison",
            },
            {
                "category": "interpretation",
                "type": "overstatement",
                "severity": "major",
                "explanation": "'Cyclin E inhibitor' implies direct mechanism not demonstrated",
                "fix": "State that compound reduces cyclin E levels by unknown mechanism",
            },
        ],
    },
    {
        "id": "design_009",
        "title": "CRISPR Screen Analysis",
        "description": """
        We performed a genome-wide CRISPR screen to find drug resistance genes.
        
        Methods:
        - Transduced cells with genome-wide sgRNA library (80,000 sgRNAs)
        - Treated with drug or vehicle for 2 weeks
        - Sequenced sgRNA representation
        - Used MAGeCK to identify enriched guides
        
        Results:
        - Top hit: ABC transporter (10-fold enriched, p=0.001)
        - Validated by generating knockout and showing resistance
        
        Conclusion: ABC transporter causes drug resistance.
        """,
        "flaws": [
            {
                "category": "controls",
                "type": "inappropriate_control",
                "severity": "major",
                "explanation": "Validation used pool-derived KO but screen was in library context",
                "fix": "Validate in clean background, test if KO in naive cells causes resistance",
            },
            {
                "category": "technical",
                "type": "insufficient_replicates",
                "severity": "major",
                "explanation": "No mention of screen replicates - single screen can have significant noise",
                "fix": "Perform screen in replicate (minimum n=2)",
            },
            {
                "category": "interpretation",
                "type": "correlation_causation",
                "severity": "minor",
                "explanation": "'Causes' is strong - more accurate to say 'sufficient to confer'",
                "fix": "Distinguish necessary vs sufficient causes",
            },
        ],
    },
    {
        "id": "design_010",
        "title": "Mouse Tumor Study",
        "description": """
        We tested new immunotherapy combination in mouse tumor model.
        
        Methods:
        - Implanted B16 melanoma in C57BL/6 mice (n=10 per group)
        - Groups: Vehicle, Drug A alone, Drug B alone, Drug A+B combination
        - Measured tumor volume every 2 days
        - Sacrificed when tumors reached 2000mm³
        
        Results:
        - Combination showed smallest tumors at day 14
        - Day 14: Vehicle=800mm³, A=600mm³, B=650mm³, A+B=300mm³
        - p<0.05 for A+B vs vehicle (t-test)
        
        Conclusion: Drug A and B are synergistic in treating melanoma.
        """,
        "flaws": [
            {
                "category": "statistics",
                "type": "wrong_test",
                "severity": "major",
                "explanation": "Synergy requires specific statistical test (Bliss, Loewe), not just better than vehicle",
                "fix": "Calculate combination index or use Bliss independence model",
            },
            {
                "category": "statistics",
                "type": "multiple_testing",
                "severity": "major",
                "explanation": "Multiple time points and comparisons without correction",
                "fix": "Pre-specify primary endpoint or correct for multiple testing",
            },
            {
                "category": "confounders",
                "type": "operator_effect",
                "severity": "minor",
                "explanation": "No mention of blinding during tumor measurement",
                "fix": "Blind tumor measurements to treatment group",
            },
        ],
    },
]


# =============================================================================
# CORRECT EXPERIMENTAL DESIGNS (for positive examples)
# =============================================================================

CORRECT_DESIGNS = [
    {
        "id": "correct_001",
        "title": "Well-designed Drug Sensitivity Assay",
        "description": """
        We tested Drug X sensitivity across cancer cell lines.
        
        Methods:
        - 10 cell lines seeded in 96-well plates (optimized density per line)
        - Treated with Drug X (8 concentrations, 3-fold dilutions) or DMSO vehicle
        - Positive control: Staurosporine (known cytotoxic)
        - Each concentration in technical triplicate
        - Experiment repeated on 3 separate days (biological replicates)
        - Cell viability measured by CellTiter-Glo at 72 hours
        - IC50 calculated using 4-parameter logistic regression
        - Statistics: IC50s compared using one-way ANOVA with Tukey's post-hoc
        
        Quality control:
        - Z' factor > 0.5 for all plates (assay robustness)
        - DMSO controls showed <10% variation between replicates
        - Staurosporine IC50 within expected range
        """,
        "strengths": [
            "Appropriate vehicle control",
            "Positive control validates assay",
            "Technical AND biological replicates",
            "Proper statistical analysis",
            "QC metrics reported",
        ],
    }
]


# =============================================================================
# EVALUATOR CLASS
# =============================================================================


class DesignCheckEvaluator(BaseEvaluator):
    """Evaluator for Experimental Design Critique tasks."""

    def __init__(self, model_name: str = "claude-sonnet-4-20250514"):
        super().__init__(model_name)
        self.flaw_categories = FLAW_CATEGORIES

    def load_tasks(self, data_tier: str = "base") -> list[EvalTask]:
        """Load DesignCheck evaluation tasks.

        Args:
            data_tier: 'base' (10 designs), 'extended' or 'all' (20 designs).
        """
        if data_tier in ("extended", "all"):
            from bioeval.designcheck.extended_data import EXTENDED_FLAWED_DESIGNS

            designs = FLAWED_DESIGNS + EXTENDED_FLAWED_DESIGNS
        else:
            designs = FLAWED_DESIGNS

        return [self._create_flaw_detection_task(d) for d in designs]

    def _create_flaw_detection_task(self, design: dict) -> EvalTask:
        """Create a flaw detection task."""
        prompt = f"""You are reviewing the following experimental design for a peer-reviewed publication.
Identify any methodological flaws, missing controls, statistical issues, or interpretation problems.

Title: {design['title']}

{design['description']}

Please provide:
1. A list of specific flaws you identify
2. For each flaw:
   - Category (controls, statistics, confounders, technical, interpretation)
   - Severity (critical, major, minor)
   - Clear explanation of why it's a problem
   - Suggested fix
3. Overall assessment of the experimental design quality

Be thorough but focus on flaws that would actually affect the validity of the conclusions."""

        return EvalTask(
            id=design["id"], component="designcheck", task_type="flaw_detection", prompt=prompt, ground_truth=design
        )

    def score_response(self, task: EvalTask, response: str) -> dict:
        """Score flaw detection response with precision, recall, and severity weighting.

        Improvements over v0.2:
        - Uses response parser for structured flaw extraction
        - Computes both recall (of GT flaws) and estimated precision
        - Severity-weighted scoring (critical=3, major=2, minor=1)
        - Per-flaw matching details
        """
        from bioeval.scoring.response_parser import extract_flaw_list
        from bioeval.scoring.matching import phrase_match, matched_list, count_matches, extract_key_terms

        gt_flaws = task.ground_truth.get("flaws", [])
        response_lower = response.lower()
        stop_words = {"that", "this", "with", "from", "have", "been", "more", "also", "which", "their"}

        # --- Recall: how many GT flaws did the model find? ---
        severity_weights = {"critical": 3, "major": 2, "minor": 1}
        flaws_detected = 0
        critical_detected = 0
        weighted_detected = 0
        weighted_total = 0
        flaw_match_details = []

        for flaw in gt_flaws:
            weight = severity_weights.get(flaw["severity"], 1)
            weighted_total += weight

            # Multi-term matching: flaw type keywords + explanation key terms
            flaw_type = flaw["type"].replace("_", " ")
            explanation_terms = [t for t in flaw["explanation"].lower().split() if len(t) > 4 and t not in stop_words][:5]

            # A flaw is "detected" if:
            # (a) the flaw type phrase appears, OR
            # (b) 2+ explanation key terms appear
            type_match = phrase_match(flaw_type, response_lower)
            term_matches = matched_list(explanation_terms, response_lower)
            is_detected = type_match or len(term_matches) >= min(2, len(explanation_terms))

            if is_detected:
                flaws_detected += 1
                weighted_detected += weight
                if flaw["severity"] == "critical":
                    critical_detected += 1

            flaw_match_details.append(
                {
                    "flaw_type": flaw["type"],
                    "severity": flaw["severity"],
                    "detected": is_detected,
                    "type_match": type_match,
                    "term_matches": term_matches[:3],
                }
            )

        total_flaws = len(gt_flaws)
        total_critical = len([f for f in gt_flaws if f["severity"] == "critical"])

        flaw_recall = flaws_detected / total_flaws if total_flaws > 0 else 0
        critical_recall = critical_detected / total_critical if total_critical > 0 else 1.0
        weighted_recall = weighted_detected / weighted_total if weighted_total > 0 else 0

        # --- Precision estimate: how many extracted flaws match a GT flaw? ---
        parse_result = extract_flaw_list(response)
        extracted_flaws = parse_result.value if parse_result.success else []
        num_extracted = len(extracted_flaws)

        # Build flaw-type synonym map for semantic matching
        _type_aliases = {
            "insufficient_replicates": ["sample size", "replicates", "underpowered", "n=1", "statistical power"],
            "wrong_test": ["statistical test", "statistical analysis", "parametric", "nonparametric", "t-test", "anova"],
            "incompatible_buffers": ["buffer", "reagent", "loading control", "incompatible"],
            "missing_negative_control": ["negative control", "vehicle control", "dmso", "untreated"],
            "missing_positive_control": ["positive control", "known", "validate"],
            "inappropriate_control": ["control", "parental", "wild-type", "selection"],
            "pseudoreplication": ["pseudoreplication", "technical replicate", "biological replicate"],
            "batch_effect": ["batch", "confound"],
            "overstatement": ["overstatement", "causation", "correlation", "indirect"],
            "cherry_picking": ["cherry", "selective", "subset"],
            "p_hacking": ["p-hack", "multiple comparison", "correction"],
            "multiple_testing": ["multiple test", "bonferroni", "correction"],
        }

        # Match each extracted flaw against GT flaws
        true_positives = 0
        matched_gt = set()
        for ex_flaw in extracted_flaws:
            ex_desc = ex_flaw.description.lower() if ex_flaw.description else ""
            for j, gt_flaw in enumerate(gt_flaws):
                if j in matched_gt:
                    continue
                gt_type = gt_flaw["type"].replace("_", " ")
                gt_terms = [t for t in gt_flaw["explanation"].lower().split() if len(t) > 4 and t not in stop_words][:8]

                # Check type match in extracted description
                type_hit = phrase_match(gt_type, ex_desc)

                # Check type alias match
                alias_hit = False
                aliases = _type_aliases.get(gt_flaw["type"], [])
                for alias in aliases:
                    if alias in ex_desc:
                        alias_hit = True
                        break

                # Check term overlap (lowered threshold: 1 match sufficient)
                term_hits = count_matches(gt_terms, ex_desc)

                if type_hit or alias_hit or term_hits >= 1:
                    true_positives += 1
                    matched_gt.add(j)
                    break

        estimated_precision = true_positives / num_extracted if num_extracted > 0 else 0
        # F1 (harmonic mean of recall and precision)
        if flaw_recall + estimated_precision > 0:
            f1 = 2 * (flaw_recall * estimated_precision) / (flaw_recall + estimated_precision)
        else:
            f1 = 0

        # --- Quality checks ---
        mentions_fix = (
            phrase_match("fix", response_lower)
            or phrase_match("should", response_lower)
            or phrase_match("recommend", response_lower)
        )
        categorizes_severity = phrase_match("critical", response_lower) or phrase_match("major", response_lower)

        # Check if severity categorization is accurate
        severity_accuracy = 0
        if parse_result.success and categorizes_severity:
            for extracted_flaw in parse_result.value:
                if extracted_flaw.severity and extracted_flaw.severity in severity_weights:
                    severity_accuracy += 1
            if num_extracted > 0:
                severity_accuracy = severity_accuracy / num_extracted

        # --- Composite score: recall-weighted (flaw detection is recall-dominant) ---
        # Rationale: missing a real flaw is worse than a spurious one in peer review.
        # Primary: severity-weighted recall (70%)
        # Bonus: quality indicators up to +30% (mentions fixes, correct severity, ok precision)
        # Penalty: heavy hallucination (estimated_precision < 0.25) deducts up to 15%
        quality_bonus = (
            0.10 * float(mentions_fix)
            + 0.10 * float(categorizes_severity)
            + 0.10 * min(1.0, estimated_precision * 2)  # soft precision credit
        )
        # Precision penalty: if >75% of extracted flaws are hallucinated, penalize score
        if estimated_precision < 0.25 and num_extracted > 0:
            precision_penalty = (0.25 - estimated_precision) * 0.6  # max 0.15 penalty
        else:
            precision_penalty = 0.0
        composite = 0.70 * weighted_recall + quality_bonus - precision_penalty
        composite = min(1.0, max(0.0, composite))

        return {
            "flaw_recall": round(flaw_recall, 3),
            "critical_recall": round(critical_recall, 3),
            "weighted_recall": round(weighted_recall, 3),
            "estimated_precision": round(estimated_precision, 3),
            "f1": round(f1, 3),
            "composite_score": round(composite, 3),
            "precision_penalty": round(precision_penalty, 3),
            "flaws_detected": flaws_detected,
            "flaws_extracted": num_extracted,
            "total_flaws": total_flaws,
            "mentions_fix": mentions_fix,
            "categorizes_severity": categorizes_severity,
            "severity_accuracy": round(severity_accuracy, 3),
            "flaw_match_details": flaw_match_details,
            "response_length": len(response),
        }


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_all_flawed_designs():
    """Return all flawed experimental designs."""
    return FLAWED_DESIGNS


def get_all_correct_designs():
    """Return all correct experimental designs."""
    return CORRECT_DESIGNS


def get_flaw_taxonomy():
    """Return the flaw taxonomy."""
    return FLAW_CATEGORIES


def get_task_statistics():
    """Return statistics about available tasks."""
    all_flaws = []
    for design in FLAWED_DESIGNS:
        all_flaws.extend(design.get("flaws", []))

    severity_counts = {}
    category_counts = {}

    for flaw in all_flaws:
        sev = flaw.get("severity", "unknown")
        cat = flaw.get("category", "unknown")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
        category_counts[cat] = category_counts.get(cat, 0) + 1

    return {
        "total_designs": len(FLAWED_DESIGNS),
        "total_flaws": len(all_flaws),
        "flaws_by_severity": severity_counts,
        "flaws_by_category": category_counts,
        "avg_flaws_per_design": len(all_flaws) / len(FLAWED_DESIGNS) if FLAWED_DESIGNS else 0,
    }


if __name__ == "__main__":
    stats = get_task_statistics()
    print("DesignCheck Dataset Statistics:")
    print(f"  Total designs: {stats['total_designs']}")
    print(f"  Total flaws: {stats['total_flaws']}")
    print(f"  Average flaws per design: {stats['avg_flaws_per_design']:.1f}")
    print(f"  By severity: {stats['flaws_by_severity']}")
    print(f"  By category: {stats['flaws_by_category']}")
