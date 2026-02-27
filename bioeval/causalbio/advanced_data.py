"""
CausalBio Advanced Dataset

Complex perturbation scenarios including:
- Combination therapy predictions
- Resistance mechanism reasoning
- Biomarker response predictions
- Multi-omic integration reasoning
"""

# =============================================================================
# COMBINATION THERAPY PREDICTIONS
# =============================================================================

COMBINATION_TASKS = [
    {
        "id": "combo_001",
        "drugs": ["BRAF inhibitor (vemurafenib)", "MEK inhibitor (trametinib)"],
        "target_disease": "BRAF V600E melanoma",
        "ground_truth": {
            "interaction_type": "synergistic",
            "mechanism": "Vertical pathway inhibition prevents resistance feedback",
            "rationale": [
                "BRAF inhibitor alone causes paradoxical MAPK activation via feedback",
                "MEK inhibitor blocks compensatory MEK activation",
                "Combined inhibition more durable than either alone",
            ],
            "clinical_evidence": "FDA-approved combination, improved PFS vs monotherapy",
            "expected_resistance": "Mutations in NRAS, MEK, or RTK amplification",
        },
    },
    {
        "id": "combo_002",
        "drugs": ["CDK4/6 inhibitor (palbociclib)", "Aromatase inhibitor (letrozole)"],
        "target_disease": "ER+ HER2- breast cancer",
        "ground_truth": {
            "interaction_type": "synergistic",
            "mechanism": "ER drives cyclin D1, CDK4/6 inhibition blocks downstream",
            "rationale": [
                "ER signaling upregulates cyclin D1-CDK4/6",
                "AI reduces ER signaling, CDK4/6i blocks remaining proliferation",
                "Together achieve more complete cell cycle arrest",
            ],
            "clinical_evidence": "FDA-approved, doubled PFS in PALOMA trials",
            "expected_resistance": "RB1 loss, CCNE1 amplification, FAT1 mutations",
        },
    },
    {
        "id": "combo_003",
        "drugs": ["PD-1 inhibitor (pembrolizumab)", "CTLA-4 inhibitor (ipilimumab)"],
        "target_disease": "Metastatic melanoma",
        "ground_truth": {
            "interaction_type": "synergistic",
            "mechanism": "Complementary immune checkpoint release",
            "rationale": [
                "CTLA-4 acts early in T cell activation (lymph node)",
                "PD-1 acts late at tumor site (effector phase)",
                "Combined release amplifies anti-tumor immunity",
            ],
            "clinical_evidence": "Improved response rate but increased toxicity",
            "toxicity_concern": "High rate of immune-related adverse events",
        },
    },
    {
        "id": "combo_004",
        "drugs": ["PARP inhibitor (olaparib)", "ATR inhibitor"],
        "target_disease": "BRCA-wild-type HGSOC",
        "ground_truth": {
            "interaction_type": "synergistic",
            "mechanism": "Dual targeting of DNA damage response",
            "rationale": [
                "PARP inhibition creates replication stress",
                "ATR inhibition prevents checkpoint activation",
                "Cells enter mitosis with damaged DNA → catastrophe",
            ],
            "context": "May extend PARP inhibitor utility to HR-proficient tumors",
            "toxicity_concern": "Overlapping hematologic toxicity",
        },
    },
    {
        "id": "combo_005",
        "drugs": ["BCL-2 inhibitor (venetoclax)", "Hypomethylating agent (azacitidine)"],
        "target_disease": "AML in elderly/unfit patients",
        "ground_truth": {
            "interaction_type": "synergistic",
            "mechanism": "Epigenetic priming + apoptosis induction",
            "rationale": [
                "Azacitidine demethylates pro-apoptotic genes (BIM, PUMA)",
                "Upregulated pro-apoptotics prime cells for BCL-2 inhibition",
                "Together overcome apoptotic threshold",
            ],
            "clinical_evidence": "FDA-approved, improved OS vs azacitidine alone",
            "expected_resistance": "MCL-1 upregulation",
        },
    },
    {
        "id": "combo_006",
        "drugs": ["KRAS G12C inhibitor (sotorasib)", "SHP2 inhibitor"],
        "target_disease": "KRAS G12C NSCLC",
        "ground_truth": {
            "interaction_type": "synergistic (predicted)",
            "mechanism": "Block adaptive resistance mechanism",
            "rationale": [
                "KRAS G12C inhibitor causes RTK-mediated feedback reactivation",
                "SHP2 is required for RTK-to-RAS signaling",
                "SHP2 inhibition blocks resistance pathway",
            ],
            "clinical_status": "In clinical trials",
            "expected_benefit": "Deeper, more durable responses",
        },
    },
]


