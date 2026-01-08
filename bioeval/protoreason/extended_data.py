"""
ProtoReason Extended Dataset

Comprehensive protocol tasks covering major experimental biology techniques.
"""

# =============================================================================
# EXTENDED PROTOCOL DATABASE
# =============================================================================

PROTOCOLS = {
    # -------------------------------------------------------------------------
    # MOLECULAR BIOLOGY
    # -------------------------------------------------------------------------
    "western_blot": {
        "name": "Western Blot",
        "category": "molecular_biology",
        "steps": [
            "Prepare cell lysate using RIPA buffer with protease and phosphatase inhibitors",
            "Incubate lysate on ice for 30 minutes with occasional vortexing",
            "Centrifuge at 14,000g for 15 minutes at 4°C to remove debris",
            "Transfer supernatant to new tube and determine protein concentration using BCA assay",
            "Prepare samples with 4X Laemmli buffer and heat at 95°C for 5 minutes",
            "Load equal amounts of protein (20-50 μg) into SDS-PAGE gel wells",
            "Include molecular weight marker in first lane",
            "Run gel at 80V through stacking gel, then 120V through resolving gel",
            "Activate PVDF membrane in methanol for 1 minute",
            "Assemble transfer sandwich: sponge-paper-gel-membrane-paper-sponge",
            "Transfer proteins at 100V for 1 hour in cold transfer buffer",
            "Verify transfer with Ponceau S staining",
            "Block membrane with 5% BSA or non-fat milk in TBST for 1 hour at RT",
            "Incubate with primary antibody diluted in blocking buffer overnight at 4°C",
            "Wash membrane 3x with TBST for 10 minutes each",
            "Incubate with HRP-conjugated secondary antibody for 1 hour at RT",
            "Wash membrane 3x with TBST for 10 minutes each",
            "Develop using ECL substrate and image immediately"
        ],
        "critical_steps": [4, 10, 11, 13],  # Most important for success
        "safety": [
            "RIPA buffer contains detergents - avoid skin contact",
            "Acrylamide is neurotoxic - handle gels with gloves",
            "Methanol is flammable - use in ventilated area"
        ],
        "common_failures": [
            "No bands: transfer failure, antibody issue, protein degradation",
            "High background: insufficient blocking, antibody too concentrated",
            "Non-specific bands: antibody cross-reactivity, protein degradation"
        ]
    },
    
    "qpcr": {
        "name": "Quantitative PCR (qPCR)",
        "category": "molecular_biology",
        "steps": [
            "Extract RNA using TRIzol: add 1mL per 10^7 cells, incubate 5 min at RT",
            "Add 200μL chloroform per 1mL TRIzol, shake vigorously for 15 seconds",
            "Centrifuge at 12,000g for 15 minutes at 4°C",
            "Transfer aqueous phase (top layer) to new tube - avoid interphase",
            "Precipitate RNA with 500μL isopropanol, incubate 10 min at RT",
            "Centrifuge at 12,000g for 10 minutes at 4°C",
            "Wash pellet with 1mL 75% ethanol",
            "Air dry pellet for 5-10 minutes - do not over-dry",
            "Resuspend in RNase-free water",
            "Measure RNA concentration and quality (260/280 should be 1.8-2.0)",
            "Treat with DNase I if genomic DNA contamination is a concern",
            "Synthesize cDNA: combine RNA, random primers, dNTPs, RT enzyme",
            "Run RT program: 25°C 10min, 37°C 120min, 85°C 5min",
            "Dilute cDNA 1:5 to 1:10 for qPCR",
            "Prepare qPCR master mix: SYBR Green mix, forward/reverse primers",
            "Add 2μL cDNA template to each well (18μL master mix)",
            "Include no-template controls (NTC) for each primer pair",
            "Include no-RT controls to check for genomic DNA contamination",
            "Run qPCR: 95°C 10min, then 40 cycles of 95°C 15s + 60°C 1min",
            "Perform melt curve analysis: 65°C to 95°C gradient",
            "Verify single peak in melt curve for primer specificity",
            "Analyze using ΔΔCt method with appropriate reference genes"
        ],
        "critical_steps": [3, 4, 10, 17, 18, 20],
        "safety": [
            "TRIzol contains phenol and guanidine - use in fume hood",
            "Chloroform is volatile and toxic - use in fume hood"
        ],
        "common_failures": [
            "High Ct values: RNA degradation, failed RT, primer issues",
            "Multiple melt peaks: primer dimers, non-specific amplification",
            "NTC amplification: contamination, primer dimers"
        ]
    },
    
    "crispr_knockout": {
        "name": "CRISPR-Cas9 Gene Knockout",
        "category": "molecular_biology",
        "steps": [
            "Design sgRNAs targeting early exons using design tools (CRISPOR, Benchling)",
            "Select 2-3 sgRNAs per gene for redundancy",
            "Clone sgRNA sequences into expression vector (e.g., lentiCRISPRv2)",
            "Verify cloning by Sanger sequencing",
            "Produce lentivirus in HEK293T cells with packaging plasmids",
            "Harvest viral supernatant at 48 and 72 hours post-transfection",
            "Filter supernatant through 0.45μm filter",
            "Concentrate virus by ultracentrifugation if needed",
            "Titer virus using serial dilution and selection",
            "Transduce target cells at MOI 0.3-0.5 for single integration",
            "Add polybrene (8μg/mL) to enhance transduction",
            "Begin antibiotic selection 48 hours post-transduction",
            "Maintain selection for 5-7 days until non-transduced cells die",
            "Single-cell clone by limiting dilution or FACS",
            "Expand clones for 2-3 weeks",
            "Extract genomic DNA from clones",
            "PCR amplify target region and sequence",
            "Identify clones with frameshift mutations",
            "Verify knockout by Western blot for protein absence",
            "Confirm phenotype with rescue experiment (re-express wild-type gene)"
        ],
        "critical_steps": [1, 4, 10, 17, 18, 19],
        "safety": [
            "Lentivirus is BSL-2 - work in certified biosafety cabinet",
            "Decontaminate all materials with 10% bleach",
            "Use appropriate PPE and follow institutional biosafety protocols"
        ],
        "common_failures": [
            "No knockout clones: inefficient sgRNA, poor transduction",
            "In-frame deletions: may retain partial function",
            "Off-target effects: verify with multiple sgRNAs"
        ]
    },
    
    "chip_seq": {
        "name": "Chromatin Immunoprecipitation (ChIP-seq)",
        "category": "molecular_biology",
        "steps": [
            "Crosslink cells with 1% formaldehyde for 10 minutes at room temperature",
            "Quench crosslinking with 125mM glycine for 5 minutes",
            "Wash cells 2x with cold PBS",
            "Lyse cells in cell lysis buffer with protease inhibitors",
            "Isolate nuclei by centrifugation at 2,500g for 5 minutes",
            "Resuspend nuclei in nuclear lysis buffer",
            "Sonicate chromatin to 200-500bp fragments (optimize cycles)",
            "Verify fragment size by agarose gel electrophoresis",
            "Centrifuge sonicated chromatin at 14,000g for 10 minutes",
            "Save 10% of supernatant as input control",
            "Pre-clear chromatin with protein A/G beads for 1 hour",
            "Add antibody and incubate overnight at 4°C with rotation",
            "Add protein A/G beads and incubate 2-4 hours at 4°C",
            "Wash beads: 2x low salt, 2x high salt, 2x LiCl, 2x TE buffer",
            "Elute chromatin from beads with elution buffer at 65°C",
            "Reverse crosslinks overnight at 65°C",
            "Treat with RNase A for 30 minutes at 37°C",
            "Treat with Proteinase K for 2 hours at 55°C",
            "Purify DNA by phenol-chloroform extraction or column",
            "Quantify DNA and assess enrichment by qPCR",
            "Prepare sequencing library following standard protocol",
            "Sequence with appropriate depth (20-40M reads for TFs)"
        ],
        "critical_steps": [1, 7, 8, 10, 12, 14],
        "safety": [
            "Formaldehyde is toxic and carcinogenic - use in fume hood",
            "Phenol is corrosive - handle with care"
        ],
        "common_failures": [
            "No enrichment: poor antibody, over-crosslinking, insufficient cells",
            "High background: insufficient washing, non-specific binding",
            "Poor fragment size: optimize sonication conditions"
        ]
    },
    
    # -------------------------------------------------------------------------
    # CELL CULTURE
    # -------------------------------------------------------------------------
    "cell_culture_thawing": {
        "name": "Thawing Cryopreserved Cells",
        "category": "cell_culture",
        "steps": [
            "Pre-warm complete culture medium to 37°C",
            "Prepare a 15mL conical tube with 9mL warm medium",
            "Retrieve cryovial from liquid nitrogen storage - wear cryogloves and face shield",
            "Immediately place vial in 37°C water bath",
            "Gently swirl vial until small ice crystal remains (1-2 minutes)",
            "Spray vial with 70% ethanol before placing in hood",
            "Transfer cell suspension dropwise into prepared medium tube",
            "Centrifuge at 200g for 5 minutes to remove DMSO",
            "Aspirate supernatant carefully without disturbing pellet",
            "Resuspend cells gently in fresh complete medium",
            "Transfer to appropriate culture vessel",
            "Place in 37°C incubator with 5% CO2",
            "Check cells after 24 hours for attachment and viability",
            "Change medium after 24 hours to remove dead cells and debris",
            "Allow cells to recover for 2-3 passages before experiments"
        ],
        "critical_steps": [4, 5, 7, 8],
        "safety": [
            "Liquid nitrogen causes severe cryogenic burns - wear appropriate PPE",
            "DMSO is cytotoxic - remove promptly by centrifugation"
        ],
        "common_failures": [
            "Low viability: cells thawed too slowly, DMSO exposure too long",
            "No attachment: wrong culture vessel, poor cell quality",
            "Contamination: non-sterile technique"
        ]
    },
    
    "cell_culture_transfection": {
        "name": "Lipofection (Plasmid Transfection)",
        "category": "cell_culture",
        "steps": [
            "Seed cells 24 hours before transfection to reach 70-80% confluence",
            "Prepare DNA: dilute plasmid DNA in serum-free medium (Opti-MEM)",
            "Prepare lipid: dilute lipofectamine in serum-free medium",
            "Incubate both tubes at room temperature for 5 minutes",
            "Combine DNA and lipid solutions by adding DNA to lipid",
            "Mix gently and incubate for 20 minutes to form complexes",
            "During incubation, replace cell medium with fresh serum-free medium",
            "Add DNA-lipid complexes dropwise to cells",
            "Gently rock plate to distribute complexes evenly",
            "Incubate at 37°C for 4-6 hours",
            "Replace with complete medium containing serum",
            "Incubate for 24-72 hours depending on experiment",
            "Assess transfection efficiency using fluorescent reporter if available",
            "Proceed with downstream analysis (Western, qPCR, functional assays)"
        ],
        "critical_steps": [1, 5, 6, 10],
        "safety": [
            "Lipofectamine can cause skin irritation",
            "Follow institutional guidelines for recombinant DNA work"
        ],
        "common_failures": [
            "Low efficiency: wrong cell density, DNA:lipid ratio off, poor DNA quality",
            "High toxicity: too much lipofectamine, serum-free too long",
            "Variable results: inconsistent complex formation time"
        ]
    },
    
    "primary_cell_isolation": {
        "name": "Primary Cell Isolation (from tissue)",
        "category": "cell_culture",
        "steps": [
            "Obtain fresh tissue and transport in cold sterile saline",
            "Work quickly - process within 2-4 hours of collection",
            "Mince tissue into 1-2mm pieces using sterile scalpels",
            "Prepare enzymatic digestion solution (collagenase, dispase, or trypsin)",
            "Transfer minced tissue to digestion solution",
            "Incubate at 37°C with gentle agitation for 30-60 minutes",
            "Monitor digestion - tissue should dissociate into single cells",
            "Stop digestion by adding serum-containing medium",
            "Filter suspension through 70μm cell strainer",
            "Centrifuge at 300g for 5 minutes",
            "If red blood cells present, perform RBC lysis",
            "Wash cells 2x with PBS or medium",
            "Count cells and assess viability using trypan blue",
            "Plate cells at appropriate density in specialized medium",
            "For enrichment, perform FACS or magnetic bead selection",
            "Culture in conditions optimized for cell type",
            "Validate cell identity by marker expression or morphology"
        ],
        "critical_steps": [2, 4, 6, 7, 13],
        "safety": [
            "Human/animal tissue may contain pathogens - use BSL-2 practices",
            "Enzymes can cause skin irritation",
            "Follow institutional guidelines for human tissue handling"
        ],
        "common_failures": [
            "Low yield: over-digestion destroying cells, tissue too old",
            "Poor viability: prolonged processing, harsh digestion",
            "Contamination: non-sterile tissue handling"
        ]
    },
    
    # -------------------------------------------------------------------------
    # GENOMICS / SEQUENCING
    # -------------------------------------------------------------------------
    "rna_seq_library": {
        "name": "RNA-seq Library Preparation",
        "category": "genomics",
        "steps": [
            "Start with high-quality total RNA (RIN > 8 for poly-A selection)",
            "Quantify RNA using Qubit fluorometer",
            "Use 100ng - 1μg total RNA as input (kit-dependent)",
            "For poly-A selection: incubate with oligo-dT beads",
            "For ribo-depletion: incubate with rRNA removal probes",
            "Fragment RNA to 200-300bp using heat and divalent cations",
            "Synthesize first-strand cDNA with random primers",
            "Synthesize second-strand cDNA (use dUTP for strand-specificity)",
            "Perform end repair on double-stranded cDNA",
            "Add A-tail to 3' ends",
            "Ligate sequencing adapters",
            "For strand-specific: digest dUTP-containing strand with UDG",
            "PCR amplify library (minimize cycles: 8-12)",
            "Size select library using beads or gel (250-400bp insert)",
            "Quantify library using qPCR or Qubit",
            "Assess library quality on Bioanalyzer or TapeStation",
            "Pool libraries at equimolar concentrations if multiplexing",
            "Sequence on appropriate platform (typically PE150)"
        ],
        "critical_steps": [1, 4, 6, 13, 14, 15],
        "safety": [
            "Work in RNase-free environment",
            "Some reagents are irritants - follow kit safety guidelines"
        ],
        "common_failures": [
            "Low complexity: PCR over-amplification, low input",
            "Adapter dimers: insufficient size selection",
            "3' bias: RNA degradation before library prep"
        ]
    },
    
    "single_cell_rnaseq": {
        "name": "Single-cell RNA-seq (10x Genomics)",
        "category": "genomics",
        "steps": [
            "Prepare single-cell suspension from tissue or culture",
            "Filter through 40μm strainer to remove clumps",
            "Count cells and assess viability (>80% required)",
            "Adjust concentration to 700-1200 cells/μL",
            "Load cells, gel beads, and oil onto Chromium chip",
            "Run Chromium controller to generate GEMs (droplets)",
            "Perform reverse transcription in GEMs",
            "Break emulsion and clean up cDNA",
            "Amplify cDNA by PCR (typically 10-14 cycles)",
            "Check cDNA quality and quantity on Bioanalyzer",
            "Fragment cDNA enzymatically",
            "Perform end repair and A-tailing",
            "Ligate sample index adapters",
            "Amplify library (typically 10-14 cycles)",
            "Size select library (target 400bp)",
            "QC library on Bioanalyzer",
            "Quantify library by qPCR",
            "Sequence on NovaSeq or NextSeq (50,000 reads/cell target)"
        ],
        "critical_steps": [2, 3, 4, 5, 9, 10],
        "safety": [
            "Handle cells according to biosafety level",
            "Some reagents are proprietary - follow 10x guidelines"
        ],
        "common_failures": [
            "Low cell recovery: poor cell quality, wrong concentration",
            "High doublet rate: overloading chip",
            "Low gene detection: dead cells, ambient RNA"
        ]
    },
    
    # -------------------------------------------------------------------------
    # PROTEOMICS
    # -------------------------------------------------------------------------
    "mass_spec_sample_prep": {
        "name": "Mass Spectrometry Sample Preparation",
        "category": "proteomics",
        "steps": [
            "Lyse cells/tissue in compatible buffer (avoid detergents if possible)",
            "Quantify protein using BCA or Bradford assay",
            "Normalize samples to equal protein amount (50-100μg)",
            "Reduce disulfide bonds with DTT (10mM, 30min, 56°C)",
            "Alkylate cysteines with iodoacetamide (20mM, 30min, dark, RT)",
            "Quench excess iodoacetamide with additional DTT",
            "For in-gel digestion: run short SDS-PAGE and cut entire lane",
            "For in-solution: precipitate proteins or use filter-aided prep",
            "Digest proteins with trypsin overnight at 37°C (1:50 enzyme:protein)",
            "Acidify samples with formic acid to pH 2-3",
            "Desalt peptides using C18 tips or columns",
            "Elute peptides with 50-80% acetonitrile",
            "Dry peptides in speed-vac",
            "Resuspend in 0.1% formic acid for LC-MS",
            "Quantify peptides using A280 or colorimetric assay",
            "Inject 1-2μg peptides for standard proteomics run"
        ],
        "critical_steps": [4, 5, 9, 10, 11],
        "safety": [
            "Iodoacetamide is toxic and light-sensitive",
            "Acetonitrile is flammable - use in fume hood",
            "Formic acid is corrosive - handle with care"
        ],
        "common_failures": [
            "Low identification: incomplete digestion, sample loss in cleanup",
            "Missed cleavages: insufficient trypsin, suboptimal pH",
            "Oxidation artifacts: sample exposure to air"
        ]
    },
    
    "coip": {
        "name": "Co-Immunoprecipitation (Co-IP)",
        "category": "proteomics",
        "steps": [
            "Lyse cells in mild non-denaturing buffer (e.g., NP-40 lysis buffer)",
            "Include protease and phosphatase inhibitors",
            "Incubate on ice for 30 minutes",
            "Centrifuge at 14,000g for 15 minutes at 4°C",
            "Transfer supernatant - save input (10%) for Western",
            "Pre-clear lysate with protein A/G beads for 1 hour at 4°C",
            "Remove beads by centrifugation",
            "Add primary antibody to pre-cleared lysate",
            "Include IgG control from same species",
            "Incubate overnight at 4°C with rotation",
            "Add protein A/G beads and incubate 2-4 hours at 4°C",
            "Wash beads 4-5x with lysis buffer",
            "Use increasing stringency washes if background is high",
            "Elute proteins with 2X Laemmli buffer at 95°C for 5 minutes",
            "Analyze by Western blot for interacting proteins",
            "Include input and IgG controls on same blot"
        ],
        "critical_steps": [1, 6, 8, 9, 12],
        "safety": [
            "Work at 4°C to preserve protein interactions",
            "NP-40 is an irritant"
        ],
        "common_failures": [
            "No interaction detected: interaction disrupted by lysis conditions",
            "High background: insufficient washing, non-specific binding",
            "False positive: antibody heavy chain co-migrating with target"
        ]
    },
    
    # -------------------------------------------------------------------------
    # IMAGING
    # -------------------------------------------------------------------------
    "immunofluorescence": {
        "name": "Immunofluorescence Staining",
        "category": "imaging",
        "steps": [
            "Seed cells on coverslips or chamber slides",
            "Allow cells to attach and reach desired confluence (24-48h)",
            "Remove medium and wash once with PBS",
            "Fix cells with 4% paraformaldehyde for 15 minutes at RT",
            "Wash 3x with PBS",
            "Permeabilize with 0.1-0.5% Triton X-100 for 10 minutes",
            "Wash 3x with PBS",
            "Block with 3-5% BSA or serum in PBS for 1 hour at RT",
            "Dilute primary antibody in blocking buffer",
            "Incubate with primary antibody overnight at 4°C",
            "Wash 3x with PBS for 5 minutes each",
            "Dilute fluorescent secondary antibody in blocking buffer",
            "Incubate with secondary antibody for 1 hour at RT in dark",
            "Wash 3x with PBS for 5 minutes each",
            "Counterstain nuclei with DAPI (1μg/mL) for 5 minutes",
            "Wash 2x with PBS",
            "Mount coverslips with anti-fade mounting medium",
            "Seal edges with nail polish",
            "Image using fluorescence or confocal microscope",
            "Store slides at 4°C protected from light"
        ],
        "critical_steps": [4, 6, 8, 10, 13],
        "safety": [
            "Paraformaldehyde is toxic - use in fume hood",
            "Protect samples from light after adding fluorescent antibodies"
        ],
        "common_failures": [
            "No signal: wrong antibody, over-fixation, epitope masked",
            "High background: insufficient blocking, antibody too concentrated",
            "Photobleaching: excessive light exposure, no anti-fade"
        ]
    },
    
    "live_cell_imaging": {
        "name": "Live Cell Time-Lapse Imaging",
        "category": "imaging",
        "steps": [
            "Seed cells in glass-bottom imaging dishes",
            "Allow cells to attach and equilibrate (24h)",
            "Pre-warm microscope incubation chamber to 37°C",
            "Equilibrate CO2 to 5% in chamber",
            "If using phenol red medium, switch to phenol red-free medium",
            "Add fluorescent reporters or dyes if needed",
            "Allow cells to equilibrate in imaging medium for 30 min",
            "Place dish in pre-warmed microscope stage",
            "Wait for temperature to stabilize (15-30 min)",
            "Find and mark positions of interest using multipoint acquisition",
            "Set up Z-stack parameters if imaging 3D structures",
            "Optimize laser power and exposure to minimize phototoxicity",
            "Set imaging interval based on biological process speed",
            "Acquire reference images before adding treatment",
            "Add treatment without moving dish if possible",
            "Start time-lapse acquisition",
            "Monitor for focus drift and cell health during acquisition",
            "Save raw data in lossless format",
            "Analyze using appropriate tracking/quantification software"
        ],
        "critical_steps": [3, 4, 9, 12, 13, 17],
        "safety": [
            "Laser light can damage eyes - follow microscope safety protocols",
            "Some fluorescent dyes are toxic - handle appropriately"
        ],
        "common_failures": [
            "Focus drift: incomplete temperature equilibration, unstable stage",
            "Cell death: phototoxicity, wrong medium, temperature fluctuation",
            "Bleaching: laser power too high, intervals too frequent"
        ]
    }
}


