"""
CausalBio Extended Dataset

Comprehensive perturbation prediction tasks covering gene knockouts, 
drug responses, pathway reasoning, and epistasis.

These tasks are designed to test causal biological reasoning using
ground truth from experimental data (DepMap, CMap, literature).
"""

# =============================================================================
# GENE KNOCKOUT PREDICTIONS
# =============================================================================

KNOCKOUT_TASKS = [
    # -------------------------------------------------------------------------
    # ONCOGENE DEPENDENCIES
    # -------------------------------------------------------------------------
    {
        "id": "ko_001",
        "gene": "KRAS",
        "cell_line": "A549",
        "cell_type": "NSCLC (KRAS G12S mutant)",
        "ground_truth": {
            "effect": "essential",
            "depmap_score": -1.2,
            "explanation": "Oncogene addiction - KRAS-mutant cells depend on mutant KRAS signaling"
        },
        "reasoning_type": "oncogene_addiction"
    },
    {
        "id": "ko_002",
        "gene": "BRAF",
        "cell_line": "A375",
        "cell_type": "Melanoma (BRAF V600E)",
        "ground_truth": {
            "effect": "essential",
            "depmap_score": -1.5,
            "explanation": "BRAF V600E is the primary driver - cells die without it"
        },
        "reasoning_type": "oncogene_addiction"
    },
    {
        "id": "ko_003",
        "gene": "EGFR",
        "cell_line": "PC9",
        "cell_type": "NSCLC (EGFR del19)",
        "ground_truth": {
            "effect": "essential",
            "depmap_score": -1.3,
            "explanation": "EGFR-mutant NSCLC lines are addicted to EGFR signaling"
        },
        "reasoning_type": "oncogene_addiction"
    },
    {
        "id": "ko_004",
        "gene": "BCR-ABL",
        "cell_line": "K562",
        "cell_type": "CML (BCR-ABL+)",
        "ground_truth": {
            "effect": "essential",
            "depmap_score": -2.0,
            "explanation": "BCR-ABL fusion is the sole driver of CML proliferation"
        },
        "reasoning_type": "oncogene_addiction"
    },
    {
        "id": "ko_005",
        "gene": "MYC",
        "cell_line": "Raji",
        "cell_type": "Burkitt lymphoma (MYC translocation)",
        "ground_truth": {
            "effect": "essential",
            "depmap_score": -1.8,
            "explanation": "MYC translocation drives proliferation in Burkitt lymphoma"
        },
        "reasoning_type": "oncogene_addiction"
    },
    
    # -------------------------------------------------------------------------
    # TUMOR SUPPRESSOR CONTEXT
    # -------------------------------------------------------------------------
    {
        "id": "ko_006",
        "gene": "TP53",
        "cell_line": "A549",
        "cell_type": "NSCLC (TP53 wild-type)",
        "ground_truth": {
            "effect": "non-essential",
            "depmap_score": 0.1,
            "explanation": "Loss of TP53 provides growth advantage but not immediately lethal"
        },
        "reasoning_type": "tumor_suppressor"
    },
    {
        "id": "ko_007",
        "gene": "RB1",
        "cell_line": "MCF7",
        "cell_type": "Breast cancer (RB1 wild-type)",
        "ground_truth": {
            "effect": "mildly_beneficial",
            "depmap_score": 0.2,
            "explanation": "RB1 loss removes cell cycle checkpoint, may enhance proliferation"
        },
        "reasoning_type": "tumor_suppressor"
    },
    {
        "id": "ko_008",
        "gene": "PTEN",
        "cell_line": "BT549",
        "cell_type": "Breast cancer (PTEN-null)",
        "ground_truth": {
            "effect": "non-essential",
            "depmap_score": 0.0,
            "explanation": "Already PTEN-null - additional knockout has no effect"
        },
        "reasoning_type": "pre_existing_loss"
    },
    {
        "id": "ko_009",
        "gene": "BRCA1",
        "cell_line": "HCC1937",
        "cell_type": "Breast cancer (BRCA1-mutant)",
        "ground_truth": {
            "effect": "non-essential",
            "depmap_score": 0.05,
            "explanation": "Already BRCA1-deficient - no additional effect"
        },
        "reasoning_type": "pre_existing_loss"
    },
    
    # -------------------------------------------------------------------------
    # SYNTHETIC LETHALITY
    # -------------------------------------------------------------------------
    {
        "id": "ko_010",
        "gene": "PARP1",
        "cell_line": "HCC1937",
        "cell_type": "Breast cancer (BRCA1-mutant)",
        "ground_truth": {
            "effect": "essential",
            "depmap_score": -0.9,
            "explanation": "Synthetic lethality - BRCA1-deficient cells depend on PARP for DNA repair"
        },
        "reasoning_type": "synthetic_lethality"
    },
    {
        "id": "ko_011",
        "gene": "PRMT5",
        "cell_line": "MTAP-deleted cancer cells",
        "cell_type": "Various (MTAP-deleted)",
        "ground_truth": {
            "effect": "essential",
            "depmap_score": -1.0,
            "explanation": "MTAP deletion creates dependency on PRMT5 for methionine salvage"
        },
        "reasoning_type": "synthetic_lethality"
    },
    {
        "id": "ko_012",
        "gene": "POLQ",
        "cell_line": "HCC1937",
        "cell_type": "Breast cancer (BRCA1-mutant)",
        "ground_truth": {
            "effect": "essential",
            "depmap_score": -0.7,
            "explanation": "HR-deficient cells depend on POLQ-mediated alternative end joining"
        },
        "reasoning_type": "synthetic_lethality"
    },
    
    # -------------------------------------------------------------------------
    # CORE ESSENTIAL GENES
    # -------------------------------------------------------------------------
    {
        "id": "ko_013",
        "gene": "RPL13",
        "cell_line": "any",
        "cell_type": "universal",
        "ground_truth": {
            "effect": "essential",
            "depmap_score": -1.5,
            "explanation": "Ribosomal protein - essential for protein synthesis in all cells"
        },
        "reasoning_type": "core_essential"
    },
    {
        "id": "ko_014",
        "gene": "POLR2A",
        "cell_line": "any",
        "cell_type": "universal",
        "ground_truth": {
            "effect": "essential",
            "depmap_score": -2.0,
            "explanation": "RNA Pol II subunit - required for mRNA transcription"
        },
        "reasoning_type": "core_essential"
    },
    {
        "id": "ko_015",
        "gene": "SF3B1",
        "cell_line": "any",
        "cell_type": "universal",
        "ground_truth": {
            "effect": "essential",
            "depmap_score": -1.8,
            "explanation": "Splicing factor - essential for mRNA processing"
        },
        "reasoning_type": "core_essential"
    },
    
    # -------------------------------------------------------------------------
    # CONTEXT-DEPENDENT
    # -------------------------------------------------------------------------
    {
        "id": "ko_016",
        "gene": "SLC7A11",
        "cell_line": "KEAP1-mutant cells",
        "cell_type": "NSCLC (KEAP1-mutant)",
        "ground_truth": {
            "effect": "essential",
            "depmap_score": -0.8,
            "explanation": "KEAP1-mutant cells have high NRF2 activity and depend on cystine import"
        },
        "reasoning_type": "context_dependency"
    },
    {
        "id": "ko_017",
        "gene": "KRAS",
        "cell_line": "MCF7",
        "cell_type": "Breast cancer (KRAS wild-type)",
        "ground_truth": {
            "effect": "non-essential",
            "depmap_score": 0.0,
            "explanation": "KRAS wild-type cells don't depend on KRAS - other drivers present"
        },
        "reasoning_type": "context_dependency"
    },
    {
        "id": "ko_018",
        "gene": "WRN",
        "cell_line": "MSI-high cancer cells",
        "cell_type": "Colorectal (MSI-high)",
        "ground_truth": {
            "effect": "essential",
            "depmap_score": -1.2,
            "explanation": "MSI-high cells have expanded TA dinucleotide repeats causing WRN dependency"
        },
        "reasoning_type": "synthetic_lethality"
    }
]


