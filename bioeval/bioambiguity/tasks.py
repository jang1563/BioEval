"""
BioAmbiguity task definitions.

Each task tests whether an LLM recognizes that a biological concept
behaves differently in different contexts.

Task types:
  - gene_context: Same gene, different tissue/disease/species function
  - pathway_crosstalk: Same pathway, context-dependent activation
  - dose_response: Concentration-dependent opposite effects
  - temporal_shift: Developmental stage changes meaning
  - species_translation: Model organism to human translational gaps

Stage 1: gene_context (9 tasks). Other types added in Stage 2.
"""

# ============================================================
# gene_context — same gene, different context → different role
# ============================================================

GENE_CONTEXT_TASKS = [
    {
        "id": "ba_gc_001",
        "title": "TP53 context-dependent roles",
        "prompt": (
            "TP53 is widely known as a tumor suppressor. However, its role "
            "varies significantly across biological contexts.\n\n"
            "Describe how TP53 functions differently in:\n"
            "1. Normal epithelial tissue under DNA damage\n"
            "2. iPSC reprogramming (Yamanaka factor-driven)\n"
            "3. Tumors carrying gain-of-function TP53 mutations (e.g., R175H, R248W)\n\n"
            "For each context, explain the specific mechanism and why the outcome differs."
        ),
        "ground_truth": {
            "contexts": {
                "dna_damage": {
                    "role": "tumor suppressor",
                    "key_terms": ["apoptosis", "cell cycle arrest", "p21", "senescence"],
                    "mechanism": "Activates p21/CDKN1A for G1 arrest; triggers BAX/PUMA for apoptosis",
                },
                "ipsc_reprogramming": {
                    "role": "barrier to reprogramming",
                    "key_terms": ["reprogramming", "barrier", "iPSC", "Yamanaka", "senescence"],
                    "mechanism": "p53 activation limits reprogramming efficiency by inducing senescence/apoptosis in partially reprogrammed cells",
                },
                "gain_of_function": {
                    "role": "oncogene / cancer driver",
                    "key_terms": ["gain of function", "dominant negative", "R175H", "R248W", "oncogene"],
                    "mechanism": "Mutant p53 acquires new functions including chromatin remodeling, enhanced invasion, and drug resistance beyond loss of wild-type function",
                },
            },
            "distinction_key": "Same gene acts as suppressor, barrier, or driver depending on mutation status and cellular context",
        },
    },
    {
        "id": "ba_gc_002",
        "title": "VEGF-A in physiological vs pathological angiogenesis",
        "prompt": (
            "VEGF-A promotes blood vessel growth, but its significance varies "
            "dramatically across contexts.\n\n"
            "Compare VEGF-A's role and therapeutic implications in:\n"
            "1. Wound healing (physiological angiogenesis)\n"
            "2. Solid tumor progression (pathological angiogenesis)\n"
            "3. Wet age-related macular degeneration (AMD)\n\n"
            "For each context, explain the mechanism and why targeting VEGF-A "
            "is beneficial in some contexts but harmful in others."
        ),
        "ground_truth": {
            "contexts": {
                "wound_healing": {
                    "role": "essential for repair",
                    "key_terms": ["wound", "repair", "granulation", "neovascularization"],
                    "mechanism": "Hypoxia-driven VEGF release recruits endothelial cells; anti-VEGF therapy would impair healing",
                },
                "tumor_angiogenesis": {
                    "role": "tumor-promoting",
                    "key_terms": ["tumor", "bevacizumab", "anti-angiogenic", "metastasis"],
                    "mechanism": "Tumor-secreted VEGF drives chaotic neovasculature; anti-VEGF (bevacizumab) is therapeutic",
                },
                "wet_amd": {
                    "role": "pathological in retina",
                    "key_terms": ["macular degeneration", "AMD", "ranibizumab", "aflibercept", "choroidal"],
                    "mechanism": "Choroidal neovascularization causes vision loss; anti-VEGF intravitreal injections are standard of care",
                },
            },
            "distinction_key": "Same growth factor is essential for healing, drives tumor growth, and causes retinal damage — context determines therapeutic strategy",
        },
    },
    {
        "id": "ba_gc_003",
        "title": "MYC in normal proliferation vs oncogenesis vs apoptosis",
        "prompt": (
            "The MYC proto-oncogene is one of the most frequently deregulated "
            "genes in cancer. However, MYC also has critical normal functions "
            "and can paradoxically promote apoptosis.\n\n"
            "Explain MYC's role in:\n"
            "1. Normal cell proliferation (e.g., activated T cells)\n"
            "2. Burkitt lymphoma (t(8;14) translocation)\n"
            "3. MYC-induced apoptosis (when survival signals are absent)\n\n"
            "Why does the same transcription factor promote both proliferation "
            "and cell death depending on context?"
        ),
        "ground_truth": {
            "contexts": {
                "normal_proliferation": {
                    "role": "regulated growth promoter",
                    "key_terms": ["proliferation", "T cell", "cell cycle", "metabolic reprogramming"],
                    "mechanism": "MYC drives ribosome biogenesis, glycolysis, and cell cycle entry in response to growth factor signaling",
                },
                "burkitt_lymphoma": {
                    "role": "oncogene",
                    "key_terms": ["Burkitt", "translocation", "t(8;14)", "immunoglobulin", "constitutive"],
                    "mechanism": "Translocation places MYC under immunoglobulin enhancer control; constitutive overexpression drives uncontrolled B-cell proliferation",
                },
                "myc_induced_apoptosis": {
                    "role": "pro-apoptotic",
                    "key_terms": ["apoptosis", "ARF", "p53", "survival signal", "dual signal"],
                    "mechanism": "MYC activates ARF-p53 axis; without concurrent survival signals (IGF-1, BCL-2), MYC triggers apoptosis as a safeguard",
                },
            },
            "distinction_key": "MYC functions as a dual-signal sensor: proliferation when survival signals present, apoptosis when absent — subverted in cancer by co-occurring mutations",
        },
    },
    {
        "id": "ba_gc_004",
        "title": "TGF-beta receptor signaling: epithelial vs mesenchymal",
        "prompt": (
            "TGF-beta signaling through TGFBR1/TGFBR2 has opposite effects "
            "in different cell types and disease stages.\n\n"
            "Compare TGF-beta signaling in:\n"
            "1. Normal epithelial cells (growth control)\n"
            "2. Advanced carcinoma cells (EMT and metastasis)\n"
            "3. Regulatory T cells (immune suppression)\n\n"
            "How can the same ligand-receptor system produce tumor-suppressive, "
            "tumor-promoting, and immunosuppressive effects?"
        ),
        "ground_truth": {
            "contexts": {
                "epithelial_growth_control": {
                    "role": "tumor suppressor",
                    "key_terms": ["growth arrest", "p15", "p21", "SMAD", "cytostatic"],
                    "mechanism": "Canonical SMAD2/3 signaling induces p15/p21 CDK inhibitors, enforcing G1 arrest in normal epithelium",
                },
                "emt_metastasis": {
                    "role": "tumor promoter",
                    "key_terms": ["EMT", "epithelial mesenchymal", "invasion", "metastasis", "SNAIL", "non-canonical"],
                    "mechanism": "Cancer cells lose cytostatic response (e.g., SMAD4 loss); TGF-beta activates non-canonical pathways (RAS, PI3K, RhoA) driving EMT",
                },
                "treg_immunosuppression": {
                    "role": "immunosuppressive",
                    "key_terms": ["Treg", "regulatory T cell", "FOXP3", "immune evasion", "immunosuppression"],
                    "mechanism": "TGF-beta induces FOXP3 expression in naive T cells, generating Tregs that suppress anti-tumor immunity",
                },
            },
            "distinction_key": "TGF-beta switch from suppressor to promoter reflects loss of cytostatic program and gain of invasive/immunosuppressive programs during cancer progression",
        },
    },
    {
        "id": "ba_gc_005",
        "title": "BRCA1 in DNA repair vs transcription regulation vs development",
        "prompt": (
            "BRCA1 is best known for its role in hereditary breast cancer risk, "
            "but it has multiple distinct molecular functions.\n\n"
            "Describe BRCA1's roles in:\n"
            "1. Homologous recombination DNA repair\n"
            "2. Transcription-coupled regulation (RNA Pol II)\n"
            "3. X chromosome inactivation during female development\n\n"
            "How do these distinct functions all relate to cancer predisposition "
            "when BRCA1 is mutated?"
        ),
        "ground_truth": {
            "contexts": {
                "dna_repair": {
                    "role": "HR repair factor",
                    "key_terms": ["homologous recombination", "RAD51", "PALB2", "BRCA1-BARD1", "double strand break"],
                    "mechanism": "BRCA1-PALB2-BRCA2 complex loads RAD51 onto ssDNA at resected DSBs for homologous recombination",
                },
                "transcription_regulation": {
                    "role": "transcriptional co-regulator",
                    "key_terms": ["RNA polymerase", "transcription", "BRCA1-BARD1", "ubiquitin", "chromatin"],
                    "mechanism": "BRCA1-BARD1 E3 ubiquitin ligase modifies histones and interacts with RNA Pol II to regulate transcription at damage sites",
                },
                "x_inactivation": {
                    "role": "XIST RNA coating facilitator",
                    "key_terms": ["X inactivation", "XIST", "Barr body", "Xi", "heterochromatin"],
                    "mechanism": "BRCA1 localizes to inactive X chromosome and maintains XIST RNA coating; loss disrupts Xi silencing",
                },
            },
            "distinction_key": "BRCA1 loss simultaneously impairs DNA repair, transcriptional fidelity, and epigenetic stability — explaining tissue-specific cancer risk",
        },
    },
    {
        "id": "ba_gc_006",
        "title": "Wnt/beta-catenin in stem cells vs colorectal cancer vs bone",
        "prompt": (
            "Wnt/beta-catenin signaling is critical for stem cell maintenance "
            "but is also one of the most commonly mutated pathways in cancer.\n\n"
            "Compare Wnt/beta-catenin pathway activity in:\n"
            "1. Intestinal stem cells (LGR5+ crypt base)\n"
            "2. Colorectal cancer (APC-mutant tumors)\n"
            "3. Bone formation (osteoblast differentiation)\n\n"
            "Why is the same pathway essential for tissue homeostasis in one "
            "context and oncogenic in another?"
        ),
        "ground_truth": {
            "contexts": {
                "intestinal_stem_cells": {
                    "role": "stem cell maintenance",
                    "key_terms": ["LGR5", "crypt", "stem cell", "Paneth", "niche", "R-spondin"],
                    "mechanism": "Wnt ligands from Paneth/mesenchymal cells maintain LGR5+ ISC self-renewal; R-spondin amplifies via LGR5-ZNRF3 axis",
                },
                "colorectal_cancer": {
                    "role": "oncogenic driver",
                    "key_terms": ["APC", "adenomatous polyposis", "beta-catenin", "constitutive", "TCF"],
                    "mechanism": "APC truncation prevents beta-catenin destruction complex assembly; constitutive nuclear beta-catenin drives proliferation via TCF/LEF targets",
                },
                "bone_formation": {
                    "role": "osteoblast differentiation",
                    "key_terms": ["osteoblast", "bone", "sclerostin", "SOST", "osteoporosis", "Wnt"],
                    "mechanism": "Canonical Wnt promotes osteoblast differentiation and bone formation; sclerostin (SOST) inhibits Wnt and is targeted in osteoporosis therapy (romosozumab)",
                },
            },
            "distinction_key": "Wnt level is tightly titrated: physiological Wnt maintains stemness and bone; oncogenic mutations remove the off-switch, causing constitutive activation",
        },
    },
    {
        "id": "ba_gc_007",
        "title": "NF-kB in inflammation vs cancer vs neuroprotection",
        "prompt": (
            "NF-kB is the master regulator of inflammation, but its role "
            "extends well beyond immune responses.\n\n"
            "Describe NF-kB's distinct roles in:\n"
            "1. Acute bacterial infection (innate immune activation)\n"
            "2. Chronic inflammation-driven cancer (e.g., hepatocellular carcinoma)\n"
            "3. Neuronal survival after ischemic injury\n\n"
            "How do the downstream targets and outcomes differ across "
            "these three contexts?"
        ),
        "ground_truth": {
            "contexts": {
                "acute_inflammation": {
                    "role": "protective immune activator",
                    "key_terms": ["TNF-alpha", "IL-6", "innate immunity", "pathogen", "inflammatory"],
                    "mechanism": "TLR/MyD88 signaling activates IKK complex; NF-kB translocates to nucleus, inducing TNF-alpha, IL-1beta, chemokines for pathogen clearance",
                },
                "cancer_promotion": {
                    "role": "tumor promoter via chronic inflammation",
                    "key_terms": ["chronic inflammation", "hepatocellular", "anti-apoptotic", "BCL-2", "proliferation"],
                    "mechanism": "Constitutive NF-kB in chronic hepatitis/cirrhosis upregulates BCL-2/BCL-XL (anti-apoptotic), cyclin D1 (proliferative), and VEGF (angiogenic), promoting HCC",
                },
                "neuroprotection": {
                    "role": "neuronal survival factor",
                    "key_terms": ["neuron", "neuroprotection", "ischemia", "survival", "BDNF", "Bcl-2"],
                    "mechanism": "In post-ischemic neurons, NF-kB induces pro-survival genes (Bcl-2, MnSOD, BDNF) — distinct target gene program from inflammatory NF-kB",
                },
            },
            "distinction_key": "Same transcription factor activates different gene programs: inflammatory in immune cells, anti-apoptotic in cancer, pro-survival in neurons — determined by cofactors and chromatin state",
        },
    },
    {
        "id": "ba_gc_008",
        "title": "Estrogen receptor alpha in breast, bone, and cardiovascular",
        "prompt": (
            "Estrogen receptor alpha (ESR1/ERalpha) mediates estrogen effects "
            "across multiple tissues with very different outcomes.\n\n"
            "Explain ERalpha's tissue-specific effects in:\n"
            "1. Breast epithelium (normal and ER+ breast cancer)\n"
            "2. Bone (osteoclast regulation)\n"
            "3. Cardiovascular endothelium\n\n"
            "Why does tamoxifen act as an antagonist in breast but a partial "
            "agonist in bone and uterus?"
        ),
        "ground_truth": {
            "contexts": {
                "breast": {
                    "role": "proliferative driver (cancer) / normal development",
                    "key_terms": ["ER-positive", "tamoxifen", "antagonist", "proliferation", "endocrine therapy"],
                    "mechanism": "ERalpha drives cyclin D1 and MYC expression; tamoxifen recruits corepressors (NCoR/SMRT) in breast tissue, blocking proliferation",
                },
                "bone": {
                    "role": "anti-resorptive",
                    "key_terms": ["osteoclast", "bone density", "osteoporosis", "RANKL", "OPG"],
                    "mechanism": "ERalpha in osteoblasts upregulates OPG and suppresses RANKL, reducing osteoclast activity; tamoxifen acts as partial agonist here (beneficial for bone)",
                },
                "cardiovascular": {
                    "role": "cardioprotective",
                    "key_terms": ["endothelium", "nitric oxide", "eNOS", "vasodilation", "cardioprotective"],
                    "mechanism": "ERalpha activates eNOS via PI3K/Akt in endothelial cells, promoting vasodilation and atheroprotection; explains premenopausal cardiovascular protection",
                },
            },
            "distinction_key": "Tamoxifen is a SERM: tissue-specific cofactor availability (coactivators vs corepressors) determines agonist vs antagonist activity — same drug, opposite effects by tissue",
        },
    },
    {
        "id": "ba_gc_009",
        "title": "PTEN in tumor suppression vs neurodevelopment vs metabolism",
        "prompt": (
            "PTEN is the second most commonly mutated tumor suppressor, "
            "but germline PTEN mutations also cause neurodevelopmental disorders "
            "and metabolic phenotypes.\n\n"
            "Compare PTEN's functions in:\n"
            "1. Tumor suppression (PI3K/AKT regulation)\n"
            "2. Neurodevelopment (PTEN hamartoma tumor syndrome / autism)\n"
            "3. Metabolic regulation (insulin sensitivity)\n\n"
            "How does loss of the same phosphatase produce cancer, "
            "macrocephaly/autism, and metabolic changes?"
        ),
        "ground_truth": {
            "contexts": {
                "tumor_suppression": {
                    "role": "negative regulator of PI3K/AKT",
                    "key_terms": ["PI3K", "AKT", "PIP3", "PIP2", "phosphatase", "mTOR"],
                    "mechanism": "PTEN dephosphorylates PIP3 to PIP2, opposing PI3K; loss causes constitutive AKT/mTOR activation driving proliferation and survival",
                },
                "neurodevelopment": {
                    "role": "brain size regulator",
                    "key_terms": ["macrocephaly", "autism", "PHTS", "hamartoma", "neuronal hypertrophy", "Cowden"],
                    "mechanism": "Neuronal PTEN loss causes AKT/mTOR hyperactivation → soma hypertrophy, excess dendritic branching, altered synaptic function → macrocephaly and ASD features",
                },
                "metabolic": {
                    "role": "insulin sensitivity modulator",
                    "key_terms": ["insulin", "sensitivity", "glucose", "adipose", "lipogenesis"],
                    "mechanism": "PTEN opposes insulin-PI3K-AKT signaling; heterozygous PTEN loss paradoxically enhances insulin sensitivity and can cause obesity via enhanced lipogenesis",
                },
            },
            "distinction_key": "PTEN loss hyperactivates the same PI3K/AKT/mTOR axis, but tissue context determines outcome: cancer (epithelium), macrocephaly (neurons), enhanced insulin response (metabolic tissues)",
        },
    },
]