# =============================================================================
# CALCULATION TASKS - EXPANDED
# =============================================================================

CALCULATION_TASKS = [
    # Basic dilutions
    {
        "id": "calc_001",
        "category": "dilution",
        "difficulty": "easy",
        "question": "Prepare 500 mL of 1X PBS from a 10X PBS stock.",
        "answer": {"10X_PBS": "50 mL", "water": "450 mL"},
        "reasoning": "C1V1 = C2V2. 10X × V1 = 1X × 500mL. V1 = 50 mL"
    },
    {
        "id": "calc_002",
        "category": "dilution",
        "difficulty": "easy",
        "question": "Dilute a 100 μM primer stock to make 500 μL of 10 μM working solution.",
        "answer": {"stock": "50 μL", "water": "450 μL"},
        "reasoning": "C1V1 = C2V2. 100μM × V1 = 10μM × 500μL. V1 = 50 μL"
    },
    {
        "id": "calc_003",
        "category": "dilution",
        "difficulty": "medium",
        "question": "You have a 5 mg/mL antibody stock. Prepare 10 mL of a 1:1000 dilution for Western blot.",
        "answer": {"stock": "10 μL", "buffer": "9.99 mL", "final_concentration": "5 μg/mL"},
        "reasoning": "1:1000 means 1 part stock + 999 parts diluent. For 10mL: 10μL stock + 9990μL buffer"
    },
    
    # Protein quantification
    {
        "id": "calc_004",
        "category": "protein",
        "difficulty": "easy",
        "question": "Your BCA assay gives an absorbance that corresponds to 2.5 mg/mL protein. You need to load 30 μg per lane. What volume should you load?",
        "answer": {"volume": "12 μL"},
        "reasoning": "Volume = mass / concentration = 30 μg / 2.5 μg/μL = 12 μL"
    },
    {
        "id": "calc_005",
        "category": "protein",
        "difficulty": "medium",
        "question": "You have 500 μL of cell lysate at 4 mg/mL. You need to run 6 Western blot lanes with 40 μg each, plus save 100 μg for IP. Do you have enough?",
        "answer": {"total_available": "2000 μg", "total_needed": "340 μg", "sufficient": "yes"},
        "reasoning": "Available: 500μL × 4mg/mL = 2000μg. Needed: (6 × 40) + 100 = 340μg. Yes, sufficient."
    },
    
    # Cell counting
    {
        "id": "calc_006",
        "category": "cell_culture",
        "difficulty": "easy",
        "question": "You count 180 cells total in 4 corner squares of a hemocytometer (each 1mm × 1mm × 0.1mm). What is the cell concentration?",
        "answer": {"concentration": "4.5 × 10^5 cells/mL"},
        "reasoning": "Average per square = 180/4 = 45. Volume per square = 0.1μL. Concentration = 45/0.0001mL = 4.5 × 10^5 cells/mL"
    },
    {
        "id": "calc_007",
        "category": "cell_culture",
        "difficulty": "medium",
        "question": "You need to seed a 6-well plate at 2 × 10^5 cells/well. Your cell suspension is 8 × 10^5 cells/mL. Each well needs 2 mL final volume. Calculate volumes needed.",
        "answer": {"cells_per_well": "250 μL", "medium_per_well": "1750 μL", "total_cell_suspension": "1.5 mL"},
        "reasoning": "Cells needed per well: 2×10^5. Volume: 2×10^5 / 8×10^5 = 0.25 mL. Medium: 2 - 0.25 = 1.75 mL. Total for 6 wells: 6 × 0.25 = 1.5 mL"
    },
    {
        "id": "calc_008",
        "category": "cell_culture",
        "difficulty": "hard",
        "question": "HeLa cells double every 24 hours. You seed 5 × 10^4 cells in a T75 flask (75 cm²). If cells reach confluence at 10^5 cells/cm², how many days until confluence?",
        "answer": {"days": "approximately 4 days", "cells_at_confluence": "7.5 × 10^6"},
        "reasoning": "Confluence = 75cm² × 10^5 = 7.5×10^6 cells. Doublings needed: log2(7.5×10^6 / 5×10^4) = log2(150) ≈ 7.2 doublings = 4.3 days"
    },
    
    # Molecular biology
    {
        "id": "calc_009",
        "category": "molecular_biology",
        "difficulty": "medium",
        "question": "Your RNA concentration is 850 ng/μL with 260/280 = 2.0. For cDNA synthesis, you need 1 μg RNA in 20 μL reaction. Calculate volumes.",
        "answer": {"rna_volume": "1.18 μL", "water_volume": "18.82 μL", "quality": "good"},
        "reasoning": "RNA volume = 1000ng / 850ng/μL = 1.18μL. Water = 20 - 1.18 = 18.82μL. 260/280 = 2.0 indicates pure RNA."
    },
    {
        "id": "calc_010",
        "category": "molecular_biology",
        "difficulty": "hard",
        "question": "Calculate the molarity of a 250 bp double-stranded DNA fragment at 50 ng/μL. (Average MW of dsDNA: 660 Da per bp)",
        "answer": {"molarity": "303 nM"},
        "reasoning": "MW = 250bp × 660Da/bp = 165,000 Da. Molarity = (50ng/μL × 10^6) / 165,000 = 303 nM"
    },
    
    # qPCR analysis
    {
        "id": "calc_011",
        "category": "qpcr",
        "difficulty": "medium",
        "question": "Calculate fold change using ΔΔCt method. Target gene: Control Ct=25, Treated Ct=22. Reference gene: Control Ct=18, Treated Ct=18.",
        "answer": {"delta_ct_control": "7", "delta_ct_treated": "4", "delta_delta_ct": "-3", "fold_change": "8"},
        "reasoning": "ΔCt(control) = 25-18 = 7. ΔCt(treated) = 22-18 = 4. ΔΔCt = 4-7 = -3. Fold change = 2^-(-3) = 8"
    },
    {
        "id": "calc_012",
        "category": "qpcr",
        "difficulty": "hard",
        "question": "Your qPCR standard curve has slope = -3.4 and R² = 0.998. Calculate the efficiency. Is this acceptable?",
        "answer": {"efficiency": "96.8%", "acceptable": "yes"},
        "reasoning": "Efficiency = 10^(-1/slope) - 1 = 10^(-1/-3.4) - 1 = 10^0.294 - 1 = 0.968 = 96.8%. Acceptable range: 90-110%"
    },
    
    # Transfection / Virus
    {
        "id": "calc_013",
        "category": "transfection",
        "difficulty": "medium",
        "question": "For lentiviral transduction, you want MOI = 0.5. You have 2 × 10^5 target cells and viral titer of 10^8 TU/mL. What volume of virus needed?",
        "answer": {"virus_volume": "1 μL", "infectious_units_needed": "10^5"},
        "reasoning": "Infectious units = cells × MOI = 2×10^5 × 0.5 = 10^5 TU. Volume = 10^5 / 10^8 = 10^-3 mL = 1 μL"
    },
    {
        "id": "calc_014",
        "category": "transfection",
        "difficulty": "hard",
        "question": "For a 6-well plate transfection, you use 2.5 μg DNA and 7.5 μL Lipofectamine per well (1:3 ratio). Scale up for a 10 cm dish (surface area 78.5 cm² vs 9.6 cm² per 6-well).",
        "answer": {"dna": "20.4 μg", "lipofectamine": "61.2 μL"},
        "reasoning": "Scale factor = 78.5/9.6 = 8.18. DNA = 2.5 × 8.18 = 20.4 μg. Lipofectamine = 7.5 × 8.18 = 61.2 μL"
    },
    
    # Solution preparation
    {
        "id": "calc_015",
        "category": "solutions",
        "difficulty": "medium",
        "question": "Prepare 100 mL of 50 mM Tris-HCl pH 7.5 from Tris base (MW = 121.14 g/mol). How much Tris base do you weigh?",
        "answer": {"mass": "0.606 g"},
        "reasoning": "Moles = 0.05M × 0.1L = 0.005 mol. Mass = 0.005 × 121.14 = 0.606 g. Adjust pH with HCl after dissolving."
    },
    {
        "id": "calc_016",
        "category": "solutions",
        "difficulty": "hard",
        "question": "Prepare 500 mL of RIPA buffer: 50 mM Tris pH 8.0, 150 mM NaCl, 1% NP-40, 0.5% sodium deoxycholate. You have 1M Tris pH 8.0, 5M NaCl, 10% NP-40, 10% sodium deoxycholate stocks.",
        "answer": {
            "1M_Tris": "25 mL",
            "5M_NaCl": "15 mL", 
            "10%_NP40": "50 mL",
            "10%_deoxycholate": "25 mL",
            "water": "385 mL"
        },
        "reasoning": "Tris: 0.05M × 500mL / 1M = 25mL. NaCl: 0.15M × 500mL / 5M = 15mL. NP-40: 1% × 500mL / 10% = 50mL. Deoxycholate: 0.5% × 500mL / 10% = 25mL"
    }
]


