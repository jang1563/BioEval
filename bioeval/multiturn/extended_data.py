"""
Extended Multi-Turn dialogue scenarios.

Additional scientific collaboration domains beyond the base tier.
"""

from bioeval.multiturn.dialogues import (
    DialogueTurn,
    DialogueType,
    MultiTurnDialogue,
    TurnType,
)

EXTENDED_DIALOGUES = [
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
