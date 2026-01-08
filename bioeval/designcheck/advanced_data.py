"""
DesignCheck Advanced Dataset

Additional experimental design critique tasks covering:
- Clinical trial designs
- Animal study designs
- High-throughput sequencing experiments
- Multi-center studies
"""

# =============================================================================
# CLINICAL TRIAL DESIGN FLAWS
# =============================================================================

CLINICAL_DESIGNS = [
    {
        "id": "clinical_001",
        "title": "Phase II Cancer Drug Trial",
        "description": """
        Single-arm Phase II trial of new targeted therapy in advanced solid tumors.
        
        Methods:
        - Enrolled 50 patients with various advanced solid tumors
        - All patients received Drug X at 200mg daily
        - Primary endpoint: Overall Response Rate (ORR) by RECIST 1.1
        - Assessed response at 8 weeks
        - ORR was 30% (15/50 patients with PR or CR)
        
        Conclusion: Drug X shows promising activity in advanced solid tumors 
        and should advance to Phase III testing.
        """,
        "flaws": [
            {
                "category": "controls",
                "type": "missing_control_arm",
                "severity": "critical",
                "explanation": "Single-arm design cannot distinguish drug effect from natural disease variation",
                "fix": "Use historical controls or randomized design, acknowledge limitation"
            },
            {
                "category": "statistics",
                "type": "underpowered",
                "severity": "critical",
                "explanation": "Heterogeneous tumor types dilutes signal - each may have different response rate",
                "fix": "Focus on single tumor type or pre-specify tumor-specific cohorts"
            },
            {
                "category": "interpretation",
                "type": "overstatement",
                "severity": "major",
                "explanation": "30% ORR in mixed tumors without comparator is insufficient for Phase III",
                "fix": "More measured conclusion about need for biomarker selection or randomized data"
            }
        ]
    },
    {
        "id": "clinical_002",
        "title": "Biomarker Validation Study",
        "description": """
        Retrospective study validating a gene expression signature for chemo response.
        
        Methods:
        - Collected archived tumor samples from 200 chemo-treated patients
        - Measured 50-gene expression signature by RNA-seq
        - Divided patients into signature-high vs signature-low groups
        - Compared survival outcomes between groups
        
        Results:
        - Signature-high group (n=80) had better survival (HR=0.6, p=0.01)
        - Multivariate analysis adjusted for age and stage
        
        Conclusion: Our signature predicts chemotherapy benefit and should guide treatment.
        """,
        "flaws": [
            {
                "category": "confounders",
                "type": "confounding_by_indication",
                "severity": "critical",
                "explanation": "Cannot distinguish prognostic vs predictive value - no untreated arm",
                "fix": "Need patients who didn't receive chemo to separate prognosis from prediction"
            },
            {
                "category": "statistics",
                "type": "overfitting",
                "severity": "critical",
                "explanation": "Signature developed and validated in same cohort - need independent validation",
                "fix": "Split into training/validation or use external cohort"
            },
            {
                "category": "confounders",
                "type": "incomplete_adjustment",
                "severity": "major",
                "explanation": "Only adjusted for age and stage - missing performance status, comorbidities",
                "fix": "Adjust for all known prognostic factors"
            },
            {
                "category": "interpretation",
                "type": "correlation_causation",
                "severity": "major",
                "explanation": "'Predicts benefit' implies interaction not demonstrated",
                "fix": "Test for interaction: signature × treatment in survival model"
            }
        ]
    },
    {
        "id": "clinical_003",
        "title": "Device Comparison Trial",
        "description": """
        Prospective study comparing new surgical device to standard technique.
        
        Methods:
        - 100 patients scheduled for surgery were enrolled
        - First 50 patients received standard technique (training period)
        - Next 50 patients received new device (after surgeon trained)
        - Compared operative time, complications, and outcomes
        
        Results:
        - New device: 45 min avg operative time, 10% complications
        - Standard: 60 min avg operative time, 15% complications
        - p<0.05 for both comparisons
        
        Conclusion: New device is superior to standard technique.
        """,
        "flaws": [
            {
                "category": "confounders",
                "type": "time_confound",
                "severity": "critical",
                "explanation": "Sequential enrollment confounds device with learning curve and time trends",
                "fix": "Randomize patients to device vs standard"
            },
            {
                "category": "confounders",
                "type": "operator_effect",
                "severity": "critical",
                "explanation": "Surgeon experience increased during study - later cases benefit from learning",
                "fix": "Account for surgeon experience, randomize to control temporal effects"
            },
            {
                "category": "statistics",
                "type": "multiple_testing",
                "severity": "major",
                "explanation": "Two primary endpoints tested without correction",
                "fix": "Pre-specify single primary endpoint or adjust alpha"
            }
        ]
    }
]