# =============================================================================
# TROUBLESHOOTING TASKS - EXPANDED
# =============================================================================

TROUBLESHOOTING_TASKS = [
    # Western Blot problems
    {
        "id": "trouble_001",
        "protocol": "western_blot",
        "scenario": "No bands visible on the membrane after development",
        "details": "Target: β-actin (42 kDa), Primary: mouse anti-β-actin 1:5000, Secondary: anti-mouse HRP 1:10000, Transfer: 1h at 100V, ECL exposure: 1 minute",
        "possible_causes": [
            "Transfer failure - proteins didn't transfer to membrane",
            "Membrane activated incorrectly (PVDF needs methanol activation)",
            "Primary antibody inactive or wrong species reactivity",
            "Secondary antibody doesn't match primary species",
            "ECL substrate expired or mixed incorrectly",
            "Over-blocking prevented antibody binding",
            "Target protein not expressed in sample"
        ],
        "diagnostic_steps": [
            "Stain membrane with Ponceau S to verify protein transfer",
            "Check gel after transfer for remaining protein",
            "Try fresh primary antibody or higher concentration",
            "Verify secondary antibody species matches primary",
            "Test ECL with fresh reagents"
        ],
        "most_likely": "Transfer failure - verify with Ponceau S staining first"
    },
    {
        "id": "trouble_002", 
        "protocol": "western_blot",
        "scenario": "Very high background obscuring specific bands",
        "details": "Target: phospho-ERK, Primary: rabbit anti-pERK 1:1000 overnight, Blocking: 5% milk in TBST for 30 min, Washes: 3x5min TBST",
        "possible_causes": [
            "Insufficient blocking time - increase to 1 hour",
            "Milk blocks phospho-epitopes - use BSA instead for phospho-proteins",
            "Primary antibody concentration too high",
            "Insufficient washing - increase washes to 3x10min",
            "Secondary antibody non-specific binding",
            "Membrane dried out during incubation"
        ],
        "diagnostic_steps": [
            "Switch to 5% BSA blocking for phospho-proteins",
            "Increase blocking time to 1 hour",
            "Titrate primary antibody (try 1:2000, 1:5000)",
            "Increase wash stringency and duration"
        ],
        "most_likely": "Using milk for phospho-protein - milk contains casein which is phosphorylated and blocks phospho-antibody binding"
    },
    
    # qPCR problems
    {
        "id": "trouble_003",
        "protocol": "qpcr",
        "scenario": "High Ct values (>35) for all samples including positive control",
        "details": "SYBR Green chemistry, cDNA from 1μg RNA, primers for GAPDH (housekeeping), primer concentration 10μM",
        "possible_causes": [
            "cDNA synthesis failed - RT enzyme inactive or wrong conditions",
            "RNA was degraded before RT",
            "Primers not working - wrong design, degraded, or wrong concentration",
            "qPCR master mix problem - enzyme degraded",
            "Template diluted too much",
            "Annealing temperature too high"
        ],
        "diagnostic_steps": [
            "Check RNA quality on gel or Bioanalyzer (before RT)",
            "Verify cDNA synthesis with PCR and gel",
            "Test primers with plasmid containing target sequence",
            "Check primer concentration in reaction (should be 200-500nM final)",
            "Run temperature gradient to optimize annealing"
        ],
        "most_likely": "cDNA synthesis failure - run conventional PCR on cDNA and visualize on gel"
    },
    {
        "id": "trouble_004",
        "protocol": "qpcr",
        "scenario": "Multiple peaks in melt curve analysis",
        "details": "SYBR Green qPCR, novel primers for gene of interest, single band expected at 150bp, Ct values ~28",
        "possible_causes": [
            "Primer dimers forming - especially visible at low template",
            "Non-specific amplification - primers binding elsewhere in genome",
            "Genomic DNA contamination - intron-spanning primers should prevent",
            "Primer degradation creating truncated products",
            "Template has splice variants"
        ],
        "diagnostic_steps": [
            "Run qPCR products on agarose gel to see band sizes",
            "Check NTC for primer dimer peak",
            "Include -RT control to rule out genomic DNA",
            "Redesign primers with better specificity",
            "Increase annealing temperature to improve specificity"
        ],
        "most_likely": "Primer dimers or non-specific products - verify by running products on gel"
    },
    
    # Cell culture problems
    {
        "id": "trouble_005",
        "protocol": "cell_culture",
        "scenario": "Cells not attaching after passaging",
        "details": "HeLa cells, passage 15, split 1:10, standard DMEM + 10% FBS, tissue culture-treated flask",
        "possible_causes": [
            "Over-trypsinization damaged cell surface proteins",
            "Trypsin not fully neutralized",
            "Wrong flask type - not tissue culture treated",
            "Medium pH off (check if color is orange, not pink or yellow)",
            "Cells are senescent or unhealthy",
            "Contamination affecting cell health",
            "Serum lot problem - try different lot"
        ],
        "diagnostic_steps": [
            "Reduce trypsin exposure time in next passage",
            "Verify trypsin is neutralized (>4x volume serum-containing medium)",
            "Check flask labeling for TC treatment",
            "Test with fresh medium and serum",
            "Examine cells for signs of contamination"
        ],
        "most_likely": "Over-trypsinization - reduce time and check cells frequently during dissociation"
    },
    {
        "id": "trouble_006",
        "protocol": "cell_culture",
        "scenario": "Contamination appeared in multiple flasks simultaneously",
        "details": "3 different cell lines affected, bacterial contamination (cloudy medium, rapid pH drop), all used same bottle of medium",
        "possible_causes": [
            "Shared medium bottle contaminated",
            "Water bath contamination",
            "Pipette contaminated",
            "Incubator contamination",
            "Non-sterile technique"
        ],
        "diagnostic_steps": [
            "Discard the shared medium bottle",
            "Clean and disinfect water bath",
            "Clean incubator with appropriate disinfectant",
            "Plate medium sample to identify organism",
            "Review aseptic technique with all users"
        ],
        "most_likely": "Shared medium bottle - discard immediately and use fresh"
    },
    
    # Transfection problems
    {
        "id": "trouble_007",
        "protocol": "transfection",
        "scenario": "Very low transfection efficiency (<5%)",
        "details": "HEK293 cells, lipofectamine 3000, GFP reporter plasmid, cells were ~90% confluent at transfection",
        "possible_causes": [
            "Cell density too high - optimal is 70-80% confluence",
            "DNA:lipid ratio not optimal",
            "DNA quality poor (check 260/280, run gel)",
            "Complex formation time wrong",
            "Serum in medium during complex formation",
            "Cells too old (high passage)"
        ],
        "diagnostic_steps": [
            "Optimize cell density at transfection (try 60-70%)",
            "Test range of DNA:lipid ratios",
            "Check DNA quality (should have 260/280 ~1.8)",
            "Ensure serum-free medium for complex formation",
            "Use low passage cells"
        ],
        "most_likely": "Cell density too high - cells at 90% may be contact-inhibited and less receptive"
    },
    
    # ChIP problems
    {
        "id": "trouble_008",
        "protocol": "chip_seq",
        "scenario": "No enrichment over input for positive control regions",
        "details": "ChIP for H3K4me3 (active promoter mark), crosslinked 10 min with 1% formaldehyde, sonicated to 200-500bp",
        "possible_causes": [
            "Antibody not suitable for ChIP (works in WB doesn't mean works in ChIP)",
            "Over-crosslinking masking epitope",
            "Under-crosslinking losing protein-DNA interactions",
            "Sonication conditions not optimal",
            "Insufficient starting material",
            "Elution incomplete"
        ],
        "diagnostic_steps": [
            "Verify antibody is ChIP-validated",
            "Test crosslinking time series (5, 10, 15 min)",
            "Verify sonication by running on gel",
            "Check input DNA amount",
            "Use positive control antibody (e.g., anti-H3)"
        ],
        "most_likely": "Antibody not ChIP-grade - verify with validated ChIP-seq antibody"
    },
    
    # Immunofluorescence problems
    {
        "id": "trouble_009",
        "protocol": "immunofluorescence",
        "scenario": "High non-specific nuclear staining with cytoplasmic protein antibody",
        "details": "Antibody against cytoplasmic protein showing strong nuclear signal, PFA fixation, 0.1% Triton permeabilization",
        "possible_causes": [
            "Over-permeabilization causing antibody penetration into nucleus",
            "Fixation not complete - protein relocalized during permeabilization",
            "Secondary antibody binding to nuclear components",
            "Primary antibody cross-reacting with nuclear protein",
            "Antibody concentration too high"
        ],
        "diagnostic_steps": [
            "Reduce Triton concentration (try 0.05%)",
            "Try different fixation (methanol instead of PFA)",
            "Run secondary-only control",
            "Titrate primary antibody",
            "Validate antibody specificity by knockdown"
        ],
        "most_likely": "Over-permeabilization - reduce Triton concentration or time"
    },
    
    # Cloning problems
    {
        "id": "trouble_010",
        "protocol": "molecular_biology",
        "scenario": "No colonies after transformation with ligation product",
        "details": "Insert and vector both cut with EcoRI/BamHI, CIP-treated vector, T4 ligase overnight at 16°C, DH5α competent cells",
        "possible_causes": [
            "Incompatible ends or incomplete digestion",
            "CIP over-treatment damaging vector",
            "Ligase inactive or wrong buffer",
            "Competent cells not competent",
            "Insert:vector ratio wrong",
            "Ligation product toxic to cells",
            "Antibiotic resistance gene problem"
        ],
        "diagnostic_steps": [
            "Transform uncut plasmid to verify competent cells",
            "Transform cut+religated vector to verify ligation",
            "Run digested products on gel to verify complete cutting",
            "Try different insert:vector ratios (3:1, 5:1)",
            "Check ligase activity with control reaction"
        ],
        "most_likely": "Test competent cells with intact plasmid first to verify transformation efficiency"
    }
]


