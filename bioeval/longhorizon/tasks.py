"""
LongHorizon task definitions.

Each task type has its own list of task dicts. The evaluator imports these
constants and builds EvalTask objects from them in load_tasks().

6 tasks across 5 types (base tier). Additional tasks added in Stage 2.
"""

# ============================================================
# constraint_tracking
# ============================================================

CONSTRAINT_TRACKING_TASKS = [
    {
        "id": "lh_ct_001",
        "title": "RNA-seq multiplexing overflow",
        "stages": [
            {
                "stage": 1,
                "name": "Experimental Design",
                "content": (
                    "You are planning a bulk RNA-seq experiment to study the transcriptomic "
                    "response to spaceflight. Design: 4 conditions (flight, ground control, "
                    "vivarium control, baseline) x 3 biological replicates x 2 timepoints "
                    "(return day 1, return day 45). Total samples: 24."
                ),
            },
            {
                "stage": 2,
                "name": "Sample Collection",
                "content": (
                    "Blood samples collected in PAXgene RNA tubes. Each crew member provides "
                    "2 tubes per timepoint. Available crew: 4 (flight condition only). Ground "
                    "and vivarium controls: 3 subjects each, matched. Baseline: same subjects "
                    "as flight, pre-flight collection. Total tubes available: "
                    "flight=4x2x2=16, ground=3x2x2=12, vivarium=3x2x2=12, baseline=4x2=8. "
                    "Total: 48 tubes."
                ),
            },
            {
                "stage": 3,
                "name": "RNA Extraction & QC",
                "content": (
                    "RNA extracted using PAXgene Blood RNA Kit. Minimum input for library "
                    "prep: 100ng total RNA. Expected yield: 2-8 ug per tube. "
                    "QC requirement: RIN >= 7.0. Historical failure rate: ~15% of samples "
                    "fail QC. Plan for 1 extraction per tube."
                ),
            },
            {
                "stage": 4,
                "name": "Library Preparation",
                "content": (
                    "Using Illumina TruSeq Stranded mRNA kit. Input requirement: 100ng-1ug "
                    "total RNA. Each library prep processes one sample. Plan to prepare "
                    "libraries for all 24 design points (one library per condition x "
                    "replicate x timepoint combination)."
                ),
            },
            {
                "stage": 5,
                "name": "Sequencing Plan",
                "content": (
                    "Sequencing on NovaSeq 6000 S4 flow cell. Read depth target: 30M "
                    "paired-end reads per sample. S4 flow cell capacity: ~10 billion "
                    "paired-end reads total. Plan: multiplex all 24 libraries on a single "
                    "S4 flow cell. Additionally, the PI requests adding 12 samples from "
                    "a collaborator's unrelated mouse liver study to the same flow cell "
                    "to save costs, bringing total to 36 libraries."
                ),
            },
        ],
        "constraint_violations": [
            {
                "location": "stage_5",
                "type": "sample_count_mismatch",
                "description": (
                    "Design specifies 3 replicates for flight condition, but only 4 crew "
                    "members available (stage 2). With 2 tubes per timepoint and ~15% QC "
                    "failure rate (stage 3), some design points may lack sufficient replicates. "
                    "More critically, adding 12 unrelated mouse samples to a human flow cell "
                    "introduces cross-species index hopping risk."
                ),
                "severity": "major",
            },
            {
                "location": "stage_5",
                "type": "cross_species_contamination",
                "description": (
                    "Multiplexing human and mouse libraries on the same flow cell risks "
                    "index hopping, leading to cross-species read contamination. This is "
                    "a known NovaSeq issue with patterned flow cells."
                ),
                "severity": "critical",
            },
        ],
        "question": (
            "Review the complete experimental plan across all 5 stages. Identify any "
            "constraint violations, inconsistencies, or risks that could compromise "
            "the study. For each issue found, specify which stages are involved and "
            "the severity (minor/major/critical)."
        ),
        "ground_truth": {
            "violations": [
                "cross_species_contamination",
                "sample_count_mismatch",
            ],
            "stages_involved": [2, 3, 5],
            "min_violations_expected": 2,
        },
    },
    {
        "id": "lh_ct_002",
        "title": "Proteomics sample volume conflict",
        "stages": [
            {
                "stage": 1,
                "name": "Study Design",
                "content": (
                    "Multi-omics study of astronaut blood: transcriptomics, proteomics, "
                    "and metabolomics from the same blood draw. 6 astronauts, 3 timepoints "
                    "(pre-flight L-90, in-flight day 3, post-flight R+1)."
                ),
            },
            {
                "stage": 2,
                "name": "Blood Collection Protocol",
                "content": (
                    "Total blood volume per draw: 20mL per astronaut per timepoint. "
                    "Collected in: 2x PAXgene RNA tubes (2.5mL each = 5mL), "
                    "2x EDTA tubes (4mL each = 8mL for plasma), "
                    "1x SST tube (5mL for serum), "
                    "1x heparin tube (2mL for PBMCs). Total: 20mL."
                ),
            },
            {
                "stage": 3,
                "name": "Sample Processing & Aliquoting",
                "content": (
                    "From EDTA tubes: centrifuge at 1500g for 10min. Expected plasma yield: "
                    "~4mL from 8mL whole blood. Aliquot into 500uL cryovials. "
                    "Allocation: 4 aliquots for proteomics (2mL total), "
                    "2 aliquots for metabolomics (1mL total), "
                    "2 aliquots for backup storage (1mL total). Total plasma needed: 4mL."
                ),
            },
            {
                "stage": 4,
                "name": "Proteomics Analysis Plan",
                "content": (
                    "SomaScan 7K platform for plasma proteomics. "
                    "Input requirement: 150uL undiluted plasma per run. "
                    "Plan: run in technical duplicate for each sample. "
                    "Total plasma per sample: 300uL x 2 = 600uL. "
                    "Wait: the PI also wants to add an Olink Explore 3072 panel. "
                    "Olink input: 2uL per sample, run in singlicate. "
                    "And a targeted MRM panel for 50 proteins: 100uL per sample."
                ),
            },
            {
                "stage": 5,
                "name": "Metabolomics Analysis Plan",
                "content": (
                    "Untargeted metabolomics using LC-MS/MS. Input: 100uL plasma. "
                    "Targeted panel (bile acids, amino acids): 200uL plasma. "
                    "Lipidomics: 100uL plasma. "
                    "Total metabolomics needs: 400uL per sample. "
                    "But only 2 aliquots (1mL total) allocated in stage 3."
                ),
            },
        ],
        "constraint_violations": [
            {
                "location": "stage_4",
                "type": "volume_exceeds_allocation",
                "description": (
                    "SomaScan technical duplicates require 600uL, but only 4 aliquots "
                    "(2mL) allocated. Adding Olink (2uL) and MRM (100uL) brings total "
                    "proteomics needs to 702uL. This is within the 2mL allocation, but "
                    "leaves only 1298uL for any repeat runs if SomaScan QC fails."
                ),
                "severity": "minor",
            },
            {
                "location": "stage_5",
                "type": "metabolomics_volume_shortfall",
                "description": (
                    "Metabolomics requires 400uL but only 1mL allocated (2 aliquots). "
                    "This is technically sufficient, but leaves only 600uL for backup, "
                    "and combined with freeze-thaw sensitivity of metabolites, "
                    "the allocation is tight with no room for failed runs."
                ),
                "severity": "minor",
            },
            {
                "location": "stages_4_5_combined",
                "type": "no_rerun_margin",
                "description": (
                    "Combined proteomics (702uL + margin) and metabolomics (400uL) "
                    "consume nearly all allocated plasma. If any assay fails QC or "
                    "needs rerunning, there is insufficient backup volume. The 1mL "
                    "backup allocation cannot cover both proteomics and metabolomics reruns."
                ),
                "severity": "major",
            },
        ],
        "question": (
            "Review the complete sample allocation plan across all 5 stages. "
            "Calculate whether the volumes allocated at each stage are sufficient "
            "for the downstream analyses planned. Identify any volume conflicts, "
            "insufficient margins, or risks. Show your calculations."
        ),
        "ground_truth": {
            "violations": [
                "no_rerun_margin",
                "volume_exceeds_allocation",
                "metabolomics_volume_shortfall",
            ],
            "stages_involved": [3, 4, 5],
            "min_violations_expected": 1,
        },
    },
    # ------------------------------------------------------------------
    # Stage 2 additions (lh_ct_003 – lh_ct_006)
    # ------------------------------------------------------------------
    {
        "id": "lh_ct_003",
        "title": "Clinical trial endpoint statistical conflict",
        "stages": [
            {
                "stage": 1,
                "name": "Trial Design",
                "content": (
                    "Phase II adaptive trial for a novel immunotherapy in non-small cell "
                    "lung cancer (NSCLC). Design: single-arm with a Simon two-stage design. "
                    "Primary endpoint: objective response rate (ORR) by RECIST 1.1 at 12 weeks. "
                    "Secondary endpoint: progression-free survival (PFS) at 6 months."
                ),
            },
            {
                "stage": 2,
                "name": "Sample Size Calculation",
                "content": (
                    "Simon two-stage design parameters for ORR: "
                    "H0 response rate p0 = 0.20 (historical docetaxel), "
                    "H1 response rate p1 = 0.40, alpha = 0.05, power = 0.80. "
                    "Stage 1: n1 = 13, reject if <= 3 responses. "
                    "Stage 2: total N = 43, reject if <= 12 responses."
                ),
            },
            {
                "stage": 3,
                "name": "PFS Secondary Analysis Plan",
                "content": (
                    "PFS analysis: Kaplan-Meier estimation with 80% power to detect "
                    "HR = 0.60 vs historical control median PFS = 3 months. "
                    "Required events: 80 events. Required enrollment: 100 patients with "
                    "12-month accrual and 6-month minimum follow-up. "
                    "The statistical plan specifies using the same 43 patients from the "
                    "Simon design for PFS analysis."
                ),
            },
            {
                "stage": 4,
                "name": "Interim Analysis Plan",
                "content": (
                    "Interim analysis after Stage 1 (13 patients). Decision rules: "
                    "If ORR > 3/13, proceed to Stage 2. The protocol also specifies an "
                    "interim PFS analysis at the same timepoint using O'Brien-Fleming "
                    "spending function with alpha = 0.025 (one-sided)."
                ),
            },
            {
                "stage": 5,
                "name": "Regulatory Submission Plan",
                "content": (
                    "Plan to submit to FDA for accelerated approval based on ORR "
                    "from 43 patients. For full approval, PFS data from the same "
                    "43-patient trial will be used as confirmatory evidence."
                ),
            },
        ],
        "question": (
            "Review the complete trial design across all 5 stages. Identify "
            "statistical inconsistencies, power issues, and regulatory risks."
        ),
        "ground_truth": {
            "violations": [
                "pfs_underpowered",
                "endpoint_sample_size_mismatch",
                "interim_alpha_spending",
            ],
            "stages_involved": [2, 3, 4, 5],
            "min_violations_expected": 2,
        },
    },
    {
        "id": "lh_ct_004",
        "title": "Mass spectrometry sample prep incompatibility",
        "stages": [
            {
                "stage": 1,
                "name": "Study Overview",
                "content": (
                    "Quantitative proteomics study comparing plasma protein changes "
                    "in 20 patients pre- and post-CAR-T cell therapy. Goal: identify "
                    "cytokine release syndrome (CRS) biomarkers using TMT-based "
                    "quantitative proteomics."
                ),
            },
            {
                "stage": 2,
                "name": "Plasma Processing",
                "content": (
                    "Plasma collected in EDTA tubes, centrifuged at 2000g for 15 min. "
                    "Top 14 abundant proteins depleted using Agilent MARS-14 column. "
                    "Depleted plasma stored at -80C in PBS buffer."
                ),
            },
            {
                "stage": 3,
                "name": "Protein Digestion",
                "content": (
                    "Protein digestion protocol: Lyse depleted plasma in 4% SDS, "
                    "100mM Tris-HCl pH 8.5 at 95C for 10 min. Reduce with 10mM DTT "
                    "at 56C for 30 min. Alkylate with 20mM iodoacetamide in dark for "
                    "30 min. Digest with trypsin (1:50 enzyme:protein) overnight at 37C."
                ),
            },
            {
                "stage": 4,
                "name": "TMT Labeling",
                "content": (
                    "Label tryptic peptides with TMT-16plex reagents. Pool labeled "
                    "peptides, fractionate by high-pH reversed-phase chromatography "
                    "into 12 fractions."
                ),
            },
            {
                "stage": 5,
                "name": "LC-MS/MS Analysis",
                "content": (
                    "Analyze fractions on Orbitrap Eclipse Tribrid. LC gradient: "
                    "120 min per fraction. MS1: 120K resolution. MS2: HCD, 50K "
                    "resolution. Data analysis: MaxQuant with TMT reporter ion "
                    "quantification."
                ),
            },
        ],
        "question": (
            "Review the proteomics workflow across all stages. Identify any "
            "technical incompatibilities, protocol errors, or steps that would "
            "prevent successful quantification."
        ),
        "ground_truth": {
            "violations": [
                "sds_lc_ms_incompatible",
                "no_sds_removal_step",
            ],
            "stages_involved": [3, 4, 5],
            "min_violations_expected": 1,
        },
    },
    {
        "id": "lh_ct_005",
        "title": "scRNA-seq cell number recovery deficit",
        "stages": [
            {
                "stage": 1,
                "name": "Experimental Goal",
                "content": (
                    "Single-cell RNA-seq profiling of rare circulating tumor cells (CTCs) "
                    "from 10 metastatic breast cancer patients. Goal: characterize "
                    "transcriptomic heterogeneity of CTCs using 10x Genomics Chromium."
                ),
            },
            {
                "stage": 2,
                "name": "CTC Enrichment",
                "content": (
                    "CTC enrichment from 7.5mL peripheral blood using CellSearch-based "
                    "EpCAM positive selection. Expected CTC count: 5-50 CTCs per 7.5mL "
                    "(median ~12 in metastatic breast cancer). Enrichment purity: ~0.1% "
                    "(CTCs among ~10,000 background WBCs)."
                ),
            },
            {
                "stage": 3,
                "name": "Single-Cell Capture",
                "content": (
                    "10x Chromium Controller for single-cell capture. Target: load 10,000 "
                    "cells per channel for optimal capture. Expected capture rate: ~50-60% "
                    "of loaded cells. Plan: load entire enriched fraction (~10,000 cells "
                    "including WBC background) onto one Chromium channel per patient."
                ),
            },
            {
                "stage": 4,
                "name": "Library Prep & Sequencing",
                "content": (
                    "10x Chromium 3' v3.1 library prep. Sequence to 20,000 reads/cell "
                    "on NovaSeq. Expected: ~5,000-6,000 cells recovered per patient "
                    "(50-60% of 10,000 loaded cells)."
                ),
            },
            {
                "stage": 5,
                "name": "Analysis Plan",
                "content": (
                    "Cluster CTCs vs. WBCs using known markers. Perform DE analysis "
                    "between CTC subclusters. Goal: identify at least 3 CTC subpopulations "
                    "with minimum 30 cells per subpopulation for statistical power."
                ),
            },
        ],
        "question": (
            "Review the entire workflow. Will the expected CTC yield support "
            "the analysis goals? Identify any fundamental feasibility issues."
        ),
        "ground_truth": {
            "violations": [
                "ctc_yield_insufficient",
                "subpopulation_power_impossible",
                "rare_cell_capture_rate",
            ],
            "stages_involved": [2, 3, 5],
            "min_violations_expected": 2,
        },
    },
    {
        "id": "lh_ct_006",
        "title": "Multi-omics timeline and degradation collision",
        "stages": [
            {
                "stage": 1,
                "name": "Study Design",
                "content": (
                    "Integrated multi-omics study from a single tissue biopsy: "
                    "bulk RNA-seq, ATAC-seq, spatial transcriptomics (Visium), "
                    "and proteomics (DIA-MS). Tissue: fresh-frozen liver biopsies "
                    "from 15 NAFLD patients."
                ),
            },
            {
                "stage": 2,
                "name": "Tissue Processing Plan",
                "content": (
                    "Biopsy divided into portions at the bedside: "
                    "Portion A (50%): flash-frozen in OCT for Visium spatial transcriptomics, "
                    "ATAC-seq, and cryosectioning. "
                    "Portion B (20%): snap-frozen for bulk RNA-seq. "
                    "Portion C (30%): fixed in 10% neutral buffered formalin (NBF) "
                    "for proteomics."
                ),
            },
            {
                "stage": 3,
                "name": "Spatial Transcriptomics",
                "content": (
                    "Visium workflow: cryosection OCT blocks at 10um, place on "
                    "Visium capture area. H&E staining, imaging, permeabilization, "
                    "cDNA synthesis. Process within 1 week of sectioning."
                ),
            },
            {
                "stage": 4,
                "name": "ATAC-seq Processing",
                "content": (
                    "ATAC-seq from Portion A (OCT-embedded). Protocol: section OCT "
                    "blocks, dissociate tissue, isolate nuclei by gentle lysis, "
                    "tagmentation with Tn5 transposase, library prep. "
                    "Note: ATAC-seq protocol states nuclei must be prepared from "
                    "tissue frozen without fixative or embedding medium."
                ),
            },
            {
                "stage": 5,
                "name": "Proteomics Processing",
                "content": (
                    "DIA-MS proteomics on formalin-fixed tissue. Protocol: "
                    "deparaffinize, heat-induced antigen retrieval, trypsin digestion, "
                    "peptide cleanup with C18, LC-MS/MS. Note: plan specifies "
                    "formalin fixation but NOT paraffin embedding (FFPE), so "
                    "deparaffinization step is incorrectly included."
                ),
            },
        ],
        "question": (
            "Review the multi-omics tissue processing plan. Identify any "
            "incompatibilities between the preservation methods and downstream "
            "assays, protocol errors, or risks of data loss."
        ),
        "ground_truth": {
            "violations": [
                "oct_atac_incompatible",
                "deparaffinization_not_needed",
            ],
            "stages_involved": [2, 4, 5],
            "min_violations_expected": 2,
        },
    },
]