# =============================================================================
# ANIMAL STUDY DESIGN FLAWS
# =============================================================================

ANIMAL_DESIGNS = [
    {
        "id": "animal_001",
        "title": "Mouse Tumor Xenograft Study",
        "description": """
        Testing new drug combination in human cancer xenograft model.
        
        Methods:
        - Implanted MDA-MB-231 cells subcutaneously in female nude mice
        - When tumors reached 100mm³, randomized to 4 groups (n=5 each):
          Vehicle, Drug A, Drug B, Drug A+B
        - Treated for 3 weeks, measured tumors 2x/week
        - Sacrificed when any tumor reached 2000mm³
        
        Results:
        - Combination showed 80% tumor growth inhibition (TGI)
        - Drug A alone: 40% TGI; Drug B alone: 30% TGI
        - Combination significantly better than vehicle (p<0.01)
        
        Conclusion: Drug A and B show synergistic anti-tumor activity.
        """,
        "flaws": [
            {
                "category": "statistics",
                "type": "underpowered",
                "severity": "critical",
                "explanation": "n=5 per group is underpowered for tumor xenograft variability",
                "fix": "Power calculation typically requires n=8-10 per group for 80% power"
            },
            {
                "category": "interpretation",
                "type": "wrong_synergy_claim",
                "severity": "critical",
                "explanation": "Synergy requires specific statistical test (Bliss, Loewe) - 'better than each alone' is additive",
                "fix": "Calculate combination index or use Bliss independence model"
            },
            {
                "category": "statistics",
                "type": "multiple_comparisons",
                "severity": "major",
                "explanation": "Only compared combo to vehicle - need all pairwise comparisons with correction",
                "fix": "ANOVA with post-hoc test (Tukey/Dunnett)"
            },
            {
                "category": "confounders",
                "type": "missing_randomization_details",
                "severity": "minor",
                "explanation": "Randomization method not specified",
                "fix": "Describe randomization method and whether treatment was blinded"
            }
        ]
    },
    {
        "id": "animal_002",
        "title": "Transgenic Mouse Phenotyping",
        "description": """
        Characterizing knockout mouse phenotype.
        
        Methods:
        - Generated Gene X knockout mice on C57BL/6 background
        - Compared KO mice (n=6) to wild-type littermates (n=6)
        - Assessed behavior, metabolism, and organ histology
        - All mice were male, 8-12 weeks old
        
        Results:
        - KO mice showed 20% reduced body weight (p<0.05)
        - KO mice showed anxiety-like behavior in elevated plus maze
        - Histology showed liver steatosis in KO mice
        
        Conclusion: Gene X regulates metabolism and behavior.
        """,
        "flaws": [
            {
                "category": "statistics",
                "type": "underpowered",
                "severity": "major",
                "explanation": "n=6 for behavioral studies typically underpowered due to high variability",
                "fix": "Power analysis for behavioral endpoints typically requires n=10-15"
            },
            {
                "category": "confounders",
                "type": "single_sex",
                "severity": "major",
                "explanation": "Only male mice tested - sex differences are common in metabolism and behavior",
                "fix": "Include both sexes and analyze as a factor, or justify single-sex with literature"
            },
            {
                "category": "controls",
                "type": "genetic_background",
                "severity": "major",
                "explanation": "Backcross generation not specified - could have mixed background effects",
                "fix": "Specify backcross generation (>N10 for congenic) or use multiple backgrounds"
            },
            {
                "category": "statistics",
                "type": "multiple_testing",
                "severity": "major",
                "explanation": "Multiple phenotypes tested without correction",
                "fix": "Pre-specify primary endpoint or correct for multiple testing"
            }
        ]
    },
    {
        "id": "animal_003",
        "title": "Drug Pharmacokinetics Study",
        "description": """
        PK study to determine drug exposure in mice.
        
        Methods:
        - Dosed mice with Drug X at 10, 30, 100 mg/kg oral
        - Collected blood at 0.5, 1, 2, 4, 8, 24 hours
        - n=3 mice per dose per time point (serial sacrifice)
        - Measured plasma drug concentration by LC-MS
        
        Results:
        - Drug showed dose-proportional exposure
        - Half-life approximately 4 hours
        - Cmax at 30 mg/kg was 1000 ng/mL
        
        Conclusion: Drug X has favorable PK supporting once-daily dosing.
        """,
        "flaws": [
            {
                "category": "statistics",
                "type": "insufficient_replicates",
                "severity": "major",
                "explanation": "n=3 provides unreliable PK parameters due to inter-animal variability",
                "fix": "n=3-5 per time point with sparse sampling or composite design"
            },
            {
                "category": "interpretation",
                "type": "extrapolation",
                "severity": "major",
                "explanation": "'Once-daily dosing' claim requires knowing target concentration, not just half-life",
                "fix": "Relate PK to efficacy data or target coverage"
            },
            {
                "category": "technical",
                "type": "missing_validation",
                "severity": "minor",
                "explanation": "LC-MS method validation not mentioned",
                "fix": "Report assay validation parameters (LOQ, linearity, recovery)"
            }
        ]
    }
]


