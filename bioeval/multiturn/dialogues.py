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

import json
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


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
                    "Suggest diagnostic tests to distinguish mechanisms"
                ],
                failure_modes=["Giving only one mechanism", "Not suggesting how to test"],
                context_dependency="None - initial question",
                scoring_criteria={"coverage": "Lists 3+ mechanisms", "actionable": "Suggests tests"}
            ),
            DialogueTurn(
                turn_number=2,
                turn_type=TurnType.NEW_INFORMATION,
                user_message="""We sequenced the resistant cells. No T790M mutation found. 
                What should we check next?""",
                expected_behaviors=[
                    "Acknowledge T790M ruled out",
                    "Suggest alternative mechanisms: MET, HER2, histological transformation",
                    "Recommend specific tests (FISH for MET, IHC for markers)"
                ],
                failure_modes=[
                    "Suggesting T790M testing again",
                    "Not updating hypothesis based on new info"
                ],
                context_dependency="Must remember T790M was ruled out",
                scoring_criteria={"updates_hypothesis": True, "suggests_alternatives": True}
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
                    "Mention specific drugs (capmatinib, tepotinib)"
                ],
                failure_modes=[
                    "Not connecting MET to EGFR resistance",
                    "Not suggesting treatment change"
                ],
                context_dependency="Must connect to initial erlotinib resistance question",
                scoring_criteria={"mechanism_correct": True, "treatment_suggestion": True}
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
                    "Suggest it's likely selection of pre-existing clone"
                ],
                failure_modes=[
                    "Ignoring the pre-treatment data",
                    "Not understanding clonal evolution"
                ],
                context_dependency="Must integrate all previous information",
                scoring_criteria={"nuanced_response": True, "understands_evolution": True}
            ),
        ]
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
                    "Ask clarifying questions about validation"
                ],
                failure_modes=["Accepting result without questioning", "Not suggesting alternatives"],
                context_dependency="None - initial question",
                scoring_criteria={"questions_result": True, "suggests_explanations": True}
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
                    "Consider cell line-specific wiring"
                ],
                failure_modes=[
                    "Continuing to question KO validity",
                    "Not considering paralog compensation"
                ],
                context_dependency="Must accept KO is valid based on evidence",
                scoring_criteria={"accepts_evidence": True, "biological_hypothesis": True}
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
                    "Mention this is known phenomenon in some cancers"
                ],
                failure_modes=["Not connecting MYCN to MYC compensation"],
                context_dependency="Must connect to initial MYC question",
                scoring_criteria={"confirms_hypothesis": True, "suggests_test": True}
            ),
        ]
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
                    "Ask about cell line and drug properties"
                ],
                failure_modes=["Jumping to protocol without clarifying questions"],
                context_dependency="None",
                scoring_criteria={"appropriate_method": True, "asks_clarification": True}
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
                    "Mention timeline considerations"
                ],
                failure_modes=["Recommending wrong screen type", "Not discussing technical parameters"],
                context_dependency="Must use the IC90/survival context",
                scoring_criteria={"correct_screen_type": True, "technical_details": True}
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
                    "Explain rationale for these numbers"
                ],
                failure_modes=["Wrong MOI recommendation", "Incorrect calculation"],
                context_dependency="Must remember they're using Brunello library",
                scoring_criteria={"correct_moi": True, "correct_calculation": True}
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
                    "Or suggest scaling up cells before screen"
                ],
                failure_modes=["Saying 20M is fine without caveats", "Not offering alternatives"],
                context_dependency="Must remember previous coverage calculation",
                scoring_criteria={"honest_about_limitation": True, "offers_solutions": True}
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
                    "Recommend validation of top hits"
                ],
                failure_modes=["Not adapting to new library choice", "Incomplete analysis plan"],
                context_dependency="Must remember switch to kinase library",
                scoring_criteria={"appropriate_analysis": True, "validation_plan": True}
            ),
        ]
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
                    "Ask if gel ran properly"
                ],
                failure_modes=["Jumping to antibody issues without basics"],
                context_dependency="None",
                scoring_criteria={"systematic_approach": True, "starts_with_basics": True}
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
                    "Ask about antibody dilutions"
                ],
                failure_modes=["Suggesting transfer problems again"],
                context_dependency="Must accept transfer is good",
                scoring_criteria={"moves_to_next_step": True, "logical_progression": True}
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
                    "Suggest trying higher antibody concentration"
                ],
                failure_modes=["Not focusing on the new antibody as likely cause"],
                context_dependency="Must note the new antibody",
                scoring_criteria={"identifies_likely_cause": True}
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
                    "Consider antibody is bad batch"
                ],
                failure_modes=["Not recognizing antibody validation issue"],
                context_dependency="Must integrate all previous troubleshooting",
                scoring_criteria={"correct_diagnosis": True, "suggests_validation": True}
            ),
        ]
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
                    "Suggest this might be expected in some contexts"
                ],
                failure_modes=[
                    "Assuming experiment is wrong",
                    "Not knowing about paradoxical activation"
                ],
                context_dependency="None",
                scoring_criteria={"recognizes_phenomenon": True, "doesnt_dismiss": True}
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
                    "Suggest the increase might be transient"
                ],
                failure_modes=["Not explaining mechanism clearly"],
                context_dependency="Must address V600E context",
                scoring_criteria={"explains_mechanism": True, "timepoint_relevant": True}
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
                    "Note this is valuable data showing drug dynamics"
                ],
                failure_modes=["Not integrating early and late timepoints"],
                context_dependency="Must connect 1h and 4h data",
                scoring_criteria={"integrates_timepoints": True, "coherent_explanation": True}
            ),
        ]
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
                    "Don't be defensive"
                ],
                failure_modes=["Being defensive", "Dismissing valid critique"],
                context_dependency="None",
                scoring_criteria={"acknowledges_validity": True, "constructive": True}
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
                    "Suggest additional experiments if possible"
                ],
                failure_modes=["Agreeing that partial isn't meaningful"],
                context_dependency="Must build on causation discussion",
                scoring_criteria={"reframes_positively": True, "scientifically_sound": True}
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
                    "Point out if results are consistent and reproducible"
                ],
                failure_modes=["Saying n=3 is definitely enough without nuance"],
                context_dependency="Different issue - sample size",
                scoring_criteria={"nuanced_response": True, "practical_advice": True}
            ),
        ]
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

    def __init__(self, model_name: str = "claude-sonnet-4-20250514"):
        self.model_name = model_name
        self._client = None
    
    @property
    def client(self):
        if self._client is None:
            from anthropic import Anthropic
            self._client = Anthropic()
        return self._client

    # -- CLI-compatible interface ------------------------------------------

    def load_tasks(self, data_tier: str = "base") -> list:
        """Return dialogues wrapped as task objects for the CLI runner.

        Args:
            data_tier: 'base' (6 dialogues), 'extended' or 'all' (12 dialogues).
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
            
            # Get assistant response (with retry on transient errors)
            import time as _time
            last_err = None
            for _attempt in range(3):
                try:
                    response = self.client.messages.create(
                        model=self.model_name,
                        max_tokens=1500,
                        system=f"You are a helpful scientific assistant discussing {dialogue.domain}. "
                               f"Engage in a multi-turn conversation, building on previous exchanges.",
                        messages=messages
                    )
                    break
                except (BrokenPipeError, ConnectionError, OSError) as exc:
                    last_err = exc
                    if _attempt < 2:
                        _time.sleep(2 ** _attempt)
                        self._client = None
            else:
                raise last_err  # type: ignore[misc]

            assistant_message = response.content[0].text
            messages.append({"role": "assistant", "content": assistant_message})
            
            # Score this turn
            scores = self._score_turn(turn, assistant_message, messages[:-1])
            
            turn_results.append(TurnResult(
                turn_number=turn.turn_number,
                user_message=turn.user_message,
                assistant_response=assistant_message,
                scores=scores,
                passed=scores.get("passed", False)
            ))
        
        # Calculate overall scores
        overall_score = sum(1 for t in turn_results if t.passed) / len(turn_results)
        memory_score = self._calculate_memory_score(dialogue, turn_results)
        
        return DialogueResult(
            dialogue_id=dialogue.id,
            dialogue_title=dialogue.title,
            turns=turn_results,
            overall_score=overall_score,
            memory_score=memory_score,
            summary=self._generate_summary(turn_results)
        )
    
    def _score_turn(
        self,
        turn: DialogueTurn,
        response: str,
        previous_messages: list
    ) -> dict:
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
            behavior_details.append({
                "behavior": behavior[:80],
                "shown": is_shown,
                "matched_terms": matched_terms,
            })

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
            failure_details.append({
                "failure": failure[:80],
                "triggered": is_triggered,
            })

        scores["failure_modes_triggered"] = failures
        scores["failure_details"] = failure_details

        # --- Context retention check ---
        scores["shows_continuity"] = False
        scores["context_retention_score"] = 0.0

        if turn.context_dependency and turn.context_dependency != "None" and previous_messages:
            # Check for explicit continuity markers
            continuity_markers = [
                "as mentioned", "as we discussed", "you said", "earlier",
                "previous", "building on", "to your point", "indeed",
                "as i noted", "given that", "based on", "from our",
                "we established", "you mentioned", "as before",
            ]
            has_continuity_marker = any_match(continuity_markers, response_lower)

            # Check for key entity references from previous assistant messages
            entity_retention = 0
            entity_total = 0
            stop_words = {'about', 'after', 'their', 'there', 'these', 'those',
                          'which', 'would', 'could', 'should', 'being', 'other',
                          'where', 'while', 'using', 'first', 'based', 'known',
                          'shown', 'given', 'since', 'might'}
            for msg in previous_messages:
                if msg.get("role") == "assistant":
                    # Extract key scientific terms from previous responses
                    sample_terms = extract_key_terms(msg["content"], min_length=4, max_terms=5,
                                                     stop_words=stop_words)
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
    
    def _calculate_memory_score(
        self, 
        dialogue: MultiTurnDialogue, 
        results: list[TurnResult]
    ) -> float:
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
            print(f"Running: {dialogue.title}...")
            result = self.run_dialogue(dialogue)
            results.append({
                "dialogue_id": result.dialogue_id,
                "title": result.dialogue_title,
                "overall_score": result.overall_score,
                "memory_score": result.memory_score,
                "turns_passed": sum(1 for t in result.turns if t.passed),
                "total_turns": len(result.turns),
                "summary": result.summary
            })
        
        # Aggregate
        avg_score = sum(r["overall_score"] for r in results) / len(results)
        avg_memory = sum(r["memory_score"] for r in results) / len(results)
        
        return {
            "model": self.model_name,
            "total_dialogues": len(results),
            "average_score": avg_score,
            "average_memory_score": avg_memory,
            "results": results
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
        "avg_turns_per_dialogue": total_turns / len(DIALOGUES) if DIALOGUES else 0
    }


if __name__ == "__main__":
    stats = get_statistics()
    print("Multi-Turn Dialogue Statistics:")
    print(f"  Total dialogues: {stats['total_dialogues']}")
    print(f"  Total turns: {stats['total_turns']}")
    print(f"  Avg turns/dialogue: {stats['avg_turns_per_dialogue']:.1f}")
    print(f"  By type: {stats['by_type']}")
    print(f"  By difficulty: {stats['by_difficulty']}")