# ============================================================
# state_accumulation
# ============================================================

STATE_ACCUMULATION_TASKS = [
    {
        "id": "lh_sa_001",
        "title": "Drug target validation campaign",
        "stages": [
            {
                "stage": 1,
                "name": "Target Identification",
                "content": (
                    "Literature review and transcriptomic analysis identified 5 candidate "
                    "drug targets for glioblastoma: EGFR, PDGFRA, CDK4, MDM2, PTEN. "
                    "All show differential expression in tumor vs. normal brain tissue."
                ),
                "active_candidates": ["EGFR", "PDGFRA", "CDK4", "MDM2", "PTEN"],
                "checkpoint_question": "List all active candidate targets.",
            },
            {
                "stage": 2,
                "name": "Expression Validation",
                "content": (
                    "Western blot validation in 5 GBM cell lines (U87, U251, T98G, A172, LN229). "
                    "Results: EGFR - high in 4/5 lines. PDGFRA - high in 3/5. "
                    "CDK4 - high in 5/5. MDM2 - detected in 2/5 only. "
                    "PTEN - PTEN is a tumor suppressor (loss-of-function); "
                    "it is deleted/mutated in 3/5 lines, making it unsuitable as a "
                    "drug target (you cannot inhibit what is already lost). "
                    "Decision: Eliminate MDM2 (insufficient expression) and PTEN "
                    "(loss-of-function, not druggable by inhibition)."
                ),
                "active_candidates": ["EGFR", "PDGFRA", "CDK4"],
                "eliminated": {"MDM2": "insufficient expression", "PTEN": "loss-of-function"},
                "checkpoint_question": (
                    "Which candidates remain active? Which were eliminated and why?"
                ),
            },
            {
                "stage": 3,
                "name": "CRISPR Knockout Phenotype",
                "content": (
                    "CRISPR-Cas9 knockout in U87 cells, measuring proliferation (MTT assay, "
                    "7 days) and invasion (Matrigel assay, 48h). Results: "
                    "EGFR KO: 45% reduction in proliferation, 60% reduction in invasion. "
                    "PDGFRA KO: 10% reduction in proliferation (not significant, p=0.23), "
                    "15% reduction in invasion (not significant, p=0.18). "
                    "CDK4 KO: 70% reduction in proliferation, no change in invasion. "
                    "Decision: Eliminate PDGFRA (no significant phenotype)."
                ),
                "active_candidates": ["EGFR", "CDK4"],
                "eliminated": {"PDGFRA": "no significant phenotype"},
                "checkpoint_question": (
                    "Which candidates remain? Summarize the cumulative evidence for each "
                    "remaining target, including ALL prior elimination decisions."
                ),
            },
            {
                "stage": 4,
                "name": "Compound Screening",
                "content": (
                    "High-throughput screen of 2,000 compounds against EGFR and CDK4. "
                    "EGFR hits: 3 compounds with IC50 < 1uM (Compound A: 0.2uM, "
                    "B: 0.5uM, C: 0.8uM). "
                    "CDK4 hits: 5 compounds with IC50 < 1uM (Compound D: 0.1uM, "
                    "E: 0.3uM, F: 0.4uM, G: 0.7uM, H: 0.9uM)."
                ),
                "active_candidates": ["EGFR", "CDK4"],
                "active_compounds": {
                    "EGFR": ["A", "B", "C"],
                    "CDK4": ["D", "E", "F", "G", "H"],
                },
                "checkpoint_question": (
                    "List all active target-compound pairs. How many total candidates "
                    "remain from the original 5 targets?"
                ),
            },
            {
                "stage": 5,
                "name": "Selectivity Profiling",
                "content": (
                    "Selectivity panel (50 kinases) for EGFR compounds: "
                    "Compound A: selective (>100x selectivity over closest off-target). "
                    "Compound B: moderate selectivity (10x over ERBB2). "
                    "Compound C: poor selectivity (hits 12 kinases at <10x window). "
                    "Eliminate Compound C. "
                    "CDK4 compounds: "
                    "Compound D: hits CDK6 equally (expected, acceptable). "
                    "Compound E: selective for CDK4 over CDK6 (50x). "
                    "Compound F: hits CDK1 (toxic, cell cycle arrest). Eliminate F. "
                    "Compound G: poor ADME (no oral bioavailability). Eliminate G. "
                    "Compound H: moderate selectivity, acceptable ADME."
                ),
                "active_compounds": {
                    "EGFR": ["A", "B"],
                    "CDK4": ["D", "E", "H"],
                },
                "eliminated_compounds": {
                    "C": "poor selectivity",
                    "F": "CDK1 toxicity",
                    "G": "poor ADME",
                },
                "checkpoint_question": (
                    "Provide a complete summary of the drug target validation campaign: "
                    "starting candidates, each elimination decision with reasoning, "
                    "remaining target-compound pairs, and recommended lead candidates "
                    "for in vivo studies."
                ),
            },
        ],
        "ground_truth": {
            "final_active_targets": ["EGFR", "CDK4"],
            "final_active_compounds": {"EGFR": ["A", "B"], "CDK4": ["D", "E", "H"]},
            "all_eliminations": {
                "MDM2": "insufficient expression (stage 2)",
                "PTEN": "loss-of-function, not druggable (stage 2)",
                "PDGFRA": "no significant phenotype in CRISPR KO (stage 3)",
                "Compound_C": "poor selectivity (stage 5)",
                "Compound_F": "CDK1 toxicity (stage 5)",
                "Compound_G": "poor ADME (stage 5)",
            },
            "total_checkpoints": 5,
        },
    },
    # ------------------------------------------------------------------
    # Stage 2 additions (lh_sa_002 – lh_sa_006)
    # ------------------------------------------------------------------
    {
        "id": "lh_sa_002",
        "title": "Antibiotic resistance gene tracking in clinical isolates",
        "stages": [
            {
                "stage": 1,
                "name": "Isolate Collection",
                "content": (
                    "A hospital ICU monitors 8 Klebsiella pneumoniae isolates from "
                    "catheter-associated bloodstream infections over 6 months. Initial "
                    "genotyping reveals resistance genes: KPC-2 (all 8), NDM-1 (5/8), "
                    "OXA-48 (3/8), CTX-M-15 (7/8), mcr-1 (2/8). All isolates carry "
                    "KPC-2 on a conjugative IncFII plasmid."
                ),
                "active_candidates": ["KPC-2", "NDM-1", "OXA-48", "CTX-M-15", "mcr-1"],
                "checkpoint_question": "List all resistance genes under surveillance.",
            },
            {
                "stage": 2,
                "name": "Phenotypic Susceptibility Testing",
                "content": (
                    "MIC testing against 6 antibiotics: meropenem, colistin, "
                    "ceftazidime-avibactam (CZA), tigecycline, aztreonam, ciprofloxacin. "
                    "Results: All isolates resistant to meropenem (MIC > 16) confirming "
                    "KPC-2. mcr-1 carriers resistant to colistin (MIC > 4). CZA susceptible "
                    "in 6/8 (KPC-2 inhibited by avibactam). CZA-resistant in 2/8 isolates "
                    "carrying NDM-1 (metallo-beta-lactamase, not inhibited by avibactam). "
                    "Decision: Remove OXA-48 from priority tracking — all OXA-48 carriers "
                    "also carry KPC-2, and OXA-48 does not confer additional clinical "
                    "resistance beyond what KPC-2 provides in this context."
                ),
                "active_candidates": ["KPC-2", "NDM-1", "CTX-M-15", "mcr-1"],
                "eliminated": {"OXA-48": "redundant with KPC-2 in this resistance profile"},
                "checkpoint_question": "Which genes remain under active surveillance? Why was OXA-48 removed?",
            },
            {
                "stage": 3,
                "name": "Plasmid Transfer Monitoring",
                "content": (
                    "Conjugation assays in vitro and patient surveillance swabs. "
                    "Finding: KPC-2 IncFII plasmid transferred to E. coli in 3 patients "
                    "(new transconjugants detected). NDM-1 found on a non-conjugative "
                    "plasmid — no horizontal transfer detected. CTX-M-15 chromosomally "
                    "integrated — no mobility. mcr-1 on IncI2 plasmid — transfer detected "
                    "to 1 E. coli isolate. "
                    "Decision: Deprioritize CTX-M-15 (chromosomal, no spread risk). "
                    "Deprioritize NDM-1 (non-mobile in this context)."
                ),
                "active_candidates": ["KPC-2", "mcr-1"],
                "eliminated": {
                    "CTX-M-15": "chromosomally integrated, no horizontal transfer",
                    "NDM-1": "non-conjugative plasmid, no transfer detected",
                },
                "checkpoint_question": (
                    "Which resistance genes still require active containment? "
                    "Summarize all elimination decisions so far."
                ),
            },
            {
                "stage": 4,
                "name": "Intervention Assessment",
                "content": (
                    "Infection control implements enhanced contact precautions and "
                    "environmental decontamination. After 2 months: KPC-2 E. coli "
                    "transconjugants cleared (negative cultures x3). KPC-2 K. pneumoniae "
                    "persists in 2 patients (chronic carriers). mcr-1 E. coli cleared. "
                    "mcr-1 K. pneumoniae persists in 1 patient. "
                    "New finding: one K. pneumoniae isolate shows KPC-3 variant (point "
                    "mutation D179Y in KPC-2 → KPC-3), conferring CZA resistance."
                ),
                "active_candidates": ["KPC-2", "KPC-3", "mcr-1"],
                "checkpoint_question": (
                    "Current status of all tracked genes? Which are spreading, "
                    "contained, or newly emerged?"
                ),
            },
            {
                "stage": 5,
                "name": "Final Risk Assessment",
                "content": (
                    "6-month review: KPC-3 variant now in 3/8 original K. pneumoniae "
                    "isolates (mutation selected by CZA treatment). mcr-1 carriers "
                    "down to 1 isolate. KPC-2 (without D179Y) stable in remaining "
                    "isolates. No new species acquisitions detected."
                ),
                "active_candidates": ["KPC-2", "KPC-3", "mcr-1"],
                "checkpoint_question": (
                    "Provide a complete 6-month surveillance summary: initial genes, "
                    "each elimination/deprioritization decision with reason, current "
                    "active threats, and which gene poses the greatest ongoing risk."
                ),
            },
        ],
        "ground_truth": {
            "final_active_targets": ["KPC-2", "KPC-3", "mcr-1"],
            "all_eliminations": {
                "OXA-48": "redundant with KPC-2 (stage 2)",
                "CTX-M-15": "chromosomally integrated, no spread (stage 3)",
                "NDM-1": "non-conjugative plasmid, no transfer (stage 3)",
            },
            "total_checkpoints": 5,
        },
    },
    {
        "id": "lh_sa_003",
        "title": "Biomarker panel refinement for early sepsis detection",
        "stages": [
            {
                "stage": 1,
                "name": "Candidate Identification",
                "content": (
                    "Literature review identifies 8 candidate sepsis biomarkers: "
                    "Procalcitonin (PCT), C-reactive protein (CRP), Interleukin-6 (IL-6), "
                    "Presepsin (sCD14-ST), Pentraxin-3 (PTX3), suPAR, MR-proADM, "
                    "and HBP (heparin-binding protein). Target: identify a 3-marker panel "
                    "for emergency department triage."
                ),
                "active_candidates": ["PCT", "CRP", "IL-6", "Presepsin", "PTX3", "suPAR", "MR-proADM", "HBP"],
                "checkpoint_question": "List all 8 candidate biomarkers.",
            },
            {
                "stage": 2,
                "name": "Analytical Validation",
                "content": (
                    "Immunoassay validation in 200 ED plasma samples. Results: "
                    "PCT: CV <10%, turnaround 20 min (rapid test available). "
                    "CRP: CV <5%, turnaround 15 min. "
                    "IL-6: CV <12%, turnaround 60 min (ELISA only, no rapid test). "
                    "Presepsin: CV <15%, turnaround 30 min. "
                    "PTX3: CV 22% — exceeds acceptable variability. Eliminate PTX3. "
                    "suPAR: CV <8%, turnaround 25 min. "
                    "MR-proADM: CV <10%, but requires specialized analyzer (BRAHMS KRYPTOR). "
                    "HBP: CV <10%, turnaround 15 min."
                ),
                "active_candidates": ["PCT", "CRP", "IL-6", "Presepsin", "suPAR", "MR-proADM", "HBP"],
                "eliminated": {"PTX3": "unacceptable inter-assay CV (22%)"},
                "checkpoint_question": "Which biomarkers passed analytical validation? Which failed and why?",
            },
            {
                "stage": 3,
                "name": "Clinical Discrimination (AUC Analysis)",
                "content": (
                    "Retrospective cohort: 500 ED patients (150 sepsis, 350 non-sepsis). "
                    "AUC for sepsis diagnosis: PCT 0.85, CRP 0.72, IL-6 0.83, "
                    "Presepsin 0.81, suPAR 0.76, MR-proADM 0.88, HBP 0.84. "
                    "Decision: Eliminate CRP (AUC < 0.75, adds little beyond WBC count) "
                    "and suPAR (AUC 0.76, outperformed by all others)."
                ),
                "active_candidates": ["PCT", "IL-6", "Presepsin", "MR-proADM", "HBP"],
                "eliminated": {
                    "CRP": "low discrimination (AUC 0.72)",
                    "suPAR": "outperformed by remaining candidates (AUC 0.76)",
                },
                "checkpoint_question": "Which 5 biomarkers remain? Rank by AUC performance.",
            },
            {
                "stage": 4,
                "name": "Practical Feasibility Assessment",
                "content": (
                    "ED implementation requirements: turnaround < 30 min, no specialized "
                    "equipment beyond standard immunoassay analyzers. "
                    "IL-6: eliminated — ELISA-only (60 min turnaround), incompatible "
                    "with ED workflow. "
                    "MR-proADM: eliminated — requires BRAHMS KRYPTOR analyzer, not "
                    "available in most EDs. "
                    "PCT, Presepsin, HBP: all compatible with standard analyzers "
                    "and < 30 min turnaround."
                ),
                "active_candidates": ["PCT", "Presepsin", "HBP"],
                "eliminated": {
                    "IL-6": "60 min ELISA turnaround, incompatible with ED workflow",
                    "MR-proADM": "requires specialized BRAHMS KRYPTOR analyzer",
                },
                "checkpoint_question": (
                    "Final 3-marker panel selected. List all elimination decisions "
                    "across all stages with reasons."
                ),
            },
        ],
        "ground_truth": {
            "final_active_targets": ["PCT", "Presepsin", "HBP"],
            "all_eliminations": {
                "PTX3": "unacceptable inter-assay CV 22% (stage 2)",
                "CRP": "low AUC 0.72 (stage 3)",
                "suPAR": "outperformed, AUC 0.76 (stage 3)",
                "IL-6": "60 min turnaround, ED incompatible (stage 4)",
                "MR-proADM": "requires specialized analyzer (stage 4)",
            },
            "total_checkpoints": 4,
        },
    },
    {
        "id": "lh_sa_004",
        "title": "Cell line authentication cascade",
        "stages": [
            {
                "stage": 1,
                "name": "Initial Panel",
                "content": (
                    "A cancer biology lab audits 6 cell lines used in a manuscript: "
                    "HeLa, MCF7, A549, HEK293T, U2OS, and MDA-MB-231. STR profiling "
                    "sent to ATCC for authentication."
                ),
                "active_candidates": ["HeLa", "MCF7", "A549", "HEK293T", "U2OS", "MDA-MB-231"],
                "checkpoint_question": "List all cell lines undergoing authentication.",
            },
            {
                "stage": 2,
                "name": "STR Profiling Results",
                "content": (
                    "ATCC STR results returned: "
                    "HeLa: 100% match to ATCC CCL-2. "
                    "MCF7: 95% match to ATCC HTB-22 (acceptable, >80% threshold). "
                    "A549: 100% match. "
                    "HEK293T: 88% match to ATCC CRL-3216. "
                    "U2OS: 72% match — BELOW authentication threshold. Further analysis "
                    "shows it matches HOS (osteosarcoma) at 96%. This is a known "
                    "cross-contamination. Eliminate U2OS (actually HOS). "
                    "MDA-MB-231: 100% match."
                ),
                "active_candidates": ["HeLa", "MCF7", "A549", "HEK293T", "MDA-MB-231"],
                "eliminated": {"U2OS": "cross-contaminated with HOS (72% match to U2OS, 96% to HOS)"},
                "checkpoint_question": "Which cell lines passed STR? Which failed?",
            },
            {
                "stage": 3,
                "name": "Mycoplasma Testing",
                "content": (
                    "PCR-based mycoplasma detection on all 5 remaining lines: "
                    "HeLa: negative. MCF7: POSITIVE for Mycoplasma hyorhinis. "
                    "A549: negative. HEK293T: negative. MDA-MB-231: negative. "
                    "Decision: Eliminate MCF7 from current experiments. Quarantine "
                    "and treat with Plasmocin for 2 weeks before retesting."
                ),
                "active_candidates": ["HeLa", "A549", "HEK293T", "MDA-MB-231"],
                "eliminated": {"MCF7": "Mycoplasma hyorhinis positive"},
                "checkpoint_question": "Which lines remain clean? What happened to MCF7?",
            },
            {
                "stage": 4,
                "name": "Karyotype & Passage Check",
                "content": (
                    "Karyotyping and passage number review: "
                    "HeLa: passage 45, hypotriploid (expected for HeLa, acceptable). "
                    "A549: passage 62, near-diploid (expected). "
                    "HEK293T: passage 78 — high passage. Functional validation shows "
                    "reduced transfection efficiency (35% vs. expected >80%). "
                    "Eliminate HEK293T from transfection-based experiments. "
                    "MDA-MB-231: passage 38, near-triploid (expected)."
                ),
                "active_candidates": ["HeLa", "A549", "MDA-MB-231"],
                "eliminated": {"HEK293T": "high passage (78), reduced transfection efficiency"},
                "checkpoint_question": (
                    "Which cell lines are fully authenticated and functional? "
                    "Provide the complete audit trail."
                ),
            },
        ],
        "ground_truth": {
            "final_active_targets": ["HeLa", "A549", "MDA-MB-231"],
            "all_eliminations": {
                "U2OS": "cross-contaminated with HOS cell line (stage 2)",
                "MCF7": "Mycoplasma hyorhinis positive (stage 3)",
                "HEK293T": "high passage, reduced transfection efficiency (stage 4)",
            },
            "total_checkpoints": 4,
        },
    },
    {
        "id": "lh_sa_005",
        "title": "Environmental microbiome site classification",
        "stages": [
            {
                "stage": 1,
                "name": "Site Survey",
                "content": (
                    "ISS environmental microbiome surveillance samples 7 locations: "
                    "Node 1 (dining table), Node 2 (exercise area), Node 3 (toilet), "
                    "US Lab (workbench), Columbus module (air vent), JEM module (handrail), "
                    "and Cupola (observation window). 16S rRNA amplicon and shotgun "
                    "metagenomics collected from each site at 3 timepoints over 6 months."
                ),
                "active_candidates": ["Node1_dining", "Node2_exercise", "Node3_toilet",
                                      "USLab_workbench", "Columbus_vent", "JEM_handrail",
                                      "Cupola_window"],
                "checkpoint_question": "List all 7 sampling sites and their descriptions.",
            },
            {
                "stage": 2,
                "name": "Alpha Diversity Screening",
                "content": (
                    "Shannon diversity index across timepoints: "
                    "Node1_dining: 3.2 (stable). Node2_exercise: 2.8 (stable). "
                    "Node3_toilet: 4.1 (highest, expected). "
                    "USLab_workbench: 2.5 (stable). Columbus_vent: 3.0 (stable). "
                    "JEM_handrail: 2.7 (stable). "
                    "Cupola_window: 0.8 (extremely low, all 3 timepoints). "
                    "Decision: Classify Cupola as 'low-biomass site' — signal dominated "
                    "by extraction kit contaminants (Ralstonia, Bradyrhizobium pattern). "
                    "Remove from community composition analysis."
                ),
                "active_candidates": ["Node1_dining", "Node2_exercise", "Node3_toilet",
                                      "USLab_workbench", "Columbus_vent", "JEM_handrail"],
                "eliminated": {"Cupola_window": "low biomass, kit contamination dominates signal"},
                "checkpoint_question": "Which sites have reliable data? Why was Cupola removed?",
            },
            {
                "stage": 3,
                "name": "Source Tracking Analysis",
                "content": (
                    "SourceTracker2 results (source: human skin, oral, gut, environmental): "
                    "Node1_dining: 60% oral, 30% skin, 10% unknown. "
                    "Node2_exercise: 75% skin, 15% oral, 10% unknown. "
                    "Node3_toilet: 45% gut, 35% skin, 20% oral. "
                    "USLab_workbench: 50% skin, 40% environmental, 10% unknown. "
                    "Columbus_vent: 85% environmental (HEPA filter associated). "
                    "JEM_handrail: 70% skin, 20% oral, 10% unknown. "
                    "Decision: Reclassify Columbus_vent as 'environmental-dominated' "
                    "— not representative of crew microbiome transfer. Remove from "
                    "crew-associated analysis (retain for environmental monitoring)."
                ),
                "active_candidates": ["Node1_dining", "Node2_exercise", "Node3_toilet",
                                      "USLab_workbench", "JEM_handrail"],
                "eliminated": {"Columbus_vent": "environmental-dominated (85% HEPA-associated)"},
                "checkpoint_question": (
                    "Which sites reflect crew microbiome? Classify each remaining "
                    "site by primary source."
                ),
            },
            {
                "stage": 4,
                "name": "Antimicrobial Resistance Screening",
                "content": (
                    "Shotgun metagenomics ARG analysis (ResFinder): "
                    "Node1_dining: 12 ARGs detected, 3 clinically relevant. "
                    "Node2_exercise: 8 ARGs, 2 clinically relevant. "
                    "Node3_toilet: 25 ARGs, 8 clinically relevant (highest). "
                    "USLab_workbench: 5 ARGs, 1 clinically relevant. "
                    "JEM_handrail: 7 ARGs, 2 clinically relevant. "
                    "Priority sites for enhanced monitoring: Node3_toilet (highest ARG "
                    "burden) and Node1_dining (food preparation area + ARG presence)."
                ),
                "active_candidates": ["Node1_dining", "Node2_exercise", "Node3_toilet",
                                      "USLab_workbench", "JEM_handrail"],
                "checkpoint_question": (
                    "Complete surveillance summary: list all original sites, "
                    "elimination decisions, remaining sites with classification, "
                    "and priority sites for enhanced monitoring."
                ),
            },
        ],
        "ground_truth": {
            "final_active_targets": ["Node1_dining", "Node2_exercise", "Node3_toilet",
                                     "USLab_workbench", "JEM_handrail"],
            "all_eliminations": {
                "Cupola_window": "low biomass, kit contamination (stage 2)",
                "Columbus_vent": "environmental-dominated, not crew-associated (stage 3)",
            },
            "total_checkpoints": 4,
        },
    },
    {
        "id": "lh_sa_006",
        "title": "Variant pathogenicity assessment pipeline",
        "stages": [
            {
                "stage": 1,
                "name": "Variant Identification",
                "content": (
                    "Clinical WES of a pediatric patient with unexplained cardiomyopathy "
                    "identifies 6 rare variants (MAF < 0.01%): "
                    "MYH7 p.R403Q (missense), TNNT2 p.R92W (missense), "
                    "MYBPC3 c.2373dupG (frameshift), LMNA p.R190W (missense), "
                    "TTN p.A5935fs (truncating), SCN5A p.V1405M (missense)."
                ),
                "active_candidates": ["MYH7_R403Q", "TNNT2_R92W", "MYBPC3_2373dupG",
                                      "LMNA_R190W", "TTN_A5935fs", "SCN5A_V1405M"],
                "checkpoint_question": "List all 6 candidate variants with type and gene.",
            },
            {
                "stage": 2,
                "name": "Population Frequency & In Silico",
                "content": (
                    "ClinVar + gnomAD analysis: "
                    "MYH7 R403Q: ClinVar Pathogenic, gnomAD absent — classic HCM mutation. "
                    "TNNT2 R92W: ClinVar Pathogenic, gnomAD 0.003%. "
                    "MYBPC3 2373dupG: ClinVar Pathogenic/Likely Pathogenic, gnomAD 0.005%. "
                    "LMNA R190W: ClinVar VUS, gnomAD 0.008%. SIFT Deleterious, "
                    "PolyPhen2 Probably Damaging. "
                    "TTN A5935fs: ClinVar Likely Benign — TTN truncating variants in "
                    "A-band (not I-band) have low penetrance for DCM. Population frequency "
                    "0.007%. Decision: Eliminate TTN_A5935fs (A-band location, LB in ClinVar). "
                    "SCN5A V1405M: ClinVar Benign, gnomAD 0.05% (too common for "
                    "rare cardiomyopathy). Eliminate SCN5A_V1405M."
                ),
                "active_candidates": ["MYH7_R403Q", "TNNT2_R92W", "MYBPC3_2373dupG", "LMNA_R190W"],
                "eliminated": {
                    "TTN_A5935fs": "A-band truncation, Likely Benign in ClinVar",
                    "SCN5A_V1405M": "Benign in ClinVar, MAF too high (0.05%)",
                },
                "checkpoint_question": "Which variants remain potentially pathogenic? Why were 2 removed?",
            },
            {
                "stage": 3,
                "name": "Segregation Analysis",
                "content": (
                    "Family segregation (trio + 2 affected siblings): "
                    "MYH7 R403Q: present in patient and both affected siblings, "
                    "absent in unaffected parents — de novo in all 3, consistent "
                    "with gonadal mosaicism in one parent. Strong segregation. "
                    "TNNT2 R92W: present in patient and unaffected father — "
                    "incomplete penetrance possible but weakens evidence. "
                    "MYBPC3 2373dupG: present in patient and affected sister, "
                    "absent in brother — partial segregation. "
                    "LMNA R190W: present in patient only, absent in both affected "
                    "siblings — does NOT segregate with disease. "
                    "Decision: Eliminate LMNA_R190W (failed segregation)."
                ),
                "active_candidates": ["MYH7_R403Q", "TNNT2_R92W", "MYBPC3_2373dupG"],
                "eliminated": {"LMNA_R190W": "failed segregation analysis"},
                "checkpoint_question": (
                    "Which variants segregate with the cardiomyopathy phenotype? "
                    "Summarize evidence strength for each remaining variant."
                ),
            },
            {
                "stage": 4,
                "name": "Functional Evidence & Final Classification",
                "content": (
                    "Literature functional studies: "
                    "MYH7 R403Q: extensive functional evidence — impaired ATPase "
                    "activity, abnormal sarcomere organization in iPSC-CMs. "
                    "ACMG classification: Pathogenic (PS1+PS2+PM2+PP3+PP1). "
                    "TNNT2 R92W: functional studies show altered calcium sensitivity. "
                    "However, incomplete penetrance in father reduces clinical significance. "
                    "ACMG classification: Likely Pathogenic (PS1+PM2+PP3). "
                    "MYBPC3 2373dupG: frameshift predicts truncated protein, confirmed "
                    "by RNA analysis showing NMD. ACMG classification: Pathogenic "
                    "(PVS1+PM2+PP1)."
                ),
                "active_candidates": ["MYH7_R403Q", "TNNT2_R92W", "MYBPC3_2373dupG"],
                "checkpoint_question": (
                    "Provide the complete variant assessment: all 6 initial variants, "
                    "each elimination with stage and reason, final ACMG classification "
                    "for remaining variants, and clinical recommendation."
                ),
            },
        ],
        "ground_truth": {
            "final_active_targets": ["MYH7_R403Q", "TNNT2_R92W", "MYBPC3_2373dupG"],
            "all_eliminations": {
                "TTN_A5935fs": "A-band truncation, Likely Benign (stage 2)",
                "SCN5A_V1405M": "Benign, MAF 0.05% (stage 2)",
                "LMNA_R190W": "failed segregation analysis (stage 3)",
            },
            "total_checkpoints": 4,
        },
    },
]