# =============================================================================
# SEQUENCING EXPERIMENT DESIGN FLAWS
# =============================================================================

SEQUENCING_DESIGNS = [
    {
        "id": "seq_001",
        "title": "Bulk RNA-seq Differential Expression",
        "description": """
        RNA-seq to identify genes changed after drug treatment.
        
        Methods:
        - Treated cells with Drug X or DMSO for 24 hours
        - n=2 biological replicates per condition
        - Extracted RNA, prepared libraries with poly-A selection
        - Sequenced on NovaSeq, 30M reads per sample
        - Analyzed with DESeq2, FDR < 0.05
        
        Results:
        - Found 2,500 differentially expressed genes
        - Top pathway: Cell cycle (downregulated)
        
        Conclusion: Drug X causes widespread transcriptional changes affecting cell cycle.
        """,
        "flaws": [
            {
                "category": "statistics",
                "type": "insufficient_replicates",
                "severity": "critical",
                "explanation": "n=2 provides very low statistical power for DE analysis",
                "fix": "Minimum n=3, ideally n=4+ for robust DE detection"
            },
            {
                "category": "confounders",
                "type": "batch_unknown",
                "severity": "major",
                "explanation": "Batch information not provided - could confound treatment",
                "fix": "Process all samples in single batch or include batch as covariate"
            },
            {
                "category": "interpretation",
                "type": "overstatement",
                "severity": "major",
                "explanation": "2,500 DEGs at n=2 likely includes many false positives",
                "fix": "Use more stringent thresholds (FDR<0.01, fold change>2) or validate hits"
            }
        ]
    },
    {
        "id": "seq_002",
        "title": "Single-cell RNA-seq Clustering",
        "description": """
        scRNA-seq to characterize tumor microenvironment.
        
        Methods:
        - Processed 3 tumors and 3 adjacent normal tissues
        - Used 10X Genomics 3' v3, targeted 5,000 cells per sample
        - Filtered to 20,000 total cells after QC
        - Clustered with Seurat using default parameters
        - Identified 15 cell clusters
        
        Results:
        - Found novel fibroblast subtype present only in tumors
        - This subtype expresses unique markers: GeneA, GeneB, GeneC
        
        Conclusion: We discovered a tumor-specific fibroblast population that may 
        promote cancer progression.
        """,
        "flaws": [
            {
                "category": "statistics",
                "type": "underpowered",
                "severity": "major",
                "explanation": "n=3 tumors insufficient to claim 'tumor-specific' - could be patient-specific",
                "fix": "Larger cohort or validate in independent dataset"
            },
            {
                "category": "technical",
                "type": "clustering_artifact",
                "severity": "major",
                "explanation": "Default Seurat parameters may overclustering - resolution not reported",
                "fix": "Report resolution parameter, validate clusters are robust"
            },
            {
                "category": "interpretation",
                "type": "causation_claim",
                "severity": "major",
                "explanation": "'Promotes cancer' is causal claim not supported by correlative data",
                "fix": "Describe as 'associated with' tumors, suggest functional validation"
            },
            {
                "category": "confounders",
                "type": "batch_effect",
                "severity": "major",
                "explanation": "Tumor vs normal from same patients? Processed same day? Unclear",
                "fix": "Describe sample pairing and batch design, use integration methods"
            }
        ]
    },
    {
        "id": "seq_003",
        "title": "ChIP-seq Peak Calling",
        "description": """
        ChIP-seq for transcription factor binding sites.
        
        Methods:
        - Performed ChIP-seq for TF-X in cell line
        - Sequenced input and IP samples
        - Called peaks using MACS2 with default parameters
        - Found 10,000 peaks genome-wide
        - Assigned peaks to nearest gene
        
        Results:
        - TF-X binds promoters of 3,000 genes
        - Motif analysis found expected TF-X motif enriched
        - Correlated with RNA-seq: TF-X targets upregulated
        
        Conclusion: TF-X directly regulates 3,000 genes in this cell type.
        """,
        "flaws": [
            {
                "category": "statistics",
                "type": "insufficient_replicates",
                "severity": "critical",
                "explanation": "n=1 ChIP-seq cannot distinguish signal from noise/artifact",
                "fix": "Minimum n=2 biological replicates, ENCODE requires n=2 with IDR"
            },
            {
                "category": "interpretation",
                "type": "direct_regulation_claim",
                "severity": "major",
                "explanation": "'Directly regulates' requires functional evidence - binding doesn't equal regulation",
                "fix": "Say 'binds near' rather than 'directly regulates'"
            },
            {
                "category": "technical",
                "type": "peak_assignment",
                "severity": "major",
                "explanation": "Nearest gene assignment is simplistic - may miss distal regulation",
                "fix": "Use chromatin interaction data (Hi-C) or more sophisticated assignment"
            },
            {
                "category": "controls",
                "type": "missing_controls",
                "severity": "minor",
                "explanation": "No mention of spike-in controls for quantitative comparison",
                "fix": "Include spike-in for quantitative analysis if comparing conditions"
            }
        ]
    }
]