# =============================================================================
# RESISTANCE MECHANISM PREDICTIONS
# =============================================================================

RESISTANCE_TASKS = [
    {
        "id": "resist_001",
        "drug": "Osimertinib (3rd-gen EGFR TKI)",
        "initial_context": "EGFR del19 or L858R NSCLC",
        "question": "Predict mechanisms of acquired resistance after initial response",
        "ground_truth": {
            "on_target_resistance": [
                {"mutation": "C797S", "frequency": "~15%", "mechanism": "Prevents covalent binding"},
                {"mutation": "G796/L792 mutations", "frequency": "<5%", "mechanism": "Steric hindrance"},
            ],
            "off_target_resistance": [
                {"mechanism": "MET amplification", "frequency": "~15%", "bypass": "Activates PI3K/AKT independently"},
                {"mechanism": "HER2 amplification", "frequency": "~5%", "bypass": "Alternative RTK activation"},
                {"mechanism": "SCLC transformation", "frequency": "~5%", "note": "Lineage plasticity, RB1/TP53 loss"},
                {"mechanism": "PIK3CA mutation", "frequency": "~5%", "bypass": "Downstream pathway activation"},
            ],
            "clinical_implications": "Rebiopsy at progression to guide next-line therapy",
        },
    },
    {
        "id": "resist_002",
        "drug": "Venetoclax (BCL-2 inhibitor)",
        "initial_context": "CLL",
        "question": "Predict mechanisms of acquired resistance",
        "ground_truth": {
            "on_target_resistance": [
                {"mutation": "BCL2 G101V", "mechanism": "Reduces venetoclax binding affinity"},
                {"mutation": "BCL2 D103 mutations", "mechanism": "Alters binding pocket"},
            ],
            "off_target_resistance": [
                {
                    "mechanism": "MCL-1 upregulation",
                    "frequency": "common",
                    "note": "Shifts dependency to alternative anti-apoptotic",
                },
                {"mechanism": "BTG1/CDKN2A loss", "note": "Reduces apoptotic priming"},
                {"mechanism": "BAX mutations", "note": "Prevents apoptosis execution"},
            ],
            "clinical_implications": "Consider MCL-1 inhibitor combinations",
        },
    },
    {
        "id": "resist_003",
        "drug": "Imatinib",
        "initial_context": "CML",
        "question": "Predict resistance mechanisms and second-line options",
        "ground_truth": {
            "on_target_resistance": [
                {"mutation": "T315I", "frequency": "~20%", "note": "Gatekeeper mutation, resistant to all 2nd-gen TKIs"},
                {"mutation": "F317L, Y253H", "mechanism": "P-loop mutations"},
                {"mutation": "BCR-ABL amplification", "mechanism": "Overwhelms drug"},
            ],
            "second_line_options": {
                "T315I": "Ponatinib (3rd-gen TKI)",
                "other_mutations": "Dasatinib or nilotinib based on mutation",
                "amplification": "Dose escalation or switch TKI",
            },
        },
    },
    {
        "id": "resist_004",
        "drug": "Anti-PD-1 (pembrolizumab)",
        "initial_context": "Melanoma with initial response",
        "question": "Predict mechanisms of acquired resistance to immunotherapy",
        "ground_truth": {
            "tumor_intrinsic": [
                {"mechanism": "B2M loss", "effect": "Loss of MHC-I surface expression"},
                {"mechanism": "JAK1/JAK2 mutations", "effect": "Cannot respond to IFN-γ"},
                {"mechanism": "Antigen loss", "effect": "Immunoediting removes targetable antigens"},
            ],
            "tumor_microenvironment": [
                {"mechanism": "T cell exhaustion", "markers": "TOX, EOMES upregulation"},
                {"mechanism": "Alternative checkpoint upregulation", "examples": "LAG-3, TIM-3, TIGIT"},
                {"mechanism": "Immunosuppressive cells", "examples": "Tregs, MDSCs, TAMs"},
            ],
            "clinical_implications": "Consider combination with other checkpoints or cellular therapy",
        },
    },
]


# =============================================================================
# BIOMARKER RESPONSE PREDICTIONS
# =============================================================================