# =============================================================================
# PATHWAY REASONING TASKS
# =============================================================================

PATHWAY_TASKS = [
    # -------------------------------------------------------------------------
    # RTK SIGNALING
    # -------------------------------------------------------------------------
    {
        "id": "pathway_001",
        "perturbation": "EGFR inhibitor (erlotinib)",
        "cell_context": "EGFR-mutant NSCLC",
        "ground_truth": {
            "affected_pathways": [
                {"pathway": "RAS-MAPK", "direction": "decreased", "key_nodes": ["RAS", "RAF", "MEK", "ERK"]},
                {"pathway": "PI3K-AKT", "direction": "decreased", "key_nodes": ["PI3K", "AKT", "mTOR"]},
                {"pathway": "STAT3", "direction": "decreased", "key_nodes": ["JAK", "STAT3"]},
            ],
            "transcriptional_effects": {
                "downregulated": ["MYC", "CCND1", "BCL2", "VEGFA"],
                "upregulated": ["BIM", "p27", "FOXO targets"]
            },
            "phenotype": "G1 arrest, apoptosis in sensitive cells",
            "resistance_mechanisms": ["T790M mutation", "MET amplification", "HER2 amplification"]
        }
    },
    {
        "id": "pathway_002",
        "perturbation": "HER2 inhibitor (trastuzumab + lapatinib)",
        "cell_context": "HER2+ breast cancer",
        "ground_truth": {
            "affected_pathways": [
                {"pathway": "PI3K-AKT", "direction": "decreased", "key_nodes": ["PI3K", "AKT"]},
                {"pathway": "RAS-MAPK", "direction": "decreased", "key_nodes": ["ERK"]},
            ],
            "transcriptional_effects": {
                "downregulated": ["MYC", "CCND1", "survival genes"],
                "upregulated": ["p27", "pro-apoptotic genes"]
            },
            "phenotype": "Growth arrest, ADCC (trastuzumab)",
            "resistance_mechanisms": ["PIK3CA mutation", "PTEN loss", "HER3 upregulation"]
        }
    },
    
    # -------------------------------------------------------------------------
    # MAPK PATHWAY
    # -------------------------------------------------------------------------
    {
        "id": "pathway_003",
        "perturbation": "BRAF V600E inhibitor (vemurafenib)",
        "cell_context": "BRAF V600E melanoma",
        "ground_truth": {
            "affected_pathways": [
                {"pathway": "MAPK", "direction": "decreased", "key_nodes": ["BRAF", "MEK", "ERK"]},
            ],
            "transcriptional_effects": {
                "downregulated": ["MYC", "CCND1", "DUSP6", "SPRY"],
                "upregulated": ["BIM", "differentiation genes"]
            },
            "phenotype": "Rapid tumor regression in sensitive cells",
            "resistance_mechanisms": ["NRAS mutation", "BRAF amplification", "MEK mutation", "RTK upregulation"],
            "paradox": "Activates MAPK in BRAF-WT cells via RAF dimerization"
        }
    },
    {
        "id": "pathway_004",
        "perturbation": "MEK inhibitor (trametinib)",
        "cell_context": "KRAS-mutant cancer",
        "ground_truth": {
            "affected_pathways": [
                {"pathway": "MAPK", "direction": "decreased", "key_nodes": ["MEK1/2", "ERK1/2"]},
            ],
            "transcriptional_effects": {
                "downregulated": ["FOS", "JUN", "EGR1", "DUSP6"],
                "upregulated": ["BIM", "p27"]
            },
            "phenotype": "Cytostatic effect, less apoptosis than expected",
            "compensatory_mechanisms": ["PI3K pathway activation", "RTK reactivation", "CRAF upregulation"]
        }
    },
    
    # -------------------------------------------------------------------------
    # PI3K-AKT-mTOR
    # -------------------------------------------------------------------------
    {
        "id": "pathway_005",
        "perturbation": "mTORC1 inhibitor (rapamycin)",
        "cell_context": "general cancer cells",
        "ground_truth": {
            "affected_pathways": [
                {"pathway": "mTORC1 signaling", "direction": "decreased", "key_nodes": ["S6K", "4EBP1"]},
                {"pathway": "Autophagy", "direction": "increased", "key_nodes": ["ULK1", "ATG genes"]},
            ],
            "transcriptional_effects": {
                "downregulated": ["ribosome biogenesis genes", "SREBP targets"],
                "upregulated": ["autophagy genes", "FOXO targets"]
            },
            "phenotype": "Cytostatic, autophagy induction",
            "compensatory_mechanisms": ["AKT activation via S6K-IRS1 feedback relief", "mTORC2 still active"]
        }
    },
    {
        "id": "pathway_006",
        "perturbation": "PI3K inhibitor (alpelisib)",
        "cell_context": "PIK3CA-mutant breast cancer",
        "ground_truth": {
            "affected_pathways": [
                {"pathway": "PI3K-AKT", "direction": "decreased", "key_nodes": ["PI3K", "AKT", "FOXO"]},
                {"pathway": "mTOR", "direction": "decreased", "key_nodes": ["mTORC1", "mTORC2"]},
            ],
            "transcriptional_effects": {
                "downregulated": ["glycolysis genes", "lipogenesis genes"],
                "upregulated": ["FOXO targets", "apoptosis genes"]
            },
            "phenotype": "Growth arrest, hyperglycemia (systemic effect)",
            "side_effects": ["Hyperglycemia due to insulin signaling inhibition"]
        }
    },
    
    # -------------------------------------------------------------------------
    # CELL CYCLE
    # -------------------------------------------------------------------------
    {
        "id": "pathway_007",
        "perturbation": "CDK4/6 inhibitor (palbociclib)",
        "cell_context": "ER+ breast cancer",
        "ground_truth": {
            "affected_pathways": [
                {"pathway": "Cell cycle G1-S", "direction": "arrested", "key_nodes": ["CDK4", "CDK6", "RB"]},
            ],
            "transcriptional_effects": {
                "downregulated": ["E2F targets", "S-phase genes", "CCNE1", "CCNA2"],
                "upregulated": ["senescence markers"]
            },
            "phenotype": "G1 arrest, senescence",
            "resistance_mechanisms": ["RB1 loss", "CCNE1 amplification", "CDK6 amplification"]
        }
    },
    
    # -------------------------------------------------------------------------
    # DNA DAMAGE RESPONSE
    # -------------------------------------------------------------------------
    {
        "id": "pathway_008",
        "perturbation": "PARP inhibitor (olaparib)",
        "cell_context": "BRCA-mutant cancer",
        "ground_truth": {
            "affected_pathways": [
                {"pathway": "Base excision repair", "direction": "impaired", "key_nodes": ["PARP1", "XRCC1"]},
                {"pathway": "Replication fork stability", "direction": "impaired", "key_nodes": ["stalled forks"]},
            ],
            "mechanism": "PARP trapping creates toxic DNA-protein complexes; HR-deficient cells cannot repair",
            "phenotype": "Synthetic lethality in HR-deficient cells, replication catastrophe",
            "resistance_mechanisms": ["BRCA reversion", "53BP1 loss", "PARP1 mutation", "drug efflux"]
        }
    },
    {
        "id": "pathway_009",
        "perturbation": "ATR inhibitor",
        "cell_context": "ATM-deficient cancer",
        "ground_truth": {
            "affected_pathways": [
                {"pathway": "Replication stress response", "direction": "impaired", "key_nodes": ["ATR", "CHK1"]},
            ],
            "mechanism": "ATM-deficient cells rely on ATR for DNA damage response",
            "phenotype": "Synthetic lethality, replication catastrophe",
            "context_dependency": "Requires high replication stress background"
        }
    },
    
    # -------------------------------------------------------------------------
    # METABOLISM
    # -------------------------------------------------------------------------
    {
        "id": "pathway_010",
        "perturbation": "Glutaminase inhibitor (CB-839)",
        "cell_context": "MYC-driven cancer",
        "ground_truth": {
            "affected_pathways": [
                {"pathway": "Glutaminolysis", "direction": "blocked", "key_nodes": ["GLS", "glutamate"]},
                {"pathway": "TCA cycle", "direction": "reduced", "key_nodes": ["α-ketoglutarate"]},
            ],
            "transcriptional_effects": {
                "downregulated": ["biosynthesis genes"],
                "upregulated": ["stress response genes", "ATF4 targets"]
            },
            "phenotype": "Growth arrest in glutamine-dependent cells",
            "context_dependency": "MYC-high cells are glutamine-addicted"
        }
    }
]