# ============================================================
# error_propagation
# ============================================================

ERROR_PROPAGATION_TASKS = [
    {
        "id": "lh_ep_001",
        "title": "Housekeeping gene instability in microgravity",
        "completed_plan": (
            "A spaceflight transcriptomics study was completed with 6 stages:\n"
            "1. Sample collection: blood from 4 astronauts, pre/post-flight\n"
            "2. RNA extraction: PAXgene, all RIN > 8.0\n"
            "3. Library prep: TruSeq Stranded mRNA, all libraries passed QC\n"
            "4. Sequencing: NovaSeq, 30M reads/sample, >90% Q30\n"
            "5. Analysis: STAR alignment, DESeq2 normalization using GAPDH, ACTB, "
            "and B2M as reference genes. 1,247 differentially expressed genes identified.\n"
            "6. Interpretation: Pathway analysis (GSEA) identified oxidative stress, "
            "DNA repair, and immune activation as top pathways. 15 biomarker candidates "
            "selected based on fold change and adjusted p-value."
        ),
        "revealed_error": (
            "Post-publication review reveals that GAPDH is differentially expressed "
            "in microgravity (2.3-fold upregulation, p=0.001). This was missed because "
            "the reference gene validation was done using ground-based datasets only."
        ),
        "question": (
            "Given this revealed error about GAPDH instability in microgravity, "
            "identify which stages and conclusions are affected and which remain valid. "
            "For each affected element, explain the specific impact. "
            "For each unaffected element, explain why it survives."
        ),
        "ground_truth": {
            "affected": [
                "stage_5_normalization",
                "stage_5_de_gene_list",
                "stage_6_pathway_analysis",
                "stage_6_biomarker_candidates",
            ],
            "unaffected": [
                "stage_1_sample_collection",
                "stage_2_rna_extraction",
                "stage_3_library_prep",
                "stage_4_sequencing",
            ],
            "required_remediation": [
                "re-normalize without GAPDH (use ACTB and B2M only, or geometric mean of stable genes)",
                "re-run DESeq2 with corrected normalization",
                "re-run pathway analysis on corrected DE gene list",
                "re-evaluate biomarker candidates",
            ],
        },
    },
    # ------------------------------------------------------------------
    # Stage 2 additions (lh_ep_002 – lh_ep_006)
    # ------------------------------------------------------------------
    {
        "id": "lh_ep_002",
        "title": "Antibody cross-reactivity in Western blot quantification",
        "completed_plan": (
            "A 4-stage protein expression study:\n"
            "1. Sample collection: liver biopsies from 12 NAFLD patients (6 NASH, 6 simple steatosis)\n"
            "2. Protein extraction: RIPA buffer lysis, BCA quantification, 30ug loaded per lane\n"
            "3. Western blot: anti-CYP2E1 antibody (primary), HRP-conjugated secondary, "
            "ECL detection. Densitometry quantified CYP2E1 expression normalized to beta-actin. "
            "Result: 2.5-fold increase in NASH vs. simple steatosis (p=0.002)\n"
            "4. Downstream: CYP2E1 proposed as NASH severity biomarker. "
            "Correlated CYP2E1 protein levels with oxidative stress markers (MDA, 4-HNE) "
            "and liver fibrosis scores. Strong correlations reported (r=0.82 with MDA)."
        ),
        "revealed_error": (
            "The anti-CYP2E1 antibody (catalog# ab28146) has documented cross-reactivity "
            "with CYP1A2 and CYP3A4. Mass spectrometry validation of the Western blot band "
            "shows it contains both CYP2E1 and CYP3A4 peptides. CYP3A4 is known to be "
            "upregulated in NASH independently of CYP2E1."
        ),
        "question": (
            "Which conclusions from the study are invalidated, and which can be salvaged? "
            "What additional experiments would resolve the ambiguity?"
        ),
        "ground_truth": {
            "affected": [
                "stage_3_cyp2e1_quantification",
                "stage_4_biomarker_proposal",
                "stage_4_correlation_with_oxidative_stress",
            ],
            "unaffected": [
                "stage_1_sample_collection",
                "stage_2_protein_extraction",
                "stage_4_fibrosis_scoring",
            ],
            "required_remediation": [
                "repeat Western blot with validated CYP2E1-specific antibody",
                "or use mass spectrometry for isoform-specific quantification",
                "separate CYP2E1 and CYP3A4 contributions to correlations",
            ],
        },
    },
    {
        "id": "lh_ep_003",
        "title": "Cell line misidentification in cancer drug study",
        "completed_plan": (
            "A 5-stage study of drug sensitivity in gastric cancer:\n"
            "1. Cell culture: MKN45 (gastric adenocarcinoma) used for all experiments\n"
            "2. Drug sensitivity: Dose-response for 5 kinase inhibitors (IC50 determined). "
            "Top hit: lapatinib (HER2 inhibitor) IC50 = 0.3 uM\n"
            "3. Mechanistic validation: HER2 knockdown by siRNA phenocopied lapatinib "
            "effect (60% growth inhibition). Phospho-HER2 Western blot confirmed "
            "on-target inhibition.\n"
            "4. In vivo: MKN45 xenograft in nude mice. Lapatinib 100mg/kg reduced "
            "tumor volume by 65% (p<0.001).\n"
            "5. Clinical translation: Proposed lapatinib for HER2+ gastric cancer. "
            "Referenced MKN45 as MET-amplified model (MKN45 is known for MET, not HER2)."
        ),
        "revealed_error": (
            "STR profiling reveals the 'MKN45' cells used are actually NCI-N87, "
            "a HER2-amplified gastric cancer line. True MKN45 cells are MET-amplified "
            "and HER2-negative. The misidentification likely occurred during passage "
            "in a shared facility."
        ),
        "question": (
            "Re-evaluate all conclusions given the cell line misidentification. "
            "Which findings remain scientifically valid (just in a different context) "
            "and which are fundamentally flawed?"
        ),
        "ground_truth": {
            "affected": [
                "stage_5_clinical_translation_context",
                "stage_5_met_model_claim",
                "stage_1_cell_line_identity",
            ],
            "unaffected": [
                "stage_2_drug_sensitivity_data",
                "stage_3_her2_mechanism",
                "stage_4_xenograft_efficacy",
            ],
            "required_remediation": [
                "re-attribute all data to NCI-N87 (HER2+ context)",
                "findings support lapatinib in HER2+ gastric cancer (valid biology)",
                "repeat key experiments in verified MKN45 for MET-driven context",
            ],
        },
    },
    {
        "id": "lh_ep_004",
        "title": "Batch effect in metabolomics normalization",
        "completed_plan": (
            "A 5-stage untargeted metabolomics study of astronaut plasma:\n"
            "1. Sample collection: Plasma from 6 astronauts, 3 timepoints "
            "(pre-flight, in-flight, post-flight R+1). Total: 18 samples.\n"
            "2. LC-MS acquisition: Reversed-phase C18, positive mode, QC samples "
            "every 10 injections. Run over 2 days (batch 1: pre-flight + in-flight "
            "samples; batch 2: post-flight samples).\n"
            "3. Feature extraction: XCMS peak picking, 4,200 features detected. "
            "Normalization: median fold-change normalization using QC samples.\n"
            "4. Statistical analysis: PCA shows clear separation of pre/in-flight "
            "vs. post-flight. Volcano plot: 380 features significantly changed "
            "(FDR < 0.05, FC > 2) between in-flight and post-flight.\n"
            "5. Pathway analysis: MetaboAnalyst MSEA identifies 'bile acid biosynthesis' "
            "(p=0.001), 'tryptophan metabolism' (p=0.003), and 'fatty acid oxidation' "
            "(p=0.008) as top altered pathways."
        ),
        "revealed_error": (
            "Post-analysis review reveals that all post-flight (R+1) samples were run "
            "in batch 2, while pre-flight and in-flight samples were in batch 1. "
            "The QC samples show a systematic 30% intensity drift between batches "
            "that the median fold-change normalization did not fully correct. "
            "Re-analysis with ComBat batch correction removes 210 of the 380 "
            "significant features."
        ),
        "question": (
            "Which stages and conclusions are compromised by the batch confound? "
            "Which biological findings might still be valid after proper correction? "
            "What would be the correct experimental design to avoid this issue?"
        ),
        "ground_truth": {
            "affected": [
                "stage_3_normalization_insufficient",
                "stage_4_pca_separation",
                "stage_4_volcano_plot_inflated",
                "stage_5_pathway_analysis",
            ],
            "unaffected": [
                "stage_1_sample_collection",
                "stage_2_lc_ms_data_acquisition",
            ],
            "required_remediation": [
                "re-normalize with batch correction (ComBat or similar)",
                "re-run statistics on batch-corrected data (170 features may survive)",
                "re-run pathway analysis on corrected feature list",
                "randomize batch assignment in future experiments",
            ],
        },
    },
    {
        "id": "lh_ep_005",
        "title": "Contaminated negative control in drug screening",
        "completed_plan": (
            "A 5-stage high-throughput drug screen:\n"
            "1. Assay setup: 384-well format, MCF7 cells, 72h treatment. "
            "2,000 FDA-approved compounds at 10 uM.\n"
            "2. Controls: Column 1 = DMSO vehicle (negative), Column 24 = "
            "staurosporine 1 uM (positive kill control). Z'-factor calculated "
            "per plate.\n"
            "3. Readout: CellTiter-Glo luminescence. Raw data normalized: "
            "% viability = (sample - positive) / (negative - positive) * 100.\n"
            "4. Hit calling: 85 compounds with viability < 50% identified as hits. "
            "Confirmation screen in dose-response (8 concentrations): 42 confirmed "
            "with IC50 < 10 uM.\n"
            "5. Target deconvolution: Top 10 hits advanced to mechanistic studies. "
            "Pathway enrichment of targets suggests 'PI3K-AKT signaling' as the most "
            "druggable pathway."
        ),
        "revealed_error": (
            "Plate audit reveals that the DMSO vehicle stock used for negative "
            "controls was contaminated with a low concentration (~0.5 uM) of the "
            "HDAC inhibitor vorinostat. This was traced to a shared liquid handler "
            "that was not properly washed between compound plates. The contamination "
            "reduces baseline viability of negative controls by approximately 20%."
        ),
        "question": (
            "How does the contaminated negative control propagate through the "
            "analysis? Which hits are likely false positives, and which may be real? "
            "Can any data be rescued?"
        ),
        "ground_truth": {
            "affected": [
                "stage_2_negative_control_baseline",
                "stage_3_normalization_calculation",
                "stage_4_hit_calling_threshold",
                "stage_4_confirmation_screen",
            ],
            "unaffected": [
                "stage_1_assay_setup",
                "stage_2_positive_control",
                "stage_5_mechanistic_studies_partially",
            ],
            "required_remediation": [
                "recalculate normalization using corrected baseline",
                "re-call hits with adjusted threshold",
                "HDAC-related hits are suspect (synergy with vorinostat contamination)",
                "non-HDAC hits may still be valid if confirmed in dose-response",
            ],
        },
    },
    {
        "id": "lh_ep_006",
        "title": "Wrong genome build in variant calling pipeline",
        "completed_plan": (
            "A 6-stage clinical WES pipeline:\n"
            "1. Sample: DNA from a pediatric patient with developmental delay.\n"
            "2. Library prep: Agilent SureSelect v7 exome capture.\n"
            "3. Sequencing: NovaSeq, 100x mean coverage.\n"
            "4. Alignment: BWA-MEM to GRCh37 (hg19) reference genome.\n"
            "5. Variant calling: GATK HaplotypeCaller. 45,000 variants called. "
            "Filtered to 1,200 rare variants (gnomAD MAF < 0.01). Prioritized to "
            "15 candidate variants after phenotype-driven filtering (HPO terms).\n"
            "6. Clinical report: Top variant SCN1A c.5536T>C p.F1846L classified "
            "as Likely Pathogenic based on in silico predictions, ClinVar, and "
            "phenotype match (epileptic encephalopathy)."
        ),
        "revealed_error": (
            "The pipeline used GRCh37 reference but the Agilent SureSelect v7 "
            "probes were designed for GRCh38. The coordinate mismatch means "
            "approximately 5% of target regions had suboptimal capture alignment. "
            "Additionally, the gnomAD frequencies used for filtering were from "
            "gnomAD v3 (GRCh38 native), creating a reference-genome mismatch "
            "in allele frequency annotation via liftover."
        ),
        "question": (
            "Trace the impact of the genome build mismatch through the pipeline. "
            "Which results are affected and how? Is the clinical finding still valid?"
        ),
        "ground_truth": {
            "affected": [
                "stage_4_alignment_coordinates",
                "stage_5_coverage_in_mismatch_regions",
                "stage_5_frequency_annotation_accuracy",
                "stage_5_variant_filtering",
            ],
            "unaffected": [
                "stage_1_sample_quality",
                "stage_2_library_prep",
                "stage_3_sequencing_data",
                "stage_6_scn1a_variant_likely_valid",
            ],
            "required_remediation": [
                "re-align to GRCh38 (match probe design)",
                "re-call variants with consistent genome build",
                "use gnomAD v3 GRCh38-native frequencies (no liftover)",
                "check if SCN1A variant persists (likely yes, well-covered gene)",
            ],
        },
    },
]