# ============================================================
# pathway_crosstalk — same pathway, different context → different outcome
# ============================================================

PATHWAY_CROSSTALK_TASKS: list[dict] = [
    {
        "id": "ba_pc_001",
        "title": "MAPK/ERK cascade in growth, cancer, and memory",
        "prompt": (
            "The RAS-RAF-MEK-ERK (MAPK) cascade is one of the most studied "
            "signaling pathways in biology.\n\n"
            "Compare MAPK/ERK pathway function in:\n"
            "1. Normal epithelial cells responding to growth factors\n"
            "2. BRAF V600E-mutant melanoma\n"
            "3. Hippocampal neurons during memory consolidation\n\n"
            "For each context, explain the activation mechanism, downstream "
            "targets, and why the same kinase cascade produces such different "
            "biological outcomes."
        ),
        "ground_truth": {
            "contexts": {
                "growth_factor_signaling": {
                    "role": "regulated proliferation signal",
                    "key_terms": ["growth factor", "RAS", "RAF", "MEK", "ERK", "proliferation", "regulated"],
                    "mechanism": "RTK activation → RAS-GTP → RAF → MEK → ERK; ERK activates cyclin D1 and MYC for controlled cell cycle entry; transient activation with negative feedback",
                },
                "braf_melanoma": {
                    "role": "constitutive oncogenic driver",
                    "key_terms": ["BRAF", "V600E", "melanoma", "vemurafenib", "constitutive", "oncogene"],
                    "mechanism": "V600E mutation locks BRAF in active conformation; constitutive MEK/ERK activation independent of RAS; vemurafenib targets mutant BRAF",
                },
                "memory_consolidation": {
                    "role": "learning and memory stabilizer",
                    "key_terms": ["synaptic plasticity", "LTP", "CREB", "memory", "hippocampus", "long-term potentiation"],
                    "mechanism": "ERK activation in post-synaptic neurons phosphorylates CREB, driving gene expression for long-term potentiation and memory consolidation",
                },
            },
            "distinction_key": "Same kinase cascade transmits growth signals in epithelia, drives melanoma when constitutively active, and consolidates memory in neurons — cell type and activation duration determine outcome",
        },
    },
    {
        "id": "ba_pc_002",
        "title": "AMPK signaling in energy, exercise, and cancer",
        "prompt": (
            "AMP-activated protein kinase (AMPK) is the master cellular energy "
            "sensor, but its biological impact varies dramatically by context.\n\n"
            "Compare AMPK signaling in:\n"
            "1. Hepatocytes under metabolic stress (energy homeostasis)\n"
            "2. Skeletal muscle during exercise\n"
            "3. Cancer cells (tumor suppression via metformin)\n\n"
            "How does the same energy sensor produce metabolic homeostasis, "
            "exercise adaptation, and tumor suppression?"
        ),
        "ground_truth": {
            "contexts": {
                "energy_homeostasis": {
                    "role": "cellular energy sensor",
                    "key_terms": ["energy sensor", "AMP/ATP ratio", "fatty acid oxidation", "glucose uptake", "LKB1"],
                    "mechanism": "Rising AMP/ATP ratio activates AMPK via LKB1; AMPK promotes catabolic pathways (FAO, autophagy) and inhibits anabolic pathways (mTORC1, lipogenesis)",
                },
                "exercise_adaptation": {
                    "role": "exercise-induced metabolic adaptation",
                    "key_terms": ["exercise", "mitochondrial biogenesis", "PGC-1alpha", "insulin sensitivity", "GLUT4"],
                    "mechanism": "Muscle contraction activates AMPK → PGC-1α → mitochondrial biogenesis; enhances GLUT4 translocation and insulin sensitivity",
                },
                "cancer_suppression": {
                    "role": "tumor suppressor",
                    "key_terms": ["metformin", "tumor suppressor", "mTOR inhibition", "Warburg", "LKB1"],
                    "mechanism": "AMPK opposes Warburg effect by inhibiting mTORC1 and lipogenesis; metformin activates AMPK; LKB1 loss in NSCLC disables AMPK tumor suppression",
                },
            },
            "distinction_key": "AMPK integrates energy status across all contexts but outcome depends on tissue — metabolic homeostasis in liver, performance adaptation in muscle, tumor suppression in epithelia",
        },
    },
    {
        "id": "ba_pc_003",
        "title": "Hedgehog pathway in development, stem cells, and cancer",
        "prompt": (
            "Hedgehog (Hh) signaling plays critical roles from embryogenesis "
            "to adult tissue maintenance, but also drives cancer.\n\n"
            "Compare Hedgehog pathway function in:\n"
            "1. Embryonic neural tube patterning (SHH morphogen gradient)\n"
            "2. Adult hair follicle stem cell cycling\n"
            "3. Basal cell carcinoma (PTCH1 loss-of-function)\n\n"
            "How does the same pathway serve as a morphogen, a stem cell "
            "activator, and an oncogenic driver?"
        ),
        "ground_truth": {
            "contexts": {
                "neural_tube_patterning": {
                    "role": "ventral morphogen",
                    "key_terms": ["morphogen", "neural tube", "ventral", "SHH gradient", "Patched", "Smoothened", "GLI"],
                    "mechanism": "SHH gradient from notochord/floor plate specifies ventral neural cell fates via concentration-dependent GLI transcription factor activation",
                },
                "hair_follicle_stem_cell": {
                    "role": "stem cell activation signal",
                    "key_terms": ["hair follicle", "stem cell", "anagen", "dermal papilla", "bulge"],
                    "mechanism": "Dermal papilla secretes SHH activating bulge stem cells for hair follicle regeneration during anagen phase",
                },
                "basal_cell_carcinoma": {
                    "role": "oncogenic driver",
                    "key_terms": ["basal cell carcinoma", "BCC", "PTCH1", "vismodegib", "Gorlin syndrome", "constitutive"],
                    "mechanism": "Loss-of-function PTCH1 mutations remove pathway inhibition; constitutive SMO-GLI activation drives BCC; vismodegib (SMO inhibitor) is therapeutic",
                },
            },
            "distinction_key": "Hedgehog is a concentration-dependent morphogen in embryo, a cyclic activation signal in hair follicle, and a constitutively active oncogene when PTCH1 is lost — same pathway, different regulation mode",
        },
    },
    {
        "id": "ba_pc_004",
        "title": "JAK-STAT signaling specificity across cytokine contexts",
        "prompt": (
            "JAK-STAT signaling mediates responses to over 50 cytokines, "
            "but uses different JAK-STAT combinations for different functions.\n\n"
            "Compare JAK-STAT signaling in:\n"
            "1. Type I interferon antiviral response (JAK1/TYK2 → STAT1/2)\n"
            "2. Erythropoietin-driven red blood cell production (JAK2 → STAT5)\n"
            "3. JAK2 V617F myeloproliferative neoplasms\n\n"
            "How does the same pathway architecture support antiviral defense, "
            "erythropoiesis, and oncogenesis through different component usage?"
        ),
        "ground_truth": {
            "contexts": {
                "interferon_antiviral": {
                    "role": "antiviral defense",
                    "key_terms": ["interferon", "IFN", "JAK1", "TYK2", "STAT1", "ISG", "antiviral"],
                    "mechanism": "Type I IFN binds IFNAR → JAK1/TYK2 → STAT1/STAT2 heterodimer → ISGF3 complex → ISG transcription for antiviral state",
                },
                "epo_erythropoiesis": {
                    "role": "red blood cell production",
                    "key_terms": ["erythropoietin", "EPO", "JAK2", "STAT5", "erythropoiesis", "erythroid"],
                    "mechanism": "EPO binds EPOR → JAK2 → STAT5 → erythroid differentiation gene program; essential for red blood cell production",
                },
                "jak2_mpn": {
                    "role": "oncogenic driver",
                    "key_terms": ["JAK2 V617F", "myeloproliferative", "polycythemia vera", "ruxolitinib", "constitutive"],
                    "mechanism": "V617F mutation in JAK2 pseudokinase domain causes constitutive kinase activation independent of EPO; ruxolitinib (JAK1/2 inhibitor) is therapeutic",
                },
            },
            "distinction_key": "JAK-STAT uses different JAK-STAT combinations for different cytokines — antiviral (JAK1/TYK2-STAT1) vs erythropoiesis (JAK2-STAT5) — and V617F converts the hematopoietic arm into an oncogene",
        },
    },
    {
        "id": "ba_pc_005",
        "title": "Hippo/YAP-TAZ in organ size, regeneration, and cancer",
        "prompt": (
            "The Hippo pathway controls organ size by regulating the "
            "transcriptional coactivators YAP and TAZ.\n\n"
            "Compare Hippo/YAP-TAZ function in:\n"
            "1. Contact inhibition and organ size control (homeostasis)\n"
            "2. Liver regeneration after partial hepatectomy\n"
            "3. Metastatic cancer (YAP as oncogene)\n\n"
            "How does the same pathway act as a growth brake, a regeneration "
            "switch, and an oncogenic driver?"
        ),
        "ground_truth": {
            "contexts": {
                "organ_size_control": {
                    "role": "growth suppressor",
                    "key_terms": ["contact inhibition", "organ size", "LATS1/2", "phosphorylation", "cytoplasmic retention"],
                    "mechanism": "At high cell density, Hippo kinase cascade (MST1/2 → LATS1/2) phosphorylates YAP/TAZ → cytoplasmic retention and degradation → growth arrest",
                },
                "liver_regeneration": {
                    "role": "regeneration driver",
                    "key_terms": ["liver regeneration", "hepatectomy", "YAP activation", "hepatocyte proliferation", "organ restoration"],
                    "mechanism": "After partial hepatectomy, Hippo pathway is transiently inactivated; nuclear YAP drives hepatocyte proliferation until organ size is restored, then re-engaged",
                },
                "metastatic_cancer": {
                    "role": "oncogene and metastasis promoter",
                    "key_terms": ["metastasis", "YAP oncogene", "drug resistance", "cancer stem cell", "immune evasion"],
                    "mechanism": "Constitutive nuclear YAP/TAZ in cancer cells drives EMT, drug resistance, cancer stemness, and immune evasion via Hippo pathway inactivation or mechanical cues",
                },
            },
            "distinction_key": "Hippo pathway acts as a rheostat — suppressive at homeostasis, transiently released for regeneration, pathologically disabled in cancer — demonstrating how the same brake mechanism serves opposite roles",
        },
    },
    {
        "id": "ba_pc_006",
        "title": "Autophagy dual role in survival, tumor suppression, and tumor promotion",
        "prompt": (
            "Autophagy is a cellular self-digestion process with paradoxical "
            "roles in cancer biology.\n\n"
            "Compare autophagy function in:\n"
            "1. Nutrient-deprived normal cells (starvation survival)\n"
            "2. Early tumorigenesis (tumor suppression)\n"
            "3. Established/advanced tumors (tumor promotion)\n\n"
            "How does the same degradation pathway suppress cancer initiation "
            "but promote cancer progression?"
        ),
        "ground_truth": {
            "contexts": {
                "starvation_survival": {
                    "role": "cellular survival mechanism",
                    "key_terms": ["starvation", "nutrient deprivation", "autophagosome", "lysosome", "recycling", "ULK1"],
                    "mechanism": "Nutrient deprivation inactivates mTORC1 → ULK1 activation → autophagosome formation → bulk degradation of organelles and proteins for amino acid recycling",
                },
                "tumor_suppression": {
                    "role": "tumor suppressor",
                    "key_terms": ["Beclin-1", "BECN1", "genomic stability", "p62", "damaged organelle", "mitophagy"],
                    "mechanism": "Autophagy removes damaged mitochondria (mitophagy) and aggregated proteins; prevents ROS accumulation and genomic instability; Beclin-1 haploinsufficiency promotes tumorigenesis",
                },
                "tumor_promotion": {
                    "role": "tumor survival mechanism",
                    "key_terms": ["metabolic stress", "hypoxia", "tumor survival", "chemoresistance", "chloroquine"],
                    "mechanism": "Established tumors hijack autophagy to survive metabolic stress, hypoxia, and chemotherapy; autophagy inhibition (chloroquine) can sensitize tumors to treatment",
                },
            },
            "distinction_key": "Autophagy is protective across all contexts but the beneficiary differs — the cell during starvation, the organism during early cancer, and paradoxically the tumor during late cancer",
        },
    },
    {
        "id": "ba_pc_007",
        "title": "cAMP/PKA signaling in heart, fat, and brain",
        "prompt": (
            "The cAMP/PKA second messenger system operates in virtually every "
            "cell type but produces tissue-specific effects.\n\n"
            "Compare cAMP/PKA signaling in:\n"
            "1. Cardiac myocytes (contractility regulation)\n"
            "2. Adipocytes (lipolysis)\n"
            "3. Hippocampal neurons (memory consolidation)\n\n"
            "How does the same second messenger system control heartbeat "
            "strength, fat metabolism, and memory formation?"
        ),
        "ground_truth": {
            "contexts": {
                "cardiac_contractility": {
                    "role": "positive inotrope",
                    "key_terms": ["cardiac", "beta-adrenergic", "contractility", "phospholamban", "calcium", "inotropic"],
                    "mechanism": "Beta-adrenergic stimulation → adenylyl cyclase → cAMP → PKA → phosphorylation of phospholamban and L-type Ca2+ channels → enhanced Ca2+ cycling and contractility",
                },
                "adipocyte_lipolysis": {
                    "role": "fat mobilization",
                    "key_terms": ["lipolysis", "adipocyte", "hormone-sensitive lipase", "HSL", "free fatty acid", "catecholamine"],
                    "mechanism": "Catecholamines activate beta-adrenergic receptors on adipocytes → cAMP/PKA → phosphorylation of HSL and perilipin → triglyceride hydrolysis → FFA release",
                },
                "memory_consolidation": {
                    "role": "memory stabilizer",
                    "key_terms": ["hippocampus", "memory", "CREB", "long-term memory", "synaptic", "consolidation"],
                    "mechanism": "cAMP/PKA in hippocampal neurons activates CREB → gene expression of BDNF and synaptic proteins → synapse stabilization for long-term memory",
                },
            },
            "distinction_key": "Same second messenger (cAMP) and kinase (PKA) control heartbeat strength, fat burning, and memory storage — tissue-specific substrates and transcriptional targets determine the biological outcome",
        },
    },
    {
        "id": "ba_pc_008",
        "title": "NLRP3 inflammasome in defense, atherosclerosis, and gout",
        "prompt": (
            "The NLRP3 inflammasome is an innate immune sensor that responds "
            "to danger signals, but its activation drives both protective and "
            "pathological inflammation.\n\n"
            "Compare NLRP3 inflammasome activation in:\n"
            "1. Acute bacterial infection (innate immune defense)\n"
            "2. Atherosclerosis (cholesterol crystal-driven sterile inflammation)\n"
            "3. Gout (monosodium urate crystal-induced arthritis)\n\n"
            "How does the same innate sensor produce protective immunity, "
            "cardiovascular disease, and joint inflammation?"
        ),
        "ground_truth": {
            "contexts": {
                "microbial_defense": {
                    "role": "pathogen alarm",
                    "key_terms": ["innate immunity", "pathogen", "IL-1beta", "pyroptosis", "caspase-1", "gasdermin D"],
                    "mechanism": "PAMPs/DAMPs activate NLRP3 → ASC speck → caspase-1 activation → IL-1β/IL-18 maturation and gasdermin D-mediated pyroptosis for pathogen clearance",
                },
                "atherosclerosis": {
                    "role": "chronic disease driver",
                    "key_terms": ["atherosclerosis", "cholesterol crystals", "plaque", "canakinumab", "CANTOS", "sterile inflammation"],
                    "mechanism": "Cholesterol crystals in arterial wall activate NLRP3 → chronic IL-1β → endothelial dysfunction and plaque growth; CANTOS trial showed canakinumab reduces cardiovascular events",
                },
                "gout": {
                    "role": "acute crystal arthritis",
                    "key_terms": ["gout", "urate crystals", "monosodium urate", "MSU", "colchicine", "acute arthritis"],
                    "mechanism": "MSU crystals phagocytosed by macrophages activate NLRP3 → massive IL-1β release → neutrophil recruitment → acute joint inflammation; colchicine inhibits inflammasome assembly",
                },
            },
            "distinction_key": "NLRP3 is a crystal/danger sensor in all contexts — microbial products (defense), cholesterol (atherosclerosis), urate (gout) — same innate sensor drives both protective and pathological inflammation",
        },
    },
    {
        "id": "ba_pc_009",
        "title": "Notch signaling in T cells, intestine, and leukemia",
        "prompt": (
            "Notch signaling determines cell fate decisions in multiple "
            "tissues but is also a major oncogene.\n\n"
            "Compare Notch signaling in:\n"
            "1. Thymic T cell lineage commitment (DLL4-Notch1)\n"
            "2. Intestinal secretory vs absorptive cell fate decision\n"
            "3. T-cell acute lymphoblastic leukemia (T-ALL, NOTCH1 mutations)\n\n"
            "How does the same receptor determine immune cell fate, gut "
            "epithelial differentiation, and drive leukemia?"
        ),
        "ground_truth": {
            "contexts": {
                "t_cell_commitment": {
                    "role": "T cell fate determinant",
                    "key_terms": ["thymus", "T cell", "DLL4", "T-lineage", "CD4", "CD8", "commitment"],
                    "mechanism": "Thymic epithelial DLL4 activates Notch1 on progenitors → T-lineage commitment over B-lineage; continued Notch signaling guides CD4/CD8 lineage choice",
                },
                "intestinal_cell_fate": {
                    "role": "absorptive fate maintainer",
                    "key_terms": ["intestinal", "goblet cell", "secretory", "Hes1", "Atoh1", "absorptive"],
                    "mechanism": "Active Notch (Hes1) suppresses Atoh1/Math1 → absorptive enterocyte fate; Notch inhibition de-represses Atoh1 → goblet/Paneth secretory differentiation",
                },
                "t_all_oncogene": {
                    "role": "oncogenic driver",
                    "key_terms": ["T-ALL", "NOTCH1 mutation", "gamma-secretase inhibitor", "gain-of-function", "leukemia"],
                    "mechanism": "Activating NOTCH1 mutations (>50% of T-ALL) cause ligand-independent signaling → constitutive MYC and proliferative program; gamma-secretase inhibitors block Notch cleavage",
                },
            },
            "distinction_key": "Notch determines cell fate by context — T-lineage commitment in thymus, absorptive vs secretory choice in gut, and uncontrolled proliferation when constitutively active in T-ALL",
        },
    },
]