# =============================================================================
# DRUG RESPONSE PREDICTIONS
# =============================================================================

DRUG_RESPONSE_TASKS = [
    {
        "id": "drug_001",
        "drug": "Dexamethasone",
        "cell_type": "T lymphocytes",
        "concentration": "100 nM",
        "duration": "24 hours",
        "ground_truth": {
            "mechanism": "Glucocorticoid receptor activation → transcriptional regulation",
            "upregulated": ["GILZ/TSC22D3", "FKBP5", "DUSP1", "SGK1", "PER1"],
            "downregulated": ["IL2", "IFNG", "TNF", "IL6", "CCL2"],
            "phenotype": "Immunosuppression, T cell apoptosis",
            "clinical_use": "Immunosuppression, lymphoid malignancies"
        }
    },
    {
        "id": "drug_002",
        "drug": "Imatinib",
        "cell_type": "BCR-ABL+ CML cells (K562)",
        "concentration": "1 μM",
        "duration": "24 hours",
        "ground_truth": {
            "mechanism": "BCR-ABL kinase inhibition → loss of survival signaling",
            "upregulated": ["BIM/BCL2L11", "CDKN1B/p27", "PUMA", "BAX"],
            "downregulated": ["MYC", "CCND1", "BCL2", "MCL1", "STAT5 targets"],
            "phenotype": "Cell cycle arrest, apoptosis",
            "clinical_use": "First-line CML treatment"
        }
    },
    {
        "id": "drug_003",
        "drug": "Interferon-alpha",
        "cell_type": "Cancer cells / immune cells",
        "concentration": "1000 U/mL",
        "duration": "6 hours",
        "ground_truth": {
            "mechanism": "IFNAR activation → JAK-STAT signaling",
            "upregulated": ["ISG15", "MX1", "OAS1", "IFIT1", "IRF7", "STAT1"],
            "downregulated": ["cell cycle genes (indirect)"],
            "phenotype": "Antiviral state, immune activation, growth inhibition",
            "clinical_use": "Hepatitis, melanoma, hairy cell leukemia"
        }
    },
    {
        "id": "drug_004",
        "drug": "Nutlin-3a",
        "cell_type": "TP53 wild-type cancer cells",
        "concentration": "10 μM",
        "duration": "24 hours",
        "ground_truth": {
            "mechanism": "MDM2 inhibition → p53 stabilization and activation",
            "upregulated": ["CDKN1A/p21", "MDM2", "BAX", "PUMA", "GADD45A", "TIGAR"],
            "downregulated": ["indirect via p53-mediated arrest"],
            "phenotype": "G1/G2 arrest, apoptosis in p53-WT cells only",
            "context_dependency": "No effect in TP53-mutant cells"
        }
    },
    {
        "id": "drug_005",
        "drug": "JQ1 (BET inhibitor)",
        "cell_type": "MYC-driven cancer cells",
        "concentration": "500 nM",
        "duration": "24 hours",
        "ground_truth": {
            "mechanism": "Displaces BRD4 from chromatin → disrupts super-enhancers",
            "upregulated": ["HEXIM1", "CDKN1A"],
            "downregulated": ["MYC", "BCL2", "FOSL1", "super-enhancer targets"],
            "phenotype": "MYC suppression, growth arrest, differentiation",
            "clinical_relevance": "Effective in MYC-amplified cancers, NUT midline carcinoma"
        }
    },
    {
        "id": "drug_006",
        "drug": "Azacitidine (DNA methyltransferase inhibitor)",
        "cell_type": "MDS/AML cells",
        "concentration": "1 μM",
        "duration": "72 hours",
        "ground_truth": {
            "mechanism": "DNA demethylation → reactivation of silenced genes",
            "upregulated": ["Tumor suppressors (p15, p16)", "ERV transcripts", "dsRNA sensors"],
            "downregulated": ["proliferation genes (indirect)"],
            "phenotype": "Differentiation, viral mimicry immune response",
            "delayed_effect": "Requires multiple cell divisions for incorporation"
        }
    },
    {
        "id": "drug_007",
        "drug": "Venetoclax (BCL2 inhibitor)",
        "cell_type": "CLL cells",
        "concentration": "100 nM",
        "duration": "4 hours",
        "ground_truth": {
            "mechanism": "BCL2 inhibition → release of pro-apoptotic proteins → MOMP",
            "upregulated": ["Caspase activation (protein level)"],
            "downregulated": ["N/A - mechanism is protein-level"],
            "phenotype": "Rapid apoptosis in BCL2-dependent cells",
            "context_dependency": "Requires BCL2 dependency - MCL1-high cells resistant"
        }
    },
    {
        "id": "drug_008",
        "drug": "Selumetinib (MEK inhibitor)",
        "cell_type": "KRAS-mutant cancer cells",
        "concentration": "1 μM",
        "duration": "24 hours",
        "ground_truth": {
            "mechanism": "MEK1/2 inhibition → loss of ERK signaling",
            "upregulated": ["BIM", "p27", "autophagy genes"],
            "downregulated": ["DUSP6", "SPRY2", "FOS", "EGR1", "MYC"],
            "phenotype": "Cytostatic in most contexts",
            "feedback": "Loss of negative feedback leads to RAF/MEK reactivation"
        }
    }
]


