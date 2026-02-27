"""
Extended DesignCheck tasks — additional flawed experimental designs.

Covers domains less represented in the base set: flow cytometry, proteomics,
organoids, ChIP-seq, base editing, immunohistochemistry, RNA-seq, and
sequencing-based assays.
"""

EXTENDED_FLAWED_DESIGNS = [
    # -------------------------------------------------------------------------
    # FLOW CYTOMETRY / SORTING
    # -------------------------------------------------------------------------
    {
        "id": "design_011",
        "title": "Apoptosis Measurement by Annexin V/PI",
        "description": """
        We measured Drug A-induced apoptosis in Jurkat T cells.

        Methods:
        - Jurkat cells treated with Drug A (10 μM) or DMSO for 24 hours
        - Stained with Annexin V-FITC and propidium iodide (PI)
        - Analysed on FACSCalibur (10,000 events per sample)
        - Gating: used unstained cells to set quadrant gates

        Results:
        - DMSO: 5% apoptotic (Annexin V+/PI-)
        - Drug A: 45% apoptotic
        - p < 0.01 (Student's t-test, n=3 biological replicates)

        Conclusion: Drug A potently induces apoptosis in T cells.
        """,
        "flaws": [
            {
                "category": "controls",
                "type": "missing_positive_control",
                "severity": "major",
                "explanation": "No positive control for apoptosis (e.g. staurosporine, camptothecin) to validate staining",
                "fix": "Include a known apoptosis inducer as a positive control",
            },
            {
                "category": "technical",
                "type": "inadequate_gating",
                "severity": "critical",
                "explanation": "Quadrant gates set on unstained cells — compensation controls (single-stain) are required for FITC/PI overlap",
                "fix": "Include single-colour Annexin V-FITC only and PI-only controls for compensation",
            },
            {
                "category": "technical",
                "type": "insufficient_events",
                "severity": "minor",
                "explanation": "10,000 events may be low if rare populations are of interest and debris is not excluded",
                "fix": "Collect at least 20,000-50,000 events with forward/side scatter gating to exclude debris",
            },
        ],
    },
    # -------------------------------------------------------------------------
    # RNA-seq EXPERIMENT
    # -------------------------------------------------------------------------
    {
        "id": "design_012",
        "title": "RNA-seq of Drug-Treated Tumour Cells",
        "description": """
        We profiled transcriptional changes induced by CDK4/6 inhibitor palbociclib.

        Methods:
        - MCF7 breast cancer cells treated with 1 μM palbociclib or DMSO for 48 hours
        - RNA extracted with TRIzol, poly-A enriched
        - Library prep: Illumina TruSeq stranded mRNA kit
        - Sequenced on NovaSeq 6000, 2×150 bp, ~30M read pairs per sample
        - Biological replicates: 2 per condition
        - Reads aligned with STAR, counts with featureCounts
        - DEGs identified with DESeq2 (padj < 0.05, |log2FC| > 1)

        Results:
        - 1,200 upregulated and 800 downregulated genes
        - Top pathway: E2F targets (strongly downregulated)

        Conclusion: Palbociclib profoundly reshapes the transcriptome via E2F.
        """,
        "flaws": [
            {
                "category": "technical",
                "type": "insufficient_replicates",
                "severity": "critical",
                "explanation": "n=2 biological replicates provides very low statistical power for DESeq2; FDR correction is unreliable with only 2 replicates",
                "fix": "Use at least n=3 biological replicates per condition (n=4 recommended)",
            },
            {
                "category": "interpretation",
                "type": "overstatement",
                "severity": "major",
                "explanation": "'Profoundly reshapes the transcriptome' overstates findings — 48h treatment will include many secondary/indirect effects",
                "fix": "Include earlier time points (4h, 12h) to separate direct vs indirect effects",
            },
            {
                "category": "confounders",
                "type": "cell_cycle_confound",
                "severity": "major",
                "explanation": "CDK4/6 inhibition causes G1 arrest — observed DEGs may reflect cell cycle state rather than direct drug targets",
                "fix": "Account for cell cycle changes; compare to serum-starved G1-arrested cells as additional control",
            },
        ],
    },
    # -------------------------------------------------------------------------
    # IMMUNOHISTOCHEMISTRY
    # -------------------------------------------------------------------------
    {
        "id": "design_013",
        "title": "PD-L1 Expression as Immunotherapy Predictor",
        "description": """
        We assessed PD-L1 as a biomarker for anti-PD-1 response.

        Methods:
        - FFPE tumour sections from 50 patients (25 responders, 25 non-responders)
        - IHC with anti-PD-L1 antibody (clone 22C3)
        - Scored by one pathologist: TPS (tumour proportion score)
        - PD-L1-positive defined as TPS ≥ 1%
        - Chi-squared test: PD-L1-positive vs response

        Results:
        - 80% of responders were PD-L1-positive
        - 50% of non-responders were PD-L1-positive
        - p = 0.03

        Conclusion: PD-L1 IHC reliably predicts immunotherapy response.
        """,
        "flaws": [
            {
                "category": "technical",
                "type": "scorer_bias",
                "severity": "critical",
                "explanation": "Single pathologist scorer with no blinding to outcome — scorer bias may inflate association",
                "fix": "Use at least two independent blinded pathologists and report inter-rater agreement (kappa)",
            },
            {
                "category": "interpretation",
                "type": "overstatement",
                "severity": "major",
                "explanation": "'Reliably predicts' is too strong — 50% of non-responders are also PD-L1-positive (low specificity)",
                "fix": "Report sensitivity, specificity, PPV, and NPV; acknowledge limited predictive power",
            },
            {
                "category": "confounders",
                "type": "selection_bias",
                "severity": "major",
                "explanation": "Retrospective case-control design — sampling 25/25 does not reflect real prevalence or response rates",
                "fix": "Use consecutive unselected cohort to avoid sampling bias",
            },
        ],
    },
    # -------------------------------------------------------------------------
    # XENOGRAFT / IN VIVO
    # -------------------------------------------------------------------------
    {
        "id": "design_014",
        "title": "Patient-Derived Xenograft Drug Study",
        "description": """
        We tested new PI3K inhibitor in patient-derived xenograft (PDX) models.

        Methods:
        - Implanted PDX fragments from one patient into 20 NSG mice
        - When tumours reached 100 mm³, assigned first 10 mice to treatment, last 10 to vehicle
        - Treatment: PI3K inhibitor 50 mg/kg orally, daily × 21 days
        - Tumour volume measured twice weekly with callipers
        - Primary endpoint: tumour growth inhibition at day 21

        Results:
        - Vehicle: average 1200 mm³; Treatment: average 400 mm³
        - TGI = 67%, p < 0.001

        Conclusion: PI3K inhibitor is highly effective in this PDX model.
        """,
        "flaws": [
            {
                "category": "confounders",
                "type": "non_random_allocation",
                "severity": "critical",
                "explanation": "Mice allocated sequentially (first 10 vs last 10) rather than randomised — cage/position effects and growth rate bias",
                "fix": "Randomise mice to groups when tumours reach target volume using stratified randomisation",
            },
            {
                "category": "technical",
                "type": "single_pdx_model",
                "severity": "major",
                "explanation": "One PDX from one patient cannot represent population-level response",
                "fix": "Test in 3-5 independent PDX models from different patients",
            },
            {
                "category": "confounders",
                "type": "operator_effect",
                "severity": "major",
                "explanation": "No blinding during tumour measurement or group allocation",
                "fix": "Blind tumour measurements; have different personnel handle dosing and measurement",
            },
        ],
    },
    # -------------------------------------------------------------------------
    # PROTEOMICS
    # -------------------------------------------------------------------------
    {
        "id": "design_015",
        "title": "Phosphoproteomics of Signalling Pathway",
        "description": """
        We mapped signalling changes downstream of receptor activation.

        Methods:
        - HeLa cells stimulated with EGF (100 ng/mL) for 0, 5, 15, 30 min
        - Lysed in 8M urea, digested with trypsin
        - Phosphopeptides enriched by TiO₂
        - LC-MS/MS on Orbitrap Exploris 480
        - Searched with MaxQuant, LFQ normalisation
        - Two biological replicates per time point
        - All eight samples run in a single MS batch on one day

        Results:
        - 5,000 phosphosites quantified
        - 800 significantly changed (ANOVA, p < 0.05)

        Conclusion: Comprehensive map of EGFR signalling dynamics.
        """,
        "flaws": [
            {
                "category": "statistics",
                "type": "multiple_testing",
                "severity": "critical",
                "explanation": "5,000 phosphosites tested by ANOVA with p<0.05 cutoff expects ~250 false positives — no FDR correction mentioned",
                "fix": "Apply Benjamini-Hochberg FDR correction; report q-values",
            },
            {
                "category": "technical",
                "type": "insufficient_replicates",
                "severity": "critical",
                "explanation": "n=2 per time point provides very limited statistical power for 5,000 comparisons",
                "fix": "Use at least n=3 biological replicates per time point",
            },
            {
                "category": "technical",
                "type": "run_order_effect",
                "severity": "major",
                "explanation": "If samples are run sequentially, LC-MS sensitivity can drift over the batch; no randomisation of run order mentioned",
                "fix": "Randomise sample run order and include QC standard injections between samples",
            },
        ],
    },
    # -------------------------------------------------------------------------
    # ChIP-seq
    # -------------------------------------------------------------------------
    {
        "id": "design_016",
        "title": "ChIP-seq for Transcription Factor Binding",
        "description": """
        We mapped genome-wide binding sites of transcription factor TF-X.

        Methods:
        - K562 cells crosslinked with 1% formaldehyde
        - Chromatin sonicated to 200-500 bp fragments
        - ChIP with anti-TF-X antibody (10 μg) overnight
        - Library prep: NEBNext Ultra II DNA, single-end 75 bp
        - Sequenced to 15 million reads
        - Peak calling: MACS2 with q-value < 0.01
        - No input DNA control sequenced

        Results:
        - 12,000 binding sites identified
        - 60% at promoters, 30% at enhancers

        Conclusion: TF-X is a major transcriptional regulator.
        """,
        "flaws": [
            {
                "category": "controls",
                "type": "missing_negative_control",
                "severity": "critical",
                "explanation": "No input DNA control — essential for MACS2 peak calling to distinguish true signal from open chromatin / sonication bias",
                "fix": "Sequence input DNA control at comparable or greater depth",
            },
            {
                "category": "technical",
                "type": "low_sequencing_depth",
                "severity": "major",
                "explanation": "15 million reads is below ENCODE guidelines (20M+ for point-source TFs); may miss lower-affinity binding sites",
                "fix": "Sequence to at least 20-30 million uniquely mapped reads",
            },
            {
                "category": "technical",
                "type": "insufficient_replicates",
                "severity": "major",
                "explanation": "Single replicate — ENCODE requires at least 2 biological replicates with IDR analysis",
                "fix": "Perform in at least 2 biological replicates; use IDR for reproducibility",
            },
        ],
    },
    # -------------------------------------------------------------------------
    # ORGANOID MODEL
    # -------------------------------------------------------------------------
    {
        "id": "design_017",
        "title": "Patient-Derived Organoid Drug Screening",
        "description": """
        We screened 50 FDA-approved drugs against patient-derived colorectal
        cancer organoids to identify repurposing candidates.

        Methods:
        - Organoids established from one patient's tumour biopsy
        - Embedded in Matrigel, cultured in defined medium
        - Seeded 1,000 cells per well in 384-well plates
        - Treated at 1 μM single dose for 72 hours
        - Viability by CellTiter-Glo 3D, triplicate wells
        - Hit threshold: < 50% viability vs DMSO control

        Results:
        - 8 compounds reduced viability below 50%
        - Top hit: an mTOR inhibitor (25% viability)

        Conclusion: mTOR inhibitor is a promising repurposing candidate for this patient.
        """,
        "flaws": [
            {
                "category": "technical",
                "type": "single_dose",
                "severity": "critical",
                "explanation": "Single 1 μM dose ignores potency differences — some drugs have IC50 > 1 μM and would be missed; others may appear active only due to toxicity",
                "fix": "Use dose-response curves (6-8 concentrations) to determine IC50 for each drug",
            },
            {
                "category": "controls",
                "type": "missing_positive_control",
                "severity": "major",
                "explanation": "No positive control drug with known activity to benchmark assay sensitivity",
                "fix": "Include a known cytotoxic agent and a drug matching the patient's actual treatment regimen",
            },
            {
                "category": "statistics",
                "type": "pseudoreplication",
                "severity": "major",
                "explanation": "Triplicate wells are technical replicates from one organoid line from one patient — no biological replication",
                "fix": "Test across multiple independent organoid cultures or multiple passages for biological variability",
            },
        ],
    },
    # -------------------------------------------------------------------------
    # CRISPR BASE EDITING
    # -------------------------------------------------------------------------
    {
        "id": "design_018",
        "title": "CRISPR Base Editing Functional Study",
        "description": """
        We used cytosine base editing to introduce TP53 R248W mutation
        and study its gain-of-function effects.

        Methods:
        - Transfected HCT116 (TP53 wild-type) with CBE4max and sgRNA
        - Selected GFP+ cells by FACS 48 hours post-transfection
        - Sanger sequencing confirmed C>T conversion in TP53 codon 248
        - Compared base-edited cells to parental HCT116
        - Assayed: proliferation, migration, colony formation

        Results:
        - R248W cells showed 2x more migration and 1.5x more colonies

        Conclusion: TP53 R248W gain-of-function drives invasion.
        """,
        "flaws": [
            {
                "category": "controls",
                "type": "inappropriate_control",
                "severity": "critical",
                "explanation": "Parental cells are wrong control — they didn't undergo transfection, sorting, or selection stress; differences may reflect these procedures",
                "fix": "Use non-targeting sgRNA + CBE4max control processed identically (transfected, sorted, sequenced)",
            },
            {
                "category": "technical",
                "type": "bystander_edits",
                "severity": "major",
                "explanation": "Cytosine base editors can edit other C residues in the editing window (positions 4-8) — bystander edits in TP53 could confound",
                "fix": "Check Sanger trace for bystander edits in the editing window; sequence full TP53 exon",
            },
            {
                "category": "technical",
                "type": "off_target_editing",
                "severity": "major",
                "explanation": "No assessment of off-target C>T edits at predicted genomic sites",
                "fix": "Check top 5-10 predicted off-target sites by amplicon sequencing",
            },
        ],
    },
    # -------------------------------------------------------------------------
    # CELL LINE AUTHENTICATION
    # -------------------------------------------------------------------------
    {
        "id": "design_019",
        "title": "Comparative Drug Sensitivity Across Cell Lines",
        "description": """
        We compared drug sensitivity across 5 breast cancer cell lines to find
        biomarkers of response.

        Methods:
        - Cell lines: MCF7, MDA-MB-231, T47D, BT549, SKBR3
        - Obtained from lab freezer stocks (frozen 3-7 years ago)
        - Treated with 8 concentrations of PARP inhibitor olaparib
        - IC50 determined by MTT assay after 5 days
        - Each cell line tested once with triplicate wells

        Results:
        - IC50 ranged from 0.5 μM (MCF7) to 50 μM (MDA-MB-231)
        - HER2+ cell lines most sensitive

        Conclusion: HER2 expression predicts PARP inhibitor sensitivity.
        """,
        "flaws": [
            {
                "category": "technical",
                "type": "cell_line_authentication",
                "severity": "critical",
                "explanation": "Old freezer stocks (3-7 years) with no authentication — cell lines may be misidentified or cross-contaminated (estimated 15-20% misidentification rate in literature)",
                "fix": "Perform STR profiling on all cell lines before experiments; compare to ATCC reference profiles",
            },
            {
                "category": "technical",
                "type": "insufficient_replicates",
                "severity": "major",
                "explanation": "Each cell line tested once — single experiment IC50 values have substantial variability",
                "fix": "Repeat entire experiment on at least 3 independent occasions",
            },
            {
                "category": "interpretation",
                "type": "overstatement",
                "severity": "major",
                "explanation": "Claiming HER2 predicts PARPi sensitivity from 5 cell lines (2 HER2+) is severe overfitting — biological correlation requires larger panel",
                "fix": "Test in ≥20 cell lines or use public datasets (GDSC, CCLE) for biomarker-response correlation",
            },
        ],
    },
    # -------------------------------------------------------------------------
    # SPATIAL TRANSCRIPTOMICS
    # -------------------------------------------------------------------------
    {
        "id": "design_020",
        "title": "Spatial Transcriptomics of Tumour Microenvironment",
        "description": """
        We used Visium spatial transcriptomics to map the tumour immune
        microenvironment in colorectal cancer.

        Methods:
        - Fresh-frozen sections from 2 CRC patients (1 microsatellite-stable,
          1 microsatellite-instable)
        - Visium 10X spatial capture, sequenced on NovaSeq
        - Spots deconvolved using RCTD for cell type proportions
        - Compared immune cell composition between MSI and MSS tumours

        Results:
        - MSI tumour had 3x more CD8+ T cell-enriched spots
        - Clear spatial separation of T cells and tumour cells in MSS

        Conclusion: MSI tumours have higher immune infiltration, explaining
        immunotherapy responsiveness.
        """,
        "flaws": [
            {
                "category": "statistics",
                "type": "underpowered",
                "severity": "critical",
                "explanation": "n=1 per group — any difference could reflect individual patient variation rather than MSI/MSS biology",
                "fix": "Include ≥5 patients per group to account for inter-patient variability",
            },
            {
                "category": "technical",
                "type": "single_section_bias",
                "severity": "major",
                "explanation": "One tissue section per patient may not represent tumour heterogeneity — immune infiltrate varies by region",
                "fix": "Profile multiple sections from different tumour regions per patient",
            },
            {
                "category": "interpretation",
                "type": "correlation_causation",
                "severity": "major",
                "explanation": "'Explaining immunotherapy responsiveness' is causal language from observational spatial data with n=2",
                "fix": "State as hypothesis; validate with clinical immunotherapy outcome data",
            },
        ],
    },
    # =========================================================================
    # BATCH 2: 10 additional designs (design_021 - design_030)
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