BIOMARKER_TASKS = [
    {
        "id": "biomarker_001",
        "biomarker": "TMB-High (≥10 mut/Mb)",
        "therapy": "Pembrolizumab",
        "tumor_type": "Solid tumors (tissue-agnostic)",
        "question": "Predict response and explain mechanism",
        "ground_truth": {
            "expected_response": "Increased likelihood of response (~30-40% ORR)",
            "mechanism": [
                "High TMB → more neoantigens",
                "More neoantigens → more T cell recognition",
                "PD-1 blockade releases T cell inhibition",
            ],
            "caveats": [
                "TMB is probabilistic, not deterministic",
                "Some TMB-high tumors are 'cold' (no T cell infiltration)",
                "Cutoff varies by assay and tumor type",
            ],
            "confounders": ["MSI status often correlates with TMB"],
        },
    },
    {
        "id": "biomarker_002",
        "biomarker": "HRD score high (≥42)",
        "therapy": "PARP inhibitor (olaparib)",
        "tumor_type": "Ovarian cancer",
        "question": "Predict response in BRCA wild-type patient with high HRD score",
        "ground_truth": {
            "expected_response": "Moderate benefit, less than BRCA-mutant",
            "mechanism": [
                "HRD indicates genomic scars from past HR deficiency",
                "May or may not have current HR deficiency",
                "PARP inhibition exploits HR deficiency",
            ],
            "caveats": [
                "HRD score is historical - tumor may have reverted",
                "Less durable responses than BRCA-mutant",
                "Benefit seen in maintenance setting post-platinum",
            ],
            "alternative_biomarkers": ["RAD51 foci (functional HR test)", "BRCA reversion testing"],
        },
    },
    {
        "id": "biomarker_003",
        "biomarker": "NTRK fusion",
        "therapy": "Larotrectinib",
        "tumor_type": "Any solid tumor",
        "question": "Predict response to TRK inhibitor",
        "ground_truth": {
            "expected_response": "High response rate (~75% ORR), tissue-agnostic",
            "mechanism": [
                "NTRK fusion creates constitutively active kinase",
                "TRK inhibitor blocks oncogenic signaling",
                "Fusion is typically the sole driver",
            ],
            "key_points": [
                "True oncogene addiction - very targetable",
                "Response independent of tumor histology",
                "Acquired resistance via kinase domain mutations (G595R, G667C)",
            ],
            "second_line": "Selitrectinib (next-gen TRK inhibitor) for resistance mutations",
        },
    },
    {
        "id": "biomarker_004",
        "biomarker": "EGFR exon 20 insertion",
        "therapy": "Standard EGFR TKIs (erlotinib, gefitinib, osimertinib)",
        "tumor_type": "NSCLC",
        "question": "Predict response compared to common EGFR mutations",
        "ground_truth": {
            "expected_response": "Poor response to standard EGFR TKIs",
            "mechanism": [
                "Exon 20 insertions cause steric changes",
                "Standard TKIs cannot bind effectively",
                "Different binding pocket conformation",
            ],
            "alternative_therapies": [
                "Amivantamab (EGFR-MET bispecific antibody)",
                "Mobocertinib (exon 20-specific TKI)",
                "Poziotinib (in clinical trials)",
            ],
            "clinical_implication": "Must distinguish exon 20 ins from del19/L858R",
        },
    },
    {
        "id": "biomarker_005",
        "biomarker": "PD-L1 TPS ≥50%",
        "therapy": "Pembrolizumab monotherapy",
        "tumor_type": "NSCLC first-line",
        "question": "Predict response and compare to chemotherapy",
        "ground_truth": {
            "expected_response": "Superior to chemotherapy, ~45% ORR",
            "mechanism": [
                "High PD-L1 indicates adaptive immune resistance",
                "Tumor is being recognized by immune system",
                "PD-1 blockade releases existing anti-tumor immunity",
            ],
            "caveats": [
                "PD-L1 is imperfect - some PD-L1 negative patients respond",
                "Intratumoral heterogeneity in PD-L1 expression",
                "Assay and scoring variations between tests",
            ],
            "contraindications": "Check for EGFR/ALK/ROS1 - targeted therapy better if present",
        },
    },
]


# =============================================================================
# MULTI-OMIC INTEGRATION REASONING
# =============================================================================