# =============================================================================
# EPISTASIS / GENETIC INTERACTION TASKS
# =============================================================================

EPISTASIS_TASKS = [
    {
        "id": "epi_001",
        "gene_a": "BRCA1",
        "gene_b": "PARP1",
        "context": "Breast cancer",
        "ground_truth": {
            "interaction_type": "synthetic_lethal",
            "single_effects": {
                "BRCA1_loss": "HR deficiency, viable",
                "PARP1_loss": "Minor effect, viable"
            },
            "combined_effect": "Lethal - trapped PARP + no HR = replication catastrophe",
            "mechanism": "PARP inhibition creates lesions requiring HR for repair",
            "clinical_relevance": "Basis for PARP inhibitor therapy in BRCA-mutant cancers"
        }
    },
    {
        "id": "epi_002",
        "gene_a": "BRCA1",
        "gene_b": "53BP1",
        "context": "Breast cancer",
        "ground_truth": {
            "interaction_type": "suppressive",
            "single_effects": {
                "BRCA1_loss": "HR deficiency, PARP-sensitive",
                "53BP1_loss": "Mild HR defect"
            },
            "combined_effect": "53BP1 loss partially rescues BRCA1 deficiency",
            "mechanism": "53BP1 blocks resection; its loss allows resection even without BRCA1",
            "clinical_relevance": "53BP1 loss causes PARP inhibitor resistance"
        }
    },
    {
        "id": "epi_003",
        "gene_a": "KRAS",
        "gene_b": "STK11/LKB1",
        "context": "Lung cancer",
        "ground_truth": {
            "interaction_type": "enhancing",
            "single_effects": {
                "KRAS_mut": "Proliferative drive",
                "STK11_loss": "Metabolic dysregulation"
            },
            "combined_effect": "Aggressive phenotype, immunotherapy resistance",
            "mechanism": "STK11 loss removes AMPK-mediated metabolic checkpoint",
            "clinical_relevance": "KRAS-STK11 co-mutation = poor prognosis, IO resistance"
        }
    },
    {
        "id": "epi_004",
        "gene_a": "RB1",
        "gene_b": "TP53",
        "context": "SCLC transformation",
        "ground_truth": {
            "interaction_type": "synergistic",
            "single_effects": {
                "RB1_loss": "Cell cycle checkpoint loss",
                "TP53_loss": "DNA damage checkpoint loss"
            },
            "combined_effect": "Enables neuroendocrine transformation (SCLC)",
            "mechanism": "Combined checkpoint loss allows lineage plasticity",
            "clinical_relevance": "Seen in de novo SCLC and EGFR-TKI transformed cases"
        }
    },
    {
        "id": "epi_005",
        "gene_a": "ARID1A",
        "gene_b": "EZH2",
        "context": "Ovarian cancer",
        "ground_truth": {
            "interaction_type": "synthetic_lethal",
            "single_effects": {
                "ARID1A_loss": "SWI/SNF dysfunction, viable",
                "EZH2_loss": "PRC2 dysfunction, viable"
            },
            "combined_effect": "Lethal in ARID1A-mutant context",
            "mechanism": "ARID1A loss creates EZH2 dependency for gene silencing",
            "clinical_relevance": "EZH2 inhibitors effective in ARID1A-mutant cancers"
        }
    },
    {
        "id": "epi_006",
        "gene_a": "MTAP",
        "gene_b": "PRMT5",
        "context": "MTAP-deleted cancers",
        "ground_truth": {
            "interaction_type": "synthetic_lethal",
            "single_effects": {
                "MTAP_deletion": "Loss of methionine salvage, MTA accumulation",
                "PRMT5_inhibition": "Reduced protein methylation"
            },
            "combined_effect": "Lethal - MTA inhibits PRMT5, cells become dependent",
            "mechanism": "MTAP deletion → MTA accumulation → partial PRMT5 inhibition → addiction",
            "clinical_relevance": "PRMT5 inhibitors in development for MTAP-deleted tumors"
        }
    },
    {
        "id": "epi_007",
        "gene_a": "TP53",
        "gene_b": "MDM2",
        "context": "TP53-wild-type cancer",
        "ground_truth": {
            "interaction_type": "suppressive",
            "single_effects": {
                "TP53_active": "Tumor suppression",
                "MDM2_overexpression": "p53 degradation"
            },
            "combined_effect": "MDM2 inhibition synthetic lethal with TP53 wild-type",
            "mechanism": "MDM2 inhibitors (Nutlins) release p53 to induce apoptosis",
            "clinical_relevance": "MDM2 inhibitors only work in TP53-WT tumors"
        }
    },
    {
        "id": "epi_008",
        "gene_a": "KEAP1",
        "gene_b": "SLC7A11",
        "context": "NSCLC",
        "ground_truth": {
            "interaction_type": "synthetic_lethal",
            "single_effects": {
                "KEAP1_mutation": "NRF2 activation, oxidative stress adaptation",
                "SLC7A11_loss": "Loss of cystine import"
            },
            "combined_effect": "Lethal - NRF2-high cells depend on cystine for glutathione",
            "mechanism": "KEAP1-mutant cells have high ROS, need cystine for antioxidant defense",
            "clinical_relevance": "SLC7A11/system xc- as target in KEAP1-mutant NSCLC"
        }
    }
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_all_knockout_tasks():
    """Return all knockout prediction tasks."""
    return KNOCKOUT_TASKS


def get_all_pathway_tasks():
    """Return all pathway reasoning tasks."""
    return PATHWAY_TASKS


def get_all_drug_response_tasks():
    """Return all drug response prediction tasks."""
    return DRUG_RESPONSE_TASKS


def get_all_epistasis_tasks():
    """Return all epistasis reasoning tasks."""
    return EPISTASIS_TASKS


def get_task_statistics():
    """Return statistics about available tasks."""
    return {
        "knockout_tasks": len(KNOCKOUT_TASKS),
        "knockout_by_type": _count_by_field(KNOCKOUT_TASKS, "reasoning_type"),
        "pathway_tasks": len(PATHWAY_TASKS),
        "drug_response_tasks": len(DRUG_RESPONSE_TASKS),
        "epistasis_tasks": len(EPISTASIS_TASKS),
        "epistasis_by_type": _count_by_field(EPISTASIS_TASKS, lambda x: x["ground_truth"]["interaction_type"]),
        "total_tasks": len(KNOCKOUT_TASKS) + len(PATHWAY_TASKS) + len(DRUG_RESPONSE_TASKS) + len(EPISTASIS_TASKS)
    }


def _count_by_field(tasks, field):
    """Count tasks by a specific field."""
    counts = {}
    for task in tasks:
        if callable(field):
            value = field(task)
        else:
            value = task.get(field, "unknown")
        counts[value] = counts.get(value, 0) + 1
    return counts


if __name__ == "__main__":
    stats = get_task_statistics()
    print("CausalBio Extended Dataset Statistics:")
    print(f"  Total tasks: {stats['total_tasks']}")
    print(f"  Knockout tasks: {stats['knockout_tasks']}")
    print(f"    By type: {stats['knockout_by_type']}")
    print(f"  Pathway tasks: {stats['pathway_tasks']}")
    print(f"  Drug response tasks: {stats['drug_response_tasks']}")
    print(f"  Epistasis tasks: {stats['epistasis_tasks']}")
    print(f"    By type: {stats['epistasis_by_type']}")