# ============================================================
# dose_response — concentration/duration-dependent opposite effects
# ============================================================

DOSE_RESPONSE_TASKS: list[dict] = [
    {
        "id": "ba_dr_001",
        "title": "ROS: signaling molecule vs oxidative damage",
        "prompt": (
            "Reactive oxygen species (ROS) have concentration-dependent "
            "effects that range from essential signaling to cellular destruction.\n\n"
            "Compare ROS effects at:\n"
            "1. Low physiological concentrations (intracellular signaling)\n"
            "2. High pathological concentrations (oxidative damage)\n"
            "3. Therapeutic exploitation (cancer treatment)\n\n"
            "Why can the same molecules be both essential signals and "
            "cytotoxic agents, and what determines the threshold?"
        ),
        "ground_truth": {
            "contexts": {
                "low_signaling": {
                    "role": "intracellular signaling mediator",
                    "key_terms": ["signaling", "low concentration", "NF-kB", "HIF-1alpha", "redox", "hydrogen peroxide"],
                    "mechanism": "Low H2O2 levels reversibly oxidize cysteine residues in phosphatases (PTP1B) and kinases, modulating NF-κB and HIF-1α signaling pathways",
                },
                "high_damage": {
                    "role": "cytotoxic agent",
                    "key_terms": ["oxidative stress", "DNA damage", "lipid peroxidation", "protein carbonylation", "apoptosis"],
                    "mechanism": "High ROS overwhelm antioxidant defenses (SOD, catalase, glutathione) → oxidize DNA, lipids, and proteins → mitochondrial dysfunction → apoptosis or necrosis",
                },
                "therapeutic": {
                    "role": "cancer treatment mechanism",
                    "key_terms": ["radiation therapy", "chemotherapy", "pro-oxidant", "antioxidant paradox", "cancer therapy"],
                    "mechanism": "Many cancer therapies generate supraphysiological ROS to kill cancer cells; antioxidant supplementation during therapy may be counterproductive",
                },
            },
            "distinction_key": "ROS concentration determines function — physiological levels enable signaling, excessive levels cause damage, and therapeutic strategies exploit high-dose toxicity while cancer cells may adapt through antioxidant upregulation",
        },
    },
    {
        "id": "ba_dr_002",
        "title": "Glucocorticoids: acute anti-inflammatory vs chronic metabolic harm",
        "prompt": (
            "Glucocorticoids are among the most prescribed anti-inflammatory "
            "drugs, yet chronic use causes severe side effects.\n\n"
            "Compare glucocorticoid effects at:\n"
            "1. Acute administration (anti-inflammatory therapy)\n"
            "2. Chronic administration (metabolic and skeletal side effects)\n"
            "3. Physiological circadian cortisol (HPA axis regulation)\n\n"
            "Why does duration of exposure fundamentally change the "
            "risk-benefit profile of the same hormone?"
        ),
        "ground_truth": {
            "contexts": {
                "acute_antiinflammatory": {
                    "role": "potent anti-inflammatory",
                    "key_terms": ["anti-inflammatory", "acute", "dexamethasone", "NF-kB suppression", "cytokine inhibition"],
                    "mechanism": "GR activation suppresses NF-κB and AP-1 → reduces TNF-α, IL-1β, IL-6; induces anti-inflammatory genes (IL-10, annexin A1); rapid clinical benefit",
                },
                "chronic_metabolic": {
                    "role": "metabolic disruptor",
                    "key_terms": ["Cushing", "metabolic syndrome", "hyperglycemia", "osteoporosis", "muscle wasting", "chronic"],
                    "mechanism": "Prolonged GR activation → hepatic gluconeogenesis (hyperglycemia), protein catabolism (muscle wasting), bone resorption (osteoporosis), fat redistribution (central obesity)",
                },
                "hpa_axis_regulation": {
                    "role": "HPA axis regulator",
                    "key_terms": ["HPA axis", "cortisol", "circadian", "negative feedback", "ACTH", "stress response"],
                    "mechanism": "Physiological cortisol follows circadian rhythm and provides negative feedback on CRH/ACTH; chronic exogenous steroids suppress HPA axis → adrenal insufficiency on withdrawal",
                },
            },
            "distinction_key": "Glucocorticoid effects depend critically on duration — acute administration suppresses inflammation therapeutically, while chronic exposure disrupts metabolic homeostasis and HPA axis feedback",
        },
    },
    {
        "id": "ba_dr_003",
        "title": "Doxorubicin: immunogenic cell death vs cytotoxicity vs cardiotoxicity",
        "prompt": (
            "Doxorubicin is a cornerstone chemotherapeutic agent, but its "
            "effects change dramatically with dose.\n\n"
            "Compare doxorubicin effects at:\n"
            "1. Low dose (immunogenic cell death)\n"
            "2. Standard therapeutic dose (direct cytotoxicity)\n"
            "3. Cumulative high dose (cardiotoxicity)\n\n"
            "How does the same drug activate anti-tumor immunity, kill "
            "cancer cells, and damage the heart through distinct mechanisms?"
        ),
        "ground_truth": {
            "contexts": {
                "low_dose_icd": {
                    "role": "immune activator",
                    "key_terms": ["immunogenic cell death", "ICD", "calreticulin", "HMGB1", "ATP release", "dendritic cell"],
                    "mechanism": "Low-dose doxorubicin induces immunogenic cell death — calreticulin exposure, HMGB1 and ATP release activate dendritic cells, triggering anti-tumor immunity",
                },
                "standard_cytotoxicity": {
                    "role": "topoisomerase II poison",
                    "key_terms": ["topoisomerase II", "DNA intercalation", "double strand break", "cell cycle arrest", "anthracycline"],
                    "mechanism": "Doxorubicin intercalates DNA and poisons topoisomerase II → trapped cleavage complexes → double-strand breaks → G2/M arrest and apoptosis",
                },
                "cumulative_cardiotoxicity": {
                    "role": "cardiotoxin",
                    "key_terms": ["cardiotoxicity", "cardiomyopathy", "cumulative dose", "topoisomerase IIbeta", "heart failure", "dexrazoxane"],
                    "mechanism": "Cumulative doxorubicin targets topoisomerase IIβ in cardiomyocytes → mitochondrial dysfunction, ROS, iron-mediated damage → irreversible cardiomyopathy; dexrazoxane is cardioprotective",
                },
            },
            "distinction_key": "Doxorubicin dose determines mechanism and target — low doses activate anti-tumor immunity, standard doses kill via DNA damage, cumulative doses cause irreversible cardiac damage through topoisomerase IIβ",
        },
    },
    {
        "id": "ba_dr_004",
        "title": "Oxygen: essential metabolite vs hypoxia signal vs toxic oxidant",
        "prompt": (
            "Oxygen concentration creates three distinct biological states "
            "with opposing consequences.\n\n"
            "Compare oxygen effects at:\n"
            "1. Normoxia (aerobic metabolism)\n"
            "2. Hypoxia (HIF-mediated adaptation)\n"
            "3. Hyperoxia (oxygen toxicity)\n\n"
            "How does the same molecule serve as essential substrate, "
            "adaptive trigger, and toxic agent?"
        ),
        "ground_truth": {
            "contexts": {
                "normoxia": {
                    "role": "terminal electron acceptor",
                    "key_terms": ["aerobic", "oxidative phosphorylation", "mitochondria", "electron transport chain", "ATP"],
                    "mechanism": "O₂ serves as terminal electron acceptor in mitochondrial ETC → efficient ATP production via oxidative phosphorylation",
                },
                "hypoxia": {
                    "role": "angiogenesis and metabolic adaptation trigger",
                    "key_terms": ["hypoxia", "HIF-1alpha", "angiogenesis", "VEGF", "glycolytic switch", "erythropoietin"],
                    "mechanism": "Low O₂ stabilizes HIF-1α (normally degraded by PHD/VHL) → VEGF (angiogenesis), EPO (erythropoiesis), glycolytic enzymes for metabolic adaptation",
                },
                "hyperoxia": {
                    "role": "tissue-damaging oxidant",
                    "key_terms": ["hyperoxia", "oxygen toxicity", "bronchopulmonary dysplasia", "retinopathy of prematurity", "neonatal"],
                    "mechanism": "Supraphysiological O₂ → excess ROS → pulmonary epithelial damage (BPD in neonates), retinal vascular injury (ROP), CNS toxicity",
                },
            },
            "distinction_key": "Oxygen concentration creates three biological states — normoxia enables metabolism, hypoxia triggers adaptive gene programs, hyperoxia causes oxidative tissue damage — the same molecule is essential, adaptive trigger, and toxin",
        },
    },
    {
        "id": "ba_dr_005",
        "title": "Nitric oxide: vasodilator vs antimicrobial vs tissue toxin",
        "prompt": (
            "Nitric oxide (NO) is produced by three NOS isoforms at vastly "
            "different concentrations with distinct biological effects.\n\n"
            "Compare NO effects at:\n"
            "1. Nanomolar (eNOS-derived, vascular signaling)\n"
            "2. Micromolar (iNOS-derived, immune defense)\n"
            "3. Pathological excess (septic shock, tissue damage)\n\n"
            "How does concentration span three orders of magnitude with "
            "completely different outcomes?"
        ),
        "ground_truth": {
            "contexts": {
                "vasodilation": {
                    "role": "vasodilator and signaling molecule",
                    "key_terms": ["vasodilation", "eNOS", "endothelial", "guanylyl cyclase", "cGMP", "smooth muscle"],
                    "mechanism": "Endothelial eNOS produces nanomolar NO → activates soluble guanylyl cyclase → cGMP → vascular smooth muscle relaxation → vasodilation",
                },
                "immune_defense": {
                    "role": "antimicrobial effector",
                    "key_terms": ["iNOS", "macrophage", "antimicrobial", "peroxynitrite", "innate immunity", "microbicidal"],
                    "mechanism": "Activated macrophages express iNOS → micromolar NO → reacts with superoxide to form peroxynitrite → direct microbial killing",
                },
                "tissue_damage": {
                    "role": "cytotoxic mediator",
                    "key_terms": ["nitrosative stress", "tissue damage", "S-nitrosylation", "septic shock", "hypotension"],
                    "mechanism": "Excessive iNOS-derived NO causes systemic vasodilation (septic shock), protein S-nitrosylation dysfunction, mitochondrial inhibition, and DNA damage",
                },
            },
            "distinction_key": "NO concentration spans three orders of magnitude — nanomolar eNOS signaling, micromolar iNOS antimicrobial, pathological excess tissue destruction — source enzyme and amount determine benefit vs harm",
        },
    },
    {
        "id": "ba_dr_006",
        "title": "Retinoic acid: morphogen vs teratogen vs cancer therapy",
        "prompt": (
            "Retinoic acid (RA) has paradoxical roles — it patterns the "
            "embryo, causes birth defects, and cures a specific leukemia.\n\n"
            "Compare retinoic acid effects in:\n"
            "1. Physiological embryonic development (morphogen gradient)\n"
            "2. Excess during pregnancy (teratogenicity — isotretinoin/Accutane)\n"
            "3. Therapeutic dose in acute promyelocytic leukemia (ATRA therapy)\n\n"
            "How does the same vitamin A metabolite serve as morphogen, "
            "teratogen, and cancer cure?"
        ),
        "ground_truth": {
            "contexts": {
                "embryonic_morphogen": {
                    "role": "morphogen and differentiation signal",
                    "key_terms": ["morphogen", "embryonic", "differentiation", "HOX genes", "RAR/RXR", "anterior-posterior"],
                    "mechanism": "RA gradient activates RAR/RXR nuclear receptors → sequential HOX gene activation → body axis patterning and organ specification",
                },
                "teratogenicity": {
                    "role": "teratogen",
                    "key_terms": ["teratogen", "birth defect", "Accutane", "isotretinoin", "craniofacial", "cardiac malformation"],
                    "mechanism": "Excess RA during pregnancy disrupts morphogen gradients → craniofacial, cardiac, and neural tube defects; isotretinoin is a documented human teratogen",
                },
                "apl_therapy": {
                    "role": "cancer differentiation agent",
                    "key_terms": ["APL", "acute promyelocytic leukemia", "ATRA", "PML-RARA", "differentiation therapy", "all-trans retinoic acid"],
                    "mechanism": "PML-RARα fusion blocks myeloid differentiation; pharmacological ATRA overcomes the block → blast differentiation into mature granulocytes → remission",
                },
            },
            "distinction_key": "Retinoic acid instructs differentiation in all three contexts — physiological levels pattern the embryo, excess disrupts gradients causing defects, and therapeutic doses exploit differentiation to cure APL",
        },
    },
    {
        "id": "ba_dr_007",
        "title": "Radiation: adaptive response vs cancer therapy vs carcinogenesis",
        "prompt": (
            "Ionizing radiation has dose-dependent biological effects that "
            "span from potential adaptation to curative therapy to cancer "
            "causation.\n\n"
            "Compare radiation biology at:\n"
            "1. Low dose (adaptive response hypothesis vs LNT model)\n"
            "2. Therapeutic fractionated dose (cancer radiotherapy)\n"
            "3. Chronic low-dose exposure (carcinogenesis risk)\n\n"
            "Explain the scientific debate between the linear no-threshold "
            "(LNT) model and radiation hormesis. How does fractionation "
            "exploit the therapeutic window?"
        ),
        "ground_truth": {
            "contexts": {
                "low_dose_debate": {
                    "role": "potential adaptive response (debated)",
                    "key_terms": ["low dose", "adaptive response", "hormesis", "linear no-threshold", "LNT", "DNA repair"],
                    "mechanism": "Some evidence suggests low-dose radiation upregulates DNA repair and antioxidant defenses (adaptive response); LNT model assumes no safe threshold — scientifically debated",
                },
                "therapeutic_dose": {
                    "role": "curative cancer therapy",
                    "key_terms": ["radiotherapy", "double strand break", "fractionation", "tumor control", "therapeutic window", "Gray"],
                    "mechanism": "Therapeutic doses (2 Gy fractions) cause lethal DSBs; fractionation allows normal tissue recovery while accumulating tumor damage; differential repair capacity is the therapeutic window",
                },
                "chronic_carcinogenesis": {
                    "role": "carcinogen",
                    "key_terms": ["carcinogenesis", "stochastic", "latency period", "Hiroshima", "Chernobyl", "occupational exposure"],
                    "mechanism": "Chronic low-dose exposure accumulates sublethal mutations → stochastic cancer risk increase with years-to-decades latency; epidemiological evidence from atomic bomb survivors",
                },
            },
            "distinction_key": "Radiation biology spans three regimes — acute low-dose effects (debated hormesis vs LNT), therapeutic fractionation (curative), chronic accumulation (carcinogenic) — with fundamental scientific disagreement about the lowest dose regime",
        },
    },
    {
        "id": "ba_dr_008",
        "title": "Iron: essential nutrient vs Fenton toxin vs ferroptosis executor",
        "prompt": (
            "Iron is essential for life but toxic in excess, and recently "
            "recognized as the driver of a novel cell death pathway.\n\n"
            "Compare iron biology at:\n"
            "1. Physiological levels (essential cofactor for hemoglobin, cytochromes)\n"
            "2. Iron overload (Fenton reaction-mediated toxicity)\n"
            "3. Ferroptosis (iron-dependent regulated cell death)\n\n"
            "How does the same metal serve as essential nutrient, oxidative "
            "toxin, and executor of a distinct cell death pathway?"
        ),
        "ground_truth": {
            "contexts": {
                "essential_nutrient": {
                    "role": "essential micronutrient",
                    "key_terms": ["hemoglobin", "cytochrome", "iron-sulfur cluster", "essential", "heme", "oxygen transport"],
                    "mechanism": "Iron is essential for heme synthesis (hemoglobin), cytochrome electron transport, and iron-sulfur cluster enzymes; deficiency causes anemia",
                },
                "fenton_toxicity": {
                    "role": "pro-oxidant toxin",
                    "key_terms": ["iron overload", "Fenton reaction", "hemochromatosis", "hydroxyl radical", "liver fibrosis", "ferritin"],
                    "mechanism": "Excess free Fe2+ catalyzes Fenton reaction (H₂O₂ → OH•) generating hydroxyl radicals → oxidative damage to liver, heart, pancreas; hemochromatosis is genetic iron overload",
                },
                "ferroptosis": {
                    "role": "ferroptosis executor",
                    "key_terms": ["ferroptosis", "GPX4", "lipid peroxidation", "iron-dependent", "regulated cell death", "erastin"],
                    "mechanism": "Iron-dependent lipid peroxidation drives ferroptosis when GPX4 is inhibited; GPX4 inhibition or cystine import blockade (erastin) can selectively kill certain tumor cells",
                },
            },
            "distinction_key": "Iron redox chemistry underlies all three roles — oxygen transport at physiological levels, tissue damage via Fenton reaction at excess, and a regulated cell death pathway (ferroptosis) exploitable in cancer therapy",
        },
    },
    {
        "id": "ba_dr_009",
        "title": "Rapamycin: mTORC1-selective vs mTORC1+2 dual inhibition",
        "prompt": (
            "Rapamycin (sirolimus) has dose-dependent and duration-dependent "
            "effects due to differential inhibition of mTOR complexes.\n\n"
            "Compare rapamycin effects at:\n"
            "1. Low dose / short term (selective mTORC1 inhibition — transplant immunosuppression)\n"
            "2. High dose / chronic (mTORC1 + mTORC2 dual inhibition — metabolic side effects)\n"
            "3. Anti-aging research context (lifespan extension in model organisms)\n\n"
            "How does the same drug produce immunosuppression, metabolic "
            "harm, and lifespan extension depending on dosing regimen?"
        ),
        "ground_truth": {
            "contexts": {
                "mtorc1_selective": {
                    "role": "transplant immunosuppressant",
                    "key_terms": ["mTORC1", "immunosuppression", "transplant", "FKBP12", "T cell proliferation", "selective"],
                    "mechanism": "Low-dose rapamycin binds FKBP12 → selectively inhibits mTORC1 → blocks IL-2-driven T cell proliferation; mTORC2 largely spared at low doses",
                },
                "mtorc1_plus_mtorc2": {
                    "role": "metabolic disruptor",
                    "key_terms": ["mTORC2", "insulin resistance", "glucose intolerance", "AKT inhibition", "metabolic", "chronic"],
                    "mechanism": "Chronic or high-dose rapamycin disrupts mTORC2 assembly → impaired AKT-Ser473 phosphorylation → insulin resistance, glucose intolerance, dyslipidemia",
                },
                "anti_aging": {
                    "role": "lifespan extender in model organisms",
                    "key_terms": ["anti-aging", "lifespan extension", "ITP", "autophagy induction", "geroprotector", "senescence"],
                    "mechanism": "Rapamycin extends lifespan in mice (NIA ITP), worms, and flies — likely via mTORC1 inhibition → enhanced autophagy, reduced senescent cell burden; human translation uncertain",
                },
            },
            "distinction_key": "Rapamycin effects depend on dose and duration — selective mTORC1 inhibition (immunosuppression, potential anti-aging) versus mTORC1+mTORC2 dual inhibition (metabolic harm) — same drug targets different complexes at different exposures",
        },
    },
]

