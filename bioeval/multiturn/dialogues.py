"""
Multi-Turn Scientific Dialogue Module

Tests ability to:
1. Maintain context across multiple exchanges
2. Refine hypotheses based on new information
3. Ask clarifying questions
4. Build on previous responses
5. Handle corrections gracefully
6. Navigate iterative experimental design

This simulates real scientific collaboration where ideas evolve through discussion.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

from bioeval.utils.logging import get_logger

_logger = get_logger(__name__)


class DialogueType(Enum):
    """Types of multi-turn dialogues."""

    HYPOTHESIS_REFINEMENT = "hypothesis_refinement"
    EXPERIMENTAL_DESIGN = "experimental_design"
    TROUBLESHOOTING = "troubleshooting"
    LITERATURE_DISCUSSION = "literature_discussion"
    DATA_INTERPRETATION = "data_interpretation"
    PEER_REVIEW = "peer_review"


class TurnType(Enum):
    """Types of dialogue turns."""

    INITIAL_QUESTION = "initial_question"
    FOLLOW_UP = "follow_up"
    CLARIFICATION_REQUEST = "clarification_request"
    NEW_INFORMATION = "new_information"
    CHALLENGE = "challenge"
    CORRECTION = "correction"
    SYNTHESIS = "synthesis"


@dataclass
class DialogueTurn:
    """Single turn in a dialogue."""

    turn_number: int
    turn_type: TurnType
    user_message: str
    expected_behaviors: list[str]  # What model should do
    failure_modes: list[str]  # Common mistakes
    context_dependency: str  # What from previous turns matters
    scoring_criteria: dict = field(default_factory=dict)


@dataclass
class MultiTurnDialogue:
    """Complete multi-turn dialogue scenario."""

    id: str
    title: str
    dialogue_type: DialogueType
    domain: str
    description: str
    turns: list[DialogueTurn]
    overall_objective: str
    requires_memory: bool = True  # Must remember previous turns
    difficulty: str = "medium"


# =============================================================================
# MULTI-TURN DIALOGUES
# =============================================================================

DIALOGUES = [
    # -------------------------------------------------------------------------
    # HYPOTHESIS REFINEMENT
    # -------------------------------------------------------------------------
    MultiTurnDialogue(
        id="mt_hyp_001",
        title="Refining a Drug Resistance Hypothesis",
        dialogue_type=DialogueType.HYPOTHESIS_REFINEMENT,
        domain="drug_response",
        description="Scientist discusses mechanism of acquired drug resistance",
        overall_objective="Iteratively refine hypothesis about resistance mechanism based on new data",
        difficulty="hard",
        turns=[
            DialogueTurn(
                turn_number=1,
                turn_type=TurnType.INITIAL_QUESTION,
                user_message="""Our EGFR-mutant lung cancer cells developed resistance to erlotinib 
                after 6 months of treatment. What are the most likely mechanisms?""",
                expected_behaviors=[
                    "List common resistance mechanisms: T790M mutation, MET amplification, etc.",
                    "Suggest diagnostic tests to distinguish mechanisms",
                ],
                failure_modes=["Giving only one mechanism", "Not suggesting how to test"],
                context_dependency="None - initial question",
                scoring_criteria={"coverage": "Lists 3+ mechanisms", "actionable": "Suggests tests"},
            ),
            DialogueTurn(
                turn_number=2,
                turn_type=TurnType.NEW_INFORMATION,
                user_message="""We sequenced the resistant cells. No T790M mutation found. 
                What should we check next?""",
                expected_behaviors=[
                    "Acknowledge T790M ruled out",
                    "Suggest alternative mechanisms: MET, HER2, histological transformation",
                    "Recommend specific tests (FISH for MET, IHC for markers)",
                ],
                failure_modes=["Suggesting T790M testing again", "Not updating hypothesis based on new info"],
                context_dependency="Must remember T790M was ruled out",
                scoring_criteria={"updates_hypothesis": True, "suggests_alternatives": True},
            ),
            DialogueTurn(
                turn_number=3,
                turn_type=TurnType.NEW_INFORMATION,
                user_message="""MET FISH showed MET amplification (gene copy number >10). 
                Does this explain the resistance? What treatment would you suggest?""",
                expected_behaviors=[
                    "Confirm MET amplification as likely resistance mechanism",
                    "Explain MET bypass signaling",
                    "Suggest combination therapy (EGFR + MET inhibitor)",
                    "Mention specific drugs (capmatinib, tepotinib)",
                ],
                failure_modes=["Not connecting MET to EGFR resistance", "Not suggesting treatment change"],
                context_dependency="Must connect to initial erlotinib resistance question",
                scoring_criteria={"mechanism_correct": True, "treatment_suggestion": True},
            ),
            DialogueTurn(
                turn_number=4,
                turn_type=TurnType.CHALLENGE,
                user_message="""But MET amplification is also present in the pre-treatment sample 
                at low levels (copy number 4). Is MET amplification really the cause, or was it 
                selected for during treatment?""",
                expected_behaviors=[
                    "Recognize the nuance - pre-existing vs acquired",
                    "Explain clonal selection under drug pressure",
                    "Acknowledge both interpretations are possible",
                    "Suggest it's likely selection of pre-existing clone",
                ],
                failure_modes=["Ignoring the pre-treatment data", "Not understanding clonal evolution"],
                context_dependency="Must integrate all previous information",
                scoring_criteria={"nuanced_response": True, "understands_evolution": True},
            ),
        ],
    ),
    MultiTurnDialogue(
        id="mt_hyp_002",
        title="Understanding Unexpected Knockout Phenotype",
        dialogue_type=DialogueType.HYPOTHESIS_REFINEMENT,
        domain="knockout_prediction",
        description="Discussing unexpected results from gene knockout experiment",
        overall_objective="Develop explanation for unexpected result through iterative discussion",
        difficulty="medium",
        turns=[
            DialogueTurn(
                turn_number=1,
                turn_type=TurnType.INITIAL_QUESTION,
                user_message="""We knocked out MYC in our cancer cell line expecting the cells to die,
                but they're growing normally. This contradicts published data. What could explain this?""",
                expected_behaviors=[
                    "Express surprise - MYC is usually essential",
                    "Suggest possible explanations: incomplete KO, MYCN compensation, etc.",
                    "Ask clarifying questions about validation",
                ],
                failure_modes=["Accepting result without questioning", "Not suggesting alternatives"],
                context_dependency="None - initial question",
                scoring_criteria={"questions_result": True, "suggests_explanations": True},
            ),
            DialogueTurn(
                turn_number=2,
                turn_type=TurnType.CLARIFICATION_REQUEST,
                user_message="""Good questions. Our Western blot shows complete loss of MYC protein.
                We used 3 different sgRNAs and all gave same result. What else could it be?""",
                expected_behaviors=[
                    "Acknowledge thorough validation",
                    "Shift to biological explanations: MYCN/MYCL compensation",
                    "Suggest checking other MYC family members",
                    "Consider cell line-specific wiring",
                ],
                failure_modes=["Continuing to question KO validity", "Not considering paralog compensation"],
                context_dependency="Must accept KO is valid based on evidence",
                scoring_criteria={"accepts_evidence": True, "biological_hypothesis": True},
            ),
            DialogueTurn(
                turn_number=3,
                turn_type=TurnType.NEW_INFORMATION,
                user_message="""We checked - MYCN is highly expressed in this cell line! 
                Could MYCN be compensating?""",
                expected_behaviors=[
                    "Confirm this is likely explanation",
                    "Explain MYC/MYCN functional redundancy",
                    "Suggest double KO experiment to test",
                    "Mention this is known phenomenon in some cancers",
                ],
                failure_modes=["Not connecting MYCN to MYC compensation"],
                context_dependency="Must connect to initial MYC question",
                scoring_criteria={"confirms_hypothesis": True, "suggests_test": True},
            ),
        ],
    ),
    # -------------------------------------------------------------------------
    # EXPERIMENTAL DESIGN
    # -------------------------------------------------------------------------
    MultiTurnDialogue(
        id="mt_exp_001",
        title="Designing a CRISPR Screen",
        dialogue_type=DialogueType.EXPERIMENTAL_DESIGN,
        domain="protocol",
        description="Iteratively designing a genome-wide CRISPR screen",
        overall_objective="Develop complete screen design through back-and-forth refinement",
        difficulty="hard",
        turns=[
            DialogueTurn(
                turn_number=1,
                turn_type=TurnType.INITIAL_QUESTION,
                user_message="""I want to find genes that cause resistance to our new drug X 
                in cancer cells. Should I do a CRISPR screen?""",
                expected_behaviors=[
                    "Confirm CRISPR screen is appropriate",
                    "Ask about positive vs negative selection",
                    "Ask about cell line and drug properties",
                ],
                failure_modes=["Jumping to protocol without clarifying questions"],
                context_dependency="None",
                scoring_criteria={"appropriate_method": True, "asks_clarification": True},
            ),
            DialogueTurn(
                turn_number=2,
                turn_type=TurnType.FOLLOW_UP,
                user_message="""It's a cytotoxic drug - kills about 90% of cells at IC90. 
                We want to find knockouts that let cells survive. Using A549 lung cancer cells.""",
                expected_behaviors=[
                    "Recommend positive selection screen",
                    "Suggest appropriate library (Brunello, Toronto)",
                    "Discuss MOI and coverage requirements",
                    "Mention timeline considerations",
                ],
                failure_modes=["Recommending wrong screen type", "Not discussing technical parameters"],
                context_dependency="Must use the IC90/survival context",
                scoring_criteria={"correct_screen_type": True, "technical_details": True},
            ),
            DialogueTurn(
                turn_number=3,
                turn_type=TurnType.FOLLOW_UP,
                user_message="""We have the Brunello library. What MOI should we use and how 
                many cells do we need to start with?""",
                expected_behaviors=[
                    "Recommend MOI 0.3-0.5 for single integration",
                    "Calculate cell numbers: 500-1000x library coverage",
                    "Brunello is ~77k guides, so need ~40-80M cells",
                    "Explain rationale for these numbers",
                ],
                failure_modes=["Wrong MOI recommendation", "Incorrect calculation"],
                context_dependency="Must remember they're using Brunello library",
                scoring_criteria={"correct_moi": True, "correct_calculation": True},
            ),
            DialogueTurn(
                turn_number=4,
                turn_type=TurnType.CHALLENGE,
                user_message="""We can only get 20M cells. Can we still do the screen or should 
                we use a smaller focused library?""",
                expected_behaviors=[
                    "Acknowledge limitation honestly",
                    "Discuss tradeoffs of reduced coverage",
                    "Suggest focused library as alternative",
                    "Or suggest scaling up cells before screen",
                ],
                failure_modes=["Saying 20M is fine without caveats", "Not offering alternatives"],
                context_dependency="Must remember previous coverage calculation",
                scoring_criteria={"honest_about_limitation": True, "offers_solutions": True},
            ),
            DialogueTurn(
                turn_number=5,
                turn_type=TurnType.FOLLOW_UP,
                user_message="""Let's go with a focused kinase library instead. After drug selection, 
                what analysis should we do to find hits?""",
                expected_behaviors=[
                    "Recommend NGS to count sgRNA abundance",
                    "Suggest analysis tools (MAGeCK, BAGEL)",
                    "Explain enrichment vs depletion analysis",
                    "Recommend validation of top hits",
                ],
                failure_modes=["Not adapting to new library choice", "Incomplete analysis plan"],
                context_dependency="Must remember switch to kinase library",
                scoring_criteria={"appropriate_analysis": True, "validation_plan": True},
            ),
        ],
    ),
    # -------------------------------------------------------------------------
    # TROUBLESHOOTING
    # -------------------------------------------------------------------------
    MultiTurnDialogue(
        id="mt_tro_001",
        title="Iterative Western Blot Troubleshooting",
        dialogue_type=DialogueType.TROUBLESHOOTING,
        domain="protocol",
        description="Back-and-forth troubleshooting of failed Western blot",
        overall_objective="Systematically diagnose and fix Western blot problem",
        difficulty="medium",
        turns=[
            DialogueTurn(
                turn_number=1,
                turn_type=TurnType.INITIAL_QUESTION,
                user_message="""My Western blot shows no bands at all - not even the loading control. 
                What should I check first?""",
                expected_behaviors=[
                    "Suggest checking transfer (Ponceau staining)",
                    "Ask about protein loading amount",
                    "Ask if gel ran properly",
                ],
                failure_modes=["Jumping to antibody issues without basics"],
                context_dependency="None",
                scoring_criteria={"systematic_approach": True, "starts_with_basics": True},
            ),
            DialogueTurn(
                turn_number=2,
                turn_type=TurnType.NEW_INFORMATION,
                user_message="""Ponceau shows good protein transfer - I can see nice bands. 
                So the transfer worked. What's next?""",
                expected_behaviors=[
                    "Acknowledge transfer is fine",
                    "Move to antibody/detection issues",
                    "Ask about blocking conditions",
                    "Ask about antibody dilutions",
                ],
                failure_modes=["Suggesting transfer problems again"],
                context_dependency="Must accept transfer is good",
                scoring_criteria={"moves_to_next_step": True, "logical_progression": True},
            ),
            DialogueTurn(
                turn_number=3,
                turn_type=TurnType.NEW_INFORMATION,
                user_message="""I'm using a new primary antibody I just bought. Blocked with 5% milk 
                for 1 hour. Primary was at 1:500 overnight at 4°C.""",
                expected_behaviors=[
                    "Note new antibody - could be issue",
                    "Ask about secondary antibody",
                    "Ask about detection method/ECL",
                    "Suggest trying higher antibody concentration",
                ],
                failure_modes=["Not focusing on the new antibody as likely cause"],
                context_dependency="Must note the new antibody",
                scoring_criteria={"identifies_likely_cause": True},
            ),
            DialogueTurn(
                turn_number=4,
                turn_type=TurnType.NEW_INFORMATION,
                user_message="""Secondary is anti-rabbit HRP at 1:10000, same bottle I always use. 
                ECL is freshly made. When I tried increasing primary to 1:100, I got very high 
                background but still no specific bands.""",
                expected_behaviors=[
                    "High background but no signal suggests antibody doesn't recognize target",
                    "New antibody might not work for Western (some work only for IP/IF)",
                    "Suggest trying positive control cell line",
                    "Consider antibody is bad batch",
                ],
                failure_modes=["Not recognizing antibody validation issue"],
                context_dependency="Must integrate all previous troubleshooting",
                scoring_criteria={"correct_diagnosis": True, "suggests_validation": True},
            ),
        ],
    ),
    # -------------------------------------------------------------------------
    # DATA INTERPRETATION
    # -------------------------------------------------------------------------
    MultiTurnDialogue(
        id="mt_int_001",
        title="Interpreting Paradoxical Drug Response Data",
        dialogue_type=DialogueType.DATA_INTERPRETATION,
        domain="drug_response",
        description="Working through confusing experimental results",
        overall_objective="Reach correct interpretation through iterative data discussion",
        difficulty="hard",
        turns=[
            DialogueTurn(
                turn_number=1,
                turn_type=TurnType.INITIAL_QUESTION,
                user_message="""We treated BRAF-mutant melanoma cells with a BRAF inhibitor and 
                surprisingly saw INCREASED phospho-ERK levels at 1 hour. This is opposite of 
                what we expected. Is our experiment wrong?""",
                expected_behaviors=[
                    "Don't dismiss as error - this is known phenomenon",
                    "Explain paradoxical activation / RAF dimerization",
                    "Ask about cell line and BRAF status",
                    "Suggest this might be expected in some contexts",
                ],
                failure_modes=["Assuming experiment is wrong", "Not knowing about paradoxical activation"],
                context_dependency="None",
                scoring_criteria={"recognizes_phenomenon": True, "doesnt_dismiss": True},
            ),
            DialogueTurn(
                turn_number=2,
                turn_type=TurnType.FOLLOW_UP,
                user_message="""Interesting! Can you explain more about this paradoxical activation? 
                The cells are A375 which are BRAF V600E mutant.""",
                expected_behaviors=[
                    "Explain RAF dimerization mechanism",
                    "Note that in V600E cells, should see inhibition eventually",
                    "1 hour might be early - ask about later timepoints",
                    "Suggest the increase might be transient",
                ],
                failure_modes=["Not explaining mechanism clearly"],
                context_dependency="Must address V600E context",
                scoring_criteria={"explains_mechanism": True, "timepoint_relevant": True},
            ),
            DialogueTurn(
                turn_number=3,
                turn_type=TurnType.NEW_INFORMATION,
                user_message="""At 4 hours, phospho-ERK is down 80% compared to DMSO control. 
                So the inhibitor does work eventually. Why the early increase though?""",
                expected_behaviors=[
                    "Confirm biphasic response is consistent with mechanism",
                    "Explain possible mechanisms for early spike",
                    "Mention feedback loops being disrupted",
                    "Note this is valuable data showing drug dynamics",
                ],
                failure_modes=["Not integrating early and late timepoints"],
                context_dependency="Must connect 1h and 4h data",
                scoring_criteria={"integrates_timepoints": True, "coherent_explanation": True},
            ),
        ],
    ),
    # -------------------------------------------------------------------------
    # PEER REVIEW SIMULATION
    # -------------------------------------------------------------------------
    MultiTurnDialogue(
        id="mt_rev_001",
        title="Responding to Reviewer Comments",
        dialogue_type=DialogueType.PEER_REVIEW,
        domain="interpretation",
        description="Helping scientist respond to tough reviewer critiques",
        overall_objective="Develop appropriate responses to reviewer concerns",
        difficulty="hard",
        turns=[
            DialogueTurn(
                turn_number=1,
                turn_type=TurnType.INITIAL_QUESTION,
                user_message="""A reviewer criticized our paper saying: 'The authors claim gene X 
                causes drug resistance but only show correlation. They need to prove causation.' 
                We showed that X is upregulated in resistant cells. How should we respond?""",
                expected_behaviors=[
                    "Acknowledge reviewer has valid point",
                    "Suggest experiments to show causation (knockdown/overexpression)",
                    "Help frame a constructive response",
                    "Don't be defensive",
                ],
                failure_modes=["Being defensive", "Dismissing valid critique"],
                context_dependency="None",
                scoring_criteria={"acknowledges_validity": True, "constructive": True},
            ),
            DialogueTurn(
                turn_number=2,
                turn_type=TurnType.FOLLOW_UP,
                user_message="""We actually did knock down gene X and it partially restored drug 
                sensitivity. But the reviewer says 'partial' isn't convincing. What do we do?""",
                expected_behaviors=[
                    "Partial restoration is actually expected",
                    "Resistance is often multifactorial",
                    "Frame this positively - X is necessary but not sufficient",
                    "Suggest additional experiments if possible",
                ],
                failure_modes=["Agreeing that partial isn't meaningful"],
                context_dependency="Must build on causation discussion",
                scoring_criteria={"reframes_positively": True, "scientifically_sound": True},
            ),
            DialogueTurn(
                turn_number=3,
                turn_type=TurnType.NEW_INFORMATION,
                user_message="""The reviewer also says our sample size is too small (n=3 per group). 
                We can't afford more samples. Is n=3 really a problem?""",
                expected_behaviors=[
                    "n=3 is common in cell biology but has limitations",
                    "Suggest emphasizing effect size over p-values",
                    "Recommend power analysis if possible",
                    "Point out if results are consistent and reproducible",
                ],
                failure_modes=["Saying n=3 is definitely enough without nuance"],
                context_dependency="Different issue - sample size",
                scoring_criteria={"nuanced_response": True, "practical_advice": True},
            ),
        ],
    ),
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
]


