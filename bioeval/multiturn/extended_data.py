"""
Extended Multi-Turn dialogue scenarios.

Covers additional scientific collaboration domains: multi-omic integration,
statistical method selection, protocol optimisation, reproducibility
discussion, and literature-based hypothesis building.
"""

from bioeval.multiturn.dialogues import (
    DialogueTurn,
    DialogueType,
    MultiTurnDialogue,
    TurnType,
)

EXTENDED_DIALOGUES = [
    # -------------------------------------------------------------------------
    # MULTI-OMIC DATA INTEGRATION
    # -------------------------------------------------------------------------
    MultiTurnDialogue(
        id="mt_omics_001",
        title="Integrating RNA-seq and Proteomics Discordance",
        dialogue_type=DialogueType.DATA_INTERPRETATION,
        domain="multi_omics",
        description="Discussing why RNA and protein levels disagree",
        overall_objective="Develop coherent interpretation of discordant multi-omic data",
        difficulty="hard",
        turns=[
            DialogueTurn(
                turn_number=1,
                turn_type=TurnType.INITIAL_QUESTION,
                user_message="""We did RNA-seq and proteomics on the same samples (drug-treated
                vs control cancer cells). The RNA-seq shows 300 upregulated genes, but
                fewer than half of those show increased protein. Some proteins even go
                DOWN while their mRNA goes UP. Is our data wrong?""",
                expected_behaviors=[
                    "Reassure this is common and expected",
                    "Explain mRNA-protein correlation is often ~0.4-0.6",
                    "List biological reasons: translation rates, protein stability, post-translational regulation",
                    "Suggest not all mRNA changes translate to protein changes",
                ],
                failure_modes=[
                    "Assuming data is wrong",
                    "Not knowing about mRNA-protein discordance",
                ],
                context_dependency="None - initial question",
                scoring_criteria={"reassures": True, "explains_biology": True},
            ),
            DialogueTurn(
                turn_number=2,
                turn_type=TurnType.FOLLOW_UP,
                user_message="""That makes sense. But we found one gene, CDKN1A (p21), where
                mRNA is 5-fold up but protein is 3-fold DOWN after drug treatment.
                How is that even possible?""",
                expected_behaviors=[
                    "This is a specific and interesting case",
                    "p21 protein is regulated by ubiquitin-proteasome degradation",
                    "Drug may activate proteolytic pathways (MDM2, SCF-Skp2)",
                    "Suggest checking if proteasome is involved (MG132 test)",
                ],
                failure_modes=[
                    "Giving generic mRNA/protein discordance answer without specifics",
                    "Not knowing p21 post-translational regulation",
                ],
                context_dependency="Must connect to general discordance discussion",
                scoring_criteria={"specific_mechanism": True, "suggests_experiment": True},
            ),
            DialogueTurn(
                turn_number=3,
                turn_type=TurnType.NEW_INFORMATION,
                user_message="""We added MG132 (proteasome inhibitor) and p21 protein is now
                strongly accumulated. So the drug IS increasing p21 transcription but
                simultaneously activating proteasomal degradation. How should we
                report this finding?""",
                expected_behaviors=[
                    "Confirm dual regulation interpretation",
                    "Suggest reporting as coordinated transcriptional and post-translational regulation",
                    "This is mechanistically interesting and worth highlighting",
                    "Recommend western blot time course to show kinetics",
                ],
                failure_modes=[
                    "Not integrating RNA-seq, proteomics, and MG132 data",
                ],
                context_dependency="Must synthesise all three data sources",
                scoring_criteria={"integrates_all_data": True, "constructive_framing": True},
            ),
            DialogueTurn(
                turn_number=4,
                turn_type=TurnType.CHALLENGE,
                user_message="""A colleague says our proteasome result might be an artefact
                because MG132 blocks ALL proteasomal degradation, not specifically
                p21. How should we address this?""",
                expected_behaviors=[
                    "Acknowledge the critique is valid",
                    "Suggest cycloheximide chase to measure p21 half-life ± drug",
                    "Could use specific E3 ligase knockdown (MDM2, Skp2)",
                    "Ubiquitination assay for p21 ± drug treatment",
                ],
                failure_modes=[
                    "Dismissing the valid critique",
                    "Not suggesting more specific experiments",
                ],
                context_dependency="Must address the specificity concern for p21",
                scoring_criteria={"acknowledges_limitation": True, "offers_specific_tests": True},
            ),
        ],
    ),
    # -------------------------------------------------------------------------
    # STATISTICAL METHOD SELECTION
    # -------------------------------------------------------------------------
    MultiTurnDialogue(
        id="mt_stat_001",
        title="Choosing Analysis for Complex Experimental Design",
        dialogue_type=DialogueType.EXPERIMENTAL_DESIGN,
        domain="statistics",
        description="Helping researcher choose appropriate statistical approach",
        overall_objective="Guide selection of correct statistical method through iterative discussion",
        difficulty="medium",
        turns=[
            DialogueTurn(
                turn_number=1,
                turn_type=TurnType.INITIAL_QUESTION,
                user_message="""I have tumour growth data from a mouse experiment. 4 treatment
                groups, 10 mice each, measured every 3 days for 3 weeks. I want to
                compare growth curves. A collaborator said 'just use t-tests at each
                time point'. Is that right?""",
                expected_behaviors=[
                    "Clearly say this is NOT appropriate",
                    "Explain multiple testing problem across time points",
                    "Recommend repeated measures / mixed-effects model",
                    "Ask about the experimental structure (cages, batches)",
                ],
                failure_modes=[
                    "Agreeing with t-tests at each time point",
                    "Not explaining why it's wrong",
                ],
                context_dependency="None - initial question",
                scoring_criteria={"correct_advice": True, "explains_why": True},
            ),
            DialogueTurn(
                turn_number=2,
                turn_type=TurnType.FOLLOW_UP,
                user_message="""OK, you're right. So should I use two-way ANOVA (group × time)?
                My data isn't normally distributed though — tumour volumes are right-skewed.""",
                expected_behaviors=[
                    "Two-way ANOVA is closer but still not ideal for longitudinal data",
                    "Recommend linear mixed-effects model (lme4 / nlme in R)",
                    "For skewed data: log-transform or use generalised linear mixed model",
                    "Random effect: mouse (repeated measures on same animal)",
                ],
                failure_modes=[
                    "Not addressing the distributional assumption",
                    "Not mentioning random effects for repeated measures",
                ],
                context_dependency="Must build on rejection of t-tests",
                scoring_criteria={"correct_method": True, "handles_skewness": True},
            ),
            DialogueTurn(
                turn_number=3,
                turn_type=TurnType.FOLLOW_UP,
                user_message="""Some mice died during the study (3 in vehicle group, 1 in
                treatment group). Should I just remove them from analysis?""",
                expected_behaviors=[
                    "Differential dropout is informative — don't just remove",
                    "This is informative censoring (dying = worst outcome)",
                    "Suggest tumour growth + survival as joint analysis",
                    "Mixed models can handle unbalanced data (missing time points)",
                ],
                failure_modes=[
                    "Advising simple removal without considering bias",
                ],
                context_dependency="Must connect to mixed model discussion",
                scoring_criteria={"handles_dropout": True, "considers_bias": True},
            ),
        ],
    ),
    # -------------------------------------------------------------------------
    # PROTOCOL OPTIMISATION
    # -------------------------------------------------------------------------
    MultiTurnDialogue(
        id="mt_opt_001",
        title="Optimising Single-Cell RNA-seq Protocol",
        dialogue_type=DialogueType.TROUBLESHOOTING,
        domain="protocol",
        description="Iteratively optimising a single-cell sequencing experiment",
        overall_objective="Diagnose and fix low-quality scRNA-seq data",
        difficulty="hard",
        turns=[
            DialogueTurn(
                turn_number=1,
                turn_type=TurnType.INITIAL_QUESTION,
                user_message="""Our 10X Chromium scRNA-seq run gave terrible results.
                We loaded 10,000 cells but only recovered 2,000 cell barcodes.
                Of those, median genes per cell is only 500. What went wrong?""",
                expected_behaviors=[
                    "Low recovery (20%) suggests cell death during processing",
                    "Low genes/cell suggests poor capture or RNA degradation",
                    "Ask about cell viability before loading",
                    "Ask about tissue type and dissociation method",
                ],
                failure_modes=[
                    "Not asking about sample preparation",
                    "Jumping to sequencing issues without checking upstream steps",
                ],
                context_dependency="None - initial question",
                scoring_criteria={"systematic_approach": True, "asks_about_viability": True},
            ),
            DialogueTurn(
                turn_number=2,
                turn_type=TurnType.NEW_INFORMATION,
                user_message="""Viability was only 60% by trypan blue. We dissociated a mouse
                brain with enzymatic digestion (collagenase + DNase I) for 45 minutes
                at 37°C. We didn't filter or remove dead cells before loading.""",
                expected_behaviors=[
                    "60% viability is below 10X's recommended >90%",
                    "Dead cells release ambient RNA that contaminates barcodes",
                    "45 min digestion may be too harsh for brain tissue",
                    "Recommend: shorter digestion, cold-active protease, dead cell removal",
                ],
                failure_modes=[
                    "Not identifying viability as the primary issue",
                    "Not suggesting dead cell removal (MACS, FACS)",
                ],
                context_dependency="Must connect low viability to low recovery",
                scoring_criteria={"identifies_cause": True, "actionable_fixes": True},
            ),
            DialogueTurn(
                turn_number=3,
                turn_type=TurnType.FOLLOW_UP,
                user_message="""We optimised: shorter digestion (20 min), added dead cell removal
                kit, viability now 92%. But now we're worried about losing certain
                cell types during dead cell removal. How do we check?""",
                expected_behaviors=[
                    "Valid concern — some fragile cell types may be lost",
                    "Suggest running FACS panel before/after dead cell removal to check",
                    "Compare cell type proportions to published brain scRNA-seq atlases",
                    "Could try Papain instead of collagenase (gentler on neurons)",
                ],
                failure_modes=[
                    "Dismissing the concern about cell type loss",
                ],
                context_dependency="Must acknowledge improvement from optimization",
                scoring_criteria={"validates_concern": True, "practical_advice": True},
            ),
        ],
    ),
    # -------------------------------------------------------------------------
    # REPRODUCIBILITY DISCUSSION
    # -------------------------------------------------------------------------
    MultiTurnDialogue(
        id="mt_repro_001",
        title="Failure to Reproduce Published Result",
        dialogue_type=DialogueType.HYPOTHESIS_REFINEMENT,
        domain="reproducibility",
        description="Discussing failure to replicate a published finding",
        overall_objective="Systematically explore why a replication failed",
        difficulty="medium",
        turns=[
            DialogueTurn(
                turn_number=1,
                turn_type=TurnType.INITIAL_QUESTION,
                user_message="""A 2020 paper in Nature reported that drug Y kills 90% of
                pancreatic cancer cells via ferroptosis. We repeated the experiment
                exactly as described but only see 20% cell death. We've tried three
                times. Should we contact the authors?""",
                expected_behaviors=[
                    "Don't immediately blame the authors",
                    "Systematic differences are common even with 'identical' protocols",
                    "Ask about key variables: cell line passage, drug batch, serum lot, media composition",
                    "Check if their cell line source matches yours",
                ],
                failure_modes=[
                    "Immediately suggesting fraud",
                    "Not considering technical differences",
                ],
                context_dependency="None - initial question",
                scoring_criteria={"systematic_approach": True, "balanced_view": True},
            ),
            DialogueTurn(
                turn_number=2,
                turn_type=TurnType.NEW_INFORMATION,
                user_message="""We're using the same cell line (PANC-1) from ATCC. Same drug
                concentration. But we noticed their paper used RPMI with 1% FBS while
                we use 10% FBS. Could that matter for ferroptosis?""",
                expected_behaviors=[
                    "YES — serum concentration is critical for ferroptosis",
                    "FBS contains lipid peroxidation inhibitors (selenium, vitamin E, albumin)",
                    "Low serum sensitises cells to ferroptosis",
                    "This alone could explain the discrepancy",
                ],
                failure_modes=[
                    "Dismissing serum as irrelevant",
                    "Not knowing about serum and ferroptosis",
                ],
                context_dependency="Must connect serum to ferroptosis mechanism",
                scoring_criteria={"identifies_key_variable": True, "mechanistic_explanation": True},
            ),
            DialogueTurn(
                turn_number=3,
                turn_type=TurnType.FOLLOW_UP,
                user_message="""We repeated with 1% FBS and now we see 85% cell death —
                matches the paper! But our PI says 1% FBS is 'artificial' and not
                physiological. Should we even publish our replication?""",
                expected_behaviors=[
                    "PI has a valid scientific point about physiological relevance",
                    "But the finding is still important — documents a key experimental variable",
                    "Suggest publishing as a 'matters arising' or technical note",
                    "Highlight that ferroptosis sensitivity is context-dependent",
                ],
                failure_modes=[
                    "Not engaging with the physiological relevance question",
                    "Either fully agreeing or fully disagreeing without nuance",
                ],
                context_dependency="Must integrate replication success with biological criticism",
                scoring_criteria={"nuanced_view": True, "constructive_suggestion": True},
            ),
        ],
    ),
    # -------------------------------------------------------------------------
    # LITERATURE-BASED HYPOTHESIS
    # -------------------------------------------------------------------------
    MultiTurnDialogue(
        id="mt_lit_001",
        title="Building Hypothesis from Contradictory Papers",
        dialogue_type=DialogueType.HYPOTHESIS_REFINEMENT,
        domain="pathway_reasoning",
        description="Reconciling contradictory published findings",
        overall_objective="Develop unifying hypothesis from conflicting data",
        difficulty="hard",
        turns=[
            DialogueTurn(
                turn_number=1,
                turn_type=TurnType.INITIAL_QUESTION,
                user_message="""Paper A says autophagy promotes tumour growth in pancreatic cancer.
                Paper B says autophagy INHIBITS tumour growth in pancreatic cancer.
                They're both in good journals. How can both be right?""",
                expected_behaviors=[
                    "Autophagy has dual roles in cancer (well-known paradox)",
                    "Context matters: stage, genetic background, microenvironment",
                    "Early tumourigenesis vs established tumours may differ",
                    "Ask about specific experimental systems used in each paper",
                ],
                failure_modes=[
                    "Saying one paper must be wrong",
                    "Not recognising the autophagy paradox in cancer",
                ],
                context_dependency="None - initial question",
                scoring_criteria={"recognises_paradox": True, "context_aware": True},
            ),
            DialogueTurn(
                turn_number=2,
                turn_type=TurnType.NEW_INFORMATION,
                user_message="""Paper A used KRAS-mutant mouse models where autophagy was
                deleted specifically in pancreas. Paper B used cell lines with
                pharmacological autophagy inhibitors. Could the model system
                explain the difference?""",
                expected_behaviors=[
                    "Genetic vs pharmacological is a key distinction",
                    "In vivo: autophagy deletion affects tumour AND stroma/immune cells",
                    "In vitro: only tumour-cell-intrinsic effects captured",
                    "KRAS-mutant context has specific autophagy dependency",
                ],
                failure_modes=[
                    "Not distinguishing in vivo vs in vitro contexts",
                    "Ignoring the KRAS-mutant genetic background",
                ],
                context_dependency="Must reconcile with dual-role framework from turn 1",
                scoring_criteria={"distinguishes_models": True, "mechanistic_insight": True},
            ),
            DialogueTurn(
                turn_number=3,
                turn_type=TurnType.SYNTHESIS,
                user_message="""So in KRAS-mutant pancreatic cancer, tumour cells depend on
                autophagy for survival, but the immune system also uses autophagy
                to fight cancer. Is there a way to exploit this therapeutically?""",
                expected_behaviors=[
                    "Recognise the therapeutic dilemma",
                    "Combining autophagy inhibition with immunotherapy has been tried",
                    "Chloroquine/hydroxychloroquine trials in PDAC + gemcitabine",
                    "Suggest timing or cell-type-specific targeting strategies",
                ],
                failure_modes=[
                    "Not engaging with the therapeutic complexity",
                    "Oversimplifying to just 'inhibit autophagy'",
                ],
                context_dependency="Must integrate all previous discussion for therapeutic angle",
                scoring_criteria={"therapeutic_insight": True, "acknowledges_complexity": True},
            ),
        ],
    ),
    # -------------------------------------------------------------------------
    # EXPERIMENTAL DESIGN — CRISPR SCREEN FOLLOW-UP
    # -------------------------------------------------------------------------
    MultiTurnDialogue(
        id="mt_exp_002",
        title="Validating High-Throughput Screen Hits",
        dialogue_type=DialogueType.EXPERIMENTAL_DESIGN,
        domain="protocol",
        description="Planning validation experiments after a CRISPR screen",
        overall_objective="Design rigorous validation of screen hits",
        difficulty="medium",
        turns=[
            DialogueTurn(
                turn_number=1,
                turn_type=TurnType.INITIAL_QUESTION,
                user_message="""Our genome-wide CRISPR screen for synthetic lethal partners with
                PARP inhibitors gave 30 top hits (FDR < 0.05). My PI says I need to
                validate them. What's the best approach?""",
                expected_behaviors=[
                    "Individual gene validation (arrayed CRISPR KO)",
                    "Suggest prioritising hits by: effect size, biological plausibility, novelty",
                    "Recommend testing with 2-3 independent sgRNAs per gene",
                    "Ask about the number of replicates and controls from the screen",
                ],
                failure_modes=[
                    "Suggesting to validate all 30 without prioritisation",
                ],
                context_dependency="None - initial question",
                scoring_criteria={"systematic_plan": True, "prioritisation": True},
            ),
            DialogueTurn(
                turn_number=2,
                turn_type=TurnType.FOLLOW_UP,
                user_message="""We chose the top 10 hits. I'm going to use CRISPRi with
                2 sgRNAs per gene. Should I do individual knockdowns or a mini-pool?""",
                expected_behaviors=[
                    "Individual (arrayed) knockdowns are better for validation",
                    "Allows clean phenotype measurement per gene",
                    "Mini-pool loses individual gene resolution",
                    "Include non-targeting and known-essential controls",
                ],
                failure_modes=[
                    "Recommending mini-pool for validation stage",
                ],
                context_dependency="Must build on validation planning from turn 1",
                scoring_criteria={"correct_approach": True, "control_design": True},
            ),
            DialogueTurn(
                turn_number=3,
                turn_type=TurnType.CHALLENGE,
                user_message="""One of our top hits is a gene with no known function
                (C12orf65). My PI says to skip it and focus on 'interesting' genes.
                Should I listen to her?""",
                expected_behaviors=[
                    "Counterargument: uncharacterised hits are potentially most novel",
                    "If it validated in the screen (FDR < 0.05), it deserves validation",
                    "This could be the most publishable finding if it confirms",
                    "Suggest a compromise: validate it alongside known genes",
                ],
                failure_modes=[
                    "Agreeing to skip it without discussion",
                    "Being dismissive of the PI's perspective",
                ],
                context_dependency="Must balance novelty vs practicality",
                scoring_criteria={"advocates_for_novel_hit": True, "respectful": True},
            ),
        ],
    ),
    # -------------------------------------------------------------------------
    # IMMUNOLOGY — T CELL EXHAUSTION
    # -------------------------------------------------------------------------
    MultiTurnDialogue(
        id="mt_immuno_001",
        title="T Cell Exhaustion in Chronic Infection",
        dialogue_type=DialogueType.HYPOTHESIS_REFINEMENT,
        domain="immunology",
        description="Interpreting T cell phenotyping data in chronic viral infection model",
        overall_objective="Distinguish T cell exhaustion from activation using multi-parameter data",
        difficulty="hard",
        turns=[
            DialogueTurn(
                turn_number=1,
                turn_type=TurnType.INITIAL_QUESTION,
                user_message="""We're studying CD8+ T cells in a chronic LCMV infection mouse model.
                Flow cytometry shows high PD-1 expression on virus-specific T cells at
                day 30. Does this mean the cells are exhausted?""",
                expected_behaviors=[
                    "PD-1 alone is not sufficient to define exhaustion",
                    "PD-1 is also expressed on recently activated T cells",
                    "Need co-expression of multiple inhibitory receptors (LAG-3, TIM-3, TIGIT)",
                    "Ask about functional readouts (cytokine production, killing capacity)",
                ],
                failure_modes=[
                    "Equating PD-1 expression alone with exhaustion",
                    "Not distinguishing activation from exhaustion",
                ],
                context_dependency="None - initial question",
                scoring_criteria={"nuanced_pd1": True, "suggests_additional_markers": True},
            ),
            DialogueTurn(
                turn_number=2,
                turn_type=TurnType.NEW_INFORMATION,
                user_message="""We checked: the cells co-express PD-1, LAG-3, and TIM-3. But
                intracellular staining shows they still produce IFN-gamma (lower than
                acute phase but detectable). Are they truly exhausted if they still
                make cytokine?""",
                expected_behaviors=[
                    "Exhaustion is a spectrum, not binary",
                    "Progenitor exhausted (TCF1+) vs terminally exhausted (TCF1-)",
                    "Retained IFN-gamma but lost IL-2 and TNF-alpha is typical of partial exhaustion",
                    "Check TCF1/TOX expression to define exhaustion subset",
                ],
                failure_modes=[
                    "Saying cells are not exhausted because they make IFN-gamma",
                    "Not mentioning the exhaustion spectrum concept",
                ],
                context_dependency="Must integrate PD-1 discussion from turn 1",
                scoring_criteria={"exhaustion_spectrum": True, "tcf1_tox": True},
            ),
            DialogueTurn(
                turn_number=3,
                turn_type=TurnType.CHALLENGE,
                user_message="""We treated mice with anti-PD-1. The virus-specific T cells expanded
                but viral titers didn't change. A reviewer says checkpoint blockade
                should reduce viral load. What's going on?""",
                expected_behaviors=[
                    "Terminally exhausted cells can expand but remain dysfunctional",
                    "Progenitor exhausted cells respond better to anti-PD-1",
                    "Expansion without functional improvement is documented",
                    "Suggest evaluating which subset expanded (TCF1+ vs TCF1-)",
                ],
                failure_modes=[
                    "Not distinguishing responder subsets",
                    "Assuming expansion always means functional restoration",
                ],
                context_dependency="Must build on exhaustion subset discussion",
                scoring_criteria={"explains_disconnect": True, "suggests_subset_analysis": True},
            ),
        ],
    ),
    # -------------------------------------------------------------------------
    # NEUROSCIENCE — ELECTROPHYSIOLOGY
    # -------------------------------------------------------------------------
    MultiTurnDialogue(
        id="mt_neuro_001",
        title="Interpreting Electrophysiology Data",
        dialogue_type=DialogueType.DATA_INTERPRETATION,
        domain="neuroscience",
        description="Troubleshooting unexpected patch clamp results",
        overall_objective="Diagnose why miniature EPSCs show paradoxical changes",
        difficulty="medium",
        turns=[
            DialogueTurn(
                turn_number=1,
                turn_type=TurnType.INITIAL_QUESTION,
                user_message="""Our patch clamp experiments show that our drug increases mEPSC
                frequency but DECREASES mEPSC amplitude in hippocampal neurons.
                That seems contradictory. More events but smaller? How is that possible?""",
                expected_behaviors=[
                    "Not contradictory — frequency and amplitude reflect different mechanisms",
                    "Frequency = presynaptic (vesicle release probability)",
                    "Amplitude = postsynaptic (receptor number/conductance)",
                    "Drug may enhance presynaptic release while downregulating postsynaptic receptors",
                ],
                failure_modes=[
                    "Agreeing this is contradictory",
                    "Not distinguishing pre- vs postsynaptic mechanisms",
                ],
                context_dependency="None - initial question",
                scoring_criteria={"pre_post_distinction": True, "mechanistic_explanation": True},
            ),
            DialogueTurn(
                turn_number=2,
                turn_type=TurnType.FOLLOW_UP,
                user_message="""That's helpful. But could the decreased amplitude just be a
                technical artefact? Like series resistance changing during recording?""",
                expected_behaviors=[
                    "Valid concern — series resistance increase would reduce all currents",
                    "Check if series resistance was monitored throughout recording",
                    "Rs increase affects evoked and miniature events equally",
                    "Could also be rundown of postsynaptic receptors (common in whole-cell)",
                ],
                failure_modes=[
                    "Dismissing the technical concern",
                    "Not mentioning series resistance monitoring",
                ],
                context_dependency="Must connect to amplitude discussion from turn 1",
                scoring_criteria={"validates_concern": True, "practical_checks": True},
            ),
            DialogueTurn(
                turn_number=3,
                turn_type=TurnType.FOLLOW_UP,
                user_message="""Rs was stable. We also applied TTX to confirm these are truly
                miniature events. Is there anything else we should control for?""",
                expected_behaviors=[
                    "TTX for minis is correct",
                    "Check access resistance and holding current stability",
                    "Temperature control (mEPSC properties are temperature-sensitive)",
                    "Time-matched vehicle controls (to rule out recording-time effects)",
                ],
                failure_modes=[
                    "Not mentioning time-matched controls",
                ],
                context_dependency="Must acknowledge Rs stability and TTX as good controls",
                scoring_criteria={"additional_controls": True, "systematic": True},
            ),
        ],
    ),
    # -------------------------------------------------------------------------
    # GENOMICS — VARIANT INTERPRETATION
    # -------------------------------------------------------------------------
    MultiTurnDialogue(
        id="mt_genomics_001",
        title="Clinical Variant Interpretation",
        dialogue_type=DialogueType.TROUBLESHOOTING,
        domain="genomics",
        description="Classifying a variant of uncertain significance",
        overall_objective="Systematically evaluate evidence for a VUS in a cancer gene",
        difficulty="hard",
        turns=[
            DialogueTurn(
                turn_number=1,
                turn_type=TurnType.INITIAL_QUESTION,
                user_message="""A patient with breast cancer has a germline variant in BRCA2:
                c.7397T>C (p.Val2466Ala). It's classified as VUS in ClinVar.
                The patient wants to know if she should tell her family to get tested.
                How should we approach this?""",
                expected_behaviors=[
                    "VUS means insufficient evidence — cannot make clinical decisions yet",
                    "Outline systematic evidence review: population frequency, in silico, functional, segregation",
                    "Check if variant is in a known functional domain of BRCA2",
                    "Cannot recommend family testing based on VUS alone",
                ],
                failure_modes=[
                    "Treating VUS as pathogenic",
                    "Treating VUS as benign",
                    "Not mentioning the ACMG classification framework",
                ],
                context_dependency="None - initial question",
                scoring_criteria={"correct_vus_handling": True, "systematic_evaluation": True},
            ),
            DialogueTurn(
                turn_number=2,
                turn_type=TurnType.NEW_INFORMATION,
                user_message="""We checked: gnomAD frequency is 0.0001 (rare). SIFT says 'tolerated',
                PolyPhen says 'possibly damaging'. The variant is in the DNA-binding
                domain. What do we make of conflicting in silico predictions?""",
                expected_behaviors=[
                    "Conflicting in silico predictions are common for missense variants",
                    "In silico alone is not sufficient for classification per ACMG",
                    "Low population frequency is consistent with either pathogenic or rare benign",
                    "DNA-binding domain location adds moderate concern",
                    "Need functional data or family segregation studies",
                ],
                failure_modes=[
                    "Relying solely on in silico to classify",
                    "Not recognizing limitations of computational predictors",
                ],
                context_dependency="Must build on VUS framework from turn 1",
                scoring_criteria={"acknowledges_limitations": True, "suggests_next_steps": True},
            ),
            DialogueTurn(
                turn_number=3,
                turn_type=TurnType.SYNTHESIS,
                user_message="""The patient says three other family members also have breast cancer.
                If we could test them for this variant, how would segregation data
                help classify it?""",
                expected_behaviors=[
                    "If variant co-segregates with cancer in family = evidence for pathogenicity",
                    "Need affected AND unaffected family members for informative analysis",
                    "ACMG BS4/PP1 criteria for segregation evidence",
                    "Phenocopies can confound (breast cancer is common)",
                ],
                failure_modes=[
                    "Not mentioning the need for unaffected family members",
                    "Ignoring phenocopy rate for breast cancer",
                ],
                context_dependency="Must integrate all evidence from previous turns",
                scoring_criteria={"correct_segregation": True, "acknowledges_limitations": True},
            ),
        ],
    ),
    # -------------------------------------------------------------------------
    # MICROBIOLOGY — ANTIBIOTIC RESISTANCE
    # -------------------------------------------------------------------------
    MultiTurnDialogue(
        id="mt_micro_001",
        title="Investigating Antibiotic Resistance Mechanism",
        dialogue_type=DialogueType.HYPOTHESIS_REFINEMENT,
        domain="microbiology",
        description="Diagnosing mechanism of carbapenem resistance in clinical isolate",
        overall_objective="Systematically determine resistance mechanism",
        difficulty="medium",
        turns=[
            DialogueTurn(
                turn_number=1,
                turn_type=TurnType.INITIAL_QUESTION,
                user_message="""Our clinical micro lab isolated a Klebsiella pneumoniae from a
                bloodstream infection that's resistant to meropenem (MIC > 16 ug/mL).
                What are the most likely resistance mechanisms?""",
                expected_behaviors=[
                    "Carbapenemase production (KPC, NDM, OXA-48, VIM, IMP)",
                    "Porin loss (OmpK35/OmpK36) combined with AmpC or ESBL",
                    "Efflux pump upregulation (less common for carbapenems)",
                    "Suggest molecular testing to distinguish mechanisms",
                ],
                failure_modes=[
                    "Only mentioning one mechanism",
                    "Not suggesting diagnostic tests",
                ],
                context_dependency="None - initial question",
                scoring_criteria={"lists_mechanisms": True, "suggests_testing": True},
            ),
            DialogueTurn(
                turn_number=2,
                turn_type=TurnType.NEW_INFORMATION,
                user_message="""PCR for KPC, NDM, VIM, IMP, OXA-48 was all NEGATIVE.
                Modified Hodge Test was also negative. But the isolate IS resistant.
                What now?""",
                expected_behaviors=[
                    "Negative carbapenemase tests suggest non-enzyme mechanism",
                    "Check for porin mutations (OmpK35/OmpK36 loss)",
                    "Look for ESBL/AmpC hyperproduction with porin loss",
                    "Whole genome sequencing would be definitive",
                ],
                failure_modes=[
                    "Assuming a rare carbapenemase was missed",
                    "Not considering non-carbapenemase mechanisms",
                ],
                context_dependency="Must pivot from carbapenemase to porin hypothesis",
                scoring_criteria={"correct_pivot": True, "suggests_porin_analysis": True},
            ),
            DialogueTurn(
                turn_number=3,
                turn_type=TurnType.FOLLOW_UP,
                user_message="""WGS revealed an IS element disrupting ompK36 and the strain
                carries CTX-M-15 (ESBL). So it's ESBL + porin loss causing carbapenem
                resistance. Does this have different clinical implications than
                carbapenemase producers?""",
                expected_behaviors=[
                    "Yes — different epidemiological implications",
                    "Carbapenemase genes are transferable (plasmid-borne), higher spread risk",
                    "Porin loss is chromosomal, less transmissible",
                    "But CTX-M-15 IS on a plasmid and can spread ESBL",
                    "Infection control implications differ",
                ],
                failure_modes=[
                    "Treating all carbapenem resistance as equivalent",
                    "Not distinguishing transmissibility implications",
                ],
                context_dependency="Must integrate WGS findings with clinical implications",
                scoring_criteria={"distinguishes_mechanisms": True, "clinical_relevance": True},
            ),
        ],
    ),
    # -------------------------------------------------------------------------
    # METABOLOMICS — BIOMARKER DISCOVERY
    # -------------------------------------------------------------------------
    MultiTurnDialogue(
        id="mt_metab_001",
        title="Metabolomics Biomarker Validation",
        dialogue_type=DialogueType.DATA_INTERPRETATION,
        domain="metabolomics",
        description="Evaluating metabolomic biomarker candidates from a discovery study",
        overall_objective="Critically assess metabolomics study design and results",
        difficulty="medium",
        turns=[
            DialogueTurn(
                turn_number=1,
                turn_type=TurnType.INITIAL_QUESTION,
                user_message="""We ran untargeted metabolomics (LC-MS) on serum from 20 cancer
                patients vs 20 healthy controls. After statistical analysis, we found
                150 significantly different features (p < 0.05). Is this a good result?""",
                expected_behaviors=[
                    "150 features out of how many total? Need context",
                    "p < 0.05 with no multiple testing correction on thousands of features = many false positives",
                    "Need FDR correction (Benjamini-Hochberg)",
                    "20 vs 20 is underpowered for untargeted metabolomics",
                ],
                failure_modes=[
                    "Accepting 150 hits without questioning multiple testing",
                    "Not asking about total number of features tested",
                ],
                context_dependency="None - initial question",
                scoring_criteria={"multiple_testing": True, "sample_size_concern": True},
            ),
            DialogueTurn(
                turn_number=2,
                turn_type=TurnType.FOLLOW_UP,
                user_message="""We tested ~5000 features total. After FDR correction (q < 0.05),
                only 8 features remain significant. Our PI wants to publish these as
                'novel cancer biomarkers'. Are we ready?""",
                expected_behaviors=[
                    "8 features surviving FDR is more reasonable",
                    "But still need validation: independent cohort, different platform if possible",
                    "Confounders: age, sex, BMI, medication, diet, sample handling time",
                    "Feature identification: are these 8 features identified metabolites or unknowns?",
                ],
                failure_modes=[
                    "Agreeing they can publish without validation",
                    "Not asking about confounders",
                ],
                context_dependency="Must build on statistical correction discussion",
                scoring_criteria={"validation_needed": True, "confounders": True},
            ),
            DialogueTurn(
                turn_number=3,
                turn_type=TurnType.CHALLENGE,
                user_message="""One of the 8 features is a lipid that's also elevated in
                inflammation, obesity, and diabetes. Three of our cancer patients have
                Type 2 diabetes. Could this be a confound?""",
                expected_behaviors=[
                    "Yes — classic confounding in biomarker studies",
                    "Must adjust for comorbidities or exclude comorbid patients",
                    "Conditional logistic regression controlling for T2D status",
                    "This is why matched controls are essential in biomarker studies",
                ],
                failure_modes=[
                    "Dismissing the confounding concern",
                    "Not suggesting statistical adjustment",
                ],
                context_dependency="Must connect to confounder discussion from turn 2",
                scoring_criteria={"identifies_confound": True, "suggests_solution": True},
            ),
        ],
    ),
    # -------------------------------------------------------------------------
    # EPIGENETICS — CHIP-SEQ ANALYSIS
    # -------------------------------------------------------------------------
    MultiTurnDialogue(
        id="mt_epigen_001",
        title="ChIP-seq Data Quality and Interpretation",
        dialogue_type=DialogueType.TROUBLESHOOTING,
        domain="epigenetics",
        description="Troubleshooting ChIP-seq experiment with poor signal",
        overall_objective="Diagnose and fix low-quality ChIP-seq experiment",
        difficulty="hard",
        turns=[
            DialogueTurn(
                turn_number=1,
                turn_type=TurnType.INITIAL_QUESTION,
                user_message="""Our H3K27ac ChIP-seq gave only 2,000 peaks with MACS2 (q < 0.05).
                Published data for the same cell type shows ~30,000 peaks. Our input
                control looks fine. What went wrong?""",
                expected_behaviors=[
                    "Very low peak count suggests poor enrichment",
                    "Check FRiP score (fraction of reads in peaks) — should be >1%",
                    "Ask about: antibody lot/amount, crosslinking conditions, sonication",
                    "Check library complexity (PCR duplication rate)",
                ],
                failure_modes=[
                    "Jumping to analysis parameters without checking wetlab steps",
                    "Not asking about FRiP or enrichment metrics",
                ],
                context_dependency="None - initial question",
                scoring_criteria={"systematic_diagnosis": True, "frip_check": True},
            ),
            DialogueTurn(
                turn_number=2,
                turn_type=TurnType.NEW_INFORMATION,
                user_message="""FRiP is 0.5% (we know that's low). Duplication rate is 60%!
                We used 50,000 cells for the ChIP. The antibody is from a reputable
                company. Could low cell input be the issue?""",
                expected_behaviors=[
                    "50K cells is very low for standard ChIP-seq (typically 1-10M)",
                    "High duplication means low library complexity from too little input DNA",
                    "Options: more cells, switch to CUT&Tag or CUT&RUN (work with fewer cells)",
                    "Alternatively: optimize ChIP by reducing immunoprecipitation volume",
                ],
                failure_modes=[
                    "Not connecting low cell input to high duplication",
                    "Not suggesting alternative methods for low-input",
                ],
                context_dependency="Must connect duplication to cell number",
                scoring_criteria={"diagnoses_input": True, "suggests_alternatives": True},
            ),
            DialogueTurn(
                turn_number=3,
                turn_type=TurnType.FOLLOW_UP,
                user_message="""We can't get more cells (rare primary cells). Should we try
                CUT&Tag? Or is there a way to rescue the existing data?""",
                expected_behaviors=[
                    "CUT&Tag works well with as few as 100-1000 cells",
                    "For existing data: can try relaxing peak calling threshold (but increases false positives)",
                    "Downsample to unique reads and recheck peak calls",
                    "Could use the current data as preliminary for grant, but repeat for publication",
                ],
                failure_modes=[
                    "Saying the data is useless without suggesting rescue strategies",
                    "Not recommending CUT&Tag for low input",
                ],
                context_dependency="Must address the constraint of limited cells",
                scoring_criteria={"cut_and_tag": True, "data_rescue": True},
            ),
        ],
    ),
    # -------------------------------------------------------------------------
    # STRUCTURAL BIOLOGY — CRYO-EM
    # -------------------------------------------------------------------------
    MultiTurnDialogue(
        id="mt_struct_001",
        title="Cryo-EM Structure Interpretation",
        dialogue_type=DialogueType.DATA_INTERPRETATION,
        domain="structural_biology",
        description="Interpreting ambiguous density in a cryo-EM map",
        overall_objective="Critically evaluate cryo-EM structure quality and model building",
        difficulty="hard",
        turns=[
            DialogueTurn(
                turn_number=1,
                turn_type=TurnType.INITIAL_QUESTION,
                user_message="""We solved a cryo-EM structure of a drug-receptor complex at 3.5A
                resolution. The overall map looks good but the drug density is weak and
                blobby. Can we still model the drug into the density?""",
                expected_behaviors=[
                    "3.5A is borderline for confident small molecule placement",
                    "Weak density could mean: low occupancy, conformational heterogeneity, or wrong site",
                    "Check local resolution at the binding site (often worse than global)",
                    "Need to be cautious about over-interpreting weak density",
                ],
                failure_modes=[
                    "Saying 3.5A is sufficient without checking local resolution",
                    "Encouraging model building into questionable density",
                ],
                context_dependency="None - initial question",
                scoring_criteria={"local_resolution": True, "cautious_approach": True},
            ),
            DialogueTurn(
                turn_number=2,
                turn_type=TurnType.NEW_INFORMATION,
                user_message="""Local resolution at the binding site is 4.5A. We tried fitting
                the drug in two orientations and both give reasonable-looking fits.
                How do we decide which is correct?""",
                expected_behaviors=[
                    "4.5A cannot distinguish drug orientations (not enough detail)",
                    "Both fits looking 'reasonable' at 4.5A is expected — you cannot tell",
                    "Biochemical data needed: mutagenesis of binding residues",
                    "Consider molecular dynamics simulations to test stability of each pose",
                    "Don't publish ambiguous ligand placement",
                ],
                failure_modes=[
                    "Suggesting to pick the 'better-looking' fit",
                    "Not acknowledging the resolution limitation",
                ],
                context_dependency="Must connect to local resolution concern from turn 1",
                scoring_criteria={"resolution_limits": True, "suggests_orthogonal_data": True},
            ),
            DialogueTurn(
                turn_number=3,
                turn_type=TurnType.CHALLENGE,
                user_message="""But many published cryo-EM structures at similar resolution
                show ligands. Are they all wrong?""",
                expected_behaviors=[
                    "Not all wrong, but many ligand placements in cryo-EM are indeed questionable",
                    "There's growing concern about ligand validation in cryo-EM",
                    "Some have strong prior knowledge (crystal structures of related complexes)",
                    "Difference density and omit maps can help validate",
                    "Standards are improving — EMDB validation reports now check this",
                ],
                failure_modes=[
                    "Either defending all published structures or dismissing them all",
                    "Not mentioning the ligand validation problem in the field",
                ],
                context_dependency="Must address the broader field concern",
                scoring_criteria={"balanced_view": True, "field_awareness": True},
            ),
        ],
    ),
    # -------------------------------------------------------------------------
    # PLANT BIOLOGY — GENE EDITING
    # -------------------------------------------------------------------------
    MultiTurnDialogue(
        id="mt_plant_001",
        title="CRISPR Gene Editing in Crops",
        dialogue_type=DialogueType.EXPERIMENTAL_DESIGN,
        domain="plant_biology",
        description="Designing CRISPR experiment for crop improvement",
        overall_objective="Plan a rigorous gene editing approach for drought resistance",
        difficulty="easy",
        turns=[
            DialogueTurn(
                turn_number=1,
                turn_type=TurnType.INITIAL_QUESTION,
                user_message="""I want to use CRISPR to knock out a negative regulator of
                drought tolerance in rice (OsDREB2A repressor). I've designed sgRNAs
                targeting exon 2. What's the basic experimental plan?""",
                expected_behaviors=[
                    "Delivery method: Agrobacterium-mediated transformation or biolistics",
                    "Construct: Cas9 + sgRNA in plant expression vector",
                    "Screening: T7 endonuclease assay or sequencing to confirm edits",
                    "Need multiple independent T0 lines (at least 10-20)",
                ],
                failure_modes=[
                    "Not mentioning the need for multiple independent lines",
                    "Assuming mammalian protocols without plant-specific considerations",
                ],
                context_dependency="None - initial question",
                scoring_criteria={"plant_specific": True, "complete_plan": True},
            ),
            DialogueTurn(
                turn_number=2,
                turn_type=TurnType.FOLLOW_UP,
                user_message="""How do I make sure any drought tolerance improvement I see
                is from the gene edit and not from tissue culture variation?""",
                expected_behaviors=[
                    "Somaclonal variation is a real concern in plant transformation",
                    "Use segregating T1 generation: compare edited vs wild-type siblings",
                    "Null segregants (same tissue culture, no edit) as controls",
                    "Test multiple independent edited lines to rule out position effects",
                ],
                failure_modes=[
                    "Not mentioning somaclonal variation",
                    "Not suggesting null segregant controls",
                ],
                context_dependency="Must connect to experimental design from turn 1",
                scoring_criteria={"somaclonal_awareness": True, "proper_controls": True},
            ),
            DialogueTurn(
                turn_number=3,
                turn_type=TurnType.FOLLOW_UP,
                user_message="""If this works, I want to use these edited rice lines commercially.
                Are there regulatory considerations for CRISPR crops?""",
                expected_behaviors=[
                    "Regulatory landscape varies by country",
                    "US: transgene-free edited crops may not be regulated as GMOs",
                    "EU: edited crops currently regulated as GMOs (but laws evolving)",
                    "Important to remove Cas9 transgene by segregation",
                    "Intellectual property considerations for CRISPR technology",
                ],
                failure_modes=[
                    "Ignoring regulatory differences between jurisdictions",
                    "Not mentioning transgene-free requirement",
                ],
                context_dependency="Must connect to commercial implications",
                scoring_criteria={"regulatory_awareness": True, "transgene_free": True},
            ),
        ],
    ),
    # =========================================================================
    # BATCH 2: 10 additional dialogues (mt_ext_015 - mt_ext_024)
    # =========================================================================
    # -------------------------------------------------------------------------
    # NEUROSCIENCE — ALZHEIMER'S BIOMARKER
    # -------------------------------------------------------------------------
    MultiTurnDialogue(
        id="mt_ext_015",
        title="Alzheimer's Biomarker Interpretation",
        dialogue_type=DialogueType.HYPOTHESIS_REFINEMENT,
        domain="neuroscience",
        description="Interpreting conflicting CSF and PET biomarker data in Alzheimer's",
        overall_objective="Develop coherent hypothesis for discordant Alzheimer's biomarkers",
        difficulty="medium",
        turns=[
            DialogueTurn(
                turn_number=1,
                turn_type=TurnType.INITIAL_QUESTION,
                user_message="""A patient has low CSF Aβ42 (suggesting amyloid pathology) but
                their amyloid PET scan is NEGATIVE. The neurologist says one test must
                be wrong. Is that necessarily true?""",
                expected_behaviors=[
                    "Not necessarily wrong — CSF and PET measure different things",
                    "CSF Aβ42 reflects soluble amyloid production/clearance",
                    "PET detects fibrillar amyloid plaques in the brain",
                    "CSF changes can precede PET positivity by years",
                ],
                failure_modes=[
                    "Agreeing one test must be wrong",
                    "Not knowing the temporal sequence of biomarker changes",
                ],
                context_dependency="None - initial question",
                scoring_criteria={"explains_difference": True, "temporal_model": True},
            ),
            DialogueTurn(
                turn_number=2,
                turn_type=TurnType.FOLLOW_UP,
                user_message="""So this could be early-stage amyloid pathology before plaques
                are visible on PET? What other biomarkers could help clarify?""",
                expected_behaviors=[
                    "Correct — could be 'CSF-first' stage in the amyloid cascade",
                    "CSF p-tau and t-tau for neurodegeneration staging",
                    "Plasma biomarkers (p-tau217, p-tau181) as confirmatory",
                    "Follow-up PET in 1-2 years to see if it converts",
                ],
                failure_modes=[
                    "Not suggesting follow-up testing",
                    "Not mentioning newer plasma biomarkers",
                ],
                context_dependency="Must build on temporal staging discussion",
                scoring_criteria={"additional_biomarkers": True, "follow_up_plan": True},
            ),
            DialogueTurn(
                turn_number=3,
                turn_type=TurnType.CHALLENGE,
                user_message="""But couldn't the low CSF Aβ42 be due to something else entirely?
                Pre-analytical issues or a non-Alzheimer's cause?""",
                expected_behaviors=[
                    "Valid point — pre-analytical factors affect CSF Aβ42",
                    "Tube type (polypropylene required), freeze-thaw cycles, collection time",
                    "Non-AD causes of low CSF Aβ42: cerebral amyloid angiopathy, Lewy body disease",
                    "Aβ42/Aβ40 ratio is more robust than Aβ42 alone",
                ],
                failure_modes=[
                    "Dismissing pre-analytical concerns",
                    "Not mentioning Aβ42/40 ratio",
                ],
                context_dependency="Must address validity concerns raised in discussion",
                scoring_criteria={"pre_analytical": True, "ratio_recommendation": True},
            ),
            DialogueTurn(
                turn_number=4,
                turn_type=TurnType.SYNTHESIS,
                user_message="""Given all this, what should the clinical recommendation be for
                this patient?""",
                expected_behaviors=[
                    "Repeat CSF with Aβ42/40 ratio and p-tau",
                    "Consider plasma p-tau217 as confirmatory",
                    "Clinical follow-up with cognitive testing over 12-18 months",
                    "Not sufficient to diagnose AD but warrants monitoring",
                ],
                failure_modes=[
                    "Making definitive diagnosis from discordant data",
                    "Dismissing the findings entirely",
                ],
                context_dependency="Must synthesize all previous biomarker discussions",
                scoring_criteria={"balanced_recommendation": True, "follow_up": True},
            ),
        ],
    ),
    # -------------------------------------------------------------------------
    # STEM CELL — iPSC DIFFERENTIATION
    # -------------------------------------------------------------------------
    MultiTurnDialogue(
        id="mt_ext_016",
        title="iPSC Differentiation for Disease Modelling",
        dialogue_type=DialogueType.EXPERIMENTAL_DESIGN,
        domain="stem_cell",
        description="Designing iPSC-derived cardiomyocyte disease model",
        overall_objective="Plan rigorous iPSC-based cardiac disease modelling experiment",
        difficulty="hard",
        turns=[
            DialogueTurn(
                turn_number=1,
                turn_type=TurnType.INITIAL_QUESTION,
                user_message="""We want to model hypertrophic cardiomyopathy (HCM) using iPSC-
                derived cardiomyocytes from a patient with a MYH7 mutation. We have
                the patient iPSC line. What's the best experimental design?""",
                expected_behaviors=[
                    "Need isogenic control: CRISPR-correct the MYH7 mutation in patient iPSCs",
                    "Unrelated healthy donor iPSCs are insufficient (genetic background differences)",
                    "Differentiation protocol: Wnt modulation (CHIR/IWP2) for cardiomyocytes",
                    "Multiple independent differentiations (biological replicates)",
                ],
                failure_modes=[
                    "Suggesting unrelated healthy donor as primary control",
                    "Not mentioning isogenic correction",
                ],
                context_dependency="None - initial question",
                scoring_criteria={"isogenic_control": True, "differentiation_protocol": True},
            ),
            DialogueTurn(
                turn_number=2,
                turn_type=TurnType.FOLLOW_UP,
                user_message="""We CRISPR-corrected the mutation and confirmed by sequencing.
                Both lines differentiate to >80% cTnT+ cardiomyocytes. But the patient
                line beats slower and cells are visibly larger. Is this already the
                HCM phenotype?""",
                expected_behaviors=[
                    "Larger cells is consistent with hypertrophy (key HCM feature)",
                    "But need to quantify: cell area measurement, sarcomere organization",
                    "Check gene expression markers: ANP, BNP, β-MHC upregulation",
                    "Functional assays: calcium transients, contractility",
                    "Day of analysis matters — iPSC-CMs mature over time",
                ],
                failure_modes=[
                    "Accepting visual observation as sufficient characterization",
                    "Not suggesting quantitative assays",
                ],
                context_dependency="Must build on isogenic comparison design",
                scoring_criteria={"quantitative_assays": True, "hypertrophy_markers": True},
            ),
            DialogueTurn(
                turn_number=3,
                turn_type=TurnType.CHALLENGE,
                user_message="""A reviewer says iPSC-derived cardiomyocytes are immature (fetal-like)
                and can't model adult-onset HCM. How do we address this criticism?""",
                expected_behaviors=[
                    "Valid concern — iPSC-CMs are indeed immature",
                    "But many HCM phenotypes ARE recapitulated (hypertrophy, arrhythmia, metabolic changes)",
                    "Maturation strategies: long-term culture, 3D engineered heart tissue, electrical pacing",
                    "Multiple iPSC-HCM papers in Nature and Cell validate the approach",
                ],
                failure_modes=[
                    "Dismissing the immaturity concern",
                    "Agreeing the model is useless",
                ],
                context_dependency="Must address limitation while defending the model",
                scoring_criteria={"acknowledges_limitation": True, "defends_model": True},
            ),
            DialogueTurn(
                turn_number=4,
                turn_type=TurnType.FOLLOW_UP,
                user_message="""We want to test drugs on these cardiomyocytes. How should we
                design the drug screening experiment?""",
                expected_behaviors=[
                    "Dose-response curves (not single dose) for each compound",
                    "Both patient and isogenic lines treated in parallel",
                    "Functional readouts: contractility (video, impedance), calcium handling",
                    "Include known HCM drugs as positive controls (mavacamten)",
                    "Multiple differentiation batches to assess reproducibility",
                ],
                failure_modes=[
                    "Not including isogenic control in drug testing",
                    "Not suggesting positive control drugs",
                ],
                context_dependency="Must integrate disease model with drug testing design",
                scoring_criteria={"drug_screen_design": True, "positive_controls": True},
            ),
        ],
    ),
    # -------------------------------------------------------------------------
    # FLOW CYTOMETRY — PANEL TROUBLESHOOTING
    # -------------------------------------------------------------------------
    MultiTurnDialogue(
        id="mt_ext_017",
        title="Flow Cytometry Panel Troubleshooting",
        dialogue_type=DialogueType.TROUBLESHOOTING,
        domain="flow_cytometry",
        description="Diagnosing compensation and gating issues in multicolour panel",
        overall_objective="Fix compensation artefacts in a 10-colour flow panel",
        difficulty="medium",
        turns=[
            DialogueTurn(
                turn_number=1,
                turn_type=TurnType.INITIAL_QUESTION,
                user_message="""Our 10-colour flow cytometry panel for T cell phenotyping is giving
                weird results. The CD4-PE population appears to be PE-Cy7 positive even
                though we know CD4 T cells shouldn't express that marker. What's happening?""",
                expected_behaviors=[
                    "Classic spillover/compensation issue: PE spills into PE-Cy7 channel",
                    "Check if compensation matrix was properly calculated",
                    "Single-colour compensation controls must match the fluorochrome brightness",
                    "Ask if they used beads or cells for compensation",
                ],
                failure_modes=[
                    "Not recognizing this as a compensation issue",
                    "Suggesting biological explanation for the artefact",
                ],
                context_dependency="None - initial question",
                scoring_criteria={"identifies_compensation": True, "asks_about_controls": True},
            ),
            DialogueTurn(
                turn_number=2,
                turn_type=TurnType.NEW_INFORMATION,
                user_message="""We used compensation beads for all colours. But our PE antibody
                (CD4-PE) is much brighter than the PE bead. Could this cause a problem?""",
                expected_behaviors=[
                    "Yes — if antibody is brighter than bead, compensation will be underestimated",
                    "Compensation beads must be at least as bright as the stained sample",
                    "For very bright PE antibodies, use stained cells instead of beads",
                    "Can also try reducing the PE antibody amount (titrate)",
                ],
                failure_modes=[
                    "Not recognizing the brightness mismatch issue",
                    "Saying beads are always sufficient",
                ],
                context_dependency="Must connect to compensation discussion from turn 1",
                scoring_criteria={"brightness_mismatch": True, "practical_fix": True},
            ),
            DialogueTurn(
                turn_number=3,
                turn_type=TurnType.FOLLOW_UP,
                user_message="""We fixed the compensation with PE-stained cells. But now we notice
                a population of cells that are double-positive for CD4 and CD8. Is this
                real or still an artefact?""",
                expected_behaviors=[
                    "CD4+CD8+ cells can be real (thymocytes, activated T cells in some conditions)",
                    "But first rule out: spreading error (especially with tandem dyes)",
                    "Check: are these in the lymphocyte gate? What tissue source?",
                    "If peripheral blood: likely <1%, higher suggests residual artefact",
                ],
                failure_modes=[
                    "Immediately dismissing as artefact",
                    "Immediately accepting as real without verification",
                ],
                context_dependency="Must consider both biological and technical explanations",
                scoring_criteria={"considers_both": True, "verification_steps": True},
            ),
        ],
    ),
    # -------------------------------------------------------------------------
    # PROTEOMICS — PHOSPHOPROTEOMICS INTERPRETATION
    # -------------------------------------------------------------------------
    MultiTurnDialogue(
        id="mt_ext_018",
        title="Phosphoproteomics Time-Course Interpretation",
        dialogue_type=DialogueType.DATA_INTERPRETATION,
        domain="proteomics",
        description="Interpreting temporal phosphoproteomics data after growth factor stimulation",
        overall_objective="Extract biological insight from complex phosphoproteomics dataset",
        difficulty="hard",
        turns=[
            DialogueTurn(
                turn_number=1,
                turn_type=TurnType.INITIAL_QUESTION,
                user_message="""We did phosphoproteomics after EGF stimulation at 0, 2, 5, 15,
                and 60 minutes. We quantified 8,000 phosphosites. How should we
                analyse the temporal dynamics?""",
                expected_behaviors=[
                    "Cluster phosphosites by temporal profile (fuzzy c-means, DPGP)",
                    "Expected patterns: immediate-early, delayed, sustained, transient",
                    "Kinase-substrate enrichment analysis (KSEA) for each time point",
                    "Normalize to the 0-minute baseline for fold-change calculation",
                ],
                failure_modes=[
                    "Treating each time point independently without temporal modelling",
                    "Not suggesting kinase activity inference",
                ],
                context_dependency="None - initial question",
                scoring_criteria={"temporal_clustering": True, "kinase_analysis": True},
            ),
            DialogueTurn(
                turn_number=2,
                turn_type=TurnType.FOLLOW_UP,
                user_message="""We clustered the data and found 5 temporal patterns. One cluster
                peaks at 2 min then drops — these are mostly MAPK substrates. Another
                cluster peaks at 15-60 min — transcription factor targets. Does this
                make biological sense?""",
                expected_behaviors=[
                    "Yes — canonical EGFR signalling: MAPK is rapid/transient, TF activation is delayed",
                    "2 min MAPK substrates = direct ERK targets",
                    "15-60 min = secondary signalling and transcriptional response",
                    "Check if the intermediate cluster (5 min) includes PI3K/AKT targets",
                ],
                failure_modes=[
                    "Not validating against known EGFR signalling biology",
                    "Not asking about intermediate time points",
                ],
                context_dependency="Must connect to EGF signalling knowledge",
                scoring_criteria={"validates_biology": True, "asks_about_pi3k": True},
            ),
            DialogueTurn(
                turn_number=3,
                turn_type=TurnType.NEW_INFORMATION,
                user_message="""Interesting — some phosphosites in the delayed cluster are on
                proteins we didn't know were EGF-responsive. One is a metabolic enzyme
                (PFKFB3 S461). Is this worth following up?""",
                expected_behaviors=[
                    "PFKFB3 regulates glycolysis (phosphofructokinase activator)",
                    "EGF driving glycolytic enzyme phosphorylation = Warburg effect connection",
                    "Delayed kinetics suggest it's downstream of transcriptional changes",
                    "Worth validating: targeted phospho-Western, functional metabolic assays",
                ],
                failure_modes=[
                    "Not recognizing PFKFB3's role in glycolysis",
                    "Not connecting to cancer metabolism",
                ],
                context_dependency="Must connect novel finding to known biology",
                scoring_criteria={"identifies_pfkfb3": True, "suggests_validation": True},
            ),
            DialogueTurn(
                turn_number=4,
                turn_type=TurnType.CHALLENGE,
                user_message="""Our PI says we need to validate ALL phosphosites by Western blot
                before publishing. That's 8,000 sites. Is that reasonable?""",
                expected_behaviors=[
                    "No — impossible to validate 8,000 sites individually",
                    "Standard practice: validate key findings (top 10-20 hits)",
                    "Orthogonal validation of pathway-level conclusions is more appropriate",
                    "Cite ENCODE/ProteomeXchange standards for mass spec data deposition",
                ],
                failure_modes=[
                    "Agreeing that all sites need validation",
                    "Not suggesting a practical validation strategy",
                ],
                context_dependency="Must provide realistic publication strategy",
                scoring_criteria={"practical_advice": True, "validation_strategy": True},
            ),
        ],
    ),
    # -------------------------------------------------------------------------
    # MICROBIOME — GUT-BRAIN AXIS
    # -------------------------------------------------------------------------
    MultiTurnDialogue(
        id="mt_ext_019",
        title="Microbiome and Neuropsychiatric Disease",
        dialogue_type=DialogueType.HYPOTHESIS_REFINEMENT,
        domain="microbiome",
        description="Evaluating gut-brain axis hypothesis in depression",
        overall_objective="Critically assess microbiome-depression association study",
        difficulty="medium",
        turns=[
            DialogueTurn(
                turn_number=1,
                turn_type=TurnType.INITIAL_QUESTION,
                user_message="""We found that depressed patients have lower Lactobacillus abundance
                in stool compared to healthy controls (16S rRNA sequencing, n=50 per group).
                Does this mean gut bacteria cause depression?""",
                expected_behaviors=[
                    "Correlation does not equal causation",
                    "Depression itself changes diet, medication, sleep — all affect microbiome",
                    "Reverse causation: depression → lifestyle changes → microbiome changes",
                    "Ask about confounders: diet, medication (especially antidepressants), antibiotics",
                ],
                failure_modes=[
                    "Accepting causal claim from cross-sectional data",
                    "Not mentioning confounders",
                ],
                context_dependency="None - initial question",
                scoring_criteria={"causal_skepticism": True, "confounders": True},
            ),
            DialogueTurn(
                turn_number=2,
                turn_type=TurnType.FOLLOW_UP,
                user_message="""Good point about confounders. 15 of our depressed patients are on
                SSRIs and 8 are on atypical antipsychotics. Should we exclude them?""",
                expected_behaviors=[
                    "Excluding = selection bias; including without adjustment = confounding",
                    "Better: adjust for medication status in analysis (stratify or covariate)",
                    "SSRIs have known antimicrobial properties (affect microbiome directly)",
                    "Report both adjusted and unadjusted results for transparency",
                ],
                failure_modes=[
                    "Simply saying to exclude medication users",
                    "Not knowing SSRIs affect microbiome",
                ],
                context_dependency="Must build on confounder discussion",
                scoring_criteria={"adjustment_strategy": True, "ssri_microbiome": True},
            ),
            DialogueTurn(
                turn_number=3,
                turn_type=TurnType.FOLLOW_UP,
                user_message="""After adjusting for medications, diet, and BMI, the Lactobacillus
                difference is no longer significant. But our PI still wants to do a
                probiotic trial. Is there justification?""",
                expected_behaviors=[
                    "If the association disappears after confounder adjustment, the original finding was likely confounded",
                    "Probiotic trials exist but with mixed results in depression",
                    "Could still justify an exploratory trial, but not based on THIS data",
                    "Need to cite existing probiotic-depression trial literature",
                ],
                failure_modes=[
                    "Encouraging trial based on null result",
                    "Completely dismissing the idea without nuance",
                ],
                context_dependency="Must integrate null finding with broader field",
                scoring_criteria={"honest_assessment": True, "literature_context": True},
            ),
            DialogueTurn(
                turn_number=4,
                turn_type=TurnType.SYNTHESIS,
                user_message="""What would be a better study design to actually test whether
                microbiome changes contribute to depression?""",
                expected_behaviors=[
                    "Longitudinal study: track microbiome before depression onset",
                    "Fecal microbiota transplant (FMT) from depressed → germ-free mice",
                    "Mendelian randomisation using genetic variants affecting microbiome",
                    "Interventional trial with proper controls (placebo probiotic)",
                ],
                failure_modes=[
                    "Only suggesting more cross-sectional studies",
                    "Not mentioning animal models for causal testing",
                ],
                context_dependency="Must synthesize all limitations discussed previously",
                scoring_criteria={"causal_designs": True, "animal_models": True},
            ),
        ],
    ),
    # -------------------------------------------------------------------------
    # CRISPR SCREEN — DESIGN
    # -------------------------------------------------------------------------
    MultiTurnDialogue(
        id="mt_ext_020",
        title="Designing a Focused CRISPR Screen",
        dialogue_type=DialogueType.EXPERIMENTAL_DESIGN,
        domain="crispr_screen",
        description="Planning a focused CRISPR screen for metabolic vulnerabilities",
        overall_objective="Design a well-controlled targeted CRISPR screen",
        difficulty="hard",
        turns=[
            DialogueTurn(
                turn_number=1,
                turn_type=TurnType.INITIAL_QUESTION,
                user_message="""We want to find metabolic vulnerabilities in AML cells. Should we
                do a genome-wide CRISPR screen or a focused metabolic gene library?
                We have limited budget.""",
                expected_behaviors=[
                    "Focused library is more practical with limited budget",
                    "Metabolism library (~3,000 genes) requires fewer cells and less sequencing",
                    "Genome-wide (18,000+ genes) needs 500+ cells per sgRNA = 40M+ cells",
                    "Focused screen has better statistical power per gene with fewer resources",
                ],
                failure_modes=[
                    "Always recommending genome-wide without considering constraints",
                    "Not discussing cell number requirements",
                ],
                context_dependency="None - initial question",
                scoring_criteria={"practical_advice": True, "resource_consideration": True},
            ),
            DialogueTurn(
                turn_number=2,
                turn_type=TurnType.FOLLOW_UP,
                user_message="""We'll use a focused metabolism library (3,000 genes, 6 sgRNAs per gene).
                For the screen, should we compare AML cells to normal bone marrow cells
                to find AML-specific vulnerabilities?""",
                expected_behaviors=[
                    "Differential screen (AML vs normal) is ideal for specificity",
                    "But normal bone marrow is hard to transduce and culture",
                    "Alternative: compare AML to isogenic non-malignant (remove oncogene)",
                    "Or: compare multiple AML lines to find shared vulnerabilities",
                ],
                failure_modes=[
                    "Not acknowledging the difficulty of using primary normal cells",
                    "Not suggesting practical alternatives",
                ],
                context_dependency="Must build on focused library decision",
                scoring_criteria={"practical_comparison": True, "acknowledges_difficulty": True},
            ),
            DialogueTurn(
                turn_number=3,
                turn_type=TurnType.CHALLENGE,
                user_message="""A colleague suggests we should use CRISPRi instead of CRISPRko
                because metabolic genes might have essential roles and knockouts could
                just kill all cells. Is that a valid concern?""",
                expected_behaviors=[
                    "Valid concern — essential gene knockouts are depleted regardless of condition",
                    "CRISPRi allows partial knockdown (gene expression reduced, not eliminated)",
                    "CRISPRi better for essential genes and dose-dependent phenotypes",
                    "Trade-off: CRISPRi may miss phenotypes requiring complete loss",
                ],
                failure_modes=[
                    "Dismissing CRISPRi as inferior",
                    "Not explaining the essential gene problem",
                ],
                context_dependency="Must address essential gene concern in metabolic screen context",
                scoring_criteria={"valid_concern": True, "crispri_advantages": True},
            ),
            DialogueTurn(
                turn_number=4,
                turn_type=TurnType.SYNTHESIS,
                user_message="""OK, so final plan: CRISPRi metabolism library in 3 AML cell lines.
                What controls do we need and how do we analyse the data?""",
                expected_behaviors=[
                    "Controls: non-targeting sgRNAs (500+), known essential genes, known non-essential",
                    "T0 baseline sample before any selection",
                    "Analysis: MAGeCK-MLE or similar, with non-targeting as null distribution",
                    "Validate top hits individually with 2-3 independent sgRNAs per gene",
                ],
                failure_modes=[
                    "Not mentioning T0 sample",
                    "Not specifying control sgRNA requirements",
                ],
                context_dependency="Must bring together all design decisions into final plan",
                scoring_criteria={"complete_controls": True, "analysis_plan": True},
            ),
        ],
    ),
    # -------------------------------------------------------------------------
    # CELL CULTURE — BASIC TROUBLESHOOTING
    # -------------------------------------------------------------------------
    MultiTurnDialogue(
        id="mt_ext_021",
        title="Cell Culture Contamination Troubleshooting",
        dialogue_type=DialogueType.TROUBLESHOOTING,
        domain="cell_culture",
        description="Diagnosing and resolving cell culture contamination",
        overall_objective="Identify contamination source and implement corrective measures",
        difficulty="easy",
        turns=[
            DialogueTurn(
                turn_number=1,
                turn_type=TurnType.INITIAL_QUESTION,
                user_message="""My cell cultures keep dying! The medium turns yellow within 24 hours
                and there are floating clumps when I look under the microscope. No one
                else in the lab has this problem. What's going on?""",
                expected_behaviors=[
                    "Yellow medium = acidic pH, likely bacterial contamination",
                    "Floating clumps could be bacterial colonies or dead cell aggregates",
                    "Ask: is it in all flasks or specific ones? Fresh medium bottle?",
                    "The fact only you have the problem suggests technique issue",
                ],
                failure_modes=[
                    "Not suspecting contamination",
                    "Not asking diagnostic questions",
                ],
                context_dependency="None - initial question",
                scoring_criteria={"identifies_contamination": True, "diagnostic_questions": True},
            ),
            DialogueTurn(
                turn_number=2,
                turn_type=TurnType.NEW_INFORMATION,
                user_message="""It happens in every flask I passage but not in flasks from other
                people. I checked: we all share the same medium bottle and PBS. Could
                it be my pipetting technique or my hood?""",
                expected_behaviors=[
                    "Shared reagents are fine (others are clean) = your technique or tools",
                    "Check your personal pipette tips, pipettes, hood surface",
                    "Common issue: reusing or cross-contaminating pipette tips",
                    "Ask about water bath for media warming (common contamination source)",
                ],
                failure_modes=[
                    "Blaming shared reagents when others are unaffected",
                    "Not asking about the water bath",
                ],
                context_dependency="Must focus on user-specific contamination source",
                scoring_criteria={"technique_focus": True, "water_bath": True},
            ),
            DialogueTurn(
                turn_number=3,
                turn_type=TurnType.FOLLOW_UP,
                user_message="""You were right — the water bath hasn't been cleaned in months and
                has green stuff growing in it. I warm my medium there. What should I do
                to decontaminate and prevent this?""",
                expected_behaviors=[
                    "Clean water bath with disinfectant (Virkon, 70% ethanol)",
                    "Add copper sulfate or commercial water bath additive to prevent growth",
                    "Spray bottles with 70% ethanol before placing in hood",
                    "Alternative: warm medium in 37°C incubator instead of water bath",
                ],
                failure_modes=[
                    "Not providing practical decontamination steps",
                    "Not suggesting prevention measures",
                ],
                context_dependency="Must provide solution building on diagnosis",
                scoring_criteria={"decontamination": True, "prevention": True},
            ),
        ],
    ),
    # -------------------------------------------------------------------------
    # SINGLE-CELL — TRAJECTORY ANALYSIS
    # -------------------------------------------------------------------------
    MultiTurnDialogue(
        id="mt_ext_022",
        title="Single-Cell Trajectory Analysis Interpretation",
        dialogue_type=DialogueType.DATA_INTERPRETATION,
        domain="single_cell",
        description="Interpreting pseudotime trajectory in hematopoietic differentiation",
        overall_objective="Critically evaluate trajectory inference from scRNA-seq",
        difficulty="hard",
        turns=[
            DialogueTurn(
                turn_number=1,
                turn_type=TurnType.INITIAL_QUESTION,
                user_message="""We ran Monocle3 trajectory analysis on our bone marrow scRNA-seq
                data and it shows a branching tree with HSCs at the root, branching
                into myeloid and lymphoid lineages. The pseudotime ordering looks clean.
                Can we trust this represents real differentiation trajectories?""",
                expected_behaviors=[
                    "Pseudotime captures transcriptional similarity, not actual time",
                    "Trajectory methods assume continuous gradients — not always biological reality",
                    "Multiple trajectory methods should give concordant results (Monocle, Slingshot, PAGA)",
                    "RNA velocity (scVelo) can add directionality information",
                ],
                failure_modes=[
                    "Accepting pseudotime as literal temporal ordering",
                    "Not suggesting validation with other methods",
                ],
                context_dependency="None - initial question",
                scoring_criteria={"pseudotime_caveats": True, "suggests_validation": True},
            ),
            DialogueTurn(
                turn_number=2,
                turn_type=TurnType.FOLLOW_UP,
                user_message="""We ran RNA velocity and it generally agrees with the Monocle
                trajectory direction. But there's one branch where velocity arrows
                point BACKWARDS (from mature cells toward progenitors). Is our
                analysis wrong?""",
                expected_behaviors=[
                    "Backward velocity can be real: dedifferentiation or transdifferentiation",
                    "But more commonly it's a technical artefact of RNA velocity",
                    "Spliced/unspliced ratio can be unreliable for lowly expressed genes",
                    "Check which genes drive the backward velocity — are they biologically relevant?",
                ],
                failure_modes=[
                    "Dismissing backward velocity as always an error",
                    "Not suggesting to check driving genes",
                ],
                context_dependency="Must connect to trajectory validation discussion",
                scoring_criteria={"considers_both": True, "gene_level_check": True},
            ),
            DialogueTurn(
                turn_number=3,
                turn_type=TurnType.NEW_INFORMATION,
                user_message="""The backward velocity branch corresponds to cells expressing both
                myeloid and lymphoid markers. Could these be bipotent progenitors or
                are they doublets?""",
                expected_behaviors=[
                    "Important to distinguish: bipotent progenitors are real biology, doublets are artefact",
                    "Check doublet scores (DoubletFinder/Scrublet) for these cells",
                    "If not doublets: check if they express known bipotent progenitor markers (LMPP markers)",
                    "Their position on the trajectory (between branches) is consistent with either interpretation",
                ],
                failure_modes=[
                    "Not considering the doublet possibility",
                    "Not mentioning known progenitor markers for validation",
                ],
                context_dependency="Must integrate trajectory and doublet concerns",
                scoring_criteria={"doublet_check": True, "progenitor_markers": True},
            ),
            DialogueTurn(
                turn_number=4,
                turn_type=TurnType.SYNTHESIS,
                user_message="""After removing predicted doublets, the mixed-marker cells remain.
                How should we validate these as true bipotent progenitors?""",
                expected_behaviors=[
                    "FACS sort the mixed-marker population",
                    "Single-cell colony assays: can one cell give rise to both lineages?",
                    "In vivo transplantation into irradiated mice",
                    "Clonal barcoding (LARRY, CellTagging) for lineage tracing",
                ],
                failure_modes=[
                    "Only suggesting computational validation",
                    "Not mentioning functional (wet-lab) validation",
                ],
                context_dependency="Must propose definitive experimental validation",
                scoring_criteria={"functional_validation": True, "lineage_tracing": True},
            ),
        ],
    ),
    # -------------------------------------------------------------------------
    # PEER REVIEW — CLINICAL TRIAL
    # -------------------------------------------------------------------------
    MultiTurnDialogue(
        id="mt_ext_023",
        title="Peer Reviewing a Clinical Trial Paper",
        dialogue_type=DialogueType.PEER_REVIEW,
        domain="clinical_trial",
        description="Reviewing a randomised controlled trial manuscript for methodological issues",
        overall_objective="Identify key methodological concerns in an RCT report",
        difficulty="medium",
        turns=[
            DialogueTurn(
                turn_number=1,
                turn_type=TurnType.INITIAL_QUESTION,
                user_message="""I'm reviewing a paper for a journal. It's a phase III trial of
                a new targeted therapy for NSCLC. The trial enrolled 500 patients
                randomised 1:1. The abstract claims 'significant improvement in OS'.
                What should I look for first?""",
                expected_behaviors=[
                    "Check primary endpoint: was OS the pre-specified primary or changed?",
                    "Look at the CONSORT flow diagram for dropout/crossover rates",
                    "Check if analysis is intention-to-treat",
                    "Look at the hazard ratio confidence interval and maturity of data",
                ],
                failure_modes=[
                    "Only checking the p-value",
                    "Not asking about pre-specified primary endpoint",
                ],
                context_dependency="None - initial question",
                scoring_criteria={"systematic_review": True, "primary_endpoint": True},
            ),
            DialogueTurn(
                turn_number=2,
                turn_type=TurnType.NEW_INFORMATION,
                user_message="""The original protocol (registered on clinicaltrials.gov) had PFS
                as the primary endpoint, not OS. PFS was not significant (HR=0.85,
                p=0.12). But OS was significant (HR=0.70, p=0.01). The paper presents
                OS as the 'key finding'. Is this a problem?""",
                expected_behaviors=[
                    "Major problem: endpoint switching (post-hoc promotion of secondary to primary)",
                    "If PFS was primary and failed, OS should be interpreted as exploratory/supportive",
                    "This is a common form of selective reporting bias",
                    "Should be flagged prominently in the review",
                ],
                failure_modes=[
                    "Accepting the endpoint switch without comment",
                    "Not checking the trial registry",
                ],
                context_dependency="Must flag the discrepancy with registered protocol",
                scoring_criteria={"identifies_switching": True, "registry_check": True},
            ),
            DialogueTurn(
                turn_number=3,
                turn_type=TurnType.FOLLOW_UP,
                user_message="""I also notice that 30% of control arm patients crossed over to
                the experimental drug after progression. Could this affect the OS
                analysis?""",
                expected_behaviors=[
                    "Yes — crossover dilutes the OS difference between arms",
                    "Paradoxically, OS is significant despite crossover, which could mean the true effect is larger",
                    "But crossover also complicates interpretation (IPCW or RPSFT methods exist)",
                    "Should request sensitivity analysis adjusting for crossover",
                ],
                failure_modes=[
                    "Saying crossover invalidates the OS result",
                    "Ignoring crossover impact on interpretation",
                ],
                context_dependency="Must integrate crossover with endpoint switching concern",
                scoring_criteria={"crossover_impact": True, "suggests_sensitivity": True},
            ),
        ],
    ),
    # -------------------------------------------------------------------------
    # EPIGENETICS — DNA METHYLATION
    # -------------------------------------------------------------------------
    MultiTurnDialogue(
        id="mt_ext_024",
        title="DNA Methylation Changes in Ageing",
        dialogue_type=DialogueType.HYPOTHESIS_REFINEMENT,
        domain="epigenetics",
        description="Interpreting age-related DNA methylation changes and epigenetic clocks",
        overall_objective="Critically evaluate epigenetic clock findings",
        difficulty="medium",
        turns=[
            DialogueTurn(
                turn_number=1,
                turn_type=TurnType.INITIAL_QUESTION,
                user_message="""We measured DNA methylation (EPIC array) in blood samples from
                100 individuals aged 20-80. We calculated the Horvath epigenetic age
                for each person. Some individuals have epigenetic age 10 years OLDER
                than their chronological age. What does this mean?""",
                expected_behaviors=[
                    "Epigenetic age acceleration = biological age > chronological age",
                    "Associated with increased mortality risk and age-related diseases",
                    "But the clock is a predictor trained on data — not a mechanistic measure",
                    "Ask about health status of those with acceleration (disease, smoking, obesity)",
                ],
                failure_modes=[
                    "Treating epigenetic age as literal biological age",
                    "Not asking about health confounders",
                ],
                context_dependency="None - initial question",
                scoring_criteria={"acceleration_concept": True, "confounders": True},
            ),
            DialogueTurn(
                turn_number=2,
                turn_type=TurnType.FOLLOW_UP,
                user_message="""The accelerated individuals are mostly smokers and have higher BMI.
                After adjusting for smoking and BMI, the acceleration is reduced but
                still present. Is the remaining acceleration 'real' biological ageing?""",
                expected_behaviors=[
                    "Residual acceleration after adjustment could be 'intrinsic' ageing",
                    "But unmeasured confounders may still explain it",
                    "Different epigenetic clocks capture different aspects (Horvath, Hannum, GrimAge, PhenoAge)",
                    "GrimAge includes smoking/plasma protein surrogates — might be more informative",
                ],
                failure_modes=[
                    "Claiming residual acceleration is definitively intrinsic ageing",
                    "Not mentioning different clock types",
                ],
                context_dependency="Must build on confounder discussion",
                scoring_criteria={"multiple_clocks": True, "residual_confounding": True},
            ),
            DialogueTurn(
                turn_number=3,
                turn_type=TurnType.CHALLENGE,
                user_message="""A reviewer asks: 'How do you know the methylation changes CAUSE
                ageing and aren't just a consequence of ageing?' How should we respond?""",
                expected_behaviors=[
                    "Legitimate question — most methylation clocks are associative, not causal",
                    "Some evidence from Yamanaka reprogramming (reversing methylation reverses age markers)",
                    "Mendelian randomisation approaches are being explored",
                    "Honest answer: we don't know if changes are causal, correlative, or consequence",
                ],
                failure_modes=[
                    "Claiming causality without evidence",
                    "Not mentioning reprogramming experiments",
                ],
                context_dependency="Must address causality question honestly",
                scoring_criteria={"honest_uncertainty": True, "reprogramming_evidence": True},
            ),
            DialogueTurn(
                turn_number=4,
                turn_type=TurnType.SYNTHESIS,
                user_message="""Given all these caveats, is there any clinical utility to
                epigenetic clocks right now?""",
                expected_behaviors=[
                    "Research tool: yes (aging research, clinical trial stratification)",
                    "Clinical utility: still limited — not FDA-approved for clinical decisions",
                    "Emerging applications: life insurance risk assessment, anti-ageing intervention trials",
                    "Need prospective validation studies linking clock acceleration to outcomes",
                ],
                failure_modes=[
                    "Overpromising clinical utility",
                    "Dismissing the entire field as useless",
                ],
                context_dependency="Must synthesize caveats with practical utility",
                scoring_criteria={"balanced_assessment": True, "current_applications": True},
            ),
        ],
    ),
]