# =============================================================================
# MULTI-CENTER STUDY DESIGN FLAWS
# =============================================================================

MULTICENTER_DESIGNS = [
    {
        "id": "multicenter_001",
        "title": "Multi-site Biomarker Study",
        "description": """
        Multi-center study to validate diagnostic biomarker.
        
        Methods:
        - Collected samples from 5 hospitals across 3 countries
        - Total n=500 (250 disease, 250 healthy controls)
        - Each site used their standard sample collection protocol
        - Samples shipped to central lab for biomarker measurement
        - Combined all data for ROC analysis
        
        Results:
        - Biomarker AUC = 0.85 for disease vs healthy
        - Sensitivity 80%, Specificity 75%
        
        Conclusion: Biomarker X is a robust diagnostic across diverse populations.
        """,
        "flaws": [
            {
                "category": "confounders",
                "type": "site_heterogeneity",
                "severity": "critical",
                "explanation": "Different collection protocols could introduce site-specific bias",
                "fix": "Standardize protocols or analyze site as a covariate"
            },
            {
                "category": "statistics",
                "type": "pooled_analysis",
                "severity": "major",
                "explanation": "Pooling ignores site-specific performance - should analyze per-site first",
                "fix": "Report per-site results and test for heterogeneity"
            },
            {
                "category": "confounders",
                "type": "population_differences",
                "severity": "major",
                "explanation": "Different demographics, disease stages, comorbidities by site not addressed",
                "fix": "Report demographics by site, stratify or adjust analysis"
            },
            {
                "category": "technical",
                "type": "preanalytical_variables",
                "severity": "major",
                "explanation": "Shipping conditions, storage time, processing delays not standardized",
                "fix": "Record and analyze impact of preanalytical variables"
            }
        ]
    }
]


# =============================================================================
# COMBINED FUNCTIONS
# =============================================================================

def get_all_advanced_designs():
    """Return all advanced flawed designs."""
    return {
        "clinical": CLINICAL_DESIGNS,
        "animal": ANIMAL_DESIGNS,
        "sequencing": SEQUENCING_DESIGNS,
        "multicenter": MULTICENTER_DESIGNS
    }


def get_advanced_design_statistics():
    """Return statistics for advanced designs."""
    all_designs = get_all_advanced_designs()
    total_designs = sum(len(v) for v in all_designs.values())
    total_flaws = sum(
        len(d["flaws"]) 
        for designs in all_designs.values() 
        for d in designs
    )
    
    return {
        "clinical_designs": len(CLINICAL_DESIGNS),
        "animal_designs": len(ANIMAL_DESIGNS),
        "sequencing_designs": len(SEQUENCING_DESIGNS),
        "multicenter_designs": len(MULTICENTER_DESIGNS),
        "total_advanced_designs": total_designs,
        "total_advanced_flaws": total_flaws
    }


if __name__ == "__main__":
    stats = get_advanced_design_statistics()
    print("DesignCheck Advanced Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
