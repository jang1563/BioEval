"""
ProtoReason Advanced Dataset

Additional specialized protocols and advanced reasoning tasks
for comprehensive evaluation.
"""

# =============================================================================
# ADVANCED PROTOCOLS
# =============================================================================

ADVANCED_PROTOCOLS = {
    # -------------------------------------------------------------------------
    # FLOW CYTOMETRY
    # -------------------------------------------------------------------------
    "flow_cytometry_surface": {
        "name": "Surface Marker Flow Cytometry",
        "category": "flow_cytometry",
        "steps": [
            "Prepare single-cell suspension from tissue or culture",
            "Count cells and assess viability - need >90% viability",
            "Aliquot 1x10^6 cells per tube",
            "Centrifuge at 300g for 5 minutes at 4°C",
            "Resuspend in 100μL Fc block solution, incubate 10 min at 4°C",
            "Add fluorochrome-conjugated antibodies at optimized concentrations",
            "Include single-color controls for compensation",
            "Include FMO (fluorescence minus one) controls for gating",
            "Include isotype controls if validating new antibody",
            "Incubate for 30 minutes at 4°C in the dark",
            "Wash with 2mL FACS buffer, centrifuge 300g 5min",
            "Resuspend in 300-500μL FACS buffer",
            "Add viability dye if not already included",
            "Filter through 40μm strainer before acquisition",
            "Acquire on flow cytometer within 1 hour",
            "Collect at least 10,000 events in gate of interest"
        ],
        "critical_steps": [2, 6, 7, 8, 14],
        "safety": [
            "Formaldehyde fixative is toxic if used",
            "Handle human samples as potentially infectious"
        ]
    },
    
    "flow_cytometry_intracellular": {
        "name": "Intracellular Cytokine Staining",
        "category": "flow_cytometry",
        "steps": [
            "Stimulate cells with PMA/ionomycin or antigen for 4-6 hours",
            "Add protein transport inhibitor (Brefeldin A or Monensin) after 1 hour",
            "Harvest cells and wash with PBS",
            "Stain surface markers first (follow surface staining protocol)",
            "Fix cells with 4% PFA or commercial fixation buffer for 20 min",
            "Wash twice with PBS",
            "Permeabilize with 0.1% saponin or commercial perm buffer",
            "Add intracellular antibodies diluted in perm buffer",
            "Incubate 30 minutes at room temperature in dark",
            "Wash twice with perm buffer",
            "Resuspend in FACS buffer for acquisition",
            "Acquire within 24 hours - fixed cells can be stored"
        ],
        "critical_steps": [1, 2, 5, 7],
        "safety": [
            "PMA is a tumor promoter - handle with care",
            "PFA is toxic - use in fume hood"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ELISA
    # -------------------------------------------------------------------------
    "sandwich_elisa": {
        "name": "Sandwich ELISA",
        "category": "immunoassay",
        "steps": [
            "Coat 96-well plate with capture antibody (1-10 μg/mL) overnight at 4°C",
            "Wash plate 3x with wash buffer (PBS + 0.05% Tween-20)",
            "Block with 1% BSA in PBS for 1-2 hours at RT",
            "Wash plate 3x with wash buffer",
            "Prepare standard curve using serial dilutions of recombinant protein",
            "Add samples and standards to wells in duplicate or triplicate",
            "Incubate for 2 hours at RT or overnight at 4°C",
            "Wash plate 5x with wash buffer",
            "Add biotinylated detection antibody, incubate 1 hour at RT",
            "Wash plate 5x with wash buffer",
            "Add streptavidin-HRP conjugate, incubate 30 min at RT",
            "Wash plate 7x with wash buffer",
            "Add TMB substrate, incubate until color develops (5-30 min)",
            "Stop reaction with 2N H2SO4",
            "Read absorbance at 450nm within 30 minutes",
            "Calculate concentrations from standard curve"
        ],
        "critical_steps": [1, 5, 6, 12, 13],
        "safety": [
            "H2SO4 is corrosive - handle with care",
            "TMB is a potential carcinogen"
        ]
    },
    
    # -------------------------------------------------------------------------
    # CLONING
    # -------------------------------------------------------------------------
    "gibson_assembly": {
        "name": "Gibson Assembly Cloning",
        "category": "molecular_biology",
        "steps": [
            "Design primers with 20-40bp overlaps between adjacent fragments",
            "Include overlaps at fragment junctions for assembly",
            "PCR amplify insert(s) with high-fidelity polymerase",
            "Linearize vector by PCR or restriction digest",
            "Gel purify all fragments",
            "Quantify fragments using Nanodrop or Qubit",
            "Calculate molar ratios - use 3:1 insert:vector for single insert",
            "Mix 50-100ng total DNA in appropriate ratios",
            "Add Gibson Assembly Master Mix (contains exonuclease, polymerase, ligase)",
            "Incubate at 50°C for 15-60 minutes",
            "Transform 2μL into competent cells",
            "Plate on selective medium",
            "Screen colonies by colony PCR spanning junctions",
            "Verify positive clones by Sanger sequencing",
            "Prepare glycerol stocks of sequence-verified clones"
        ],
        "critical_steps": [1, 2, 7, 10, 13, 14],
        "safety": [
            "UV exposure during gel visualization - wear protection",
            "EtBr if used is mutagenic"
        ]
    },
    
    "gateway_cloning": {
        "name": "Gateway Cloning",
        "category": "molecular_biology",
        "steps": [
            "Design gene-specific primers with attB1/attB2 sites",
            "PCR amplify gene of interest with attB-flanked primers",
            "Gel purify PCR product",
            "Perform BP reaction: attB-PCR product + pDONR vector + BP Clonase",
            "Incubate at 25°C for 1-18 hours",
            "Add Proteinase K, incubate 10 min at 37°C",
            "Transform into ccdB-sensitive competent cells",
            "Select entry clones on kanamycin plates",
            "Verify entry clone by sequencing",
            "Perform LR reaction: entry clone + destination vector + LR Clonase",
            "Incubate at 25°C for 1-18 hours",
            "Add Proteinase K, incubate 10 min at 37°C",
            "Transform and select on appropriate antibiotic",
            "Verify expression clone by restriction digest and sequencing"
        ],
        "critical_steps": [1, 4, 9, 10, 14],
        "safety": [
            "Standard molecular biology safety precautions"
        ]
    },
    
    # -------------------------------------------------------------------------
    # EPIGENOMICS
    # -------------------------------------------------------------------------
    "atac_seq": {
        "name": "ATAC-seq Library Preparation",
        "category": "genomics",
        "steps": [
            "Prepare single-cell suspension - viability >90% required",
            "Count cells and aliquot 50,000-100,000 cells",
            "Centrifuge at 500g for 5 minutes at 4°C",
            "Resuspend pellet in cold lysis buffer",
            "Incubate on ice for 3 minutes - do not over-lyse",
            "Centrifuge at 500g for 10 minutes at 4°C to pellet nuclei",
            "Resuspend nuclei in transposition reaction mix",
            "Incubate at 37°C for 30 minutes with gentle mixing",
            "Purify transposed DNA using MinElute or similar",
            "Amplify library with indexed primers (determine cycle number by qPCR)",
            "Typically 8-12 PCR cycles to avoid over-amplification",
            "Size select library (150-700bp) using beads or gel",
            "QC library on Bioanalyzer - should see nucleosomal pattern",
            "Quantify library and sequence (50M paired-end reads recommended)"
        ],
        "critical_steps": [1, 4, 5, 7, 10, 11, 13],
        "safety": [
            "Transposase enzyme is expensive - handle carefully"
        ]
    },
    
    "bisulfite_sequencing": {
        "name": "Bisulfite Sequencing for DNA Methylation",
        "category": "genomics",
        "steps": [
            "Extract high-quality genomic DNA (>10kb fragments)",
            "Quantify DNA using Qubit - need 200ng-1μg input",
            "Add unmethylated lambda DNA as conversion control (0.5%)",
            "Denature DNA at 98°C for 10 minutes",
            "Add bisulfite conversion reagent",
            "Incubate at 64°C for 2.5 hours (or per kit instructions)",
            "Desalt and purify converted DNA",
            "Elute in low-EDTA TE buffer",
            "Amplify target regions with bisulfite-specific primers",
            "Use primers designed for converted sequence (C→T)",
            "Clone PCR products or prepare for sequencing",
            "Sequence and analyze methylation patterns",
            "Calculate conversion efficiency from lambda control (>98% required)"
        ],
        "critical_steps": [1, 3, 5, 6, 9, 10, 13],
        "safety": [
            "Bisulfite reagents are corrosive and toxic",
            "Work in fume hood during conversion"
        ]
    },
    
    # -------------------------------------------------------------------------
    # METABOLOMICS
    # -------------------------------------------------------------------------
    "metabolite_extraction": {
        "name": "Metabolite Extraction for LC-MS",
        "category": "metabolomics",
        "steps": [
            "Rapidly quench metabolism: snap-freeze cells or add cold solvent",
            "For adherent cells: aspirate medium, wash quickly with cold PBS",
            "Add cold extraction solvent (80% methanol at -80°C)",
            "Scrape cells into solvent",
            "Transfer to microcentrifuge tube",
            "Vortex vigorously for 30 seconds",
            "Incubate at -80°C for 15 minutes to precipitate proteins",
            "Centrifuge at 14,000g for 10 minutes at 4°C",
            "Transfer supernatant to new tube",
            "Dry under nitrogen or in speed-vac",
            "Resuspend in appropriate solvent for LC-MS",
            "Add internal standards if not added earlier",
            "Centrifuge to remove any particulates",
            "Transfer to LC-MS vials",
            "Keep samples at 4°C in autosampler, analyze within 24h"
        ],
        "critical_steps": [1, 2, 3, 7, 10, 12],
        "safety": [
            "Methanol is flammable and toxic - use in fume hood",
            "Liquid nitrogen for snap-freezing - cryogenic hazard"
        ]
    },
    
    # -------------------------------------------------------------------------
    # CRISPR APPLICATIONS
    # -------------------------------------------------------------------------
    "crispr_activation": {
        "name": "CRISPR Activation (CRISPRa)",
        "category": "molecular_biology",
        "steps": [
            "Design sgRNAs targeting promoter region (-400 to -50 bp from TSS)",
            "Multiple sgRNAs (3-4) per gene often needed for robust activation",
            "Clone sgRNAs into CRISPRa vector (contains dCas9-VP64 or SAM system)",
            "Verify cloning by sequencing",
            "Produce lentivirus in HEK293T cells",
            "Titer virus and determine optimal MOI",
            "Transduce target cells",
            "Select with appropriate antibiotic",
            "Wait 3-7 days for maximal activation",
            "Measure target gene expression by qPCR",
            "Verify protein upregulation by Western blot",
            "Compare to positive control (known activating sgRNA)"
        ],
        "critical_steps": [1, 2, 9, 10, 11],
        "safety": [
            "Lentivirus requires BSL-2 practices"
        ]
    },
    
    "base_editing": {
        "name": "Base Editing (CBE/ABE)",
        "category": "molecular_biology",
        "steps": [
            "Identify target site with desired base in editing window (positions 4-8)",
            "Design sgRNA placing target C or A in editing window",
            "Check for bystander edits - other C/A in window may also be edited",
            "Clone sgRNA into base editor expression vector",
            "Transfect or electroporate cells with base editor + sgRNA",
            "For CBE: expect C→T conversion; for ABE: expect A→G conversion",
            "Wait 72 hours for editing to complete",
            "Extract genomic DNA from bulk population",
            "PCR amplify target region",
            "Analyze by Sanger sequencing (EditR) or deep sequencing",
            "Calculate editing efficiency at target and bystander positions",
            "If needed, single-cell clone to isolate pure edited population"
        ],
        "critical_steps": [1, 2, 3, 10, 11],
        "safety": [
            "Standard molecular biology safety"
        ]
    },
    
    # -------------------------------------------------------------------------
    # PROTEIN BIOCHEMISTRY
    # -------------------------------------------------------------------------
    "protein_purification_his": {
        "name": "His-tag Protein Purification",
        "category": "biochemistry",
        "steps": [
            "Express protein in E. coli - induce with IPTG at optimal OD and temperature",
            "Harvest cells by centrifugation at 4000g for 20 minutes",
            "Resuspend pellet in lysis buffer (50mM Tris, 300mM NaCl, 10mM imidazole)",
            "Add protease inhibitors and lysozyme",
            "Sonicate on ice: 30s on, 30s off, total 5 minutes",
            "Centrifuge lysate at 20,000g for 30 minutes at 4°C",
            "Equilibrate Ni-NTA resin with lysis buffer",
            "Batch bind: incubate lysate with resin for 1 hour at 4°C",
            "Pour into column and collect flow-through",
            "Wash with 10 column volumes of wash buffer (20mM imidazole)",
            "Wash with 10 column volumes of higher imidazole (40mM)",
            "Elute with elution buffer (250mM imidazole)",
            "Collect fractions and analyze by SDS-PAGE",
            "Pool pure fractions and dialyze to remove imidazole",
            "Concentrate if needed and determine final concentration",
            "Aliquot and store at -80°C or use fresh"
        ],
        "critical_steps": [1, 5, 6, 8, 12, 14],
        "safety": [
            "Imidazole can cause skin irritation",
            "PMSF (if used as protease inhibitor) is toxic"
        ]
    },
    
    "size_exclusion_chromatography": {
        "name": "Size Exclusion Chromatography",
        "category": "biochemistry",
        "steps": [
            "Equilibrate SEC column with at least 2 column volumes of buffer",
            "Filter and degas buffer to prevent air bubbles",
            "Centrifuge protein sample at 14,000g for 10 minutes to remove aggregates",
            "Load sample - volume should be <2% of column volume",
            "Run at appropriate flow rate (typically 0.5 mL/min for analytical)",
            "Monitor absorbance at 280nm (protein) and 260nm (nucleic acid)",
            "Collect fractions across elution profile",
            "Analyze fractions by SDS-PAGE",
            "Pool fractions containing target protein",
            "Calculate apparent molecular weight from calibration curve",
            "Oligomeric state can be determined from elution volume"
        ],
        "critical_steps": [1, 3, 4, 10],
        "safety": [
            "High pressure in FPLC system - follow instrument safety"
        ]
    }
}


# =============================================================================
# ADVANCED CALCULATION TASKS
# =============================================================================

ADVANCED_CALCULATIONS = [
    # MOI and viral calculations
    {
        "id": "calc_adv_001",
        "category": "virology",
        "difficulty": "hard",
        "question": """You need to transduce 5 × 10^5 cells at MOI 10. Your lentiviral stock is 
        2 × 10^8 TU/mL. What volume of virus do you need? If transduction efficiency 
        at MOI 10 is typically 95%, how many cells will be transduced?""",
        "answer": {
            "virus_needed_TU": "5 × 10^6 TU",
            "virus_volume": "25 μL",
            "cells_transduced": "4.75 × 10^5 cells"
        },
        "reasoning": "TU needed = cells × MOI = 5×10^5 × 10 = 5×10^6. Volume = 5×10^6 / 2×10^8 = 25μL. Transduced = 5×10^5 × 0.95 = 4.75×10^5"
    },
    
    # Flow cytometry compensation
    {
        "id": "calc_adv_002",
        "category": "flow_cytometry",
        "difficulty": "hard",
        "question": """Your FITC single-color control shows 15% spillover into the PE channel. 
        Your PE single-color control shows 5% spillover into FITC. In a sample, 
        the raw FITC signal is 10,000 and raw PE is 8,000. What are the corrected values?""",
        "answer": {
            "corrected_FITC": "approximately 9,600",
            "corrected_PE": "approximately 6,500"
        },
        "reasoning": "Spillover correction: FITC_corrected ≈ 10000 - (8000 × 0.05) = 9600. PE_corrected ≈ 8000 - (10000 × 0.15) = 6500. (Note: actual compensation uses matrix algebra)"
    },
    
    # Protein concentration from A280
    {
        "id": "calc_adv_003",
        "category": "biochemistry",
        "difficulty": "medium",
        "question": """Your purified antibody has A280 = 1.5. The extinction coefficient for IgG 
        is 1.4 (mg/mL)^-1 cm^-1. What is the concentration? If you need 50 μg for an 
        experiment, what volume do you use?""",
        "answer": {
            "concentration": "1.07 mg/mL",
            "volume_needed": "46.7 μL"
        },
        "reasoning": "C = A280 / ε = 1.5 / 1.4 = 1.07 mg/mL. Volume = 50μg / 1.07μg/μL = 46.7μL"
    },
    
    # Gibson assembly ratios
    {
        "id": "calc_adv_004",
        "category": "cloning",
        "difficulty": "hard",
        "question": """For Gibson assembly, you have a 5 kb vector (100 ng/μL) and a 1.5 kb insert 
        (50 ng/μL). You want 100 ng total DNA with a 3:1 insert:vector molar ratio. 
        How much of each do you need?""",
        "answer": {
            "vector_ng": "50 ng",
            "vector_volume": "0.5 μL",
            "insert_ng": "50 ng × (1.5/5) × 3 = 45 ng",
            "insert_volume": "0.9 μL"
        },
        "reasoning": "At 1:1 molar, insert mass = vector mass × (insert size/vector size). For 3:1: insert = 50 × (1.5/5) × 3 = 45ng. Total = 50 + 45 = 95ng ≈ 100ng"
    },
    
    # Metabolomics normalization
    {
        "id": "calc_adv_005",
        "category": "metabolomics",
        "difficulty": "hard",
        "question": """Your internal standard (IS) peak area is 50,000 in sample A and 75,000 in 
        sample B. A metabolite shows peak area 100,000 in sample A and 120,000 in sample B. 
        Calculate IS-normalized abundances and fold change.""",
        "answer": {
            "normalized_A": "2.0",
            "normalized_B": "1.6",
            "fold_change": "0.8 (sample B is 20% lower)"
        },
        "reasoning": "Normalized = metabolite/IS. A: 100000/50000 = 2.0. B: 120000/75000 = 1.6. FC = 1.6/2.0 = 0.8"
    },
    
    # ELISA standard curve
    {
        "id": "calc_adv_006",
        "category": "immunoassay",
        "difficulty": "hard",
        "question": """Your ELISA standard curve has the equation: OD = 0.002 × [conc] + 0.05, 
        where [conc] is in pg/mL. Sample A has OD = 0.85 and was diluted 1:10. 
        What is the original concentration?""",
        "answer": {
            "diluted_concentration": "400 pg/mL",
            "original_concentration": "4000 pg/mL or 4 ng/mL"
        },
        "reasoning": "[conc] = (OD - 0.05) / 0.002 = (0.85 - 0.05) / 0.002 = 400 pg/mL (diluted). Original = 400 × 10 = 4000 pg/mL"
    },
    
    # Sequencing depth calculation
    {
        "id": "calc_adv_007",
        "category": "genomics",
        "difficulty": "hard",
        "question": """You're doing whole genome sequencing of a 3 Gb genome. You want 30× average 
        coverage with 150 bp paired-end reads. How many read pairs do you need? 
        If your sequencer produces 400M read pairs per run, how many samples can you multiplex?""",
        "answer": {
            "total_bases_needed": "90 Gb",
            "bases_per_read_pair": "300 bp",
            "read_pairs_needed": "300 million",
            "samples_per_run": "1 (barely)"
        },
        "reasoning": "Bases needed = 3Gb × 30 = 90Gb. Per read pair = 300bp. Read pairs = 90Gb / 300bp = 3×10^8. At 400M pairs, can do ~1 sample."
    },
    
    # Transfection efficiency
    {
        "id": "calc_adv_008",
        "category": "cell_biology",
        "difficulty": "medium",
        "question": """You transfected cells with GFP plasmid. Flow cytometry shows 45% GFP+ cells. 
        The GFP+ population has mean fluorescence intensity (MFI) of 15,000 while 
        GFP- is 200 (autofluorescence). If you need 10^6 GFP+ cells for an experiment 
        and you have 80% viability post-transfection, how many cells should you start with?""",
        "answer": {
            "starting_cells": "approximately 2.8 × 10^6 cells"
        },
        "reasoning": "Final GFP+ needed = 10^6. After viability: need 10^6 / 0.8 = 1.25×10^6 viable. After transfection: need 1.25×10^6 / 0.45 = 2.78×10^6 starting"
    }
]


# =============================================================================
# ADVANCED TROUBLESHOOTING
# =============================================================================

ADVANCED_TROUBLESHOOTING = [
    {
        "id": "trouble_adv_001",
        "protocol": "flow_cytometry",
        "scenario": "Flow cytometry showing high percentage of 'double positive' cells that shouldn't exist biologically",
        "details": "Staining T cells for CD4 and CD8. Getting 25% CD4+CD8+ which should be <2% in peripheral blood. Single colors look correct.",
        "possible_causes": [
            "Compensation not set correctly - spillover creating false positives",
            "Doublets not excluded - two cells stuck together",
            "Dead cells binding antibodies non-specifically",
            "Tandem dye degradation creating spillover",
            "Voltage settings too high causing spreading error"
        ],
        "diagnostic_steps": [
            "Check SSC-H vs SSC-A to gate out doublets",
            "Include viability dye and gate on live cells only",
            "Verify compensation with single-color controls",
            "Check if tandem dyes are fresh (degrade over time)",
            "Lower voltages and re-compensate"
        ]
    },
    {
        "id": "trouble_adv_002",
        "protocol": "crispr",
        "scenario": "CRISPR editing efficiency is very low (<5%) despite good sgRNA design",
        "details": "Targeting safe harbor locus in HEK293 cells. sgRNA scores well in silico. Transfected Cas9-sgRNA RNP.",
        "possible_causes": [
            "RNP assembly failed - wrong molar ratios or conditions",
            "Transfection/electroporation conditions not optimal",
            "Cells have low Cas9 activity (some cell lines are resistant)",
            "sgRNA not synthesized correctly or degraded",
            "Target site is in heterochromatin and inaccessible",
            "Cells are polyploid making detection difficult"
        ],
        "diagnostic_steps": [
            "Verify RNP formation by gel shift assay",
            "Check transfection efficiency with fluorescent control",
            "Try in vitro cleavage assay to verify sgRNA activity",
            "Test positive control sgRNA to rule out cell-specific issues",
            "Try CRISPResso2 analysis instead of Sanger for sensitive detection"
        ]
    },
    {
        "id": "trouble_adv_003",
        "protocol": "protein_purification",
        "scenario": "His-tagged protein elutes in flow-through during Ni-NTA purification",
        "details": "6xHis-tagged protein expressed in E. coli. Most protein in flow-through, little binds to column.",
        "possible_causes": [
            "His-tag is buried or cleaved",
            "Imidazole in lysis buffer too high (>20mM prevents binding)",
            "pH too low (His protonation reduces binding)",
            "Protein is aggregated and tag is inaccessible",
            "Reducing agent (DTT/BME) stripping Ni from resin",
            "Resin is old or stripped of nickel"
        ],
        "diagnostic_steps": [
            "Check lysis buffer imidazole concentration",
            "Verify pH is 7.5-8.0",
            "Try denaturing purification (6M guanidine) to expose tag",
            "Re-charge resin with NiSO4",
            "Check if protein is soluble (not aggregated)"
        ]
    },
    {
        "id": "trouble_adv_004",
        "protocol": "rnaseq",
        "scenario": "RNA-seq library shows very high rRNA contamination (>50%)",
        "details": "Used poly-A selection on human cell line. Library QC looked good but sequencing shows mostly rRNA reads.",
        "possible_causes": [
            "RNA degraded - fragmented RNA loses poly-A tail",
            "Poly-A selection beads were old or improperly stored",
            "Insufficient washes during selection",
            "RNA input was too low - rRNA binds non-specifically",
            "Contamination with genomic DNA carrying rRNA genes",
            "Wrong species beads used"
        ],
        "diagnostic_steps": [
            "Check RNA quality on Bioanalyzer - RIN should be >8",
            "Verify poly-A selection worked by qPCR for rRNA vs mRNA",
            "Try ribo-depletion instead of poly-A selection",
            "Increase wash stringency",
            "Include DNase treatment step"
        ]
    },
    {
        "id": "trouble_adv_005",
        "protocol": "metabolomics",
        "scenario": "LC-MS metabolomics showing severe batch effects between runs",
        "details": "Same samples measured on day 1 and day 5 cluster separately by day rather than by condition.",
        "possible_causes": [
            "Column degradation over time",
            "Mobile phase prepared differently",
            "MS source requires cleaning",
            "Temperature variations",
            "Sample degradation if not stored properly",
            "Internal standards not added or added inconsistently"
        ],
        "diagnostic_steps": [
            "Check QC samples across batches",
            "Verify column pressure is stable",
            "Clean MS source and recalibrate",
            "Ensure internal standards normalize batch variation",
            "Use batch correction algorithms (ComBat, etc.)",
            "Run all samples in single batch if possible"
        ]
    }
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_advanced_protocols():
    """Return advanced protocols."""
    return ADVANCED_PROTOCOLS


def get_advanced_calculations():
    """Return advanced calculation tasks."""
    return ADVANCED_CALCULATIONS


def get_advanced_troubleshooting():
    """Return advanced troubleshooting tasks."""
    return ADVANCED_TROUBLESHOOTING


def get_all_extended_statistics():
    """Return combined statistics."""
    from bioeval.protoreason.extended_data import get_task_statistics as base_stats
    
    base = base_stats()
    advanced = {
        "advanced_protocols": len(ADVANCED_PROTOCOLS),
        "advanced_calculations": len(ADVANCED_CALCULATIONS),
        "advanced_troubleshooting": len(ADVANCED_TROUBLESHOOTING)
    }
    
    return {
        **base,
        **advanced,
        "total_protocols": base["protocols"] + advanced["advanced_protocols"],
        "total_calculations": base["calculation_tasks"] + advanced["advanced_calculations"],
        "total_troubleshooting": base["troubleshooting_tasks"] + advanced["advanced_troubleshooting"]
    }


if __name__ == "__main__":
    stats = get_all_extended_statistics()
    print("Extended ProtoReason Statistics:")
    print(f"  Total protocols: {stats['total_protocols']}")
    print(f"  Total calculations: {stats['total_calculations']}")
    print(f"  Total troubleshooting: {stats['total_troubleshooting']}")