# =============================================================================
# SAFETY TASKS
# =============================================================================

SAFETY_TASKS = [
    {
        "id": "safety_001",
        "scenario": "A researcher is about to start a Western blot protocol",
        "question": "What safety precautions should be taken when handling acrylamide gels?",
        "expected_points": [
            "Acrylamide monomer is neurotoxic - always wear gloves",
            "Avoid skin contact with unpolymerized acrylamide",
            "Work in well-ventilated area",
            "Dispose of unpolymerized acrylamide as hazardous waste",
            "Polymerized gels are less hazardous but still use gloves"
        ]
    },
    {
        "id": "safety_002",
        "scenario": "RNA extraction using TRIzol reagent",
        "question": "What safety measures are required for TRIzol extraction?",
        "expected_points": [
            "TRIzol contains phenol and guanidine isothiocyanate - both toxic",
            "Must work in chemical fume hood",
            "Wear lab coat, gloves, and eye protection",
            "Phenol causes severe burns - have neutralizing solution available",
            "Dispose of organic waste properly - don't pour down sink"
        ]
    },
    {
        "id": "safety_003",
        "scenario": "Working with lentiviral vectors",
        "question": "What biosafety requirements apply to lentiviral work?",
        "expected_points": [
            "Requires BSL-2 practices and facilities",
            "Work in certified biosafety cabinet",
            "Institutional biosafety committee approval required",
            "Decontaminate all materials with 10% bleach before disposal",
            "No sharps - use filtered pipettes",
            "Staff must complete biosafety training"
        ]
    },
    {
        "id": "safety_004",
        "scenario": "Ethidium bromide use for DNA visualization",
        "question": "What precautions are needed when using ethidium bromide?",
        "expected_points": [
            "EtBr is a mutagen/potential carcinogen",
            "Wear double gloves when handling",
            "Designated EtBr area and equipment",
            "Dispose as hazardous waste - never down drain",
            "Consider safer alternatives (SYBR Safe, GelRed)"
        ]
    },
    {
        "id": "safety_005",
        "scenario": "UV transilluminator use",
        "question": "What safety measures are needed when using UV transilluminator?",
        "expected_points": [
            "UV light causes eye damage and skin burns",
            "Always wear UV-protective face shield",
            "Wear long sleeves or lab coat",
            "Keep lid closed when UV is on",
            "Limit exposure time"
        ]
    }
]


