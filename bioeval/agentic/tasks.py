"""
Agentic task definitions.

Each task is a multi-step scientific workflow. The model reasons through
each step, and milestone criteria are checked via phrase_match.

4 categories × 6 tasks = 24 tasks (target).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AgenticStep:
    """A single step in an agentic task."""

    step_number: int
    name: str
    prompt: str
    milestone_name: str
    milestone_criteria: list[str] = field(default_factory=list)


@dataclass
class AgenticTask:
    """A multi-step agentic task."""

    id: str
    category: str
    title: str
    scenario: str
    steps: list[AgenticStep] = field(default_factory=list)
    ground_truth: dict = field(default_factory=dict)


# ============================================================
# experimental_design (6 tasks)
# ============================================================

EXPERIMENTAL_DESIGN_TASKS = [
    AgenticTask(
        id="ag_ed_001",
        category="experimental_design",
        title="CRISPR screen for drug resistance genes",
        scenario=(
            "You are designing a genome-wide CRISPR knockout screen to identify "
            "genes that confer resistance to the EGFR inhibitor osimertinib in "
            "NSCLC. The lab has access to a GeCKO v2 library (targeting ~19,000 "
            "genes, 6 sgRNAs per gene), a NovaSeq sequencer, and PC9 cells "
            "(EGFR-mutant NSCLC line, sensitive to osimertinib IC50 = 10 nM). "
            "Budget: $50,000. Timeline: 6 months."
        ),
        steps=[
            AgenticStep(
                step_number=1,
                name="Library Design & MOI Planning",
                prompt=(
                    "Plan the lentiviral library transduction. Determine the "
                    "appropriate MOI, cell number requirements, and coverage. "
                    "Consider library complexity (number of sgRNAs) and "
                    "recommended coverage per sgRNA."
                ),
                milestone_name="library_coverage",
                milestone_criteria=[
                    "MOI",
                    "coverage",
                    "cell number",
                    "lentiviral",
                    "puromycin",
                ],
            ),
            AgenticStep(
                step_number=2,
                name="Selection Strategy",
                prompt=(
                    "Design the drug selection protocol. How will you treat "
                    "with osimertinib to select for resistance? Include "
                    "concentration, duration, media changes, and controls."
                ),
                milestone_name="drug_selection",
                milestone_criteria=[
                    "osimertinib concentration",
                    "selection duration",
                    "vehicle control",
                    "media change",
                    "replicates",
                ],
            ),
            AgenticStep(
                step_number=3,
                name="Genomic DNA Harvesting & Library Prep",
                prompt=(
                    "Plan the gDNA extraction and NGS library preparation "
                    "from surviving cells. How will you amplify the sgRNA "
                    "cassettes and prepare for sequencing?"
                ),
                milestone_name="library_prep",
                milestone_criteria=[
                    "genomic DNA",
                    "PCR amplification",
                    "sgRNA cassette",
                    "sequencing adapter",
                ],
            ),
            AgenticStep(
                step_number=4,
                name="Sequencing & Analysis Plan",
                prompt=(
                    "Specify the sequencing parameters and computational "
                    "analysis pipeline. What tools will you use to identify "
                    "enriched sgRNAs and hit genes?"
                ),
                milestone_name="analysis_pipeline",
                milestone_criteria=[
                    "read depth",
                    "MAGeCK",
                    "fold change",
                    "FDR",
                    "enrichment",
                ],
            ),
            AgenticStep(
                step_number=5,
                name="Validation Strategy",
                prompt=(
                    "Design the validation experiments for the top hit genes. "
                    "How will you confirm that individual gene knockouts confer "
                    "resistance? Include secondary assays."
                ),
                milestone_name="validation",
                milestone_criteria=[
                    "individual sgRNA",
                    "dose response",
                    "proliferation",
                    "Western blot",
                    "rescue experiment",
                ],
            ),
        ],
        ground_truth={
            "total_milestones": 5,
            "key_concepts": [
                "MOI 0.3 for single integration",
                "500x-1000x coverage per sgRNA",
                "IC90 or 10x IC50 for selection",
                "MAGeCK or similar enrichment analysis",
                "individual gene validation with independent sgRNAs",
            ],
        },
    ),
    AgenticTask(
        id="ag_ed_002",
        category="experimental_design",
        title="Clinical biomarker validation study",
        scenario=(
            "You are designing a biomarker validation study for a novel "
            "circulating tumor DNA (ctDNA) assay to detect minimal residual "
            "disease (MRD) in stage II-III colorectal cancer after curative "
            "surgery. The assay is a tumor-informed 16-gene panel using "
            "digital PCR. You have access to a prospective cohort of 200 "
            "CRC patients with banked plasma (pre-surgery, post-surgery "
            "day 30, and q3 months for 2 years). Clinical outcomes "
            "(recurrence, DFS, OS) are available."
        ),
        steps=[
            AgenticStep(
                step_number=1,
                name="Study Population & Endpoints",
                prompt=(
                    "Define the study population, inclusion/exclusion criteria, "
                    "primary and secondary endpoints, and sample size justification."
                ),
                milestone_name="study_design",
                milestone_criteria=[
                    "inclusion criteria",
                    "primary endpoint",
                    "disease-free survival",
                    "sensitivity",
                    "specificity",
                ],
            ),
            AgenticStep(
                step_number=2,
                name="Specimen Handling & Pre-analytics",
                prompt=(
                    "Specify the pre-analytical requirements for ctDNA testing. "
                    "Include specimen type, collection tubes, processing time, "
                    "storage, and quality control measures."
                ),
                milestone_name="preanalytics",
                milestone_criteria=[
                    "plasma",
                    "cell-free DNA",
                    "Streck tube",
                    "centrifugation",
                    "extraction",
                ],
            ),
            AgenticStep(
                step_number=3,
                name="Assay Validation Parameters",
                prompt=(
                    "Define the analytical validation parameters. What are the "
                    "limit of detection, analytical sensitivity, specificity, "
                    "reproducibility, and interference testing requirements?"
                ),
                milestone_name="analytical_validation",
                milestone_criteria=[
                    "limit of detection",
                    "analytical sensitivity",
                    "reproducibility",
                    "variant allele frequency",
                ],
            ),
            AgenticStep(
                step_number=4,
                name="Clinical Validation Analysis Plan",
                prompt=(
                    "Design the statistical analysis plan for clinical validation. "
                    "How will you assess the association between ctDNA status and "
                    "recurrence? Include time-to-event analysis methods."
                ),
                milestone_name="statistical_plan",
                milestone_criteria=[
                    "Kaplan-Meier",
                    "Cox proportional hazards",
                    "hazard ratio",
                    "landmark analysis",
                    "ctDNA clearance",
                ],
            ),
            AgenticStep(
                step_number=5,
                name="Clinical Utility Assessment",
                prompt=(
                    "How will you assess the clinical utility of the ctDNA assay? "
                    "Can it change treatment decisions? Design a framework for "
                    "evaluating whether MRD-guided therapy improves outcomes."
                ),
                milestone_name="clinical_utility",
                milestone_criteria=[
                    "clinical utility",
                    "treatment escalation",
                    "adjuvant chemotherapy",
                    "surveillance",
                    "randomized",
                ],
            ),
        ],
        ground_truth={
            "total_milestones": 5,
            "key_concepts": [
                "tumor-informed vs tumor-agnostic approach",
                "landmark analysis at post-op timepoint",
                "ctDNA clearance kinetics",
                "MRD-guided treatment escalation/de-escalation",
                "prospective-retrospective validation design",
            ],
        },
    ),
    AgenticTask(
        id="ag_ed_003",
        category="experimental_design",
        title="Gut microbiome longitudinal intervention study",
        scenario=(
            "You are designing a longitudinal study to assess the impact of "
            "a high-fiber dietary intervention on gut microbiome composition "
            "and metabolic health markers in 60 adults with pre-diabetes "
            "(HbA1c 5.7-6.4%). The intervention is a controlled feeding study: "
            "30 subjects receive a high-fiber diet (40g/day) and 30 receive a "
            "standard Western diet (15g/day) for 12 weeks. Budget: $200,000."
        ),
        steps=[
            AgenticStep(
                step_number=1,
                name="Study Design & Randomization",
                prompt=(
                    "Design the study including randomization strategy, blinding "
                    "feasibility, control group design, and timeline for sample "
                    "collection. Address compliance monitoring."
                ),
                milestone_name="study_design",
                milestone_criteria=[
                    "randomized",
                    "controlled",
                    "compliance",
                    "run-in",
                    "sample collection",
                ],
            ),
            AgenticStep(
                step_number=2,
                name="Microbiome Sampling & Sequencing Strategy",
                prompt=(
                    "Specify the microbiome sampling protocol. What sequencing "
                    "approach (16S vs shotgun), depth, and longitudinal sampling "
                    "frequency will you use? Justify your choices."
                ),
                milestone_name="sequencing_strategy",
                milestone_criteria=[
                    "stool collection",
                    "shotgun metagenomics",
                    "sequencing depth",
                    "timepoints",
                    "negative control",
                ],
            ),
            AgenticStep(
                step_number=3,
                name="Metabolic & Clinical Outcomes",
                prompt=(
                    "Define the metabolic outcome measures. What clinical "
                    "parameters, blood biomarkers, and metabolomic profiles "
                    "will you measure? How will you correlate with microbiome data?"
                ),
                milestone_name="metabolic_outcomes",
                milestone_criteria=[
                    "HbA1c",
                    "fasting glucose",
                    "insulin",
                    "short-chain fatty acids",
                    "metabolomics",
                ],
            ),
            AgenticStep(
                step_number=4,
                name="Bioinformatics & Statistical Analysis",
                prompt=(
                    "Plan the bioinformatics and statistical analysis pipeline. "
                    "How will you handle compositional data, longitudinal modeling, "
                    "and multiple testing correction?"
                ),
                milestone_name="analysis_plan",
                milestone_criteria=[
                    "compositional",
                    "mixed-effects model",
                    "alpha diversity",
                    "beta diversity",
                    "multiple testing",
                ],
            ),
            AgenticStep(
                step_number=5,
                name="Confounding Variables & Limitations",
                prompt=(
                    "Identify potential confounders and biases. How will you "
                    "control for medication use, baseline microbiome variation, "
                    "exercise, and antibiotic exposure?"
                ),
                milestone_name="confounders",
                milestone_criteria=[
                    "antibiotic",
                    "medication",
                    "baseline",
                    "diet diary",
                    "confounder",
                ],
            ),
        ],
        ground_truth={
            "total_milestones": 5,
            "key_concepts": [
                "shotgun metagenomics preferred for functional analysis",
                "SCFA as mechanistic link between fiber and metabolic health",
                "compositional data analysis (not raw abundance)",
                "longitudinal mixed-effects models",
                "antibiotic exclusion or stratification",
            ],
        },
    ),
    AgenticTask(
        id="ag_ed_004",
        category="experimental_design",
        title="AAV gene therapy safety assessment",
        scenario=(
            "You are designing a pre-clinical safety assessment for an AAV9-based "
            "gene therapy delivering SMN1 for spinal muscular atrophy (SMA) type 1. "
            "The therapy will be delivered via intrathecal injection in neonatal "
            "mice (SMA model: SMN-delta7). You need to establish a comprehensive "
            "safety package for IND-enabling studies. The regulatory target is FDA "
            "CBER guidance for gene therapy products."
        ),
        steps=[
            AgenticStep(
                step_number=1,
                name="Dose Selection & Route of Administration",
                prompt=(
                    "Determine the dose range, route of administration, and "
                    "dose escalation strategy. Address species-specific "
                    "considerations for AAV9 biodistribution."
                ),
                milestone_name="dose_strategy",
                milestone_criteria=[
                    "intrathecal",
                    "dose escalation",
                    "vector genome",
                    "biodistribution",
                    "dose-limiting toxicity",
                ],
            ),
            AgenticStep(
                step_number=2,
                name="Toxicology Study Design",
                prompt=(
                    "Design the GLP toxicology study. Include group sizes, "
                    "endpoints, duration, pathology assessments, and "
                    "species selection rationale."
                ),
                milestone_name="tox_study",
                milestone_criteria=[
                    "GLP",
                    "histopathology",
                    "clinical pathology",
                    "non-human primate",
                    "necropsy",
                ],
            ),
            AgenticStep(
                step_number=3,
                name="Immunogenicity Assessment",
                prompt=(
                    "Plan the immunogenicity testing. How will you assess "
                    "pre-existing anti-AAV9 antibodies, T-cell responses to "
                    "capsid and transgene, and complement activation?"
                ),
                milestone_name="immunogenicity",
                milestone_criteria=[
                    "neutralizing antibody",
                    "anti-AAV",
                    "T cell",
                    "ELISpot",
                    "complement",
                ],
            ),
            AgenticStep(
                step_number=4,
                name="Genotoxicity & Integration Analysis",
                prompt=(
                    "Address the risk of insertional mutagenesis. What assays "
                    "will you use to assess AAV integration? How will you "
                    "monitor for oncogenic risk?"
                ),
                milestone_name="genotoxicity",
                milestone_criteria=[
                    "integration site",
                    "insertional mutagenesis",
                    "LAM-PCR",
                    "tumorigenicity",
                ],
            ),
            AgenticStep(
                step_number=5,
                name="Long-term Safety Monitoring Plan",
                prompt=(
                    "Design the long-term follow-up plan for the clinical trial. "
                    "What is the recommended duration? What safety signals will "
                    "you monitor? Address shedding and germline transmission."
                ),
                milestone_name="long_term_safety",
                milestone_criteria=[
                    "long-term follow-up",
                    "shedding",
                    "germline",
                    "hepatotoxicity",
                    "dorsal root ganglia",
                ],
            ),
        ],
        ground_truth={
            "total_milestones": 5,
            "key_concepts": [
                "AAV9 tropism for CNS and liver",
                "DRG toxicity is known AAV9 concern",
                "minimum 5-year long-term follow-up per FDA guidance (up to 15 years for integrating vectors)",
                "pre-existing anti-AAV9 antibodies can block transduction",
                "GLP tox study in NHP required for IND",
            ],
        },
    ),
    AgenticTask(
        id="ag_ed_005",
        category="experimental_design",
        title="Spatial transcriptomics tissue mapping study",
        scenario=(
            "You are designing a spatial transcriptomics study to map the tumor "
            "microenvironment (TME) of triple-negative breast cancer (TNBC). "
            "You have access to 20 TNBC FFPE specimens (10 responders, 10 "
            "non-responders to neoadjuvant immune checkpoint inhibitor therapy). "
            "Available platforms: 10x Visium, 10x Xenium, and MERFISH. "
            "Budget: $150,000."
        ),
        steps=[
            AgenticStep(
                step_number=1,
                name="Platform Selection & Rationale",
                prompt=(
                    "Compare the available spatial platforms (Visium, Xenium, "
                    "MERFISH) for this study. Recommend one and justify based "
                    "on resolution, throughput, gene panel, and cost."
                ),
                milestone_name="platform_selection",
                milestone_criteria=[
                    "Visium",
                    "Xenium",
                    "resolution",
                    "gene panel",
                    "cost per sample",
                ],
            ),
            AgenticStep(
                step_number=2,
                name="Panel Design & Gene Selection",
                prompt=(
                    "Design the gene panel for the chosen platform. What TME "
                    "cell types and immune markers should be included? How many "
                    "genes are needed for adequate cell type deconvolution?"
                ),
                milestone_name="panel_design",
                milestone_criteria=[
                    "T cell",
                    "macrophage",
                    "PD-L1",
                    "cell type deconvolution",
                    "marker genes",
                ],
            ),
            AgenticStep(
                step_number=3,
                name="Tissue Processing & Quality Control",
                prompt=(
                    "Specify tissue processing requirements. Address FFPE "
                    "section thickness, RNA quality assessment, and quality "
                    "control steps specific to spatial transcriptomics."
                ),
                milestone_name="tissue_qc",
                milestone_criteria=[
                    "FFPE",
                    "section thickness",
                    "RNA quality",
                    "DV200",
                    "tissue optimization",
                ],
            ),
            AgenticStep(
                step_number=4,
                name="Computational Analysis Pipeline",
                prompt=(
                    "Design the computational analysis pipeline. Include "
                    "cell segmentation, spatial clustering, neighborhood "
                    "analysis, and comparison between responders and "
                    "non-responders."
                ),
                milestone_name="computational_analysis",
                milestone_criteria=[
                    "cell segmentation",
                    "spatial clustering",
                    "neighborhood",
                    "differential expression",
                    "responder",
                ],
            ),
            AgenticStep(
                step_number=5,
                name="Validation & Clinical Correlation",
                prompt=(
                    "Plan validation experiments and clinical correlation. "
                    "How will you validate spatial findings with orthogonal "
                    "methods? How will you correlate spatial features with "
                    "treatment response?"
                ),
                milestone_name="validation",
                milestone_criteria=[
                    "multiplex immunofluorescence",
                    "validation",
                    "spatial biomarker",
                    "treatment response",
                ],
            ),
        ],
        ground_truth={
            "total_milestones": 5,
            "key_concepts": [
                "Xenium or MERFISH for single-cell resolution",
                "immune cell infiltration patterns as predictive features",
                "DV200 > 50% for FFPE spatial transcriptomics",
                "spatial neighborhood analysis for immune-tumor interaction",
                "validation with multiplex IHC/IF",
            ],
        },
    ),
    AgenticTask(
        id="ag_ed_006",
        category="experimental_design",
        title="Pharmacogenomics-guided clinical trial",
        scenario=(
            "You are designing a pharmacogenomics-guided randomized clinical trial "
            "for warfarin dosing in patients starting anticoagulation therapy for "
            "atrial fibrillation. The goal is to compare genotype-guided dosing "
            "(using CYP2C9 and VKORC1 variants) versus standard clinical dosing "
            "algorithms. The primary outcome is time in therapeutic range (TTR) "
            "over 12 weeks. Target enrollment: 400 patients across 5 sites."
        ),
        steps=[
            AgenticStep(
                step_number=1,
                name="Genotyping Strategy",
                prompt=(
                    "Define the pharmacogenomic variants to test and the "
                    "genotyping platform. Include turnaround time requirements "
                    "for clinical decision-making."
                ),
                milestone_name="genotyping",
                milestone_criteria=[
                    "CYP2C9",
                    "VKORC1",
                    "CYP4F2",
                    "genotyping",
                    "turnaround time",
                ],
            ),
            AgenticStep(
                step_number=2,
                name="Dosing Algorithm Design",
                prompt=(
                    "Design the genotype-guided dosing algorithm. How will you "
                    "incorporate genotype, age, weight, concomitant medications, "
                    "and INR targets into dose calculation?"
                ),
                milestone_name="dosing_algorithm",
                milestone_criteria=[
                    "dosing algorithm",
                    "genotype",
                    "INR",
                    "age",
                    "weight",
                ],
            ),
            AgenticStep(
                step_number=3,
                name="Trial Design & Randomization",
                prompt=(
                    "Specify the trial design, randomization method, blinding "
                    "strategy, and sample size calculation. Address stratification "
                    "by genotype frequency across ethnic groups."
                ),
                milestone_name="trial_design",
                milestone_criteria=[
                    "randomized",
                    "sample size",
                    "power",
                    "stratification",
                    "ethnic",
                ],
            ),
            AgenticStep(
                step_number=4,
                name="Safety Monitoring & Endpoints",
                prompt=(
                    "Define the safety monitoring plan. Include DSMB charter, "
                    "stopping rules, adverse event definitions (major bleeding, "
                    "thromboembolic events), and INR monitoring frequency."
                ),
                milestone_name="safety_monitoring",
                milestone_criteria=[
                    "DSMB",
                    "bleeding",
                    "thromboembolic",
                    "INR monitoring",
                    "stopping rule",
                ],
            ),
            AgenticStep(
                step_number=5,
                name="Health Economics & Implementation",
                prompt=(
                    "Design the health economic analysis. How will you assess "
                    "cost-effectiveness of genotype-guided dosing versus "
                    "standard care? Address implementation barriers."
                ),
                milestone_name="health_economics",
                milestone_criteria=[
                    "cost-effectiveness",
                    "QALY",
                    "implementation",
                    "point-of-care",
                ],
            ),
        ],
        ground_truth={
            "total_milestones": 5,
            "key_concepts": [
                "CYP2C9 *2 and *3 variants reduce enzyme activity",
                "VKORC1 -1639G>A affects warfarin sensitivity",
                "genotype-guided dosing may improve TTR (EU-PACT showed ~7% benefit; COAG showed no significant difference)",
                "ethnic variation in allele frequencies affects generalizability",
                "rapid turnaround genotyping essential for clinical utility",
            ],
        },
    ),
]


# ============================================================
# bioinformatics_pipeline (6 tasks)
# ============================================================

BIOINFORMATICS_PIPELINE_TASKS = [
    AgenticTask(
        id="ag_bp_001",
        category="bioinformatics_pipeline",
        title="RNA-seq differential expression analysis",
        scenario=(
            "You have paired tumor/normal RNA-seq data from 20 breast cancer "
            "patients (40 samples total). Samples were sequenced on an Illumina "
            "NovaSeq 6000, 150 bp paired-end, ~50 million reads per sample. "
            "Raw FASTQ files have been delivered. The goal is to identify "
            "differentially expressed genes between tumor and matched normal "
            "tissue, and to characterize the dysregulated pathways. The reference "
            "genome is GRCh38 with GENCODE v44 annotation."
        ),
        steps=[
            AgenticStep(
                step_number=1,
                name="Quality Control & Read Trimming",
                prompt=(
                    "Describe the QC and preprocessing steps for the raw FASTQ "
                    "files. What tools will you use for quality assessment and "
                    "adapter trimming? What quality metrics indicate a problem, "
                    "and what are acceptable thresholds?"
                ),
                milestone_name="qc_trimming",
                milestone_criteria=[
                    "FastQC",
                    "adapter trimming",
                    "Phred quality score",
                    "fastp",
                    "MultiQC",
                ],
            ),
            AgenticStep(
                step_number=2,
                name="Read Alignment to Reference Genome",
                prompt=(
                    "Specify the alignment strategy. Which aligner is appropriate "
                    "for RNA-seq and why? What reference files are needed? Describe "
                    "the index building and alignment parameters, and how you will "
                    "assess alignment quality."
                ),
                milestone_name="alignment",
                milestone_criteria=[
                    "STAR",
                    "splice-aware",
                    "genome index",
                    "two-pass",
                    "mapping rate",
                ],
            ),
            AgenticStep(
                step_number=3,
                name="Gene-Level Quantification",
                prompt=(
                    "Describe how you will quantify gene expression from the "
                    "aligned BAM files. What tool and counting mode will you use? "
                    "How do you handle multi-mapped reads and strandedness? What "
                    "output format is needed for downstream DE analysis?"
                ),
                milestone_name="quantification",
                milestone_criteria=[
                    "featureCounts",
                    "count matrix",
                    "strandedness",
                    "gene annotation",
                    "multi-mapped reads",
                ],
            ),
            AgenticStep(
                step_number=4,
                name="Differential Expression Analysis",
                prompt=(
                    "Walk through the differential expression analysis. What "
                    "statistical framework will you use? How do you handle the "
                    "paired design (tumor vs matched normal)? Describe "
                    "normalization, dispersion estimation, filtering criteria, "
                    "and multiple testing correction."
                ),
                milestone_name="differential_expression",
                milestone_criteria=[
                    "DESeq2",
                    "paired design",
                    "FDR",
                    "log2 fold change",
                    "normalized counts",
                ],
            ),
            AgenticStep(
                step_number=5,
                name="Pathway & Gene Set Enrichment Analysis",
                prompt=(
                    "Describe the pathway enrichment analysis for the DE results. "
                    "Compare over-representation analysis (ORA) versus gene set "
                    "enrichment analysis (GSEA). What databases and tools will "
                    "you use? How do you interpret the results?"
                ),
                milestone_name="pathway_enrichment",
                milestone_criteria=[
                    "GSEA",
                    "gene set enrichment",
                    "KEGG",
                    "Gene Ontology",
                    "ranked gene list",
                ],
            ),
            AgenticStep(
                step_number=6,
                name="Visualization & Reporting",
                prompt=(
                    "Describe the key visualizations for presenting DE results. "
                    "What plots are standard for RNA-seq analysis? How will you "
                    "summarize the findings and assess overall data quality in "
                    "the final report?"
                ),
                milestone_name="visualization",
                milestone_criteria=[
                    "volcano plot",
                    "MA plot",
                    "PCA",
                    "heatmap",
                    "sample clustering",
                ],
            ),
        ],
        ground_truth={
            "total_milestones": 6,
            "key_concepts": [
                "STAR aligner for splice-aware RNA-seq alignment",
                "DESeq2 with paired design formula ~patient + condition",
                "Benjamini-Hochberg FDR correction at 0.05",
                "GSEA uses full ranked list unlike ORA which uses cutoff",
                "PCA and hierarchical clustering for batch effect detection",
            ],
        },
    ),
    AgenticTask(
        id="ag_bp_002",
        category="bioinformatics_pipeline",
        title="Whole exome sequencing variant calling",
        scenario=(
            "You have whole exome sequencing data from a pediatric B-cell acute "
            "lymphoblastic leukemia (B-ALL) patient. Both tumor (bone marrow at "
            "diagnosis) and matched normal (remission blood) samples were "
            "sequenced using the Agilent SureSelect Human All Exon V7 capture "
            "kit on an Illumina NovaSeq 6000, 150 bp paired-end, achieving "
            "~100x mean coverage. The goal is to identify somatic mutations "
            "and classify clinically actionable variants."
        ),
        steps=[
            AgenticStep(
                step_number=1,
                name="Read QC & Preprocessing",
                prompt=(
                    "Describe the quality control and preprocessing steps for the "
                    "WES FASTQ files. What adapter sequences need trimming for the "
                    "SureSelect kit? How do you assess sequencing quality, and what "
                    "metrics are critical for exome data specifically?"
                ),
                milestone_name="read_qc",
                milestone_criteria=[
                    "FastQC",
                    "adapter trimming",
                    "on-target rate",
                    "coverage uniformity",
                    "duplicate rate",
                ],
            ),
            AgenticStep(
                step_number=2,
                name="Alignment & Duplicate Marking",
                prompt=(
                    "Describe the alignment workflow. What aligner is standard for "
                    "WES? How do you mark and handle PCR duplicates? Explain the "
                    "GATK Best Practices preprocessing steps including base quality "
                    "score recalibration."
                ),
                milestone_name="alignment_dedup",
                milestone_criteria=[
                    "BWA-MEM",
                    "Picard MarkDuplicates",
                    "base quality score recalibration",
                    "GATK",
                    "known sites",
                ],
            ),
            AgenticStep(
                step_number=3,
                name="Somatic Variant Calling",
                prompt=(
                    "Describe the somatic variant calling approach for the "
                    "tumor-normal pair. What caller is appropriate? How does it "
                    "distinguish somatic from germline variants? What filtering "
                    "steps are applied post-calling?"
                ),
                milestone_name="variant_calling",
                milestone_criteria=[
                    "Mutect2",
                    "tumor-normal pair",
                    "panel of normals",
                    "somatic variant",
                    "FilterMutectCalls",
                ],
            ),
            AgenticStep(
                step_number=4,
                name="Variant Annotation",
                prompt=(
                    "How will you annotate the somatic variants? What annotation "
                    "tools and databases will you use? What functional impact "
                    "predictions are most important for clinical interpretation?"
                ),
                milestone_name="annotation",
                milestone_criteria=[
                    "VEP",
                    "ClinVar",
                    "COSMIC",
                    "protein consequence",
                    "population frequency",
                ],
            ),
            AgenticStep(
                step_number=5,
                name="Clinical Variant Filtering & Classification",
                prompt=(
                    "Describe how you filter and prioritize variants for clinical "
                    "relevance. What criteria define pathogenic versus benign "
                    "somatic variants? How do you identify known oncogenic drivers "
                    "in B-ALL specifically?"
                ),
                milestone_name="clinical_filtering",
                milestone_criteria=[
                    "oncogenic driver",
                    "variant allele frequency",
                    "pathogenic",
                    "AMP/ASCO/CAP",
                    "actionable",
                ],
            ),
            AgenticStep(
                step_number=6,
                name="Reporting & Clinical Integration",
                prompt=(
                    "Describe the clinical report structure. What information must "
                    "be included? How do you report variant tier classifications? "
                    "What B-ALL-specific genes and fusions should be highlighted?"
                ),
                milestone_name="clinical_reporting",
                milestone_criteria=[
                    "tier classification",
                    "therapeutic implication",
                    "IKZF1",
                    "copy number",
                    "structural variant",
                ],
            ),
        ],
        ground_truth={
            "total_milestones": 6,
            "key_concepts": [
                "Mutect2 for somatic variant calling with matched normal",
                "BQSR uses known variant sites from dbSNP and Mills indels",
                "VEP or ANNOVAR for functional annotation with COSMIC and ClinVar",
                "AMP/ASCO/CAP tiered classification for somatic variants",
                "B-ALL driver genes include IKZF1, PAX5, CDKN2A, JAK2",
            ],
        },
    ),
    AgenticTask(
        id="ag_bp_003",
        category="bioinformatics_pipeline",
        title="16S rRNA microbiome analysis",
        scenario=(
            "You have 16S rRNA amplicon sequencing data (V3-V4 region) from a "
            "gut microbiome study. There are 100 stool samples from 3 treatment "
            "groups: 40 healthy controls, 30 patients with Crohn's disease in "
            "remission, and 30 patients with active Crohn's disease. Sequencing "
            "was performed on Illumina MiSeq 2x300 bp. The goal is to characterize "
            "microbial community differences between groups and identify taxa "
            "associated with disease activity."
        ),
        steps=[
            AgenticStep(
                step_number=1,
                name="Demultiplexing & Quality Filtering",
                prompt=(
                    "Describe the initial processing of the raw 16S sequencing "
                    "data. How do you demultiplex, assess quality, and filter "
                    "low-quality reads? What are appropriate quality thresholds "
                    "for V3-V4 amplicon data on MiSeq?"
                ),
                milestone_name="demux_qc",
                milestone_criteria=[
                    "demultiplex",
                    "quality filtering",
                    "primer removal",
                    "paired-end merging",
                    "QIIME 2",
                ],
            ),
            AgenticStep(
                step_number=2,
                name="Denoising & ASV Generation",
                prompt=(
                    "Describe the denoising approach to generate amplicon sequence "
                    "variants (ASVs). Compare DADA2 versus OTU-based methods. "
                    "What parameters need tuning for your data? How do you remove "
                    "chimeric sequences?"
                ),
                milestone_name="denoising",
                milestone_criteria=[
                    "DADA2",
                    "ASV",
                    "chimera removal",
                    "error model",
                    "sequence variant",
                ],
            ),
            AgenticStep(
                step_number=3,
                name="Taxonomic Classification",
                prompt=(
                    "How will you assign taxonomy to the ASVs? What reference "
                    "database and classifier will you use? How do you evaluate "
                    "classification confidence and handle unclassified sequences?"
                ),
                milestone_name="taxonomy",
                milestone_criteria=[
                    "SILVA",
                    "naive Bayes classifier",
                    "taxonomy",
                    "confidence threshold",
                    "genus level",
                ],
            ),
            AgenticStep(
                step_number=4,
                name="Diversity Analysis",
                prompt=(
                    "Describe the alpha and beta diversity analyses. What metrics "
                    "will you calculate? How do you assess rarefaction adequacy? "
                    "What statistical tests compare community structure between "
                    "the three groups?"
                ),
                milestone_name="diversity",
                milestone_criteria=[
                    "Shannon",
                    "UniFrac",
                    "Bray-Curtis",
                    "PERMANOVA",
                    "rarefaction",
                ],
            ),
            AgenticStep(
                step_number=5,
                name="Differential Abundance Testing",
                prompt=(
                    "How will you identify taxa differentially abundant between "
                    "groups? Compare methods such as LEfSe, ANCOM-BC, and ALDEx2. "
                    "How do you address compositionality and zero-inflation in "
                    "microbiome data?"
                ),
                milestone_name="differential_abundance",
                milestone_criteria=[
                    "ANCOM",
                    "compositionality",
                    "differential abundance",
                    "zero-inflation",
                    "effect size",
                ],
            ),
            AgenticStep(
                step_number=6,
                name="Visualization & Biological Interpretation",
                prompt=(
                    "Describe the key visualizations and how you will interpret "
                    "the results biologically. What taxa are known to be altered "
                    "in Crohn's disease? How do you present community structure "
                    "and differentially abundant taxa?"
                ),
                milestone_name="visualization_interpretation",
                milestone_criteria=[
                    "PCoA",
                    "bar plot",
                    "Faecalibacterium",
                    "dysbiosis",
                    "taxonomic bar plot",
                ],
            ),
        ],
        ground_truth={
            "total_milestones": 6,
            "key_concepts": [
                "DADA2 produces ASVs with single-nucleotide resolution",
                "SILVA or Greengenes2 for 16S taxonomy assignment",
                "UniFrac incorporates phylogenetic distance for beta diversity",
                "ANCOM-BC handles compositionality better than standard tests",
                "Faecalibacterium prausnitzii depletion is hallmark of Crohn's disease",
            ],
        },
    ),
    AgenticTask(
        id="ag_bp_004",
        category="bioinformatics_pipeline",
        title="Spatial transcriptomics analysis",
        scenario=(
            "You have 10x Visium spatial transcriptomics data from 5 FFPE "
            "pancreatic ductal adenocarcinoma (PDAC) sections. Each section "
            "was processed using the Visium CytAssist workflow with H&E "
            "staining. Space Ranger output (filtered feature-barcode matrices "
            "and tissue images) is available. The goal is to identify spatially "
            "distinct tissue compartments, deconvolve cell type composition per "
            "spot, and characterize ligand-receptor interactions between tumor "
            "and stromal compartments."
        ),
        steps=[
            AgenticStep(
                step_number=1,
                name="Image Alignment & Spot QC",
                prompt=(
                    "Describe the initial quality assessment of the Space Ranger "
                    "output. What metrics indicate good data quality? How do you "
                    "filter low-quality spots and what thresholds apply for UMI "
                    "counts, gene detection, and mitochondrial content?"
                ),
                milestone_name="spot_qc",
                milestone_criteria=[
                    "Space Ranger",
                    "UMI counts",
                    "mitochondrial percentage",
                    "genes per spot",
                    "tissue coverage",
                ],
            ),
            AgenticStep(
                step_number=2,
                name="Normalization & Feature Selection",
                prompt=(
                    "How will you normalize the spatial expression data? Compare "
                    "SCTransform versus standard log-normalization for Visium data. "
                    "How do you select highly variable genes while accounting for "
                    "spatial structure?"
                ),
                milestone_name="normalization",
                milestone_criteria=[
                    "SCTransform",
                    "normalization",
                    "highly variable genes",
                    "batch effect",
                    "integration",
                ],
            ),
            AgenticStep(
                step_number=3,
                name="Spatial Clustering & Domain Identification",
                prompt=(
                    "Describe how you perform spatially-aware clustering to "
                    "identify tissue domains. Compare standard Louvain/Leiden "
                    "clustering with spatial methods like BayesSpace or SpaGCN. "
                    "How do you map clusters to histological features?"
                ),
                milestone_name="spatial_clustering",
                milestone_criteria=[
                    "BayesSpace",
                    "spatial clustering",
                    "Louvain",
                    "tissue domain",
                    "histology",
                ],
            ),
            AgenticStep(
                step_number=4,
                name="Cell Type Deconvolution",
                prompt=(
                    "How will you estimate cell type proportions within each "
                    "Visium spot? What deconvolution method will you use and "
                    "what single-cell reference is needed? How do you validate "
                    "the deconvolution results?"
                ),
                milestone_name="deconvolution",
                milestone_criteria=[
                    "cell2location",
                    "deconvolution",
                    "single-cell reference",
                    "cell type proportion",
                    "RCTD",
                ],
            ),
            AgenticStep(
                step_number=5,
                name="Ligand-Receptor Interaction Analysis",
                prompt=(
                    "Describe how you will identify and characterize cell-cell "
                    "communication in the spatial context. What ligand-receptor "
                    "database and analysis framework will you use? How does "
                    "spatial proximity inform interaction confidence?"
                ),
                milestone_name="ligand_receptor",
                milestone_criteria=[
                    "CellChat",
                    "ligand-receptor",
                    "NicheNet",
                    "spatial proximity",
                    "cell-cell communication",
                ],
            ),
        ],
        ground_truth={
            "total_milestones": 5,
            "key_concepts": [
                "SCTransform for variance stabilization in Visium data",
                "BayesSpace or SpaGCN use spatial coordinates for clustering",
                "cell2location or RCTD require scRNA-seq reference for deconvolution",
                "CellChat or NicheNet for ligand-receptor inference",
                "PDAC stroma includes cancer-associated fibroblasts and immune infiltrate",
            ],
        },
    ),
    AgenticTask(
        id="ag_bp_005",
        category="bioinformatics_pipeline",
        title="ChIP-seq peak calling and analysis",
        scenario=(
            "You have H3K27ac ChIP-seq data from 4 conditions: MCF7 (ER+ breast "
            "cancer) treated with vehicle or estradiol (E2), and MDA-MB-231 "
            "(triple-negative breast cancer) treated with vehicle or E2. Each "
            "condition has 2 biological replicates plus matched input controls "
            "(16 libraries total). Sequencing was performed on NovaSeq 6000, "
            "75 bp single-end, ~40 million reads per library. The goal is to "
            "identify differential enhancer activity between cell types and "
            "treatment conditions, and to characterize super-enhancers."
        ),
        steps=[
            AgenticStep(
                step_number=1,
                name="Read QC & Alignment",
                prompt=(
                    "Describe the QC and alignment workflow for ChIP-seq reads. "
                    "What aligner is standard? How do you handle multi-mapped "
                    "reads, and what alignment quality metrics are important for "
                    "ChIP-seq specifically?"
                ),
                milestone_name="alignment_qc",
                milestone_criteria=[
                    "Bowtie2",
                    "multi-mapped reads",
                    "mapping quality",
                    "fragment size",
                    "PCR duplicates",
                ],
            ),
            AgenticStep(
                step_number=2,
                name="Peak Calling",
                prompt=(
                    "How will you call H3K27ac peaks? What peak caller and mode "
                    "are appropriate for this histone mark? How do you use the "
                    "input controls? Describe how to assess replicate concordance "
                    "using IDR."
                ),
                milestone_name="peak_calling",
                milestone_criteria=[
                    "MACS2",
                    "peak calling",
                    "input control",
                    "IDR",
                    "q-value",
                ],
            ),
            AgenticStep(
                step_number=3,
                name="Differential Binding Analysis",
                prompt=(
                    "Describe how to identify differentially bound regions between "
                    "conditions. What tool and statistical model will you use? How "
                    "do you create a consensus peak set and handle the multi-factor "
                    "design (cell type x treatment)?"
                ),
                milestone_name="differential_binding",
                milestone_criteria=[
                    "DiffBind",
                    "consensus peaks",
                    "DESeq2",
                    "contrast",
                    "fold change",
                ],
            ),
            AgenticStep(
                step_number=4,
                name="Motif Enrichment & Genomic Annotation",
                prompt=(
                    "How will you identify transcription factor motifs enriched "
                    "in differentially bound regions? What tools will you use for "
                    "motif discovery and genomic annotation of peaks? How do you "
                    "interpret motif results in the context of ER signaling?"
                ),
                milestone_name="motif_annotation",
                milestone_criteria=[
                    "HOMER",
                    "motif enrichment",
                    "GREAT",
                    "estrogen response element",
                    "transcription factor binding",
                ],
            ),
            AgenticStep(
                step_number=5,
                name="Super-Enhancer Identification",
                prompt=(
                    "Describe how to identify super-enhancers from H3K27ac "
                    "ChIP-seq data. What algorithm is used? How do super-enhancers "
                    "differ from typical enhancers? What genes are associated with "
                    "the identified super-enhancers, and what is their biological "
                    "significance in breast cancer?"
                ),
                milestone_name="super_enhancers",
                milestone_criteria=[
                    "ROSE",
                    "super-enhancer",
                    "hockey stick plot",
                    "BRD4",
                    "oncogene",
                ],
            ),
        ],
        ground_truth={
            "total_milestones": 5,
            "key_concepts": [
                "MACS2 peak calling for H3K27ac (narrow per ENCODE or broad for super-enhancer analysis)",
                "IDR for replicate concordance at 0.05 threshold",
                "DiffBind uses DESeq2 or edgeR for differential binding statistics",
                "HOMER findMotifsGenome for de novo and known motif discovery",
                "ROSE algorithm identifies super-enhancers by H3K27ac signal ranking",
            ],
        },
    ),
    AgenticTask(
        id="ag_bp_006",
        category="bioinformatics_pipeline",
        title="Proteomics DIA quantification workflow",
        scenario=(
            "You have data-independent acquisition (DIA) mass spectrometry data "
            "from a clinical biomarker discovery study. Fifty plasma samples from "
            "a cohort of 25 early-stage hepatocellular carcinoma (HCC) patients "
            "and 25 matched cirrhosis controls were analyzed on a Thermo Orbitrap "
            "Exploris 480 with a 60-min gradient. A project-specific spectral "
            "library was generated from 12 fractionated DDA runs of pooled "
            "samples. The goal is to identify differentially abundant proteins "
            "and nominate candidate biomarkers for early HCC detection."
        ),
        steps=[
            AgenticStep(
                step_number=1,
                name="Spectral Library Generation",
                prompt=(
                    "Describe how the project-specific spectral library is built "
                    "from the DDA fractionation data. What search engine and "
                    "parameters are used? How do you assess library quality, and "
                    "what is the expected library depth for plasma proteomics?"
                ),
                milestone_name="spectral_library",
                milestone_criteria=[
                    "spectral library",
                    "DDA fractionation",
                    "search engine",
                    "FDR",
                    "precursor",
                ],
            ),
            AgenticStep(
                step_number=2,
                name="DIA Data Extraction & Quantification",
                prompt=(
                    "Describe the DIA data processing workflow. What software "
                    "will you use to extract and quantify peptides from the DIA "
                    "runs? How does library-based search differ from library-free "
                    "approaches? What quantification strategy is applied?"
                ),
                milestone_name="dia_search",
                milestone_criteria=[
                    "DIA-NN",
                    "library-free",
                    "peptide quantification",
                    "retention time alignment",
                    "mass accuracy",
                ],
            ),
            AgenticStep(
                step_number=3,
                name="Data Normalization & Missing Value Handling",
                prompt=(
                    "How will you normalize the protein-level quantification "
                    "matrix? Address batch effects and systematic biases. How "
                    "do you handle missing values in DIA proteomics: what is the "
                    "expected missingness pattern, and what imputation strategy "
                    "is appropriate?"
                ),
                milestone_name="normalization_imputation",
                milestone_criteria=[
                    "MaxLFQ",
                    "median normalization",
                    "missing value imputation",
                    "MNAR",
                    "batch correction",
                ],
            ),
            AgenticStep(
                step_number=4,
                name="Differential Abundance Analysis",
                prompt=(
                    "Describe the statistical framework for identifying "
                    "differentially abundant proteins between HCC and cirrhosis. "
                    "What tool and model will you use? How do you handle the "
                    "matched design and multiple testing correction?"
                ),
                milestone_name="differential_analysis",
                milestone_criteria=[
                    "limma",
                    "moderated t-test",
                    "Benjamini-Hochberg",
                    "log2 fold change",
                    "adjusted p-value",
                ],
            ),
            AgenticStep(
                step_number=5,
                name="Pathway Enrichment & Functional Analysis",
                prompt=(
                    "How will you characterize the biological functions of "
                    "differentially abundant proteins? What enrichment analyses "
                    "will you perform? How do you interpret pathway results in "
                    "the context of HCC biology?"
                ),
                milestone_name="pathway_analysis",
                milestone_criteria=[
                    "Gene Ontology",
                    "Reactome",
                    "STRING",
                    "protein-protein interaction",
                    "enrichment analysis",
                ],
            ),
            AgenticStep(
                step_number=6,
                name="Biomarker Candidate Selection & Validation Strategy",
                prompt=(
                    "Describe how you will select candidate biomarkers from the "
                    "differentially abundant proteins. What criteria define a "
                    "good candidate? How will you assess classifier performance, "
                    "and what validation strategy is needed before clinical "
                    "translation?"
                ),
                milestone_name="biomarker_selection",
                milestone_criteria=[
                    "ROC curve",
                    "AUC",
                    "cross-validation",
                    "ELISA",
                    "independent cohort",
                ],
            ),
        ],
        ground_truth={
            "total_milestones": 6,
            "key_concepts": [
                "DIA-NN for library-free or library-based DIA quantification",
                "MaxLFQ for label-free protein quantification normalization",
                "limma with empirical Bayes moderation for small-sample proteomics",
                "MNAR imputation strategies differ from MCAR for proteomics",
                "biomarker validation requires independent cohort and orthogonal assay like ELISA",
            ],
        },
    ),
]


# ============================================================
# literature_research (6 tasks)
# ============================================================

LITERATURE_RESEARCH_TASKS = [
    AgenticTask(
        id="ag_lr_001",
        category="literature_research",
        title="Therapeutic target identification from GWAS",
        scenario=(
            "You are a computational biologist tasked with identifying druggable "
            "therapeutic targets from recent genome-wide association study (GWAS) "
            "findings for inflammatory bowel disease (IBD). A recent meta-analysis "
            "has identified 25 new genome-wide significant loci (p < 5e-8) for IBD, "
            "bringing the total to over 240 loci. Your goal is to systematically "
            "evaluate these loci, prioritize causal genes, assess their druggability, "
            "and propose an experimental validation plan for the top candidates."
        ),
        steps=[
            AgenticStep(
                step_number=1,
                name="GWAS Signal Interpretation",
                prompt=(
                    "Interpret the GWAS signals for IBD. For the lead SNPs at "
                    "genome-wide significant loci, describe how you would perform "
                    "fine-mapping to identify causal variants. Explain the role of "
                    "eQTL colocalization analysis (e.g., using COLOC or eCAVIAR) "
                    "to link variants to target genes, and discuss how linkage "
                    "disequilibrium and credible sets inform causal variant "
                    "identification."
                ),
                milestone_name="gwas_interpretation",
                milestone_criteria=[
                    "lead SNP",
                    "eQTL colocalization",
                    "fine-mapping",
                    "credible set",
                    "linkage disequilibrium",
                ],
            ),
            AgenticStep(
                step_number=2,
                name="Target Prioritization",
                prompt=(
                    "Prioritize candidate causal genes from the GWAS loci using "
                    "multiple lines of evidence. Discuss how Mendelian randomization "
                    "can establish causal directionality, how protein-protein "
                    "interaction networks and pathway enrichment (particularly the "
                    "JAK-STAT and TNF signaling pathways) help identify convergent "
                    "biology, and how integration with single-cell expression data "
                    "from intestinal tissue can prioritize cell-type-specific targets."
                ),
                milestone_name="target_prioritization",
                milestone_criteria=[
                    "Mendelian randomization",
                    "JAK-STAT pathway",
                    "TNF",
                    "protein-protein interaction",
                    "single-cell expression",
                ],
            ),
            AgenticStep(
                step_number=3,
                name="Druggability Assessment",
                prompt=(
                    "Assess the druggability of the prioritized targets. Evaluate "
                    "each target against the druggable genome databases (e.g., DGIdb, "
                    "Open Targets). Discuss structural considerations for small "
                    "molecule binding, existing drugs or clinical compounds targeting "
                    "the same pathway (e.g., tofacitinib for JAK, infliximab for TNF), "
                    "and the feasibility of novel modalities such as antisense "
                    "oligonucleotides or PROTACs for undruggable targets."
                ),
                milestone_name="druggability_assessment",
                milestone_criteria=[
                    "druggable genome",
                    "small molecule",
                    "tofacitinib",
                    "Open Targets",
                    "binding pocket",
                ],
            ),
            AgenticStep(
                step_number=4,
                name="Experimental Validation Plan",
                prompt=(
                    "Propose an experimental validation plan for the top 3 targets. "
                    "Include CRISPR perturbation in intestinal organoids, target "
                    "engagement assays, and in vivo validation in colitis models "
                    "(e.g., DSS or IL-10 knockout). Discuss how you would confirm "
                    "that modulating the target affects the inflammatory phenotype "
                    "and outline go/no-go criteria for advancing to lead optimization."
                ),
                milestone_name="validation_plan",
                milestone_criteria=[
                    "CRISPR",
                    "intestinal organoid",
                    "colitis model",
                    "target engagement",
                    "lead optimization",
                ],
            ),
        ],
        ground_truth={
            "total_milestones": 4,
            "key_concepts": [
                "eQTL colocalization links GWAS variants to causal genes",
                "Mendelian randomization provides causal evidence for target-disease relationship",
                "JAK-STAT pathway is a validated IBD target (tofacitinib approved)",
                "druggable genome assessment filters targets by tractability",
                "intestinal organoids provide disease-relevant functional validation",
            ],
        },
    ),
    AgenticTask(
        id="ag_lr_002",
        category="literature_research",
        title="Drug repurposing from side effect profiles",
        scenario=(
            "You are a pharmacologist investigating drug repurposing opportunities "
            "for Parkinson's disease using computational analysis of drug side effect "
            "similarities. The hypothesis is that drugs sharing side effect profiles "
            "may share molecular targets or pathways, and some existing drugs may have "
            "beneficial off-target effects on dopaminergic pathways. You have access to "
            "the SIDER side effect database, DrugBank, and ATC classification data for "
            "over 1,400 marketed drugs."
        ),
        steps=[
            AgenticStep(
                step_number=1,
                name="Side Effect Profile Analysis",
                prompt=(
                    "Describe how you would systematically analyze drug side effect "
                    "profiles to identify candidates for Parkinson's disease. Explain "
                    "how to extract structured side effect data from SIDER, compute "
                    "pairwise drug similarity using Jaccard or cosine metrics on "
                    "MedDRA-coded adverse events, and cluster drugs by ATC "
                    "classification to identify unexpected cross-class similarities "
                    "with known dopaminergic agents (e.g., levodopa, pramipexole)."
                ),
                milestone_name="side_effect_analysis",
                milestone_criteria=[
                    "SIDER database",
                    "ATC classification",
                    "Jaccard",
                    "MedDRA",
                    "dopaminergic",
                ],
            ),
            AgenticStep(
                step_number=2,
                name="Mechanism of Action Hypothesis",
                prompt=(
                    "For the top repurposing candidates identified from side effect "
                    "similarity, formulate mechanistic hypotheses. Discuss how these "
                    "drugs might interact with dopamine biosynthesis, dopamine "
                    "receptor signaling, alpha-synuclein aggregation, mitochondrial "
                    "function, or neuroinflammatory pathways relevant to Parkinson's. "
                    "Use target prediction tools and pathway databases to support "
                    "your hypotheses."
                ),
                milestone_name="mechanism_hypothesis",
                milestone_criteria=[
                    "dopamine receptor",
                    "alpha-synuclein",
                    "mitochondrial dysfunction",
                    "neuroinflammation",
                    "target prediction",
                ],
            ),
            AgenticStep(
                step_number=3,
                name="Evidence Assessment and Integration",
                prompt=(
                    "Critically evaluate the strength of evidence for each "
                    "repurposing candidate. Synthesize evidence from epidemiological "
                    "studies (e.g., reduced PD incidence in users of certain drug "
                    "classes), in vitro neuroprotection data, animal model studies "
                    "(e.g., MPTP or 6-OHDA models), and any existing clinical data. "
                    "Address blood-brain barrier penetration as a key feasibility "
                    "factor and assess pharmacokinetic suitability."
                ),
                milestone_name="evidence_assessment",
                milestone_criteria=[
                    "blood-brain barrier",
                    "MPTP model",
                    "neuroprotection",
                    "epidemiological",
                    "pharmacokinetic",
                ],
            ),
            AgenticStep(
                step_number=4,
                name="Clinical Feasibility and Trial Design",
                prompt=(
                    "For the most promising repurposing candidate, outline the "
                    "clinical development strategy. Design a phase II proof-of-concept "
                    "trial including patient selection criteria (Hoehn and Yahr stage), "
                    "primary endpoints (UPDRS score, DaTscan imaging), trial duration, "
                    "dose selection rationale, and safety monitoring plan. Discuss "
                    "regulatory advantages of repurposing an already-approved drug."
                ),
                milestone_name="clinical_feasibility",
                milestone_criteria=[
                    "phase II trial",
                    "UPDRS",
                    "DaTscan",
                    "Hoehn and Yahr",
                    "dose selection",
                ],
            ),
        ],
        ground_truth={
            "total_milestones": 4,
            "key_concepts": [
                "SIDER enables systematic side effect similarity analysis across drugs",
                "blood-brain barrier penetration is critical for CNS drug repurposing",
                "dopamine pathway modulation is the primary therapeutic mechanism in PD",
                "epidemiological evidence can support repurposing hypotheses",
                "phase II proof-of-concept with imaging biomarkers accelerates development",
            ],
        },
    ),
    AgenticTask(
        id="ag_lr_003",
        category="literature_research",
        title="Multi-omics biomarker discovery for early pancreatic cancer",
        scenario=(
            "You are leading a literature synthesis effort to design a multi-omics "
            "liquid biopsy panel for early detection of pancreatic ductal "
            "adenocarcinoma (PDAC). Current screening relies on CA 19-9, which has "
            "poor sensitivity (~79% overall, but only 40-65% for stage I-II) and "
            "specificity (~82%) for early-stage disease. "
            "You need to synthesize published evidence across cfDNA methylation, "
            "proteomics, metabolomics, and circulating microRNA studies to propose "
            "a superior multi-analyte biomarker panel."
        ),
        steps=[
            AgenticStep(
                step_number=1,
                name="Systematic Literature Search Strategy",
                prompt=(
                    "Design a systematic literature search strategy for identifying "
                    "candidate biomarkers for early PDAC detection. Specify databases "
                    "(PubMed, Embase, Cochrane), search terms, inclusion and exclusion "
                    "criteria, and the PRISMA framework for reporting. Discuss how you "
                    "would handle heterogeneity across studies using different platforms "
                    "and cohort sizes, and define quality assessment criteria using "
                    "QUADAS-2 for diagnostic accuracy studies."
                ),
                milestone_name="search_strategy",
                milestone_criteria=[
                    "PRISMA",
                    "QUADAS-2",
                    "inclusion criteria",
                    "PubMed",
                    "diagnostic accuracy",
                ],
            ),
            AgenticStep(
                step_number=2,
                name="Multi-omics Data Extraction and Synthesis",
                prompt=(
                    "Extract and synthesize biomarker evidence across four omics "
                    "layers. For cfDNA, discuss methylation markers (e.g., ADAMTS1, "
                    "BNC1) and fragmentation patterns. For proteomics, evaluate "
                    "markers beyond CA 19-9 such as thrombospondin-2 and tissue "
                    "factor pathway inhibitor. For metabolomics, consider branched-chain "
                    "amino acids and lipid alterations. For circulating microRNAs, "
                    "discuss miR-21 and miR-155. Report sensitivity, specificity, and "
                    "AUC for each individual marker where available."
                ),
                milestone_name="data_extraction",
                milestone_criteria=[
                    "cfDNA methylation",
                    "CA 19-9",
                    "sensitivity and specificity",
                    "metabolomics",
                    "circulating microRNA",
                ],
            ),
            AgenticStep(
                step_number=3,
                name="Multi-analyte Biomarker Panel Design",
                prompt=(
                    "Propose an optimal multi-analyte biomarker panel that combines "
                    "markers from different omics layers. Discuss the statistical "
                    "approach for combining markers (logistic regression, random "
                    "forest, or deep learning classifiers), the expected improvement "
                    "in AUC over CA 19-9 alone, and how a liquid biopsy panel would "
                    "be implemented in a clinical laboratory (assay format, sample "
                    "requirements, cost considerations). Address potential issues of "
                    "overfitting when combining many markers in small cohorts."
                ),
                milestone_name="panel_design",
                milestone_criteria=[
                    "liquid biopsy",
                    "AUC",
                    "overfitting",
                    "multi-analyte panel",
                    "logistic regression",
                ],
            ),
            AgenticStep(
                step_number=4,
                name="Prospective Validation Study Proposal",
                prompt=(
                    "Design a prospective validation study for the proposed panel. "
                    "Specify the target population (high-risk cohort: new-onset "
                    "diabetes, hereditary pancreatitis, BRCA2 carriers), required "
                    "sample size calculation based on expected sensitivity and "
                    "prevalence, specimen collection protocol for liquid biopsy, "
                    "pre-specified performance thresholds (sensitivity >85%, "
                    "specificity >90% for stage I-II PDAC), and an interim analysis "
                    "plan. Discuss FDA regulatory pathway for an in vitro diagnostic."
                ),
                milestone_name="validation_proposal",
                milestone_criteria=[
                    "prospective validation",
                    "high-risk cohort",
                    "sample size calculation",
                    "sensitivity threshold",
                    "regulatory pathway",
                ],
            ),
        ],
        ground_truth={
            "total_milestones": 4,
            "key_concepts": [
                "CA 19-9 alone is insufficient for early PDAC detection",
                "cfDNA methylation markers improve sensitivity for early-stage disease",
                "multi-analyte panels combining omics layers outperform single markers",
                "overfitting risk is high when combining many markers in small cohorts",
                "prospective validation in high-risk populations is essential for clinical translation",
            ],
        },
    ),
    AgenticTask(
        id="ag_lr_004",
        category="literature_research",
        title="Microgravity effects on human immune system",
        scenario=(
            "You are a space biology researcher preparing a comprehensive literature "
            "synthesis on microgravity effects on the human immune system for NASA's "
            "Human Research Program. The synthesis will inform countermeasure "
            "development for long-duration missions to Mars (estimated 2.5 years). "
            "Key data sources include the NASA Twins Study, ISS crew health "
            "monitoring data, ground-based analogs (bed rest, HDBR), and in vitro "
            "spaceflight experiments."
        ),
        steps=[
            AgenticStep(
                step_number=1,
                name="Systematic Evidence Search",
                prompt=(
                    "Design a systematic search to catalog published evidence on "
                    "spaceflight-associated immune dysregulation. Cover both human "
                    "data (ISS missions, Shuttle-era studies, NASA Twins Study) and "
                    "ground-based analogs (head-down bed rest, hindlimb unloading "
                    "in rodents, clinostat experiments). Identify the key immune "
                    "parameters studied: T-cell subset redistribution, cytokine "
                    "profiles, NK cell function, viral reactivation (EBV, VZV, CMV), "
                    "and mucosal immunity changes."
                ),
                milestone_name="evidence_search",
                milestone_criteria=[
                    "NASA Twins Study",
                    "T-cell dysfunction",
                    "viral reactivation",
                    "cytokine dysregulation",
                    "head-down bed rest",
                ],
            ),
            AgenticStep(
                step_number=2,
                name="Mechanistic Synthesis",
                prompt=(
                    "Synthesize the mechanistic evidence linking microgravity to "
                    "immune dysfunction. Discuss the interplay between fluid shift, "
                    "stress hormone elevation (cortisol, catecholamines), altered "
                    "leukocyte gene expression, impaired T-cell activation signaling, "
                    "thymic involution, and bone marrow changes. Integrate evidence "
                    "from the NASA Twins Study showing persistent immune gene "
                    "expression changes post-flight. Address how radiation exposure "
                    "compounds immune effects during deep-space missions."
                ),
                milestone_name="mechanistic_synthesis",
                milestone_criteria=[
                    "cortisol",
                    "T-cell activation",
                    "bone marrow",
                    "radiation exposure",
                    "gene expression",
                ],
            ),
            AgenticStep(
                step_number=3,
                name="Countermeasure Evaluation",
                prompt=(
                    "Evaluate proposed and existing countermeasures for spaceflight "
                    "immune dysregulation. Review evidence for exercise protocols, "
                    "pharmacological interventions (e.g., immune modulators, "
                    "antiviral prophylaxis for herpesvirus reactivation), nutritional "
                    "supplements (vitamin D, omega-3 fatty acids), and artificial "
                    "gravity. Critically assess the level of evidence (in vitro vs "
                    "in vivo vs human trial) and feasibility for long-duration Mars "
                    "missions. Discuss bone loss and its connection to immune "
                    "regulation via osteoimmunology."
                ),
                milestone_name="countermeasure_evaluation",
                milestone_criteria=[
                    "exercise countermeasure",
                    "antiviral prophylaxis",
                    "vitamin D",
                    "artificial gravity",
                    "bone loss",
                ],
            ),
            AgenticStep(
                step_number=4,
                name="Research Gap Identification",
                prompt=(
                    "Identify critical knowledge gaps that must be addressed before "
                    "a Mars mission. Discuss the lack of data on immune function "
                    "beyond 1-year missions, the unknown combined effects of "
                    "microgravity plus galactic cosmic radiation, limited "
                    "understanding of mucosal immunity in space, the need for "
                    "real-time immune monitoring technology, and insufficient data "
                    "on recovery kinetics after prolonged exposure. Propose specific "
                    "ISS experiments or Artemis mission add-ons to close these gaps."
                ),
                milestone_name="gap_identification",
                milestone_criteria=[
                    "galactic cosmic radiation",
                    "mucosal immunity",
                    "immune monitoring",
                    "recovery kinetics",
                    "Mars mission",
                ],
            ),
        ],
        ground_truth={
            "total_milestones": 4,
            "key_concepts": [
                "spaceflight causes T-cell dysfunction and cytokine dysregulation",
                "herpesvirus reactivation (EBV, VZV, CMV) is a validated in-flight immune marker",
                "NASA Twins Study showed persistent immune gene expression changes",
                "combined microgravity and radiation effects are poorly understood",
                "countermeasure evidence is mostly from ground analogs, not long-duration spaceflight",
            ],
        },
    ),
    AgenticTask(
        id="ag_lr_005",
        category="literature_research",
        title="Acquired resistance to anti-PD-1 immunotherapy",
        scenario=(
            "You are an immuno-oncology researcher tasked with reviewing the "
            "mechanisms of acquired resistance to anti-PD-1 checkpoint immunotherapy "
            "in solid tumors. While anti-PD-1 agents (nivolumab, pembrolizumab) "
            "have transformed cancer treatment, approximately 25-33% of initial "
            "responders develop acquired resistance within 2 years. Your goal is to "
            "classify resistance mechanisms, identify predictive biomarkers, and "
            "propose evidence-based combination strategies to overcome resistance."
        ),
        steps=[
            AgenticStep(
                step_number=1,
                name="Resistance Mechanism Classification",
                prompt=(
                    "Classify the known mechanisms of acquired resistance to anti-PD-1 "
                    "therapy from published literature. Organize into tumor-intrinsic "
                    "mechanisms (loss of beta-2-microglobulin, JAK1/JAK2 loss-of-function "
                    "mutations disrupting interferon-gamma signaling, neoantigen loss "
                    "through immunoediting, WNT/beta-catenin activation) and "
                    "tumor-extrinsic mechanisms (upregulation of alternative checkpoints "
                    "like LAG-3, TIM-3, TIGIT; expansion of regulatory T cells and "
                    "myeloid-derived suppressor cells in the tumor microenvironment). "
                    "Discuss the frequency and tumor-type specificity of each mechanism."
                ),
                milestone_name="resistance_classification",
                milestone_criteria=[
                    "beta-2-microglobulin",
                    "JAK1/JAK2 mutation",
                    "tumor microenvironment",
                    "alternative checkpoint",
                    "neoantigen loss",
                ],
            ),
            AgenticStep(
                step_number=2,
                name="Predictive Biomarker Identification",
                prompt=(
                    "Identify biomarkers that could predict or detect emerging "
                    "acquired resistance. Evaluate the evidence for tumor mutational "
                    "burden dynamics, PD-L1 expression changes, circulating tumor DNA "
                    "for tracking clonal evolution, T-cell receptor repertoire "
                    "analysis, and serial biopsy transcriptomic profiling. Discuss "
                    "the practical limitations of serial biopsies and the promise "
                    "of liquid biopsy approaches for longitudinal monitoring."
                ),
                milestone_name="biomarker_identification",
                milestone_criteria=[
                    "tumor mutational burden",
                    "PD-L1 expression",
                    "circulating tumor DNA",
                    "T-cell receptor repertoire",
                    "clonal evolution",
                ],
            ),
            AgenticStep(
                step_number=3,
                name="Combination Strategy Design",
                prompt=(
                    "Based on the resistance mechanisms identified, design rational "
                    "combination strategies. Evaluate published evidence for combining "
                    "anti-PD-1 with anti-LAG-3 (relatlimab), anti-CTLA-4 (ipilimumab), "
                    "STING agonists, oncolytic viruses, or targeted therapies (MEK "
                    "inhibitors, CDK4/6 inhibitors). Discuss the concept of sequential "
                    "versus concurrent combination therapy and how to match the "
                    "combination to the specific resistance mechanism."
                ),
                milestone_name="combination_strategy",
                milestone_criteria=[
                    "anti-LAG-3",
                    "ipilimumab",
                    "combination therapy",
                    "STING agonist",
                    "sequential therapy",
                ],
            ),
            AgenticStep(
                step_number=4,
                name="Adaptive Clinical Trial Proposal",
                prompt=(
                    "Propose an adaptive clinical trial design to test biomarker-guided "
                    "combination strategies in patients with acquired anti-PD-1 "
                    "resistance. Include a re-biopsy-at-progression requirement, "
                    "molecular profiling to assign patients to mechanism-matched "
                    "combination arms, Bayesian adaptive randomization, interim "
                    "futility analyses, and primary endpoints (objective response "
                    "rate, progression-free survival). Discuss the platform trial "
                    "model and how new combination arms could be added."
                ),
                milestone_name="trial_proposal",
                milestone_criteria=[
                    "adaptive trial",
                    "Bayesian",
                    "progression-free survival",
                    "re-biopsy",
                    "platform trial",
                ],
            ),
        ],
        ground_truth={
            "total_milestones": 4,
            "key_concepts": [
                "beta-2-microglobulin loss disrupts MHC-I antigen presentation",
                "JAK1/JAK2 mutations impair interferon-gamma signaling",
                "alternative checkpoint upregulation (LAG-3, TIM-3) is a common resistance mechanism",
                "liquid biopsy enables longitudinal resistance monitoring without serial biopsies",
                "biomarker-matched combination therapy is more rational than empiric combinations",
            ],
        },
    ),
    AgenticTask(
        id="ag_lr_006",
        category="literature_research",
        title="Microbiome-gut-brain axis in major depressive disorder",
        scenario=(
            "You are a neuroscience researcher evaluating the evidence for gut "
            "microbiome involvement in major depressive disorder (MDD). Growing "
            "evidence suggests bidirectional communication between the gut microbiome "
            "and the brain via the vagus nerve, immune signaling, and microbial "
            "metabolites. Your task is to systematically evaluate this evidence, "
            "map the mechanistic pathways, assess therapeutic approaches, and "
            "identify the most promising research directions for clinical translation."
        ),
        steps=[
            AgenticStep(
                step_number=1,
                name="Evidence Mapping",
                prompt=(
                    "Map the published evidence linking gut microbiome alterations to "
                    "MDD. Synthesize findings from case-control 16S rRNA and shotgun "
                    "metagenomics studies comparing MDD patients to healthy controls. "
                    "Discuss consistently reported taxonomic differences (reduced "
                    "Faecalibacterium, Coprococcus, Lactobacillus; increased "
                    "Eggerthella), the large Flemish Gut Flora Project findings, "
                    "and germ-free mouse experiments showing that fecal microbiota "
                    "transplant from MDD patients induces depressive-like behavior "
                    "in recipient animals. Critically assess confounders such as "
                    "diet, medication, and study heterogeneity."
                ),
                milestone_name="evidence_mapping",
                milestone_criteria=[
                    "Faecalibacterium",
                    "fecal microbiota transplant",
                    "germ-free mouse",
                    "16S rRNA",
                    "case-control",
                ],
            ),
            AgenticStep(
                step_number=2,
                name="Mechanistic Pathway Analysis",
                prompt=(
                    "Analyze the mechanistic pathways connecting the gut microbiome "
                    "to brain function and mood regulation. Discuss the vagus nerve "
                    "as a direct neural communication route, short-chain fatty acid "
                    "production (butyrate, propionate) and their effects on blood-brain "
                    "barrier integrity and microglial function, tryptophan metabolism "
                    "and its impact on serotonin biosynthesis (~95% of the body's "
                    "serotonin is produced in the gut), immune activation via microbial "
                    "translocation and systemic inflammation (IL-6, TNF-alpha, CRP), "
                    "and HPA axis modulation through cortisol signaling."
                ),
                milestone_name="mechanistic_pathways",
                milestone_criteria=[
                    "vagus nerve",
                    "short-chain fatty acids",
                    "tryptophan metabolism",
                    "serotonin",
                    "HPA axis",
                ],
            ),
            AgenticStep(
                step_number=3,
                name="Therapeutic Approach Assessment",
                prompt=(
                    "Evaluate the evidence for microbiome-targeted therapeutic "
                    "approaches in MDD. Review clinical trial data for probiotics "
                    "(psychobiotics: specific Lactobacillus and Bifidobacterium strains), "
                    "prebiotics (galacto-oligosaccharides, fructo-oligosaccharides), "
                    "fecal microbiota transplantation, dietary interventions "
                    "(Mediterranean diet trials), and synbiotics. Assess the quality "
                    "of evidence (effect sizes, sample sizes, blinding adequacy) and "
                    "discuss which approaches have the strongest translational "
                    "potential. Address the challenge of strain-specificity and "
                    "individual variation in microbiome response."
                ),
                milestone_name="therapeutic_assessment",
                milestone_criteria=[
                    "psychobiotics",
                    "Lactobacillus",
                    "Bifidobacterium",
                    "prebiotic",
                    "Mediterranean diet",
                ],
            ),
            AgenticStep(
                step_number=4,
                name="Research Agenda and Clinical Translation",
                prompt=(
                    "Propose a prioritized research agenda for advancing microbiome-"
                    "gut-brain axis therapies toward clinical use in MDD. Identify "
                    "the most critical unanswered questions: causality versus "
                    "correlation, strain-level specificity of probiotic effects, "
                    "optimal treatment duration, biomarkers for patient stratification "
                    "(enterotype, metabolomic signature), and the need for large "
                    "multi-center RCTs with standardized protocols. Propose specific "
                    "study designs that would provide definitive evidence, including "
                    "a mechanistic clinical trial combining microbiome profiling "
                    "with neuroimaging (fMRI) and metabolomics."
                ),
                milestone_name="research_agenda",
                milestone_criteria=[
                    "causality versus correlation",
                    "patient stratification",
                    "multi-center RCT",
                    "neuroimaging",
                    "metabolomic signature",
                ],
            ),
        ],
        ground_truth={
            "total_milestones": 4,
            "key_concepts": [
                "vagus nerve provides direct neural communication between gut microbiome and brain",
                "tryptophan metabolism links gut microbes to serotonin biosynthesis",
                "short-chain fatty acids modulate neuroinflammation and blood-brain barrier integrity",
                "psychobiotic clinical trials show modest but significant effect sizes",
                "causality remains unestablished; confounders (diet, medication) limit current evidence",
            ],
        },
    ),
]


# ============================================================
# troubleshooting (6 tasks)
# ============================================================

TROUBLESHOOTING_TASKS = [
    AgenticTask(
        id="ag_ts_001",
        category="troubleshooting",
        title="Failed PCR amplification of GC-rich genomic region",
        scenario=(
            "A PhD student in your molecular biology lab is attempting to PCR-amplify "
            "a 2.5 kb genomic region from human DNA for cloning. The target region has "
            "72% GC content and contains several CpG islands. The student reports no "
            "bands on the agarose gel after multiple attempts. Current conditions: "
            "standard Taq polymerase, annealing temperature 55C, 1.5 mM MgCl2, "
            "35 cycles, 20-mer primers designed with Primer3 defaults, and 50 ng "
            "genomic DNA template. The gel shows only primer dimers in all lanes. "
            "Positive control (a 1 kb non-GC-rich region) amplifies normally."
        ),
        steps=[
            AgenticStep(
                step_number=1,
                name="Systematic Diagnosis",
                prompt=(
                    "Analyze the failed PCR systematically. The positive control works, "
                    "so general reagent issues are unlikely. Given the 72% GC content "
                    "and 2.5 kb target, what are the most probable root causes? "
                    "Evaluate the primer design, annealing temperature, polymerase "
                    "choice, and reaction conditions for GC-rich template compatibility."
                ),
                milestone_name="root_cause_analysis",
                milestone_criteria=[
                    "GC-rich secondary structure",
                    "melting temperature",
                    "Taq polymerase",
                    "annealing temperature",
                    "primer dimer",
                ],
            ),
            AgenticStep(
                step_number=2,
                name="Parameter Optimization",
                prompt=(
                    "Based on your diagnosis, propose a systematic optimization "
                    "strategy. Design a gradient PCR experiment to find the optimal "
                    "annealing temperature. What MgCl2 concentration range should "
                    "be tested? Should the extension time be adjusted for the 2.5 kb "
                    "product? Recommend specific cycling parameters."
                ),
                milestone_name="parameter_optimization",
                milestone_criteria=[
                    "gradient PCR",
                    "annealing temperature",
                    "MgCl2 concentration",
                    "extension time",
                    "touchdown PCR",
                ],
            ),
            AgenticStep(
                step_number=3,
                name="GC-Rich Specific Solutions",
                prompt=(
                    "The gradient PCR still shows no amplification across all "
                    "annealing temperatures tested (50-72C). Propose GC-rich-specific "
                    "interventions. What additives, alternative polymerases, or "
                    "template modifications could resolve the secondary structure "
                    "problem? Be specific about concentrations and rationale."
                ),
                milestone_name="gc_specific_solutions",
                milestone_criteria=[
                    "DMSO",
                    "betaine",
                    "high-fidelity polymerase",
                    "denaturation temperature",
                ],
            ),
            AgenticStep(
                step_number=4,
                name="Verification Strategy",
                prompt=(
                    "After obtaining a band at the expected size using optimized "
                    "conditions, how will you verify the product is correct and "
                    "not a non-specific artifact? Design a verification workflow "
                    "including sequencing and restriction digest analysis. What "
                    "controls should be included for the final optimized protocol?"
                ),
                milestone_name="verification",
                milestone_criteria=[
                    "Sanger sequencing",
                    "restriction digest",
                    "gel extraction",
                    "no-template control",
                ],
            ),
        ],
        ground_truth={
            "total_milestones": 4,
            "key_concepts": [
                "GC-rich secondary structures prevent Taq processivity",
                "DMSO (5-10%) or betaine (1-2 M) destabilize secondary structures",
                "high-fidelity polymerase with GC-rich buffer system",
                "touchdown PCR reduces non-specific priming",
                "increased denaturation temperature (98C) for GC-rich templates",
            ],
        },
    ),
    AgenticTask(
        id="ag_ts_002",
        category="troubleshooting",
        title="Unexpected RNA-seq differential expression pattern",
        scenario=(
            "Your bioinformatics core has received RNA-seq results from a drug "
            "treatment experiment. The study compared HepG2 cells treated with a "
            "novel kinase inhibitor (24 hr, n=3) versus DMSO vehicle controls (n=3). "
            "The PI expected 200-500 differentially expressed genes (DEGs) based on "
            "pilot qPCR data for 10 target genes. However, the DESeq2 analysis shows "
            "8,247 DEGs (padj < 0.05), representing nearly half the expressed "
            "transcriptome. More troublingly, PCA reveals that all 6 samples cluster "
            "together rather than separating by treatment group. The library prep used "
            "poly-A selection, paired-end 150 bp sequencing at ~30M reads per sample."
        ),
        steps=[
            AgenticStep(
                step_number=1,
                name="Quality Assessment",
                prompt=(
                    "Before investigating the biology, assess the data quality "
                    "systematically. The PCA shows no treatment separation yet "
                    "DESeq2 reports 8,247 DEGs - these findings seem contradictory. "
                    "What quality metrics should you examine? Check the alignment "
                    "statistics, library complexity, RIN values, and sample "
                    "correlation patterns to identify the source of the discrepancy."
                ),
                milestone_name="quality_assessment",
                milestone_criteria=[
                    "PCA",
                    "sample correlation heatmap",
                    "RIN value",
                    "mapping rate",
                    "library complexity",
                ],
            ),
            AgenticStep(
                step_number=2,
                name="Contamination and Sample Swap Check",
                prompt=(
                    "Quality metrics reveal that samples labeled as biological "
                    "replicates have lower pairwise correlation (r=0.85) than "
                    "expected (typically r>0.95 for cell line replicates). Two "
                    "'control' samples correlate more highly with treated samples "
                    "than with the third control. How will you check for sample "
                    "swaps or cross-contamination? What computational approaches "
                    "can identify sample identity issues?"
                ),
                milestone_name="swap_detection",
                milestone_criteria=[
                    "sample swap",
                    "SNP genotyping",
                    "sex-linked genes",
                    "cross-contamination",
                    "sample correlation",
                ],
            ),
            AgenticStep(
                step_number=3,
                name="Batch Effect Investigation",
                prompt=(
                    "SNP analysis confirms sample identities are correct (no swap), "
                    "but you discover the 6 samples were processed in two batches "
                    "(batch 1: control_1, control_2, treated_1, treated_2; batch 2: "
                    "control_3, treated_3). Batch 2 samples used a different lot of "
                    "library prep reagents. The PCA now shows clear batch separation "
                    "on PC1 (explaining 60% of variance) while treatment separates "
                    "on PC2 (8%). How do you diagnose and quantify this batch effect?"
                ),
                milestone_name="batch_effect_diagnosis",
                milestone_criteria=[
                    "batch effect",
                    "principal component",
                    "variance explained",
                    "confounding",
                ],
            ),
            AgenticStep(
                step_number=4,
                name="Corrective Analysis",
                prompt=(
                    "Design the corrective analysis strategy. Should you apply "
                    "computational batch correction, and if so, which method? "
                    "Given the partial confounding between batch and treatment "
                    "(unbalanced design), what are the risks of overcorrection? "
                    "Propose a revised analysis pipeline and recommendations for "
                    "the PI, including whether additional samples are needed."
                ),
                milestone_name="corrective_analysis",
                milestone_criteria=[
                    "ComBat",
                    "batch correction",
                    "confounding",
                    "additional replicates",
                    "DESeq2 design formula",
                ],
            ),
        ],
        ground_truth={
            "total_milestones": 4,
            "key_concepts": [
                "batch effect from reagent lot confounded with treatment groups",
                "include batch as covariate in DESeq2 design formula",
                "ComBat or limma removeBatchEffect for batch correction",
                "unbalanced batch-treatment design risks overcorrection",
                "recommend repeating with balanced randomized design",
            ],
        },
    ),
    AgenticTask(
        id="ag_ts_003",
        category="troubleshooting",
        title="Low lentiviral transduction efficiency in primary T cells",
        scenario=(
            "A gene therapy lab reports critically low transduction efficiency when "
            "delivering a CAR construct via lentiviral vector into primary human T "
            "cells from healthy donor PBMCs. Flow cytometry shows only 3-5% GFP+ "
            "cells 72 hours post-transduction (target: >50%). The same lentiviral "
            "preparation was titered on HEK293T cells at 1 x 10^8 TU/mL by flow "
            "cytometry. Current transduction protocol: T cells isolated by negative "
            "selection, activated with anti-CD3/CD28 beads for 24 hr, transduced at "
            "MOI 10 with 8 ug/mL polybrene in standard RPMI + 10% FBS, and assessed "
            "at 72 hr post-transduction."
        ),
        steps=[
            AgenticStep(
                step_number=1,
                name="Titer Verification and MOI Assessment",
                prompt=(
                    "The HEK293T titer is 10^8 TU/mL, but effective titer on T "
                    "cells is likely very different. Analyze why the functional "
                    "titer on primary T cells may be much lower than on HEK293T. "
                    "What factors cause the discrepancy between cell-line titer and "
                    "primary cell transduction? Should the MOI be recalculated?"
                ),
                milestone_name="titer_assessment",
                milestone_criteria=[
                    "functional titer",
                    "MOI",
                    "HEK293T",
                    "primary cell",
                    "receptor expression",
                ],
            ),
            AgenticStep(
                step_number=2,
                name="Transduction Condition Optimization",
                prompt=(
                    "Propose specific protocol modifications to increase transduction "
                    "efficiency. Address the transduction enhancer (polybrene may be "
                    "toxic to T cells), physical methods to increase virus-cell contact, "
                    "optimal timing relative to activation, and culture conditions. "
                    "Include specific concentrations and centrifugation parameters."
                ),
                milestone_name="condition_optimization",
                milestone_criteria=[
                    "spinoculation",
                    "RetroNectin",
                    "polybrene",
                    "centrifugation",
                    "activation",
                ],
            ),
            AgenticStep(
                step_number=3,
                name="T Cell-Specific Considerations",
                prompt=(
                    "Primary T cells have unique biology that affects transduction. "
                    "The cells were activated for only 24 hours before transduction. "
                    "Evaluate the T cell activation state, cell cycle status, and "
                    "innate immune sensing (SAMHD1, IFITM proteins) as barriers to "
                    "lentiviral transduction. What is the optimal activation window?"
                ),
                milestone_name="tcell_biology",
                milestone_criteria=[
                    "T cell activation",
                    "CD3/CD28",
                    "cell cycle",
                    "SAMHD1",
                    "IL-2",
                ],
            ),
            AgenticStep(
                step_number=4,
                name="Alternative Approaches and Verification",
                prompt=(
                    "If optimized lentiviral transduction still falls short, what "
                    "alternative delivery strategies should be considered? Evaluate "
                    "pseudotyping options, concentrated virus preparations, and "
                    "non-viral alternatives. How will you verify CAR expression and "
                    "function in successfully transduced cells?"
                ),
                milestone_name="alternatives",
                milestone_criteria=[
                    "VSV-G",
                    "virus concentration",
                    "electroporation",
                    "CAR expression",
                ],
            ),
        ],
        ground_truth={
            "total_milestones": 4,
            "key_concepts": [
                "HEK293T titer overestimates functional titer on primary T cells",
                "RetroNectin replaces polybrene for T cell transduction",
                "spinoculation (800-1200g) increases virus-cell contact",
                "48-72 hr activation optimal for T cell transduction",
                "SAMHD1 restriction factor is depleted in cycling T cells",
            ],
        },
    ),
    AgenticTask(
        id="ag_ts_004",
        category="troubleshooting",
        title="Batch effect in clinical TMT proteomics",
        scenario=(
            "A clinical proteomics study has completed TMT-labeled quantitative "
            "proteomics on 120 plasma samples from a cancer biomarker discovery "
            "cohort (60 cases, 60 controls). Samples were analyzed in 3 batches "
            "of 40 samples each using TMT11-plex (12 plexes total, 4 plexes per "
            "batch, with one bridge/reference channel per plex). After data processing with "
            "MaxQuant, PCA of the 4,200 quantified proteins reveals that PC1 "
            "(42% variance) separates samples by TMT batch rather than by disease "
            "status. Cases and controls were randomized across batches, but the "
            "batch effect dominates the biology. The PI needs to submit the "
            "manuscript in 6 weeks."
        ),
        steps=[
            AgenticStep(
                step_number=1,
                name="Batch Effect Characterization",
                prompt=(
                    "Characterize the batch effect in detail. Beyond PCA, what "
                    "analyses should you perform to understand the nature and "
                    "magnitude of the batch effect? Examine the bridge/reference "
                    "channel consistency, protein-level intensity distributions, "
                    "and the relationship between batch and known covariates "
                    "(age, sex, collection site)."
                ),
                milestone_name="batch_characterization",
                milestone_criteria=[
                    "bridge sample",
                    "intensity distribution",
                    "PCA",
                    "batch variance",
                    "covariate",
                ],
            ),
            AgenticStep(
                step_number=2,
                name="Source Identification",
                prompt=(
                    "The bridge sample analysis reveals that channel intensities "
                    "in batch 3 are systematically 30% lower than batches 1 and 2. "
                    "Batch 3 was processed 3 months after the first two batches. "
                    "Investigate potential sources: TMT reagent lot differences, "
                    "LC-MS instrument maintenance events, column aging, sample "
                    "storage duration, and operator effects. What is the most "
                    "likely root cause?"
                ),
                milestone_name="source_identification",
                milestone_criteria=[
                    "TMT reagent lot",
                    "instrument performance",
                    "column aging",
                    "sample storage",
                    "normalization",
                ],
            ),
            AgenticStep(
                step_number=3,
                name="Computational Correction",
                prompt=(
                    "Propose a computational correction strategy. Compare median "
                    "centering, quantile normalization, ComBat, and bridge-sample "
                    "ratio correction. Given that cases and controls are balanced "
                    "across batches, which approach best preserves biological "
                    "signal while removing the batch effect? Include validation "
                    "steps to confirm correction is not removing real biology."
                ),
                milestone_name="computational_correction",
                milestone_criteria=[
                    "median centering",
                    "ComBat",
                    "quantile normalization",
                    "bridge sample ratio",
                    "biological signal",
                ],
            ),
            AgenticStep(
                step_number=4,
                name="Prevention Strategy",
                prompt=(
                    "Design a prevention strategy for future TMT proteomics "
                    "studies. How should the experimental design be structured to "
                    "minimize batch effects? Address randomization schemes, "
                    "pooled reference design, instrument QC, and study-wide "
                    "normalization strategies."
                ),
                milestone_name="prevention",
                milestone_criteria=[
                    "randomized block design",
                    "pooled reference",
                    "instrument QC",
                    "sample randomization",
                ],
            ),
        ],
        ground_truth={
            "total_milestones": 4,
            "key_concepts": [
                "bridge sample used to normalize across TMT plexes",
                "systematic intensity drop in batch 3 due to instrument or reagent drift",
                "ComBat with balanced design preserves biological signal",
                "randomized block design prevents batch-biology confounding",
                "pooled reference channel enables cross-plex normalization",
            ],
        },
    ),
    AgenticTask(
        id="ag_ts_005",
        category="troubleshooting",
        title="Single-cell RNA-seq low cell recovery and poor quality",
        scenario=(
            "A neuroscience lab performed a 10x Chromium single-cell RNA-seq "
            "experiment on adult mouse cortex tissue. They targeted 10,000 cells "
            "per sample but Cell Ranger reports only 1,200 cells recovered. The "
            "web summary shows a median of 800 genes per cell (expected: 2,000+), "
            "a 12% estimated doublet rate, and 38% of reads mapping to "
            "mitochondrial genes. The tissue was dissociated using mechanical "
            "trituration with a standard enzymatic protocol (trypsin, 30 min at "
            "37C). Cell viability by trypan blue was reported as 65% before "
            "loading. The lab loaded 16,000 cells onto the chip expecting 60% "
            "capture rate."
        ),
        steps=[
            AgenticStep(
                step_number=1,
                name="Dissociation Troubleshooting",
                prompt=(
                    "The 65% viability is well below the 10x Genomics recommendation "
                    "of >90%. Diagnose the dissociation protocol problems. Trypsin "
                    "at 37C for 30 minutes on brain tissue is likely causing excessive "
                    "cell death. What enzymatic and mechanical dissociation parameters "
                    "should be optimized for adult mouse cortex? Consider enzyme "
                    "choice, temperature, duration, and mechanical force."
                ),
                milestone_name="dissociation_diagnosis",
                milestone_criteria=[
                    "cell viability",
                    "papain",
                    "dissociation protocol",
                    "trypsin",
                    "enzymatic digestion",
                ],
            ),
            AgenticStep(
                step_number=2,
                name="Viability Optimization and Dead Cell Removal",
                prompt=(
                    "Even with optimized dissociation, some dead cells are "
                    "inevitable with adult brain tissue. The 38% mitochondrial "
                    "reads strongly suggest dead/dying cells are being captured. "
                    "What dead cell removal strategies should be employed before "
                    "loading the 10x chip? Compare FACS, MACS dead cell removal "
                    "kits, and density gradient approaches. What viability "
                    "threshold is acceptable?"
                ),
                milestone_name="viability_optimization",
                milestone_criteria=[
                    "dead cell removal",
                    "MACS",
                    "FACS",
                    "mitochondrial percentage",
                    "cell strainer",
                ],
            ),
            AgenticStep(
                step_number=3,
                name="Loading Parameter Adjustment",
                prompt=(
                    "With improved viability (now >90% after dead cell removal), "
                    "recalculate the loading parameters. The original loading of "
                    "16,000 cells with 65% viability means ~10,400 live cells were "
                    "loaded but only 1,200 captured. Address the relationship "
                    "between cell concentration, loading volume, and capture "
                    "efficiency. How does the high doublet rate (12%) relate to "
                    "the low recovery?"
                ),
                milestone_name="loading_optimization",
                milestone_criteria=[
                    "cell concentration",
                    "loading volume",
                    "capture efficiency",
                    "doublet rate",
                    "cell counting",
                ],
            ),
            AgenticStep(
                step_number=4,
                name="Quality Threshold Setting and Computational QC",
                prompt=(
                    "For the data already collected (1,200 cells), define the "
                    "computational QC filtering strategy. What mitochondrial "
                    "percentage cutoff should be applied? How will you identify "
                    "and remove doublets computationally? What minimum gene count "
                    "threshold is appropriate for mouse cortex? Design the QC "
                    "pipeline and estimate how many cells will pass filters."
                ),
                milestone_name="computational_qc",
                milestone_criteria=[
                    "mitochondrial threshold",
                    "doublet detection",
                    "Scrublet",
                    "minimum genes",
                    "quality filtering",
                ],
            ),
        ],
        ground_truth={
            "total_milestones": 4,
            "key_concepts": [
                "papain preferred over trypsin for adult brain dissociation",
                "dead cell removal (MACS or FACS) essential before 10x loading",
                "viability must exceed 90% for quality scRNA-seq",
                "high mitochondrial reads indicate damaged or dying cells",
                "Scrublet or DoubletFinder for computational doublet detection",
            ],
        },
    ),
    AgenticTask(
        id="ag_ts_006",
        category="troubleshooting",
        title="HPLC-MS metabolomics systematic signal drift",
        scenario=(
            "An untargeted metabolomics study analyzing 200 plasma samples by "
            "LC-MS/MS (reverse-phase C18, ESI positive mode) shows systematic "
            "signal intensity decrease across the analytical batch. The run order "
            "spans 4 days of continuous acquisition. Quality control (QC) samples "
            "(pooled plasma injected every 10 samples) show a clear monotonic "
            "decrease: the last QC sample has 55% lower total ion current than "
            "the first. Internal standards (isotope-labeled) show 40% intensity "
            "drop. Retention times have shifted by +0.3 minutes for late-eluting "
            "compounds. Mass accuracy remains within 3 ppm."
        ),
        steps=[
            AgenticStep(
                step_number=1,
                name="Drift Characterization",
                prompt=(
                    "Characterize the signal drift in detail. The QC samples show "
                    "55% TIC drop and internal standards drop 40%. What does it "
                    "mean that the internal standard intensity also decreases - "
                    "does this indicate a matrix effect or an instrument issue? "
                    "Analyze the retention time shift and mass accuracy data. "
                    "What patterns differentiate instrument drift from matrix "
                    "buildup or column degradation?"
                ),
                milestone_name="drift_characterization",
                milestone_criteria=[
                    "internal standard",
                    "total ion current",
                    "retention time shift",
                    "signal intensity",
                    "QC sample",
                ],
            ),
            AgenticStep(
                step_number=2,
                name="Instrument Diagnosis",
                prompt=(
                    "The internal standard drop (40%) combined with retention "
                    "time shift (+0.3 min) and preserved mass accuracy points to "
                    "specific instrument components. Diagnose the most likely "
                    "hardware causes. Consider the ESI source contamination, "
                    "column degradation, mobile phase issues, and ion optics. "
                    "What instrument checks and maintenance should be performed?"
                ),
                milestone_name="instrument_diagnosis",
                milestone_criteria=[
                    "ESI source",
                    "column degradation",
                    "ion suppression",
                    "spray stability",
                    "system suitability",
                ],
            ),
            AgenticStep(
                step_number=3,
                name="Computational Correction",
                prompt=(
                    "The 200 samples have already been run and re-acquisition is "
                    "not feasible due to limited sample volume. Design a "
                    "computational correction strategy using the QC samples. "
                    "Compare QC-RLSC (robust LOESS signal correction), median "
                    "fold-change normalization, and internal standard-based "
                    "correction. Which approach is most appropriate given that "
                    "both QC samples and internal standards show drift?"
                ),
                milestone_name="computational_correction",
                milestone_criteria=[
                    "QC-RLSC",
                    "LOESS",
                    "signal correction",
                    "normalization",
                    "internal standard correction",
                ],
            ),
            AgenticStep(
                step_number=4,
                name="Prevention Protocol",
                prompt=(
                    "Design a prevention protocol for future large-batch "
                    "metabolomics runs. Address maximum batch size, instrument "
                    "conditioning, QC injection frequency, system suitability "
                    "criteria for continuing acquisition, sample randomization, "
                    "and column conditioning strategies. What stopping criteria "
                    "should be implemented to detect drift in real-time?"
                ),
                milestone_name="prevention",
                milestone_criteria=[
                    "column conditioning",
                    "sample randomization",
                    "system suitability",
                    "batch size",
                    "QC frequency",
                ],
            ),
        ],
        ground_truth={
            "total_milestones": 4,
            "key_concepts": [
                "ESI source contamination and column degradation cause progressive signal loss",
                "QC-RLSC with LOESS regression corrects run-order-dependent drift",
                "internal standard drop indicates instrument-level sensitivity loss",
                "retention time shift suggests column degradation or mobile phase change",
                "real-time system suitability criteria prevent data loss from undetected drift",
            ],
        },
    ),
]


# ============================================================
# Aggregate list (grows as categories are added in Stage 4)
# ============================================================

AGENTIC_TASKS: list[AgenticTask] = [
    *EXPERIMENTAL_DESIGN_TASKS,
    *BIOINFORMATICS_PIPELINE_TASKS,
    *LITERATURE_RESEARCH_TASKS,
    *TROUBLESHOOTING_TASKS,
]