# ============================================================
# resource_management
# ============================================================

RESOURCE_MANAGEMENT_TASKS = [
    {
        "id": "lh_rm_001",
        "title": "Biobank aliquot allocation under constraints",
        "scenario": (
            "You manage a spaceflight biobank with plasma samples from 8 astronauts. "
            "Each astronaut has 10 aliquots of 500uL plasma (5mL total per astronaut). "
            "Samples are irreplaceable.\n\n"
            "Committed assays (cannot be removed):\n"
            "- SomaScan 7K proteomics: 150uL per sample, singlicate\n"
            "- Olink Explore 3072: 2uL per sample, singlicate\n"
            "- Untargeted metabolomics (LC-MS): 100uL per sample\n"
            "- cfDNA extraction: 1000uL (2 aliquots) per sample\n"
            "- Backup storage minimum: 500uL (1 aliquot) per sample\n\n"
            "Current allocation: 150 + 2 + 100 + 1000 + 500 = 1752uL committed "
            "(3.5 aliquots rounded up to 4 aliquots).\n"
            "Remaining: 6 aliquots (3000uL) per astronaut.\n\n"
            "New requests (prioritized by PI):\n"
            "1. Cytokine panel (Luminex): 50uL per sample\n"
            "2. Targeted lipidomics: 200uL per sample\n"
            "3. Epigenomics (cfDNA methylation): 500uL per sample\n"
            "4. Additional backup aliquot: 500uL\n"
            "5. Exosome isolation: 1000uL per sample\n"
            "6. Functional immune assay: 500uL per sample (but requires FRESH sample, "
            "   not frozen. These samples are all frozen.)"
        ),
        "question": (
            "Determine which new requests can be accommodated. For each request: "
            "(a) state whether it is feasible, (b) calculate the volume impact, "
            "(c) identify any constraints beyond volume. "
            "Show cumulative allocation after each addition."
        ),
        "ground_truth": {
            "feasible": {
                "cytokine_panel": {"volume": 50, "feasible": True},
                "targeted_lipidomics": {"volume": 200, "feasible": True},
                "epigenomics": {"volume": 500, "feasible": True},
                "additional_backup": {"volume": 500, "feasible": True},
                "exosome_isolation": {"volume": 1000, "feasible": True},
            },
            "infeasible": {
                "functional_immune_assay": {
                    "reason": "requires fresh sample, all samples are frozen",
                    "volume_feasible": True,
                    "constraint_violated": "sample_state",
                },
            },
            "cumulative_after_all_feasible": {
                "total_committed": 3502,
                "remaining_per_astronaut": 1498,
                "aliquots_used": 8,
                "aliquots_remaining": 2,
            },
        },
    },
    # ------------------------------------------------------------------
    # Stage 2 additions (lh_rm_002 – lh_rm_006)
    # ------------------------------------------------------------------
    {
        "id": "lh_rm_002",
        "title": "Sequencing lane allocation optimization",
        "scenario": (
            "A genomics core facility has ONE remaining NovaSeq S4 flow cell "
            "(4 lanes, ~2.5 billion clusters per lane = 10 billion total clusters). "
            "Budget: $8,000 for the flow cell.\n\n"
            "Pending projects (PI priority order):\n"
            "1. Whole-genome sequencing (WGS) x 3 samples at 30x: ~1.2B clusters per "
            "sample = 3.6B clusters total. Cost allocation: $2,880\n"
            "2. RNA-seq x 24 samples at 30M reads: ~720M clusters total. Cost: $576\n"
            "3. Exome-seq x 8 samples at 100x: ~1.6B clusters total. Cost: $1,280\n"
            "4. ATAC-seq x 12 samples at 50M reads: ~600M clusters total. Cost: $480\n"
            "5. ChIP-seq x 16 samples at 20M reads: ~320M clusters total. Cost: $256\n"
            "6. Metagenomics x 20 samples at 10M reads: ~200M clusters total. Cost: $160\n"
            "7. Single-cell RNA-seq (10x) x 4 libraries at 50K reads/cell x 10K cells: "
            "~2.0B clusters total. Cost: $1,600\n\n"
            "Constraint: WGS and scRNA-seq CANNOT share a lane (different read lengths: "
            "WGS 150PE vs scRNA 28+90). All other libraries are 150PE compatible.\n"
            "Constraint: All samples from a single project should be on the same lane(s) "
            "to avoid batch effects."
        ),
        "question": (
            "Design an optimal lane allocation. Which projects can be accommodated? "
            "Show cluster counts per lane, identify any projects that must be excluded "
            "or reduced, and explain any constraints violated."
        ),
        "ground_truth": {
            "feasible": {
                "wgs_30x": {"clusters": 3600, "feasible": True},
                "rna_seq": {"clusters": 720, "feasible": True},
                "exome_seq": {"clusters": 1600, "feasible": True},
                "atac_seq": {"clusters": 600, "feasible": True},
                "chip_seq": {"clusters": 320, "feasible": True},
                "metagenomics": {"clusters": 200, "feasible": True},
            },
            "infeasible": {
                "scrna_seq": {
                    "reason": "incompatible read length with WGS and insufficient remaining capacity",
                    "volume_feasible": False,
                    "constraint_violated": "read_length_compatibility",
                },
            },
            "cumulative_after_all_feasible": {
                "total_clusters_million": 7040,
                "capacity_million": 10000,
                "utilization_pct": 70.4,
            },
        },
    },
    {
        "id": "lh_rm_003",
        "title": "R01 grant budget allocation across aims",
        "scenario": (
            "An R01 grant ($1.5M direct costs over 5 years = $300K/year) funds "
            "a multi-omics study with 3 specific aims. The PI must re-allocate "
            "Year 3 budget after Year 2 underspending on Aim 1 and cost overruns on Aim 2.\n\n"
            "Year 3 budget: $300,000 (direct costs only)\n\n"
            "Fixed costs (non-negotiable):\n"
            "- PI salary (25% effort): $45,000\n"
            "- Postdoc salary + benefits: $65,000\n"
            "- Graduate student stipend: $35,000\n"
            "- Lab supplies & overhead basics: $20,000\n"
            "Total fixed: $165,000. Remaining for research: $135,000\n\n"
            "Aim-specific requests:\n"
            "Aim 1 (Genomics): WGS of 30 samples ($200/sample = $6,000), "
            "scRNA-seq of 12 samples ($2,500/sample = $30,000), "
            "computational cloud time: $5,000. Aim 1 total: $41,000\n\n"
            "Aim 2 (Proteomics): TMT-MS for 60 samples ($150/sample = $9,000), "
            "phosphoproteomics for 30 samples ($300/sample = $9,000), "
            "antibody reagents: $8,000. Aim 2 total: $26,000\n\n"
            "Aim 3 (Integration): Spatial transcriptomics (Visium) for 15 samples "
            "($3,000/sample = $45,000), multi-omics integration analysis (cloud): "
            "$10,000, manuscript preparation costs: $5,000. Aim 3 total: $60,000\n\n"
            "Additional request from co-PI: travel to 2 conferences ($6,000), "
            "new laptop for postdoc ($2,500). Additional total: $8,500\n\n"
            "Grand total requested: $135,500 (research) vs $135,000 available."
        ),
        "question": (
            "Can all research activities be funded within the $135,000 research budget? "
            "If not, what should be cut or deferred? Identify any hidden feasibility "
            "issues beyond the budget arithmetic."
        ),
        "ground_truth": {
            "feasible": {
                "aim1_genomics": {"cost": 41000, "feasible": True},
                "aim2_proteomics": {"cost": 26000, "feasible": True},
                "aim3_integration": {"cost": 60000, "feasible": True},
            },
            "infeasible": {
                "conference_travel_and_laptop": {
                    "reason": "not feasible within remaining $135K; $500 over budget",
                    "volume_feasible": False,
                    "constraint_violated": "budget_ceiling",
                },
            },
            "cumulative_after_all_feasible": {
                "total_committed": 135500,
                "remaining": -500,
            },
        },
    },
    {
        "id": "lh_rm_004",
        "title": "Core facility microscopy time scheduling",
        "scenario": (
            "An imaging core has ONE confocal microscope (Zeiss LSM 980) available "
            "for the next 2 weeks (10 working days, 8 hours/day = 80 total hours). "
            "The microscope requires 30 min warm-up at the start of each day "
            "(5 hours total, leaving 75 usable hours).\n\n"
            "Pending requests (deadline-ordered):\n"
            "1. PI Chen (deadline Day 5): Live cell imaging of 20 wells, "
            "15 min/well = 5 hours imaging + 0.5 hour setup = 5.5 hours. "
            "Constraint: MUST use the environmental chamber (37°C, 5% CO2), "
            "which takes 1 hour to stabilize.\n"
            "2. PI Smith (deadline Day 7): Fixed tissue sections, 30 slides, "
            "20 min/slide = 10 hours. No special requirements.\n"
            "3. PI Kumar (deadline Day 10): FRAP experiment, 8 cells, "
            "45 min/cell + setup = 7 hours. Requires the environmental chamber.\n"
            "4. PI Lee (deadline Day 14): Tile scan of 6 whole brain sections, "
            "3 hours/section = 18 hours. Requires automated stage.\n"
            "5. PI Garcia (deadline Day 14): Super-resolution (Airyscan), "
            "40 samples, 30 min/sample = 20 hours. Requires Airyscan module "
            "calibration (2 hours, once).\n"
            "6. Facility maintenance: Laser alignment check (4 hours, must be "
            "done before Day 8). Cannot image during maintenance.\n"
            "7. PI Wong: Fluorescence lifetime imaging (FLIM), 10 samples, "
            "1 hour/sample = 10 hours. Requires FLIM detector that is "
            "currently out for repair (expected return Day 12)."
        ),
        "question": (
            "Create a scheduling plan. Which requests can be accommodated? "
            "Identify any infeasible requests and explain why. "
            "Account for equipment constraints and deadlines."
        ),
        "ground_truth": {
            "feasible": {
                "pi_chen_live_imaging": {"hours": 6.5, "feasible": True},
                "pi_smith_tissue": {"hours": 10, "feasible": True},
                "pi_kumar_frap": {"hours": 7, "feasible": True},
                "pi_lee_tile_scan": {"hours": 18, "feasible": True},
                "pi_garcia_airyscan": {"hours": 22, "feasible": True},
                "maintenance": {"hours": 4, "feasible": True},
            },
            "infeasible": {
                "pi_wong_flim": {
                    "reason": "not feasible: FLIM detector out for repair, returns Day 12 with insufficient time remaining",
                    "volume_feasible": False,
                    "constraint_violated": "equipment_unavailable",
                },
            },
            "cumulative_after_all_feasible": {
                "total_committed": 67.5,
                "remaining_hours": 7.5,
            },
        },
    },
    {
        "id": "lh_rm_005",
        "title": "Bioprocess reagent inventory for cell therapy manufacturing",
        "scenario": (
            "A cell therapy CDMO is manufacturing autologous CAR-T cells for 5 "
            "patients. Each manufacturing run requires (per patient):\n\n"
            "Materials per patient run:\n"
            "- CliniMACS CD4/CD8 beads: 1 vial\n"
            "- Anti-CD3/CD28 Dynabeads: 1 vial (4e7 beads)\n"
            "- Lentiviral vector (CAR construct): 2 mL at 1e8 TU/mL\n"
            "- X-VIVO 15 media: 5 liters\n"
            "- Human AB serum: 500 mL\n"
            "- IL-2 (clinical grade): 1 vial (1M IU)\n"
            "- RetroNectin plates: 2 plates\n"
            "- Release testing reagents (flow cytometry panel): 1 kit\n\n"
            "Current inventory:\n"
            "- CliniMACS beads: 6 vials\n"
            "- Dynabeads: 4 vials (ONLY 4 available, lead time 8 weeks for reorder)\n"
            "- Lentiviral vector: 12 mL (lot expires in 6 weeks)\n"
            "- X-VIVO 15: 30 liters\n"
            "- Human AB serum: 2 liters (lot expires in 3 weeks)\n"
            "- IL-2: 7 vials\n"
            "- RetroNectin plates: 10 plates\n"
            "- Release testing kits: 5 kits\n\n"
            "Manufacturing schedule: 1 patient per week, starting next week. "
            "Each run takes 12 days.\n\n"
            "Additional constraint: GMP suite available only Mon-Fri, so "
            "overlapping runs require separate suites (only 2 available)."
        ),
        "question": (
            "Can all 5 patients be manufactured on schedule? Identify any "
            "reagent shortfalls, expiry risks, and scheduling conflicts. "
            "Propose a modified schedule if needed."
        ),
        "ground_truth": {
            "feasible": {
                "clinimacs_beads": {"needed": 5, "available": 6, "feasible": True},
                "lentiviral_vector": {"needed": 10, "available": 12, "feasible": True},
                "xvivo_media": {"needed": 25, "available": 30, "feasible": True},
                "il2": {"needed": 5, "available": 7, "feasible": True},
                "retronectin": {"needed": 10, "available": 10, "feasible": True},
                "release_kits": {"needed": 5, "available": 5, "feasible": True},
            },
            "infeasible": {
                "dynabeads_shortage": {
                    "reason": "not feasible: need 5 vials, only 4 available, 8-week reorder lead time",
                    "volume_feasible": False,
                    "constraint_violated": "reagent_shortage",
                },
                "human_ab_serum_expiry": {
                    "reason": "not feasible: lot expires in 3 weeks, can only manufacture 3 patients before expiry",
                    "volume_feasible": False,
                    "constraint_violated": "reagent_expiry",
                },
            },
            "cumulative_after_all_feasible": {
                "patients_on_schedule": 3,
                "patients_delayed": 2,
            },
        },
    },
    {
        "id": "lh_rm_006",
        "title": "Clinical trial site and patient allocation",
        "scenario": (
            "A Phase III oncology trial (target N=300) is allocating patients "
            "across 5 clinical sites. Total enrollment period: 18 months.\n\n"
            "Site capabilities and constraints:\n"
            "Site A (academic medical center): IRB approved, 8 oncologists, "
            "expected enrollment 5 patients/month. Has pharmacy compounding "
            "for investigational product (IP). MRI and PET-CT on-site.\n\n"
            "Site B (community hospital): IRB approved, 3 oncologists, "
            "expected enrollment 3 patients/month. No pharmacy compounding — "
            "IP must be shipped from central pharmacy (2-day lead time). "
            "MRI on-site, PET-CT at affiliated facility (30 min away).\n\n"
            "Site C (international — Japan): Ethics approval pending (expected "
            "3 months). 5 oncologists, expected enrollment 4 patients/month "
            "once approved. All facilities available. IP requires cold-chain "
            "international shipping (5-day lead time).\n\n"
            "Site D (VA hospital): IRB approved, 2 oncologists, expected "
            "enrollment 2 patients/month. All facilities. But: eligible "
            "patient population is 95% male, creating gender imbalance.\n\n"
            "Site E (rural clinic): Letter of intent only (not yet submitted "
            "to IRB). 1 oncologist, expected enrollment 1 patient/month. "
            "No PET-CT within 100 miles. Protocol requires baseline PET-CT.\n\n"
            "IP supply: Central pharmacy can produce 20 patient-courses per "
            "month maximum. Current inventory: 50 patient-courses.\n\n"
            "Protocol requires: baseline PET-CT, MRI at weeks 8 and 16, "
            "and PET-CT at week 24 for all patients."
        ),
        "question": (
            "Can the trial enroll 300 patients in 18 months? Identify "
            "infeasible sites, supply constraints, and enrollment risks."
        ),
        "ground_truth": {
            "feasible": {
                "site_a": {"enrollment_18mo": 90, "feasible": True},
                "site_b": {"enrollment_18mo": 54, "feasible": True},
                "site_c": {"enrollment_15mo": 60, "feasible": True},
                "site_d": {"enrollment_18mo": 36, "feasible": True},
            },
            "infeasible": {
                "site_e": {
                    "reason": "not feasible: no PET-CT within 100 miles, protocol requires baseline PET-CT; IRB not yet submitted",
                    "volume_feasible": False,
                    "constraint_violated": "imaging_requirement",
                },
            },
            "cumulative_after_all_feasible": {
                "total_enrollment_projected": 240,
                "target": 300,
                "shortfall": 60,
            },
        },
    },
]