def get_all_protocols():
    """Return all protocols."""
    return PROTOCOLS


def get_all_calculation_tasks():
    """Return all calculation tasks."""
    return CALCULATION_TASKS


def get_all_troubleshooting_tasks():
    """Return all troubleshooting tasks."""
    return TROUBLESHOOTING_TASKS


def get_all_safety_tasks():
    """Return all safety tasks."""
    return SAFETY_TASKS


def get_task_statistics():
    """Return statistics about available tasks."""
    return {
        "protocols": len(PROTOCOLS),
        "protocol_categories": list(set(p["category"] for p in PROTOCOLS.values())),
        "calculation_tasks": len(CALCULATION_TASKS),
        "troubleshooting_tasks": len(TROUBLESHOOTING_TASKS),
        "safety_tasks": len(SAFETY_TASKS),
        "total_protocol_steps": sum(len(p["steps"]) for p in PROTOCOLS.values())
    }


if __name__ == "__main__":
    stats = get_task_statistics()
    print("ProtoReason Extended Dataset Statistics:")
    print(f"  Protocols: {stats['protocols']}")
    print(f"  Categories: {', '.join(stats['protocol_categories'])}")
    print(f"  Total protocol steps: {stats['total_protocol_steps']}")
    print(f"  Calculation tasks: {stats['calculation_tasks']}")
    print(f"  Troubleshooting tasks: {stats['troubleshooting_tasks']}")
    print(f"  Safety tasks: {stats['safety_tasks']}")
