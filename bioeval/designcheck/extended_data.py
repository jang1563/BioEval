"""
Extended DesignCheck tasks — additional flawed experimental designs.

Covers advanced domains: CRISPR screens, immunotherapy animal models,
metabolomics, clinical trials, single-cell sequencing, IHC, proteomics,
drug combinations, longitudinal studies, and ELISA.
"""

EXTENDED_FLAWED_DESIGNS = [
    # =========================================================================
    # 10 extended designs (design_021 - design_030)
    # =========================================================================
    # -------------------------------------------------------------------------
    # CRISPR SCREEN
    # -------------------------------------------------------------------------
    {
        "id": "design_021",
        "title": "Genome-wide CRISPR Knockout Screen for Drug Resistance",
        "description": """
        We performed a genome-wide CRISPR screen to identify genes whose loss
        confers resistance to MEK inhibitor trametinib.

        Methods:
        - A375 melanoma cells transduced with Brunello library (77,441 sgRNAs)
        - Selected with puromycin for 3 days, then treated with trametinib (100 nM) or DMSO for 14 days
        - Surviving cells harvested, sgRNA cassettes amplified and sequenced
        - MAGeCK analysis: trametinib vs DMSO
        - Hits: FDR < 0.05

        Results:
        - 45 genes enriched in trametinib arm
        - Top hits: NF1, DUSP6, PTEN

        Conclusion: NF1 loss is the primary driver of trametinib resistance.
        """,
        "flaws": [
            {
                "category": "controls",
                "type": "missing_nontargeting_control",
                "severity": "critical",
                "explanation": "No non-targeting control sgRNAs mentioned for baseline — essential for MAGeCK null distribution and FDR calibration",
                "fix": "Ensure non-targeting sgRNAs (~1000) are included and used as negative controls in MAGeCK analysis",
            },
            {
                "category": "technical",
                "type": "no_baseline_reference",
                "severity": "major",
                "explanation": "No T0 (pre-treatment) baseline sample to distinguish resistance genes from essential genes depleted during growth",
                "fix": "Collect a T0 sample at start of drug treatment to separate essentiality from drug-specific effects",
            },
            {
                "category": "technical",
                "type": "library_coverage",
                "severity": "major",
                "explanation": "No mention of library representation or coverage (cells per sgRNA) — low coverage leads to noise and false negatives",
                "fix": "Maintain ≥500x library representation (38M+ cells); verify coverage by sequencing plasmid library",
            },
        ],
    },
    # -------------------------------------------------------------------------
    # ANIMAL STUDY RANDOMIZATION
    # -------------------------------------------------------------------------
    {
        "id": "design_022",
        "title": "Syngeneic Mouse Tumour Immunotherapy Study",
        "description": """
        We tested anti-PD-1 therapy in a syngeneic mouse model.

        Methods:
        - CT26 colon cancer cells injected subcutaneously into 30 BALB/c mice
        - Mice housed 5 per cage (6 cages total)
        - Cages 1-3 assigned to anti-PD-1, cages 4-6 to isotype control
        - Treatment started when average tumour volume reached 80 mm³
        - Tumour volume measured every 3 days for 28 days
        - Mice with tumour > 2000 mm³ euthanised per protocol

        Results:
        - Anti-PD-1: 40% tumour-free at day 28
        - Isotype: 0% tumour-free
        - p = 0.003 (log-rank test for tumour-free survival)

        Conclusion: Anti-PD-1 is highly effective in the CT26 model.
        """,
        "flaws": [
            {
                "category": "confounders",
                "type": "cage_effect_confound",
                "severity": "critical",
                "explanation": "Cage-level allocation (not individual randomisation) — treatment is confounded with cage effects (microbiome, stress, dominance hierarchies)",
                "fix": "Randomise individual mice across cages so each cage has both treatment and control animals",
            },
            {
                "category": "confounders",
                "type": "non_individual_randomization",
                "severity": "major",
                "explanation": "Treatment started at average tumour volume across all mice — individual tumour sizes at treatment start may differ substantially",
                "fix": "Enrol mice individually when each reaches target volume; stratify randomisation by tumour size",
            },
            {
                "category": "technical",
                "type": "no_blinding",
                "severity": "major",
                "explanation": "No mention of blinding for tumour measurement — knowing treatment assignment can bias calliper measurements",
                "fix": "Have tumour measurements performed by personnel blinded to treatment group",
            },
        ],
    },
    # -------------------------------------------------------------------------
    # METABOLOMICS BATCH EFFECTS
    # -------------------------------------------------------------------------
    {
        "id": "design_023",
        "title": "Untargeted Metabolomics for Disease Biomarker Discovery",
        "description": """
        We performed untargeted metabolomics to identify biomarkers that
        distinguish type 2 diabetes (T2D) from healthy controls.

        Methods:
        - Plasma samples from 50 T2D patients and 50 healthy controls
        - T2D samples collected at Hospital A, controls at Hospital B
        - T2D samples processed in batch 1 (January), controls in batch 2 (March)
        - LC-MS/MS on Q Exactive Plus
        - 2,500 features detected after deconvolution
        - PCA showed clear separation of T2D vs control groups
        - 300 significantly different metabolites (t-test, p < 0.05)

        Results:
        - Clear metabolomic signature of T2D
        - Top discriminators: amino acids and lipid species

        Conclusion: Metabolomics reliably distinguishes T2D from healthy individuals.
        """,
        "flaws": [
            {
                "category": "confounders",
                "type": "batch_effect_confound",
                "severity": "critical",
                "explanation": "Disease status is completely confounded with batch (T2D=batch1, controls=batch2) — observed differences may reflect batch, not biology",
                "fix": "Randomise samples across batches; include pooled QC samples; use batch correction methods (ComBat)",
            },
            {
                "category": "confounders",
                "type": "site_confound",
                "severity": "critical",
                "explanation": "T2D from Hospital A, controls from Hospital B — site differences (diet, demographics, sample handling) are confounded with disease",
                "fix": "Recruit cases and controls from the same site/cohort; match on key confounders",
            },
            {
                "category": "statistics",
                "type": "multiple_testing",
                "severity": "major",
                "explanation": "2,500 features tested with uncorrected p < 0.05 — expected ~125 false positives by chance",
                "fix": "Apply FDR correction (Benjamini-Hochberg); use permutation-based testing for robustness",
            },
        ],
    },
    # -------------------------------------------------------------------------
    # CLINICAL TRIAL ITT
    # -------------------------------------------------------------------------
    {
        "id": "design_024",
        "title": "Randomised Trial of Novel Antibiotic for UTI",
        "description": """
        Phase III trial comparing novel antibiotic X to ciprofloxacin for
        uncomplicated urinary tract infections (UTIs).

        Methods:
        - 400 patients randomised 1:1 (200 per arm)
        - Primary endpoint: microbiological cure at day 10
        - 35 patients in the X arm and 20 in cipro arm discontinued early
          (adverse events, lost to follow-up, protocol violations)
        - Analysis included only patients who completed the full course
          (per-protocol population: 165 vs 180)

        Results:
        - Antibiotic X: 82% cure (135/165)
        - Ciprofloxacin: 79% cure (142/180)
        - Difference: +3%, p = 0.48 (not significant)

        Conclusion: Antibiotic X is comparable to ciprofloxacin in efficacy.
        """,
        "flaws": [
            {
                "category": "statistics",
                "type": "no_intention_to_treat",
                "severity": "critical",
                "explanation": "Primary analysis used per-protocol population instead of intention-to-treat (ITT) — excludes 55 randomised patients, breaking randomisation",
                "fix": "Primary analysis must use full ITT population (all randomised); per-protocol as sensitivity analysis",
            },
            {
                "category": "statistics",
                "type": "differential_dropout",
                "severity": "major",
                "explanation": "More dropouts in antibiotic X arm (35 vs 20) — differential dropout suggests tolerability issues that PP analysis hides",
                "fix": "Report dropout reasons per arm; perform worst-case ITT sensitivity analysis (assume dropouts = failures)",
            },
            {
                "category": "interpretation",
                "type": "non_inferiority_misuse",
                "severity": "major",
                "explanation": "'Comparable' implies non-inferiority but no non-inferiority margin was pre-specified — p=0.48 only shows no significant difference",
                "fix": "If non-inferiority is the goal, pre-specify margin (e.g., -10%) and calculate CI for difference",
            },
        ],
    },
    # -------------------------------------------------------------------------
    # SINGLE-CELL RNA-seq DOUBLETS
    # -------------------------------------------------------------------------
    {
        "id": "design_025",
        "title": "Single-Cell RNA-seq of Tumour Heterogeneity",
        "description": """
        We performed scRNA-seq to map intra-tumour heterogeneity in glioblastoma.

        Methods:
        - Fresh GBM tissue dissociated with papain
        - 20,000 cells loaded onto 10X Chromium (target: 10,000 recovered)
        - Sequenced on NovaSeq, ~50,000 reads/cell
        - Clustered with Seurat (PCA → UMAP → Louvain)
        - 8 clusters identified; annotated by marker genes
        - One cluster co-expressed markers of neurons and macrophages

        Results:
        - 8 distinct cell populations identified
        - A novel "neuro-immune" hybrid population discovered
        - This population expressed both MAP2 and CD68

        Conclusion: A novel neuro-immune hybrid cell type exists in GBM.
        """,
        "flaws": [
            {
                "category": "technical",
                "type": "doublet_contamination",
                "severity": "critical",
                "explanation": "Co-expression of neuron (MAP2) and macrophage (CD68) markers is the hallmark signature of doublets — two cells captured in one droplet",
                "fix": "Run doublet detection (DoubletFinder, Scrublet) before cluster annotation; loading 20K for 10K recovery gives ~8% expected doublet rate",
            },
            {
                "category": "technical",
                "type": "high_doublet_rate",
                "severity": "major",
                "explanation": "Loading 20,000 cells to recover 10,000 on 10X Chromium exceeds recommended overloading — expected doublet rate ~8-10%",
                "fix": "Load fewer cells (recommended 6,000-8,000 for 10,000 target) or explicitly account for doublet rate",
            },
            {
                "category": "interpretation",
                "type": "novel_cell_type_claim",
                "severity": "major",
                "explanation": "Claiming a novel cell type from scRNA-seq alone without validation is premature — requires orthogonal confirmation",
                "fix": "Validate with multiplex FISH (smFISH), immunofluorescence co-staining, or spatial transcriptomics",
            },
        ],
    },
    # -------------------------------------------------------------------------
    # IHC NO ISOTYPE CONTROL
    # -------------------------------------------------------------------------
    {
        "id": "design_026",
        "title": "Immunohistochemistry for Novel Biomarker",
        "description": """
        We developed IHC staining for novel protein BioX as a prognostic
        biomarker in breast cancer.

        Methods:
        - FFPE sections from 100 breast cancer patients
        - Rabbit polyclonal anti-BioX antibody (1:200 dilution)
        - Antigen retrieval: citrate buffer pH 6.0
        - Detection: HRP-DAB system
        - Scored semi-quantitatively (0-3) by one pathologist
        - No isotype control or secondary-only control performed

        Results:
        - 60% of tumours scored 2-3 (BioX-high)
        - BioX-high associated with worse overall survival (p = 0.02)

        Conclusion: BioX is a novel prognostic biomarker in breast cancer.
        """,
        "flaws": [
            {
                "category": "controls",
                "type": "no_isotype_control",
                "severity": "critical",
                "explanation": "No isotype control or secondary-only control — cannot distinguish specific BioX staining from non-specific antibody binding",
                "fix": "Include rabbit IgG isotype control and secondary-antibody-only control on serial sections",
            },
            {
                "category": "technical",
                "type": "polyclonal_antibody",
                "severity": "major",
                "explanation": "Rabbit polyclonal antibodies have batch-to-batch variability and higher non-specific binding risk — problematic for clinical biomarker development",
                "fix": "Validate with a monoclonal antibody; perform Western blot to confirm antibody specificity (single band at expected MW)",
            },
            {
                "category": "technical",
                "type": "single_scorer",
                "severity": "major",
                "explanation": "Semi-quantitative scoring by a single pathologist — subjective scoring without inter-rater reliability assessment",
                "fix": "Use at least two independent pathologists; report inter-rater kappa; consider digital image analysis",
            },
        ],
    },
    # -------------------------------------------------------------------------
    # PROTEOMICS REPLICATES
    # -------------------------------------------------------------------------
    {
        "id": "design_027",
        "title": "TMT Proteomics Comparing Cancer Subtypes",
        "description": """
        We compared protein expression between basal and luminal breast cancer
        using TMT quantitative proteomics.

        Methods:
        - 3 basal and 3 luminal breast cancer cell lines
        - One biological sample per cell line
        - 6-plex TMT labelling
        - LC-MS/MS on Orbitrap Fusion Lumos
        - 6,000 proteins quantified
        - t-test (p < 0.01) between basal and luminal groups

        Results:
        - 450 differentially expressed proteins
        - Basal subtype enriched for EMT and integrin signalling

        Conclusion: Proteomic profiling reveals fundamental differences between subtypes.
        """,
        "flaws": [
            {
                "category": "technical",
                "type": "no_biological_replicates",
                "severity": "critical",
                "explanation": "Each cell line measured once — 3 cell lines per group means cell line variability is confounded with subtype differences; n=3 is underpowered for 6,000 tests",
                "fix": "Include 2-3 biological replicates per cell line; alternatively, use ≥6 cell lines per subtype with replicated measurements",
            },
            {
                "category": "statistics",
                "type": "multiple_testing",
                "severity": "major",
                "explanation": "6,000 proteins tested with p < 0.01 cutoff expects ~60 false positives — no FDR correction mentioned",
                "fix": "Apply Benjamini-Hochberg correction; report q-values; use limma for proteomics statistical testing",
            },
            {
                "category": "interpretation",
                "type": "cell_line_vs_tissue",
                "severity": "major",
                "explanation": "Cell line proteomes may not reflect in vivo tumour differences — cultured cells lack microenvironment context",
                "fix": "Validate key findings in patient tumour tissue samples (IHC or tissue proteomics)",
            },
        ],
    },
    # -------------------------------------------------------------------------
    # DRUG COMBINATION
    # -------------------------------------------------------------------------
    {
        "id": "design_028",
        "title": "Drug Combination Synergy Study",
        "description": """
        We tested the combination of Drug A (MEK inhibitor) and Drug B (PI3K inhibitor)
        in pancreatic cancer cells.

        Methods:
        - PANC-1 cells treated with combination Drug A + Drug B for 72 hours
        - 5 concentrations of each drug combined at fixed ratio (1:1)
        - Cell viability by MTT assay, triplicate wells
        - Combination index (CI) calculated by Chou-Talalay method
        - CI < 1 defined as synergistic

        Results:
        - CI values ranged from 0.3 to 0.7 across all combinations
        - Strong synergy at all ratios tested

        Conclusion: Drug A + Drug B is synergistic and should advance to clinical trials.
        """,
        "flaws": [
            {
                "category": "controls",
                "type": "missing_single_agent",
                "severity": "critical",
                "explanation": "No single-agent dose-response curves shown for individual drugs — CI calculation requires accurate single-agent IC50s",
                "fix": "Generate full dose-response curves for each drug alone alongside the combination experiment",
            },
            {
                "category": "technical",
                "type": "fixed_ratio_only",
                "severity": "major",
                "explanation": "Only 1:1 ratio tested — synergy may be ratio-dependent; optimal combination ratio unknown",
                "fix": "Test multiple ratios (e.g., 1:3, 1:1, 3:1) or use a full dose matrix design (e.g., 6×6)",
            },
            {
                "category": "interpretation",
                "type": "overstatement",
                "severity": "major",
                "explanation": "'Should advance to clinical trials' from in vitro synergy in one cell line ignores PK/PD, toxicity, and in vivo validation requirements",
                "fix": "Validate in multiple cell lines and in vivo models before clinical translation claims",
            },
        ],
    },
    # -------------------------------------------------------------------------
    # LONGITUDINAL SURVIVORSHIP BIAS
    # -------------------------------------------------------------------------
    {
        "id": "design_029",
        "title": "Longitudinal Biomarker Study in Metastatic Cancer",
        "description": """
        We tracked circulating tumour DNA (ctDNA) as a treatment response biomarker
        in metastatic colorectal cancer patients receiving chemotherapy.

        Methods:
        - 80 patients enrolled at cycle 1, day 1
        - Blood drawn at baseline, cycle 3, cycle 6, and cycle 9
        - ctDNA measured by ddPCR for patient-specific mutations
        - Analysed ctDNA kinetics in patients with all 4 time points available
        - 45 patients had complete data (all 4 blood draws)

        Results:
        - Median ctDNA decreased 85% by cycle 6 in evaluable patients
        - Patients with >50% ctDNA reduction had better OS (HR=0.4, p=0.001)

        Conclusion: ctDNA kinetics predict overall survival in metastatic CRC.
        """,
        "flaws": [
            {
                "category": "confounders",
                "type": "survivorship_bias",
                "severity": "critical",
                "explanation": "Analysing only 45/80 patients with complete data introduces severe survivorship bias — patients who died or progressed early (worst outcomes) are excluded",
                "fix": "Use all 80 patients with landmark analysis or joint modelling of longitudinal biomarker + survival",
            },
            {
                "category": "confounders",
                "type": "informative_censoring",
                "severity": "major",
                "explanation": "Dropout is likely informative (disease progression or death) rather than random — complete-case analysis is biased",
                "fix": "Report reasons for missing data per time point; use multiple imputation or inverse-probability weighting",
            },
            {
                "category": "statistics",
                "type": "guarantee_time_bias",
                "severity": "major",
                "explanation": "Requiring survival to cycle 9 for inclusion guarantees a minimum survival time — biases OS comparison",
                "fix": "Use time-varying covariate models or landmark analysis at a fixed earlier time point",
            },
        ],
    },
    # -------------------------------------------------------------------------
    # ELISA STANDARD CURVE
    # -------------------------------------------------------------------------
    {
        "id": "design_030",
        "title": "ELISA Quantification of Serum Cytokine",
        "description": """
        We measured serum IL-6 levels in rheumatoid arthritis (RA) patients
        before and after anti-TNF therapy.

        Methods:
        - 30 RA patients, serum collected at baseline and week 12
        - Commercial IL-6 ELISA kit (range: 3.1 - 200 pg/mL)
        - Standard curve prepared: 7 dilutions from 200 to 3.1 pg/mL
        - Samples run in duplicate, mean OD used for interpolation
        - Samples with OD above the highest standard extrapolated from curve

        Results:
        - Baseline IL-6: mean 380 pg/mL (range 45-850)
        - Week 12 IL-6: mean 85 pg/mL (range 5-220)
        - p < 0.0001 (paired t-test)

        Conclusion: Anti-TNF therapy significantly reduces IL-6 in RA.
        """,
        "flaws": [
            {
                "category": "technical",
                "type": "extrapolation_beyond_range",
                "severity": "critical",
                "explanation": "Samples above 200 pg/mL (kit max) were extrapolated — ELISA curves are sigmoidal and plateau at high concentrations; extrapolation is unreliable and underestimates true values",
                "fix": "Dilute samples above the standard range and re-run; never extrapolate beyond the standard curve",
            },
            {
                "category": "technical",
                "type": "out_of_range_data",
                "severity": "major",
                "explanation": "Baseline mean (380 pg/mL) and max (850 pg/mL) are far above the 200 pg/mL kit range — most baseline values are unreliable",
                "fix": "Pre-dilute samples (1:5 or 1:10) based on expected concentration range; report how many samples fell within range",
            },
            {
                "category": "statistics",
                "type": "parametric_on_skewed",
                "severity": "major",
                "explanation": "Cytokine data is typically right-skewed (range 45-850) — paired t-test assumes normality of differences",
                "fix": "Log-transform data or use Wilcoxon signed-rank test for paired comparison",
            },
        ],
    },
]