# =============================================================================
# DIALOGUE RUNNER
# =============================================================================


@dataclass
class TurnResult:
    """Result from a single dialogue turn."""

    turn_number: int
    user_message: str
    assistant_response: str
    scores: dict
    passed: bool


@dataclass
class DialogueResult:
    """Result from complete dialogue."""

    dialogue_id: str
    dialogue_title: str
    turns: list[TurnResult]
    overall_score: float
    memory_score: float  # How well it maintained context
    summary: str


class _DialogueTaskWrapper:
    """Wrapper to give MultiTurnDialogue the .id / .task_type interface the CLI expects."""

    __slots__ = ("id", "task_type", "prompt", "ground_truth", "dialogue")

    def __init__(self, dialogue: "MultiTurnDialogue"):
        self.id = dialogue.id
        self.task_type = "multiturn_dialogue"
        self.prompt = dialogue.turns[0].user_message if dialogue.turns else ""
        self.ground_truth = {"dialogue_id": dialogue.id, "num_turns": len(dialogue.turns)}
        self.dialogue = dialogue


class MultiTurnEvaluator:
    """Evaluator for multi-turn dialogues."""

    def __init__(self, model_name: str = "claude-sonnet-4-20250514", temperature: float = 0.0):
        self.model_name = model_name
        self.temperature = temperature
        self._model_client = None

    @property
    def model_client(self):
        if self._model_client is None:
            from bioeval.models.base import init_model

            self._model_client = init_model(self.model_name, temperature=self.temperature)
        return self._model_client

    # -- CLI-compatible interface ------------------------------------------

    def load_tasks(self, data_tier: str = "base") -> list:
        """Return dialogues wrapped as task objects for the CLI runner.

        Args:
            data_tier: 'base' (15 dialogues), 'extended' or 'all' (30 dialogues).
        """
        if data_tier in ("extended", "all"):
            from bioeval.multiturn.extended_data import EXTENDED_DIALOGUES

            dialogues = list(DIALOGUES) + EXTENDED_DIALOGUES
        else:
            dialogues = DIALOGUES
        return [_DialogueTaskWrapper(d) for d in dialogues]

    def evaluate_task(self, task) -> dict:
        """Evaluate a single dialogue task (CLI entry-point)."""
        dialogue = task.dialogue if hasattr(task, "dialogue") else task
        result = self.run_dialogue(dialogue)
        return {
            "task_id": result.dialogue_id,
            "response": result.summary,
            "scores": {
                "overall_score": result.overall_score,
                "memory_score": result.memory_score,
                "turns_passed": sum(1 for t in result.turns if t.passed),
                "total_turns": len(result.turns),
            },
            "error_annotations": None,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        }

    # -- Original dialogue runner ------------------------------------------

    def run_dialogue(self, dialogue: MultiTurnDialogue) -> DialogueResult:
        """Run a complete multi-turn dialogue."""
        messages = []
        turn_results = []

        for turn in dialogue.turns:
            # Add user message
            messages.append({"role": "user", "content": turn.user_message})

            # Get assistant response
            system_prompt = (
                f"You are a helpful scientific assistant discussing {dialogue.domain}. "
                f"Engage in a multi-turn conversation, building on previous exchanges."
            )
            assistant_message = self.model_client.generate_chat(messages, max_tokens=1500, system=system_prompt)
            messages.append({"role": "assistant", "content": assistant_message})

            # Score this turn
            scores = self._score_turn(turn, assistant_message, messages[:-1])

            turn_results.append(
                TurnResult(
                    turn_number=turn.turn_number,
                    user_message=turn.user_message,
                    assistant_response=assistant_message,
                    scores=scores,
                    passed=scores.get("passed", False),
                )
            )

        # Calculate overall scores
        overall_score = sum(1 for t in turn_results if t.passed) / len(turn_results)
        memory_score = self._calculate_memory_score(dialogue, turn_results)

        return DialogueResult(
            dialogue_id=dialogue.id,
            dialogue_title=dialogue.title,
            turns=turn_results,
            overall_score=overall_score,
            memory_score=memory_score,
            summary=self._generate_summary(turn_results),
        )

    def _score_turn(self, turn: DialogueTurn, response: str, previous_messages: list) -> dict:
        """Score a single turn with improved behavior matching and context retention.

        Improvements over v0.2:
        - Multi-term matching (2+ terms) for behavior detection
        - Per-behavior match detail tracking
        - Context retention: checks for key entities from previous turns
        - Graduated scoring instead of binary pass/fail
        """
        from bioeval.scoring.matching import extract_key_terms, matched_list, any_match, phrase_match

        response_lower = response.lower()

        scores = {
            "turn_number": turn.turn_number,
            "turn_type": turn.turn_type.value,
        }

        # --- Check expected behaviors with improved matching ---
        behaviors_shown = 0
        behavior_details = []
        for behavior in turn.expected_behaviors:
            key_terms = extract_key_terms(behavior, min_length=5, max_terms=5)
            matched_terms = matched_list(key_terms, response_lower)
            # Require 2+ term matches for longer behaviors, 1 for short
            threshold = min(2, len(key_terms))
            is_shown = len(matched_terms) >= threshold
            if is_shown:
                behaviors_shown += 1
            behavior_details.append(
                {
                    "behavior": behavior[:80],
                    "shown": is_shown,
                    "matched_terms": matched_terms,
                }
            )

        scores["behavior_coverage"] = behaviors_shown / len(turn.expected_behaviors) if turn.expected_behaviors else 0
        scores["behavior_details"] = behavior_details

        # --- Check failure modes ---
        failures = 0
        failure_details = []
        for failure in turn.failure_modes:
            key_terms = extract_key_terms(failure, min_length=5, max_terms=3)
            matched = matched_list(key_terms, response_lower)
            # All terms must match to trigger a failure
            is_triggered = len(matched) == len(key_terms) and len(key_terms) > 0
            if is_triggered:
                failures += 1
            failure_details.append(
                {
                    "failure": failure[:80],
                    "triggered": is_triggered,
                }
            )

        scores["failure_modes_triggered"] = failures
        scores["failure_details"] = failure_details

        # --- Context retention check ---
        scores["shows_continuity"] = False
        scores["context_retention_score"] = 0.0

        if turn.context_dependency and turn.context_dependency != "None" and previous_messages:
            # Check for explicit continuity markers
            continuity_markers = [
                "as mentioned",
                "as we discussed",
                "you said",
                "earlier",
                "previous",
                "building on",
                "to your point",
                "indeed",
                "as i noted",
                "given that",
                "based on",
                "from our",
                "we established",
                "you mentioned",
                "as before",
            ]
            has_continuity_marker = any_match(continuity_markers, response_lower)

            # Check for key entity references from previous assistant messages
            entity_retention = 0
            entity_total = 0
            stop_words = {
                "about",
                "after",
                "their",
                "there",
                "these",
                "those",
                "which",
                "would",
                "could",
                "should",
                "being",
                "other",
                "where",
                "while",
                "using",
                "first",
                "based",
                "known",
                "shown",
                "given",
                "since",
                "might",
            }
            for msg in previous_messages:
                if msg.get("role") == "assistant":
                    # Extract key scientific terms from previous responses
                    sample_terms = extract_key_terms(msg["content"], min_length=4, max_terms=5, stop_words=stop_words)
                    for term in sample_terms:
                        entity_total += 1
                        if phrase_match(term, response_lower):
                            entity_retention += 1

            entity_score = entity_retention / entity_total if entity_total > 0 else 0
            scores["shows_continuity"] = has_continuity_marker or entity_score > 0.3
            scores["context_retention_score"] = round(entity_score, 3)

        # --- Graduated pass/fail ---
        # Instead of binary, use a graduated score
        behavior_score = scores["behavior_coverage"]
        failure_penalty = min(failures * 0.3, 1.0)  # Each failure deducts 0.3
        turn_score = max(0, behavior_score - failure_penalty)

        scores["turn_score"] = round(turn_score, 3)
        scores["passed"] = turn_score >= 0.4  # Slightly relaxed from 0.5

        return scores

    def _calculate_memory_score(self, dialogue: MultiTurnDialogue, results: list[TurnResult]) -> float:
        """Calculate how well model maintained context across turns."""
        if len(results) <= 1:
            return 1.0

        memory_checks = 0
        memory_passes = 0

        for i, result in enumerate(results[1:], 1):
            # Check if later turns properly reference earlier context
            turn = dialogue.turns[i]

            if turn.context_dependency and turn.context_dependency != "None":
                memory_checks += 1

                # Simple check: does response show awareness of previous turns?
                if result.scores.get("shows_continuity", False):
                    memory_passes += 1
                elif result.scores.get("behavior_coverage", 0) >= 0.5:
                    # If behaviors are right, probably remembers context
                    memory_passes += 0.5

        return memory_passes / memory_checks if memory_checks > 0 else 1.0

    def _generate_summary(self, results: list[TurnResult]) -> str:
        """Generate summary of dialogue performance."""
        passed = sum(1 for r in results if r.passed)
        total = len(results)

        if passed == total:
            return "All turns handled successfully"
        elif passed >= total * 0.7:
            return f"Good performance: {passed}/{total} turns passed"
        elif passed >= total * 0.5:
            return f"Mixed performance: {passed}/{total} turns passed"
        else:
            return f"Poor performance: only {passed}/{total} turns passed"

    def run_all_dialogues(self) -> dict:
        """Run all dialogues and aggregate results."""
        results = []

        for dialogue in DIALOGUES:
            _logger.info("Running: %s...", dialogue.title)
            result = self.run_dialogue(dialogue)
            results.append(
                {
                    "dialogue_id": result.dialogue_id,
                    "title": result.dialogue_title,
                    "overall_score": result.overall_score,
                    "memory_score": result.memory_score,
                    "turns_passed": sum(1 for t in result.turns if t.passed),
                    "total_turns": len(result.turns),
                    "summary": result.summary,
                }
            )

        # Aggregate
        avg_score = sum(r["overall_score"] for r in results) / len(results)
        avg_memory = sum(r["memory_score"] for r in results) / len(results)

        return {
            "model": self.model_name,
            "total_dialogues": len(results),
            "average_score": avg_score,
            "average_memory_score": avg_memory,
            "results": results,
        }


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_all_dialogues() -> list[MultiTurnDialogue]:
    """Return all dialogue scenarios."""
    return DIALOGUES


def get_statistics() -> dict:
    """Get statistics about dialogues."""
    by_type = {}
    by_difficulty = {}
    total_turns = 0

    for d in DIALOGUES:
        t = d.dialogue_type.value
        by_type[t] = by_type.get(t, 0) + 1

        diff = d.difficulty
        by_difficulty[diff] = by_difficulty.get(diff, 0) + 1

        total_turns += len(d.turns)

    return {
        "total_dialogues": len(DIALOGUES),
        "total_turns": total_turns,
        "by_type": by_type,
        "by_difficulty": by_difficulty,
        "avg_turns_per_dialogue": total_turns / len(DIALOGUES) if DIALOGUES else 0,
    }


if __name__ == "__main__":
    stats = get_statistics()
    print("Multi-Turn Dialogue Statistics:")
    print(f"  Total dialogues: {stats['total_dialogues']}")
    print(f"  Total turns: {stats['total_turns']}")
    print(f"  Avg turns/dialogue: {stats['avg_turns_per_dialogue']:.1f}")
    print(f"  By type: {stats['by_type']}")
    print(f"  By difficulty: {stats['by_difficulty']}")