MULTI_OMIC_TASKS = [
    {
        "id": "multiomics_001",
        "scenario": "RNA-seq shows Gene X is highly expressed, but proteomics shows protein X is low",
        "question": "What biological explanations could account for this discordance?",
        "ground_truth": {
            "explanations": [
                {"mechanism": "Translational repression", "example": "miRNA targeting mRNA, preventing translation"},
                {"mechanism": "Protein degradation", "example": "Ubiquitin-proteasome pathway actively degrading protein"},
                {"mechanism": "Transcript variant", "example": "Detected transcript may be non-coding or NMD target"},
                {"mechanism": "Technical artifact", "example": "Protein below detection limit or poor antibody in MS"},
            ],
            "follow_up_experiments": [
                "Ribosome profiling to assess translation",
                "Protein half-life measurement (CHX chase)",
                "Validate transcript with targeted qPCR for specific isoforms",
            ],
        },
    },
    {
        "id": "multiomics_002",
        "scenario": "ATAC-seq shows open chromatin at Gene Y promoter, but RNA-seq shows no expression",
        "question": "What could explain accessible but inactive chromatin?",
        "ground_truth": {
            "explanations": [
                {"mechanism": "Poised promoter", "note": "H3K4me3 present but also H3K27me3 (bivalent)"},
                {"mechanism": "Missing activating TF", "note": "Chromatin open but required TF not expressed"},
                {"mechanism": "Repressive TF bound", "note": "Repressor occupying accessible site"},
                {"mechanism": "Enhancer requirement", "note": "Promoter accessible but enhancer inactive"},
                {"mechanism": "Paused polymerase", "note": "Pol II loaded but paused, not elongating"},
            ],
            "follow_up_experiments": [
                "ChIP-seq for H3K27me3 (bivalent) and H3K27ac (active)",
                "Check expression of known activating TFs",
                "GRO-seq or PRO-seq for nascent transcription",
            ],
        },
    },
    {
        "id": "multiomics_003",
        "scenario": "DNA methylation is reduced at Gene Z promoter after treatment, but expression doesn't change",
        "question": "Why might demethylation not lead to activation?",
        "ground_truth": {
            "explanations": [
                {"mechanism": "Insufficient demethylation", "note": "Partial demethylation may not be enough"},
                {"mechanism": "Other repressive marks", "note": "H3K9me3 or H3K27me3 still present"},
                {"mechanism": "Missing TFs", "note": "Site accessible but activators not expressed"},
                {"mechanism": "Kinetics", "note": "Expression may increase later (check time course)"},
                {"mechanism": "Not the causal promoter", "note": "Alternative TSS may be functional"},
            ],
            "key_insight": "DNA methylation is necessary but not sufficient for activation - must also have activating conditions",
        },
    },
    {
        "id": "multiomics_004",
        "scenario": "Patient tumor shows BRCA1 mutation, but functional assay shows intact HR",
        "question": "How could HR be intact despite BRCA1 mutation?",
        "ground_truth": {
            "explanations": [
                {"mechanism": "Hypomorphic mutation", "note": "Mutation reduces but doesn't eliminate function"},
                {"mechanism": "Reversion mutation", "note": "Second mutation restored reading frame"},
                {"mechanism": "Alternative splicing", "note": "Exon skipping bypasses mutation"},
                {"mechanism": "BRCA1 paralog compensation", "note": "Other HR genes compensating"},
                {"mechanism": "Somatic mosaicism", "note": "Mutation not present in all cells"},
            ],
            "clinical_implication": "Patient may not respond well to PARP inhibitor despite BRCA1 mutation",
            "recommended_test": "RAD51 foci assay is more predictive than genomic BRCA status",
        },
    },
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_combination_tasks():
    """Return combination therapy tasks."""
    return COMBINATION_TASKS


def get_resistance_tasks():
    """Return resistance mechanism tasks."""
    return RESISTANCE_TASKS


def get_biomarker_tasks():
    """Return biomarker response tasks."""
    return BIOMARKER_TASKS


def get_multi_omic_tasks():
    """Return multi-omic integration tasks."""
    return MULTI_OMIC_TASKS


def get_advanced_statistics():
    """Return statistics for advanced tasks."""
    return {
        "combination_tasks": len(COMBINATION_TASKS),
        "resistance_tasks": len(RESISTANCE_TASKS),
        "biomarker_tasks": len(BIOMARKER_TASKS),
        "multi_omic_tasks": len(MULTI_OMIC_TASKS),
        "total_advanced": len(COMBINATION_TASKS) + len(RESISTANCE_TASKS) + len(BIOMARKER_TASKS) + len(MULTI_OMIC_TASKS),
    }


if __name__ == "__main__":
    stats = get_advanced_statistics()
    print("CausalBio Advanced Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