# ============================================================
# adaptive_replanning
# ============================================================

ADAPTIVE_REPLANNING_TASKS = [
    {
        "id": "lh_ar_001",
        "title": "scRNA-seq batch effect forces analysis pivot",
        "original_plan": (
            "Single-cell RNA-seq comparison of spaceflight vs. ground control.\n"
            "Design: 4 cell types (T cells, monocytes, NK cells, B cells) across "
            "2 conditions (flight, ground) x 3 timepoints.\n"
            "Analysis plan: CellRanger -> Seurat -> integration (Harmony) -> "
            "per-cell-type DE analysis -> pathway enrichment -> cell-cell communication.\n"
            "Statistical power: 500+ cells per cell type per condition for DE "
            "(based on power analysis with expected effect size 0.5, alpha=0.05)."
        ),
        "unexpected_result": (
            "After integration, QC reveals that B cells show a strong batch effect "
            "that Harmony cannot resolve (LISI score 0.3 vs. >0.8 for other cell types). "
            "Investigation shows the B cell batch effect correlates with sample processing "
            "delay: flight samples were processed 4 hours later than ground samples due "
            "to logistics. This delay disproportionately affected B cells (known to be "
            "sensitive to processing delay). The B cell data cannot be used for "
            "flight vs. ground comparison."
        ),
        "question": (
            "Revise the analysis plan given the unusable B cell data. Your revised plan must:\n"
            "1. Address what to do with B cell data specifically\n"
            "2. Adjust the remaining analysis for 3 cell types\n"
            "3. Reconsider statistical power implications\n"
            "4. Preserve all valid prior work\n"
            "5. Add any new analyses that the B cell finding enables\n"
            "Do NOT propose restarting from scratch or re-collecting samples."
        ),
        "ground_truth": {
            "required_elements": [
                "drop B cells from flight vs. ground comparison",
                "proceed with T cells, monocytes, NK cells comparison",
                "adjust multiple testing correction (fewer cell types)",
                "document B cell exclusion criteria and reasoning",
                "preserve CellRanger/alignment/QC work for all cell types",
            ],
            "bonus_elements": [
                "use B cell data for within-condition analysis only",
                "report B cell processing sensitivity as a methodological finding",
                "adjust cell-cell communication analysis to exclude B cell interactions",
                "update power analysis for 3 cell types",
            ],
            "prohibited_elements": [
                "restart from raw data unnecessarily",
                "ignore the batch effect and proceed",
                "re-collect samples",
                "exclude all data from the study",
            ],
        },
    },
    # ------------------------------------------------------------------
    # Stage 2 additions (lh_ar_002 – lh_ar_006)
    # ------------------------------------------------------------------
    {
        "id": "lh_ar_002",
        "title": "Failed antibody validation forces assay change",
        "original_plan": (
            "Immunohistochemistry (IHC) study of PD-L1 expression in 200 NSCLC "
            "tumor biopsies for companion diagnostic development.\n"
            "Plan: Use clone 22C3 antibody (Dako) on FFPE sections. Score by "
            "Tumor Proportion Score (TPS): negative (<1%), low (1-49%), high (>=50%). "
            "Validate against RNA-seq PD-L1 (CD274) expression from matched samples.\n"
            "Downstream: Train a digital pathology AI model on IHC-scored images "
            "for automated TPS prediction."
        ),
        "unexpected_result": (
            "Validation reveals the 22C3 antibody lot fails on 60% of archival FFPE "
            "blocks (>5 years old) due to epitope masking from prolonged formalin fixation. "
            "Only blocks fixed within the last 2 years stain reliably. This reduces the "
            "usable cohort from 200 to 80 samples. The antibody vendor confirms this is "
            "a known lot-specific issue and offers no replacement timeline."
        ),
        "question": (
            "Revise the study plan. Maintain the goal of PD-L1 assessment across "
            "the full 200-sample cohort. Consider alternative assays, the impact on "
            "the AI training set, and what can be preserved from existing work."
        ),
        "ground_truth": {
            "required_elements": [
                "switch to SP263 or SP142 antibody for archival samples",
                "validate new antibody against 22C3 on the 80 overlapping samples",
                "retain 80 samples with valid 22C3 staining",
                "use RNA-seq CD274 expression as ground truth for concordance",
            ],
            "bonus_elements": [
                "combine IHC and RNA-seq for composite PD-L1 score",
                "report fixation time as a covariate in analysis",
                "increase AI training diversity by including both antibody results",
            ],
            "prohibited_elements": [
                "discard all existing IHC data",
                "proceed with only 80 samples without acknowledging power loss",
                "use the failed stains for scoring",
            ],
        },
    },
    {
        "id": "lh_ar_003",
        "title": "Unexpected drug resistance in compound screen",
        "original_plan": (
            "Pre-clinical evaluation of a novel KRAS G12C inhibitor (Compound X) "
            "in pancreatic cancer.\n"
            "Plan: Test in 5 KRAS-G12C mutant PDAC cell lines (PANC-1 variant, "
            "MIA PaCa-2, SW1990, Capan-1, AsPC-1). Dose-response (72h, 8 "
            "concentrations), followed by combination screening with standard-of-care "
            "(gemcitabine, nab-paclitaxel). Lead combinations advance to PDX models."
        ),
        "unexpected_result": (
            "Dose-response results: Compound X shows potent activity in MIA PaCa-2 "
            "(IC50 = 0.1 uM) and SW1990 (IC50 = 0.3 uM). However, PANC-1, Capan-1, "
            "and AsPC-1 show NO response up to 10 uM despite confirmed KRAS G12C "
            "mutation. Investigation reveals these 3 lines have co-occurring "
            "NF1 loss-of-function mutations, causing KRAS-independent MAPK pathway "
            "activation that bypasses KRAS G12C inhibition."
        ),
        "question": (
            "Revise the study plan given the NF1-mediated resistance. How should "
            "the combination screening and PDX model selection be adjusted? "
            "What new biological insights does this finding enable?"
        ),
        "ground_truth": {
            "required_elements": [
                "focus single-agent Compound X on sensitive lines",
                "test Compound X plus MEK inhibitor in NF1-loss lines",
                "stratify cell lines by NF1 status",
                "adjust PDX model selection based on NF1 genotype",
            ],
            "bonus_elements": [
                "propose NF1 loss as a predictive biomarker for resistance",
                "test SHP2 inhibitor combination for NF1-loss cells",
                "report resistance mechanism as a translational finding",
            ],
            "prohibited_elements": [
                "exclude resistant lines entirely from the study",
                "ignore NF1 status in combination screening",
                "conclude Compound X is ineffective in PDAC",
            ],
        },
    },
    {
        "id": "lh_ar_004",
        "title": "Contamination discovered mid-experiment in microbiome study",
        "original_plan": (
            "16S rRNA amplicon sequencing of gut microbiome from a dietary intervention "
            "trial: 30 subjects, 2 groups (Mediterranean diet vs. Western diet control), "
            "3 timepoints (baseline, 4 weeks, 12 weeks). Total: 180 stool samples.\n"
            "Planned analysis: compositional analysis (QIIME2), alpha/beta diversity, "
            "differential abundance (ANCOM-BC), taxa-diet correlation.\n"
            "Extraction: PowerSoil Pro kit. Sequencing: V4 region, Illumina MiSeq "
            "2x250 PE, 50,000 reads/sample target."
        ),
        "unexpected_result": (
            "After sequencing the first batch (90 samples — all baseline + 4-week), "
            "quality review reveals that 8 extraction blanks (negative controls) contain "
            "substantial DNA: 2,000-8,000 reads per blank, dominated by Ralstonia, "
            "Bradyrhizobium, and Methylobacterium (known kit contaminants). These taxa "
            "are also detected in 60% of actual samples at 0.5-3% relative abundance. "
            "The second batch (12-week samples) has not yet been extracted."
        ),
        "question": (
            "How should you handle the kit contamination? Revise the analysis plan "
            "for batch 1 and the extraction protocol for batch 2. What data can "
            "be salvaged, and what must be discarded?"
        ),
        "ground_truth": {
            "required_elements": [
                "apply decontam or microDecon to batch 1 data",
                "remove Ralstonia, Bradyrhizobium, Methylobacterium from analysis",
                "include negative controls in decontamination pipeline",
                "use different extraction kit lot or method for batch 2",
            ],
            "bonus_elements": [
                "report contamination prevalence as methodological finding",
                "compare pre- and post-decontamination results to assess impact",
                "add positive mock community control to batch 2",
                "use extraction batch as covariate in statistical models",
            ],
            "prohibited_elements": [
                "ignore contamination and proceed with raw data",
                "discard all batch 1 data entirely",
                "re-extract batch 1 samples (insufficient remaining material noted)",
            ],
        },
    },
    {
        "id": "lh_ar_005",
        "title": "Regulatory hold on clinical trial primary endpoint",
        "original_plan": (
            "Phase II trial of a CDK4/6 inhibitor in HR+/HER2- metastatic breast cancer.\n"
            "Primary endpoint: PFS by investigator assessment (RECIST 1.1).\n"
            "Secondary endpoints: ORR, OS, patient-reported outcomes (PRO-CTCAE).\n"
            "Design: single-arm, 60 patients, Simon two-stage. Stage 1: 20 patients "
            "enrolled, 18 evaluable (2 withdrew consent). Results: 12/18 progression-free "
            "at 6 months. Proceed to stage 2 per protocol.\n"
            "Stage 2: 40 additional patients, enrollment 70% complete."
        ),
        "unexpected_result": (
            "FDA issues a partial clinical hold based on a safety signal from another "
            "trial of the same drug class: unexpected grade 4 hepatotoxicity in 3% of "
            "patients (ALT >20x ULN). The hold requires:\n"
            "1. Enhanced liver function monitoring (weekly LFTs for first 8 weeks)\n"
            "2. Modified inclusion criteria: exclude patients with baseline ALT >1.5x ULN\n"
            "3. New stopping rule: discontinue drug if ALT >10x ULN\n"
            "The hold does NOT require stopping treatment in currently enrolled patients "
            "who are tolerating the drug, but new enrollment is paused for 3 months."
        ),
        "question": (
            "Revise the trial execution plan. How does the 3-month enrollment hold "
            "affect the statistical analysis plan, timeline, and budget? What changes "
            "are needed for currently enrolled vs. new patients?"
        ),
        "ground_truth": {
            "required_elements": [
                "implement weekly LFTs for all current patients",
                "apply modified inclusion criteria to new enrollments",
                "add ALT stopping rule to protocol",
                "extend enrollment period by at least 3 months",
                "file protocol amendment with IRB and FDA",
            ],
            "bonus_elements": [
                "assess impact of modified inclusion criteria on enrollment rate",
                "add hepatotoxicity as an exploratory safety endpoint",
                "update informed consent for current and new patients",
                "budget for additional LFT monitoring costs",
            ],
            "prohibited_elements": [
                "continue enrolling during the hold period",
                "ignore the new stopping rule for current patients",
                "terminate the trial entirely",
                "remove hepatotoxicity data from safety reporting",
            ],
        },
    },
    {
        "id": "lh_ar_006",
        "title": "Instrument breakdown forces method pivot in proteomics",
        "original_plan": (
            "Quantitative proteomics of plasma samples from a COVID-19 severity study: "
            "60 patients (20 mild, 20 severe, 20 ICU). Original method: TMT-16plex "
            "labeling, high-pH fractionation (12 fractions), LC-MS/MS on Orbitrap "
            "Eclipse with SPS-MS3 quantification.\n"
            "Analysis plan: MaxQuant processing, Perseus statistical analysis, "
            "6 TMT sets x 10 samples + reference channel.\n"
            "Progress: 3 of 6 TMT sets completed (30 samples analyzed)."
        ),
        "unexpected_result": (
            "The Orbitrap Eclipse suffers a catastrophic hardware failure (HV power "
            "supply failure) mid-experiment. Repair estimate: 6-8 weeks, $45,000. "
            "Available alternative: a Thermo Q Exactive HF in the same facility. "
            "The Q Exactive HF can run DDA and DIA experiments but does NOT support "
            "SPS-MS3 (required for accurate TMT quantification without ratio "
            "compression). The TMT reagents for the remaining 3 sets are already "
            "purchased ($18,000 worth)."
        ),
        "question": (
            "Revise the proteomics plan. How should the remaining 30 samples be "
            "analyzed to ensure comparability with the first 30? Consider method "
            "compatibility, cost, and timeline constraints."
        ),
        "ground_truth": {
            "required_elements": [
                "switch to DIA for remaining 30 samples on Q Exactive HF",
                "re-analyze first 30 samples by DIA for cross-method comparability",
                "include bridging samples analyzed by both TMT and DIA",
                "adjust statistical analysis to account for method batch",
            ],
            "bonus_elements": [
                "use TMT data as discovery and DIA as validation",
                "compare protein coverage between TMT-MS3 and DIA",
                "save TMT reagents for future use (check stability/expiry)",
                "request repair quote and timeline for Orbitrap Eclipse",
            ],
            "prohibited_elements": [
                "run TMT on Q Exactive HF without MS3 (ratio compression)",
                "discard the first 30 TMT-analyzed samples",
                "wait 6-8 weeks for repair without starting alternative",
                "mix TMT and label-free without batch correction",
            ],
        },
    },
]