# ============================================================
# temporal_shift — developmental stage changes function
# ============================================================

TEMPORAL_SHIFT_TASKS: list[dict] = [
    {
        "id": "ba_ts_001",
        "title": "EGFR signaling: embryonic organogenesis to adult cancer",
        "prompt": (
            "EGFR (Epidermal Growth Factor Receptor) plays different roles "
            "at different life stages.\n\n"
            "Compare EGFR function in:\n"
            "1. Embryonic epithelial organ development (branching morphogenesis)\n"
            "2. Adult wound healing (re-epithelialization)\n"
            "3. Non-small cell lung cancer (EGFR-mutant oncogene)\n\n"
            "How does the same receptor transition from developmental "
            "orchestrator to tissue repair mediator to cancer driver?"
        ),
        "ground_truth": {
            "contexts": {
                "embryonic_development": {
                    "role": "branching morphogenesis regulator",
                    "key_terms": ["branching morphogenesis", "lung development", "embryonic", "epithelial", "organogenesis"],
                    "mechanism": "EGFR signaling drives branching morphogenesis in developing lung, mammary gland, and kidney; EGF family ligands coordinate proliferation and differentiation",
                },
                "wound_healing": {
                    "role": "re-epithelialization promoter",
                    "key_terms": ["wound healing", "re-epithelialization", "keratinocyte migration", "tissue repair", "EGF"],
                    "mechanism": "EGF activates EGFR in wound-edge keratinocytes → MAPK and PI3K signaling → cell migration and proliferation for wound closure",
                },
                "nsclc_oncogene": {
                    "role": "oncogenic driver",
                    "key_terms": ["NSCLC", "EGFR mutation", "L858R", "exon 19 deletion", "erlotinib", "osimertinib"],
                    "mechanism": "Activating EGFR mutations (L858R, exon 19 deletion) cause ligand-independent constitutive signaling → uncontrolled proliferation; TKIs (erlotinib, osimertinib) are targeted therapy",
                },
            },
            "distinction_key": "EGFR transitions from orchestrating organ development to maintaining tissue repair to driving cancer when mutationally activated — the same receptor serves constructive and destructive roles depending on life stage and mutation status",
        },
    },
    {
        "id": "ba_ts_002",
        "title": "Cellular senescence: developmental tool to aging driver",
        "prompt": (
            "Cellular senescence has been discovered in three temporal "
            "contexts with opposing consequences.\n\n"
            "Compare senescence in:\n"
            "1. Embryonic development (developmental senescence)\n"
            "2. Adult life (oncogene-induced senescence as tumor suppressor)\n"
            "3. Aging (senescent cell accumulation and SASP)\n\n"
            "How does the same cellular state shift from constructive "
            "(morphogenesis) to protective (tumor suppression) to "
            "destructive (aging) across the lifespan?"
        ),
        "ground_truth": {
            "contexts": {
                "developmental_senescence": {
                    "role": "tissue morphogenesis participant",
                    "key_terms": ["developmental senescence", "embryonic", "AER", "limb patterning", "mesonephros", "p21"],
                    "mechanism": "Programmed senescence in embryonic structures (apical ectodermal ridge, mesonephros) contributes to tissue remodeling; p21-dependent but p53-independent",
                },
                "tumor_suppression": {
                    "role": "anti-cancer barrier",
                    "key_terms": ["oncogene-induced senescence", "OIS", "RAS", "tumor suppression", "cell cycle arrest", "p16"],
                    "mechanism": "Oncogenic stress (e.g., RAS activation) triggers permanent cell cycle arrest via p53-p21 and p16-Rb pathways; seen in human nevi (BRAF V600E-induced senescence)",
                },
                "aging_sasp": {
                    "role": "aging driver",
                    "key_terms": ["SASP", "senescence-associated secretory phenotype", "aging", "senolytics", "chronic inflammation", "tissue dysfunction"],
                    "mechanism": "Accumulated senescent cells secrete SASP factors (IL-6, IL-8, MMPs) → chronic inflammation, tissue dysfunction, stem cell exhaustion; senolytics can improve healthspan in mice",
                },
            },
            "distinction_key": "Senescence is beneficial at two life stages (embryonic morphogenesis and adult tumor suppression) but harmful when senescent cells accumulate with age — the same cellular state shifts from constructive to destructive over the lifespan",
        },
    },
    {
        "id": "ba_ts_003",
        "title": "SOX9: cartilage development to adult stem cells to cancer",
        "prompt": (
            "SOX9 is a master transcription factor whose role evolves "
            "across developmental stages.\n\n"
            "Compare SOX9 function in:\n"
            "1. Embryonic development (chondrogenesis and sex determination)\n"
            "2. Adult tissue homeostasis (stem/progenitor cell maintenance)\n"
            "3. Cancer (cancer stem cell marker and tumor promoter)\n\n"
            "How does the same transcription factor transition from "
            "developmental master regulator to cancer stemness driver?"
        ),
        "ground_truth": {
            "contexts": {
                "embryonic_development": {
                    "role": "master regulator of chondrogenesis and sex determination",
                    "key_terms": ["chondrogenesis", "cartilage", "sex determination", "SRY", "testis", "campomelic dysplasia"],
                    "mechanism": "SOX9 activates COL2A1 and aggrecan for cartilage formation; downstream of SRY for male gonad development; haploinsufficiency causes campomelic dysplasia with sex reversal",
                },
                "adult_stem_cell": {
                    "role": "stem/progenitor cell marker",
                    "key_terms": ["stem cell", "hair follicle", "intestinal progenitor", "pancreatic progenitor", "adult tissue"],
                    "mechanism": "SOX9 marks and maintains stem/progenitor populations in adult intestine, hair follicle bulge, and pancreatic ducts; essential for tissue homeostasis",
                },
                "cancer_stemness": {
                    "role": "cancer stem cell promoter",
                    "key_terms": ["colorectal cancer", "pancreatic cancer", "cancer stem cell", "Wnt target", "tumor heterogeneity"],
                    "mechanism": "SOX9 overexpression in CRC and pancreatic cancer drives cancer stemness and tumor heterogeneity; acts as Wnt target gene and promotes chemoresistance",
                },
            },
            "distinction_key": "SOX9 transitions from essential developmental regulator (skeleton, gonads) to adult stem cell maintainer to cancer stem cell driver — retaining its core stemness function while the context shifts from constructive to pathological",
        },
    },
    {
        "id": "ba_ts_004",
        "title": "FGF family: embryonic induction to postnatal growth to adult pathology",
        "prompt": (
            "The FGF family contains 22 members with temporally distinct "
            "roles. Different FGF subfamily members dominate at different "
            "life stages.\n\n"
            "Compare FGF signaling in:\n"
            "1. Embryonic gastrulation — FGF4/FGF8 (mesoderm induction)\n"
            "2. Postnatal organ development — FGF10 (branching morphogenesis)\n"
            "3. Adult disease — FGF23 (chronic kidney disease) and FGF2 (fibrosis)\n\n"
            "How do different members of the same growth factor family "
            "serve construction in embryo and destruction in adult disease?"
        ),
        "ground_truth": {
            "contexts": {
                "embryonic_induction": {
                    "role": "mesoderm inducer",
                    "key_terms": ["mesoderm", "gastrulation", "FGF4", "FGF8", "primitive streak", "embryonic induction"],
                    "mechanism": "FGF4/FGF8 from primitive streak induce mesoderm formation; FGF-MAPK/ERK signaling essential for mesoderm specification and posterior neural patterning",
                },
                "postnatal_growth": {
                    "role": "branching morphogenesis and growth",
                    "key_terms": ["FGF10", "limb bud", "lung branching", "FGFR2b", "Apert syndrome", "growth"],
                    "mechanism": "FGF10 mesenchyme-to-epithelium signals via FGFR2b → lung branching morphogenesis; FGF10-FGF8 limb bud feedback loop; FGFR2 gain-of-function causes Apert syndrome",
                },
                "adult_pathology": {
                    "role": "fibrosis and disease driver",
                    "key_terms": ["fibrosis", "FGF23", "chronic kidney disease", "cardiac hypertrophy", "FGF2", "pathological"],
                    "mechanism": "FGF23 elevation in CKD drives cardiac hypertrophy; FGF2 overexpression promotes fibrosis in chronic injury; same growth factor family shifts from developmental to pathological role",
                },
            },
            "distinction_key": "FGF family spans 22 members with temporally distinct roles — mesoderm induction in embryo (FGF4/8), organ growth postnatally (FGF10), and disease-associated remodeling in adults (FGF23/FGF2) — construction then destruction",
        },
    },
    {
        "id": "ba_ts_005",
        "title": "Hematopoietic stem cells across lifespan",
        "prompt": (
            "Hematopoietic stem cells (HSCs) exhibit fundamentally "
            "different behaviors at different life stages.\n\n"
            "Compare HSC biology in:\n"
            "1. Fetal liver hematopoiesis (expansion phase)\n"
            "2. Adult bone marrow (quiescence and homeostasis)\n"
            "3. Aging (clonal hematopoiesis — CHIP)\n\n"
            "How does the same stem cell type switch from active expansion "
            "to protective quiescence to pathological clonal dominance?"
        ),
        "ground_truth": {
            "contexts": {
                "fetal_expansion": {
                    "role": "developmental blood formation",
                    "key_terms": ["fetal liver", "HSC expansion", "definitive hematopoiesis", "yolk sac", "AGM", "cycling"],
                    "mechanism": "Definitive HSCs from AGM colonize fetal liver → massive expansion with balanced multilineage output; fetal HSCs are actively cycling unlike adult HSCs",
                },
                "adult_quiescence": {
                    "role": "quiescent reserve",
                    "key_terms": ["bone marrow", "quiescence", "niche", "self-renewal", "dormancy", "homeostasis"],
                    "mechanism": "Adult HSCs reside in bone marrow niches in deep quiescence (G0); activated only on demand; quiescence protects from replication-associated DNA damage and exhaustion",
                },
                "aging_chip": {
                    "role": "clonal expansion and disease precursor",
                    "key_terms": ["clonal hematopoiesis", "CHIP", "DNMT3A", "TET2", "myeloid bias", "cardiovascular risk"],
                    "mechanism": "Aging HSCs accumulate somatic mutations (DNMT3A, TET2); mutant clones expand (CHIP) → myeloid-biased output, reduced lymphopoiesis, increased cardiovascular and MDS/AML risk",
                },
            },
            "distinction_key": "HSC behavior fundamentally changes across life — active expansion in fetal liver, protective quiescence in adult bone marrow, clonal dominance with myeloid bias in aging — opposite proliferative strategies at different life stages",
        },
    },
    {
        "id": "ba_ts_006",
        "title": "IGF-1: fetal growth factor to aging trade-off",
        "prompt": (
            "IGF-1 (Insulin-like Growth Factor 1) is essential for early "
            "life but may be harmful in later life.\n\n"
            "Compare IGF-1 effects at:\n"
            "1. Fetal development (essential growth)\n"
            "2. Puberty (GH-IGF-1 axis growth spurt)\n"
            "3. Post-reproductive life (cancer risk and longevity trade-off)\n\n"
            "How does IGF-1 illustrate the concept of antagonistic "
            "pleiotropy — beneficial early, harmful late?"
        ),
        "ground_truth": {
            "contexts": {
                "fetal_growth": {
                    "role": "essential fetal growth factor",
                    "key_terms": ["fetal growth", "birth weight", "IGF-1R", "intrauterine growth restriction", "essential"],
                    "mechanism": "IGF-1/IGF-1R signaling is essential for fetal growth; IGF-1 knockout mice are 60% smaller at birth; human IGF-1R mutations cause severe growth restriction",
                },
                "puberty_growth": {
                    "role": "growth hormone mediator",
                    "key_terms": ["growth hormone", "puberty", "growth spurt", "GH-IGF-1 axis", "Laron syndrome", "bone growth"],
                    "mechanism": "GH → hepatic IGF-1 secretion → growth plate chondrocyte proliferation; GH-IGF-1 axis peaks during puberty; Laron syndrome (low IGF-1) causes dwarfism",
                },
                "aging_tradeoff": {
                    "role": "aging accelerator and cancer risk factor",
                    "key_terms": ["longevity", "cancer risk", "daf-2", "insulin/IGF signaling", "caloric restriction", "antagonistic pleiotropy"],
                    "mechanism": "Reduced IGF-1 signaling extends lifespan in worms (daf-2), flies, and mice; Laron patients show reduced cancer; high IGF-1 associated with cancer risk — growth promotion becomes harmful post-reproduction",
                },
            },
            "distinction_key": "IGF-1 demonstrates antagonistic pleiotropy — essential for fetal development, beneficial during growth, but potentially harmful during aging — natural selection favors early growth at the cost of late-life disease",
        },
    },
    {
        "id": "ba_ts_007",
        "title": "EMT: embryonic program to wound healing to cancer metastasis",
        "prompt": (
            "Epithelial-mesenchymal transition (EMT) is an ancient "
            "developmental program reactivated in adult contexts.\n\n"
            "Compare EMT in:\n"
            "1. Embryonic neural crest migration\n"
            "2. Adult wound healing (partial, transient EMT)\n"
            "3. Cancer metastasis (pathological EMT reactivation)\n\n"
            "How is the same cellular program regulated in development, "
            "transiently used in repair, and pathologically hijacked in cancer?"
        ),
        "ground_truth": {
            "contexts": {
                "neural_crest_migration": {
                    "role": "essential developmental program",
                    "key_terms": ["neural crest", "migration", "delamination", "SNAIL", "embryonic", "craniofacial"],
                    "mechanism": "Neural crest cells undergo EMT (E-cadherin loss, SNAIL/SLUG activation) → delamination from neural tube → migration → craniofacial structures, peripheral neurons, melanocytes",
                },
                "wound_healing": {
                    "role": "transient repair response",
                    "key_terms": ["wound healing", "partial EMT", "keratinocyte migration", "re-epithelialization", "transient", "reversible"],
                    "mechanism": "Wound-edge keratinocytes undergo partial EMT → increased motility for wound closure → MET restores epithelial integrity; tightly regulated and reversible",
                },
                "cancer_metastasis": {
                    "role": "metastasis driver",
                    "key_terms": ["metastasis", "invasion", "E-cadherin loss", "circulating tumor cell", "drug resistance", "partial EMT"],
                    "mechanism": "Cancer cells reactivate embryonic EMT program → invasion, intravasation; partial EMT (hybrid state) may be most metastatic; confers chemoresistance",
                },
            },
            "distinction_key": "EMT is the same cellular program at three life stages — essential for embryonic morphogenesis, transiently reactivated for wound repair, pathologically co-opted for metastasis — regulation vs deregulation determines outcome",
        },
    },
    {
        "id": "ba_ts_008",
        "title": "Myelination: postnatal development to adult plasticity to MS failure",
        "prompt": (
            "CNS myelination has distinct phases across life with "
            "dramatically different outcomes.\n\n"
            "Compare myelination in:\n"
            "1. Postnatal CNS development (oligodendrocyte myelination)\n"
            "2. Adult brain (activity-dependent myelin plasticity)\n"
            "3. Multiple sclerosis (demyelination and remyelination failure)\n\n"
            "Why does the same cell lineage (OPC → oligodendrocyte) "
            "succeed in development but fail in disease?"
        ),
        "ground_truth": {
            "contexts": {
                "postnatal_myelination": {
                    "role": "neural circuit maturation",
                    "key_terms": ["myelination", "oligodendrocyte", "postnatal", "white matter", "conduction velocity", "myelin basic protein"],
                    "mechanism": "OPCs differentiate and ensheath axons with myelin during postnatal CNS development → saltatory conduction → rapid neural circuit function",
                },
                "adult_plasticity": {
                    "role": "activity-dependent adaptation",
                    "key_terms": ["myelin plasticity", "adaptive myelination", "adult OPC", "learning", "motor skill"],
                    "mechanism": "Adult OPCs continuously generate new oligodendrocytes; myelin remodeling occurs with learning and motor skill acquisition (adaptive myelination)",
                },
                "ms_failure": {
                    "role": "pathological target and failed repair",
                    "key_terms": ["multiple sclerosis", "MS", "demyelination", "remyelination failure", "OPC differentiation block"],
                    "mechanism": "In MS, autoimmune attack destroys myelin; OPCs are present in lesions but fail to differentiate → progressive axonal degeneration; promoting OPC differentiation is therapeutic goal",
                },
            },
            "distinction_key": "Myelination transitions from robust developmental program to activity-dependent plasticity to failed repair in MS — the same OPC-to-oligodendrocyte lineage succeeds in development but fails in disease",
        },
    },
    {
        "id": "ba_ts_009",
        "title": "Apoptosis: digit sculpting to immune homeostasis to neurodegeneration",
        "prompt": (
            "Apoptosis (programmed cell death) uses the same core caspase "
            "machinery for opposing purposes at different life stages.\n\n"
            "Compare apoptosis in:\n"
            "1. Embryonic interdigital tissue removal (digit separation)\n"
            "2. Adult immune system (activation-induced cell death — AICD)\n"
            "3. Parkinson's disease (dopaminergic neuron loss)\n\n"
            "How does the same death program serve morphogenesis, immune "
            "homeostasis, and pathological neurodegeneration?"
        ),
        "ground_truth": {
            "contexts": {
                "interdigital_morphogenesis": {
                    "role": "morphogenetic sculptor",
                    "key_terms": ["interdigital", "digit separation", "BMP", "morphogenesis", "programmed cell death", "syndactyly"],
                    "mechanism": "BMP signaling triggers apoptosis in interdigital mesenchyme → digit separation; failure causes syndactyly (webbed digits); apoptosis sculpts limb morphology",
                },
                "immune_aicd": {
                    "role": "immune homeostasis regulator",
                    "key_terms": ["AICD", "activation-induced cell death", "FAS", "FASL", "T cell contraction", "ALPS"],
                    "mechanism": "After immune response, activated T cells upregulate FAS/FASL → fratricidal apoptosis → clonal contraction; prevents autoimmunity; failure causes ALPS",
                },
                "parkinsons_neurodegeneration": {
                    "role": "pathological neuron loss",
                    "key_terms": ["Parkinson", "dopaminergic neuron", "substantia nigra", "alpha-synuclein", "neurodegeneration"],
                    "mechanism": "Progressive dopaminergic neuron loss in substantia nigra via apoptosis — triggered by alpha-synuclein aggregation, mitochondrial dysfunction, oxidative stress",
                },
            },
            "distinction_key": "Apoptosis uses the same caspase cascade constructively (digit formation), homeostatically (immune contraction), and destructively (neurodegeneration) — the same death machinery serves life at different temporal and tissue contexts",
        },
    },
]

# ============================================================
# species_translation — model organism to human translational gaps
# ============================================================

SPECIES_TRANSLATION_TASKS: list[dict] = [
    {
        "id": "ba_st_001",
        "title": "Mouse IL-8 absence: neutrophil biology translational gap",
        "prompt": (
            "Mice lack a functional IL-8 (CXCL8) ortholog, which is the "
            "primary neutrophil chemoattractant in humans.\n\n"
            "Compare:\n"
            "1. Mouse neutrophil recruitment (KC/CXCL1, MIP-2/CXCL2)\n"
            "2. Human neutrophil recruitment (IL-8/CXCL8 via CXCR1/CXCR2)\n"
            "3. Translational implications for inflammation research\n\n"
            "How does this chemokine gap affect the validity of mouse "
            "inflammation models for human therapeutic development?"
        ),
        "ground_truth": {
            "contexts": {
                "mouse_neutrophils": {
                    "role": "IL-8-independent neutrophil recruitment",
                    "key_terms": ["CXCL15", "CXCL1", "KC", "MIP-2", "CXCL2", "mouse", "partial homolog"],
                    "mechanism": "Mice lack IL-8; neutrophil recruitment relies on KC (CXCL1) and MIP-2 (CXCL2) which are not functional equivalents of human IL-8",
                },
                "human_neutrophils": {
                    "role": "IL-8-dependent neutrophil recruiter",
                    "key_terms": ["IL-8", "CXCL8", "neutrophil", "CXCR1", "CXCR2", "inflammation", "human"],
                    "mechanism": "IL-8 (CXCL8) is the primary neutrophil chemoattractant in humans; binds CXCR1/CXCR2; critical in acute inflammation, wound healing, and tumor microenvironment",
                },
                "translational_gap": {
                    "role": "study limitation",
                    "key_terms": ["translational failure", "humanized mouse", "anti-IL-8", "clinical trial", "preclinical model"],
                    "mechanism": "Mouse models cannot evaluate IL-8/CXCR1 biology; anti-IL-8 strategies cannot be tested in standard mice; requires humanized models or human tissue systems",
                },
            },
            "distinction_key": "The absence of functional IL-8 in mice means neutrophil-dependent inflammatory processes studied in mouse models may not reflect human biology — a fundamental chemokine gap that has misled therapeutic development",
        },
    },
    {
        "id": "ba_st_002",
        "title": "Telomerase expression: mouse constitutive vs human repressed",
        "prompt": (
            "Mouse and human cells have fundamentally different telomerase "
            "regulation, affecting cancer biology research.\n\n"
            "Compare:\n"
            "1. Mouse telomerase (constitutive somatic expression, long telomeres)\n"
            "2. Human telomerase (somatic repression, Hayflick limit)\n"
            "3. Impact on cancer model validity\n\n"
            "How does this difference affect the interpretation of mouse "
            "cancer models and their translatability to human oncology?"
        ),
        "ground_truth": {
            "contexts": {
                "mouse_telomerase": {
                    "role": "naturally active in most tissues",
                    "key_terms": ["constitutive", "mouse telomerase", "mTERT", "long telomeres", "somatic expression", "inbred"],
                    "mechanism": "Laboratory mice express telomerase in most somatic tissues with very long telomeres (50-150 kb vs human 5-15 kb); inbred strains maintain telomere length",
                },
                "human_telomerase": {
                    "role": "repressed in somatic cells",
                    "key_terms": ["hTERT silencing", "somatic repression", "Hayflick limit", "replicative senescence", "telomere shortening"],
                    "mechanism": "Human somatic cells silence hTERT → progressive telomere shortening → replicative senescence; only stem cells, germ cells, and activated lymphocytes maintain low activity",
                },
                "cancer_model_impact": {
                    "role": "fundamental model limitation",
                    "key_terms": ["cancer model limitation", "telomere crisis", "immortalization", "TERT reactivation", "tumor evolution"],
                    "mechanism": "Human cancers must reactivate TERT (or ALT) for immortalization — a critical step absent in mouse models; mouse tumors bypass telomere crisis",
                },
            },
            "distinction_key": "Mouse-human telomerase differences create a fundamental cancer modeling gap — mouse tumors bypass a critical human carcinogenesis bottleneck (telomerase reactivation), overestimating ease of tumor formation",
        },
    },
    {
        "id": "ba_st_003",
        "title": "CYP drug metabolism: species-specific toxicity (Fialuridine case)",
        "prompt": (
            "Drug metabolism differs substantially between mouse and human "
            "CYP enzymes, with sometimes fatal consequences.\n\n"
            "Compare:\n"
            "1. Mouse drug metabolism (expanded CYP2 family, different specificity)\n"
            "2. Human drug metabolism (CYP3A4-dominated, pharmacogenomics)\n"
            "3. The Fialuridine disaster as a case study of translational failure\n\n"
            "How did species differences in drug metabolism and transport "
            "lead to human deaths despite clean preclinical safety data?"
        ),
        "ground_truth": {
            "contexts": {
                "mouse_metabolism": {
                    "role": "distinct drug metabolizer",
                    "key_terms": ["CYP isoform", "mouse CYP", "metabolic rate", "species-specific", "CYP2 family"],
                    "mechanism": "Mice have expanded CYP2 family with different substrate specificities; much higher metabolic rate per body weight; many drugs metabolized via different CYP isoforms than humans",
                },
                "human_metabolism": {
                    "role": "CYP3A4-dependent metabolizer",
                    "key_terms": ["CYP3A4", "first-pass metabolism", "drug-drug interaction", "pharmacogenomics", "CYP2D6"],
                    "mechanism": "CYP3A4 metabolizes ~50% of clinical drugs; genetic polymorphisms (CYP2D6, CYP2C19) cause interindividual variation; first-pass metabolism determines oral bioavailability",
                },
                "fialuridine_disaster": {
                    "role": "fatal translational failure",
                    "key_terms": ["Fialuridine", "FIAU", "hepatotoxicity", "mitochondrial toxicity", "clinical trial death", "nucleoside transporter"],
                    "mechanism": "FIAU showed no toxicity in mice/rats but caused fatal hepatotoxicity in humans (5 deaths, 1993); species difference in mitochondrial nucleoside transporter allowed mitochondrial incorporation only in humans",
                },
            },
            "distinction_key": "Species-specific CYP metabolism and drug transporter differences mean mouse safety data does not guarantee human safety — Fialuridine demonstrates how a molecular transporter difference converts a safe compound into a lethal one",
        },
    },
    {
        "id": "ba_st_004",
        "title": "Cardiac regeneration: zebrafish vs neonatal vs adult mammalian",
        "prompt": (
            "Cardiac regenerative capacity differs dramatically across "
            "species and developmental stages.\n\n"
            "Compare:\n"
            "1. Zebrafish (full ventricular regeneration)\n"
            "2. Neonatal mouse (transient regenerative window before P7)\n"
            "3. Adult mammalian heart (fibrotic scarring after MI)\n\n"
            "Why can zebrafish regenerate their heart but adult mammals "
            "cannot, and what does the neonatal window tell us about "
            "therapeutic possibilities?"
        ),
        "ground_truth": {
            "contexts": {
                "zebrafish_regeneration": {
                    "role": "natural heart regenerator",
                    "key_terms": ["zebrafish", "cardiac regeneration", "cardiomyocyte proliferation", "dedifferentiation", "ventricular resection"],
                    "mechanism": "After ventricular resection, zebrafish cardiomyocytes dedifferentiate and proliferate → complete regeneration within 60 days; dependent on NRG1/ERBB2 signaling",
                },
                "neonatal_window": {
                    "role": "transient regenerative capacity",
                    "key_terms": ["neonatal", "regenerative window", "postnatal day 7", "P7", "cardiomyocyte cell cycle", "transient"],
                    "mechanism": "Neonatal mice (before P7) can regenerate heart; cardiomyocytes still proliferative; window closes as cardiomyocytes binucleate and exit cell cycle",
                },
                "adult_fibrosis": {
                    "role": "non-regenerative scar formation",
                    "key_terms": ["fibrosis", "scar", "post-mitotic", "myocardial infarction", "cardiac fibroblast", "collagen"],
                    "mechanism": "Adult mammalian cardiomyocytes are post-mitotic; after MI, dead tissue replaced by fibrotic scar; very limited endogenous regenerative capacity (<1% annual turnover)",
                },
            },
            "distinction_key": "Cardiac regeneration capacity is species and age-dependent — constitutive in zebrafish, transiently present in neonatal mammals, lost in adults — regeneration is silenced rather than absent, suggesting therapeutic potential",
        },
    },
    {
        "id": "ba_st_005",
        "title": "Drosophila Toll vs human TLR: conserved architecture, divergent function",
        "prompt": (
            "Drosophila Toll and human TLRs share domain architecture but "
            "differ in fundamental ways.\n\n"
            "Compare:\n"
            "1. Drosophila Toll (dual developmental and immune function, indirect pathogen sensing)\n"
            "2. Human TLRs (pure innate immune sensors, direct PAMP recognition)\n"
            "3. Translational limitations for innate immunity drug development\n\n"
            "How do differences in ligand recognition mechanism (indirect "
            "vs direct) and functional scope (developmental vs immune-only) "
            "limit cross-species translation?"
        ),
        "ground_truth": {
            "contexts": {
                "drosophila_toll": {
                    "role": "dual developmental and immune receptor",
                    "key_terms": ["Toll receptor", "dorso-ventral", "Spatzle", "Drosophila", "Dif", "dual function", "indirect"],
                    "mechanism": "Toll was discovered as developmental patterning gene (dorso-ventral axis); also activates Dif/Dorsal (NF-κB homologs) for antifungal immunity; does NOT directly bind pathogens — uses Spätzle processing",
                },
                "human_tlr": {
                    "role": "direct pathogen recognition receptor",
                    "key_terms": ["TLR", "pathogen recognition", "PAMP", "TLR4", "LPS", "MyD88", "direct binding"],
                    "mechanism": "Human TLRs (TLR1-10) directly recognize specific PAMPs (TLR4-LPS, TLR3-dsRNA, TLR9-CpG); purely immune with no developmental role; signal via MyD88 → NF-κB",
                },
                "translational_limitation": {
                    "role": "ligand-receptor mismatch across species",
                    "key_terms": ["ligand specificity", "indirect recognition", "direct recognition", "translational gap", "drug development"],
                    "mechanism": "Drosophila Toll uses indirect sensing (proteolytic cascade) while human TLRs directly bind PAMPs — TLR4/LPS binding has no fly equivalent; Drosophila informs pathway logic but not receptor pharmacology",
                },
            },
            "distinction_key": "Toll and TLR share ancestral architecture but diverge in function (developmental+immune vs immune-only) and mechanism (indirect vs direct pathogen recognition) — fly studies reveal pathway principles but not receptor-ligand pharmacology",
        },
    },
    {
        "id": "ba_st_006",
        "title": "Fc receptor IgG subclass hierarchy: mouse vs human inversion",
        "prompt": (
            "Mouse and human IgG subclasses have partially inverted "
            "effector function hierarchies, causing therapeutic antibody "
            "translation problems.\n\n"
            "Compare:\n"
            "1. Mouse IgG subclass effector functions (IgG2a strongest)\n"
            "2. Human IgG subclass effector functions (IgG1 strongest, IgG4 inert)\n"
            "3. Implications for therapeutic antibody preclinical testing\n\n"
            "Why can't mouse efficacy data for therapeutic antibodies be "
            "directly translated to human clinical outcomes?"
        ),
        "ground_truth": {
            "contexts": {
                "mouse_igg": {
                    "role": "different effector hierarchy",
                    "key_terms": ["mouse IgG2a", "FcgammaRIV", "ADCC", "mouse Fc receptor", "effector function", "mouse IgG1"],
                    "mechanism": "In mice, IgG2a is the strongest effector subclass with high affinity for activating FcγRI and FcγRIV; mouse IgG1 has weak effector function",
                },
                "human_igg": {
                    "role": "different subclass-function mapping",
                    "key_terms": ["human IgG1", "human IgG4", "FcgammaRIIIA", "ADCC", "therapeutic antibody", "effector function"],
                    "mechanism": "Human IgG1 is strongest effector (high FcγRIIIA affinity, robust ADCC); IgG4 is functionally inert; hierarchy does NOT correspond to mouse by number",
                },
                "translation_failure": {
                    "role": "preclinical efficacy overestimation",
                    "key_terms": ["Fc engineering", "preclinical model", "species difference", "FcgammaR transgenic", "antibody engineering"],
                    "mechanism": "Human IgG1 in mice binds mouse FcγRs differently than human FcγRs; led to development of human FcγR transgenic mice for better preclinical testing",
                },
            },
            "distinction_key": "Mouse and human IgG subclasses have partially inverted effector hierarchies and non-equivalent Fc receptor binding — standard mouse studies are unreliable for predicting therapeutic antibody performance in humans",
        },
    },
    {
        "id": "ba_st_007",
        "title": "Diabetes models: STZ chemical vs NOD autoimmune vs human T1D",
        "prompt": (
            "Mouse diabetes models differ fundamentally from human Type 1 "
            "diabetes in mechanism and translatability.\n\n"
            "Compare:\n"
            "1. STZ (streptozotocin) model — chemical β-cell destruction\n"
            "2. NOD mouse — spontaneous autoimmune diabetes\n"
            "3. Human Type 1 diabetes — complex autoimmune disease\n\n"
            "Why have over 200 interventions prevented diabetes in NOD mice "
            "while almost none translate to human T1D? What does this tell "
            "us about model organism limitations?"
        ),
        "ground_truth": {
            "contexts": {
                "stz_model": {
                    "role": "chemical diabetes model (wrong mechanism)",
                    "key_terms": ["streptozotocin", "STZ", "beta cell destruction", "chemical", "GLUT2", "DNA alkylation"],
                    "mechanism": "STZ enters β-cells via GLUT2 → DNA alkylation and oxidative damage → rapid β-cell death within days; creates insulin-deficient diabetes without autoimmune component",
                },
                "nod_mouse": {
                    "role": "better but flawed autoimmune model",
                    "key_terms": ["NOD mouse", "autoimmune model", "female bias", "MHC I-Ag7", "immunomodulation", "translational gap"],
                    "mechanism": "NOD mice develop spontaneous autoimmune diabetes (female bias ~80%); however, >200 interventions prevent diabetes in NOD but almost none translate to human T1D",
                },
                "human_t1d": {
                    "role": "complex polygenic autoimmune disease",
                    "key_terms": ["autoimmune", "T1D", "insulitis", "CD8 T cell", "GAD65", "HLA-DR3/DR4", "years-long"],
                    "mechanism": "Human T1D involves CD4/CD8 T cell-mediated β-cell destruction over months to years; autoantibodies appear years before onset; HLA-DR3/DR4 susceptibility",
                },
            },
            "distinction_key": "Three diabetes models represent escalating translational fidelity — STZ (wrong mechanism), NOD (right mechanism, wrong details), human T1D (complex polygenic autoimmunity) — the NOD paradox exemplifies the translational gap",
        },
    },
    {
        "id": "ba_st_008",
        "title": "C. elegans apoptosis: conserved core, divergent regulation",
        "prompt": (
            "C. elegans was where programmed cell death was first genetically "
            "defined (Nobel Prize 2002), but the regulatory complexity "
            "differs enormously from humans.\n\n"
            "Compare:\n"
            "1. C. elegans apoptosis (ced-3/ced-9/ced-4, invariant lineage)\n"
            "2. Human apoptosis (Bcl-2 family, intrinsic/extrinsic pathways)\n"
            "3. Translational success and limitations (venetoclax as example)\n\n"
            "What was conserved vs diverged, and how did worm genetics "
            "ultimately lead to human cancer therapy?"
        ),
        "ground_truth": {
            "contexts": {
                "c_elegans_simple": {
                    "role": "invariant developmental death program",
                    "key_terms": ["ced-3", "ced-9", "ced-4", "egl-1", "invariant lineage", "131 cells", "linear pathway"],
                    "mechanism": "Exactly 131 cells die in invariant lineage; linear pathway: EGL-1 → inhibits CED-9 (Bcl-2) → releases CED-4 (Apaf-1) → activates CED-3 (caspase)",
                },
                "human_complex": {
                    "role": "multi-pathway regulated decision",
                    "key_terms": ["Bcl-2 family", "intrinsic pathway", "extrinsic pathway", "MOMP", "cytochrome c", "IAP"],
                    "mechanism": "Human apoptosis uses intrinsic/extrinsic pathways, >20 Bcl-2 family members, MOMP, cytochrome c release, apoptosome, IAP regulation — regulated at every step",
                },
                "translational_outcome": {
                    "role": "core discovery enabling targeted therapy",
                    "key_terms": ["venetoclax", "BH3 mimetic", "cancer therapy", "Bcl-2 inhibitor", "CLL", "translational success"],
                    "mechanism": "C. elegans identified core death machinery; human therapy required species-specific Bcl-2 family knowledge — venetoclax (Bcl-2 BH3 mimetic for CLL) designed from human structure, not worm genetics directly",
                },
            },
            "distinction_key": "C. elegans provided the conceptual framework for programmed death, but human apoptosis regulation is far more complex — successful therapy (venetoclax) required species-specific knowledge of the expanded Bcl-2 family",
        },
    },
    {
        "id": "ba_st_009",
        "title": "TGN1412/CD28 superagonist: mouse safety to human cytokine storm",
        "prompt": (
            "The TGN1412 clinical trial disaster (2006) is the most dramatic "
            "example of species-specific immune biology causing harm.\n\n"
            "Compare:\n"
            "1. Mouse/rat preclinical results (safe, Treg expansion)\n"
            "2. Human first-in-human trial (catastrophic cytokine storm)\n"
            "3. Underlying species difference in T cell biology\n\n"
            "What specific biological difference between laboratory mice "
            "and humans caused the same antibody to expand Tregs in one "
            "species and trigger multi-organ failure in the other?"
        ),
        "ground_truth": {
            "contexts": {
                "mouse_safe": {
                    "role": "apparently safe in preclinical",
                    "key_terms": ["preclinical", "mouse safety", "CD28 superagonist", "Treg expansion", "immunomodulation", "well-tolerated"],
                    "mechanism": "TGN1412 expanded Tregs and showed immunomodulatory effects in mice/rats without significant adverse events; NHP studies used a version with lower CD28 affinity",
                },
                "human_disaster": {
                    "role": "catastrophic cytokine release",
                    "key_terms": ["cytokine storm", "TGN1412", "cytokine release syndrome", "2006 trial", "multiple organ failure", "first-in-human"],
                    "mechanism": "All 6 healthy volunteers developed severe cytokine storm within hours (TNF-α, IFN-γ, IL-2 surge) → multi-organ failure; caused by effector memory T cell activation",
                },
                "species_difference": {
                    "role": "fundamental T cell biology gap",
                    "key_terms": ["effector memory T cell", "CD4+CD28+", "species difference", "immune experience", "SPF housing", "naive T cell"],
                    "mechanism": "Humans accumulate effector memory CD4+CD28+ T cells from lifelong pathogen exposure; SPF lab mice have mostly naive T cells; CD28 superagonist activates effector memory (humans) vs Tregs (mice)",
                },
            },
            "distinction_key": "TGN1412 is the most dramatic example of species-specific immune biology — same antibody activates Tregs in immunologically naive mice but triggers effector memory T cell cytokine storms in immunologically experienced humans",
        },
    },
]
