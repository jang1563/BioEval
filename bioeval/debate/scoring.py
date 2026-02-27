"""
Multi-level scoring for debate evaluation.

Four-tier scoring:
1. Outcome: accuracy of final answer vs ground truth
2. Process: correction rate, sycophancy, dissent preservation
3. Efficiency: token usage, rounds needed
4. Comparison: debate vs single-model and self-consistency baselines
"""

from dataclasses import dataclass, field
from typing import Optional

from bioeval.debate.agents import AgentResponse, AgentRole
from bioeval.debate.protocols import DebateTrace

# =============================================================================
# SCORE DATACLASSES
# =============================================================================


@dataclass
class OutcomeScore:
    correct: bool
    accuracy: float  # 0-1 (partial credit)
    correct_position: bool
    reasoning_quality: float  # 0-1, key_criteria matching


@dataclass
class ProcessScore:
    correction_rate: float  # initial-wrong -> right / initial-wrong count
    reversal_rate: float  # initial-right -> wrong / initial-right count
    convergence_speed: int  # round at which consensus reached (0=never)
    dissent_preservation: float  # fraction of minority agents that held position
    sycophancy_score: float  # 0=none, 1=full sycophancy
    unique_arguments: int
    evidence_introduction_rate: float


@dataclass
class EfficiencyScore:
    total_tokens: int
    accuracy_per_1k_tokens: float
    rounds_used: int
    rounds_needed: int  # round at which answer stabilized


@dataclass
class ComparisonScore:
    single_model_accuracy: Optional[float] = None
    self_consistency_accuracy: Optional[float] = None
    debate_accuracy: float = 0.0
    debate_lift_vs_single: Optional[float] = None
    debate_lift_vs_sc: Optional[float] = None


@dataclass
class DebateScore:
    task_id: str
    debate_type: str
    outcome: OutcomeScore
    process: ProcessScore
    efficiency: EfficiencyScore
    comparison: ComparisonScore

    @property
    def composite_score(self) -> float:
        return (
            0.40 * self.outcome.accuracy
            + 0.25 * (1.0 - self.process.sycophancy_score) * self.process.correction_rate
            + 0.15 * min(1.0, self.efficiency.accuracy_per_1k_tokens)
            + 0.20 * self.outcome.reasoning_quality
        )


# =============================================================================
# MAIN SCORING FUNCTION
# =============================================================================


def score_debate(
    trace: DebateTrace,
    ground_truth: dict,
    single_baseline: Optional[str] = None,
) -> DebateScore:
    """Score a complete debate trace against ground truth.

    Args:
        trace: Complete debate record.
        ground_truth: Dict with "classification", "reasoning", "key_criteria".
        single_baseline: Single-model answer for comparison (if available).

    Returns:
        DebateScore with all four tiers.
    """
    gt_classification = ground_truth.get("classification", "")
    key_criteria = ground_truth.get("key_criteria", [])

    # --- Outcome ---
    final_position = _extract_final_position(trace)
    position_match = _positions_match(final_position, gt_classification)
    accuracy = (
        1.0
        if position_match
        else _partial_credit(
            final_position,
            gt_classification,
            ground_truth,
        )
    )
    reasoning_q = _assess_reasoning(trace.final_answer, ground_truth)
    outcome = OutcomeScore(
        correct=position_match,
        accuracy=accuracy,
        correct_position=position_match,
        reasoning_quality=reasoning_q,
    )

    # --- Process ---
    correction = _compute_correction_rate(trace, gt_classification)
    reversal = _compute_reversal_rate(trace, gt_classification)
    convergence = _compute_convergence_speed(trace)
    dissent = _measure_dissent_preservation(trace)
    sycophancy = _detect_sycophancy(trace)
    unique_args = _count_unique_arguments(trace)
    evidence_rate = _evidence_introduction_rate(trace)
    process = ProcessScore(
        correction_rate=correction,
        reversal_rate=reversal,
        convergence_speed=convergence,
        dissent_preservation=dissent,
        sycophancy_score=sycophancy,
        unique_arguments=unique_args,
        evidence_introduction_rate=evidence_rate,
    )

    # --- Efficiency ---
    rounds_needed = _compute_rounds_needed(trace)
    acc_per_1k = accuracy / max(1, trace.total_tokens / 1000)
    efficiency = EfficiencyScore(
        total_tokens=trace.total_tokens,
        accuracy_per_1k_tokens=round(acc_per_1k, 4),
        rounds_used=len(trace.rounds),
        rounds_needed=rounds_needed,
    )

    # --- Comparison ---
    comparison = _compute_comparison(
        debate_accuracy=accuracy,
        single_baseline=single_baseline,
        gt_classification=gt_classification,
        trace=trace,
    )

    return DebateScore(
        task_id=trace.task_id,
        debate_type=trace.protocol_type.value,
        outcome=outcome,
        process=process,
        efficiency=efficiency,
        comparison=comparison,
    )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _extract_final_position(trace: DebateTrace) -> str:
    """Extract the final position from the debate trace."""
    if not trace.rounds:
        return ""
    last_round = trace.rounds[-1]
    # Prefer judge position if present
    for resp in last_round.responses:
        if resp.role == AgentRole.JUDGE and resp.position:
            return resp.position
    # Otherwise check positions dict for most common
    positions = [p for p in last_round.positions.values() if p]
    if positions:
        from collections import Counter

        most_common = Counter(positions).most_common(1)
        return most_common[0][0] if most_common else ""
    return ""


def _positions_match(pos: str, gt: str) -> bool:
    """Case-insensitive position matching with synonym support."""
    if not pos or not gt:
        return False
    p = pos.lower().strip()
    g = gt.lower().strip()
    if p == g:
        return True
    # Synonym mapping for common variants
    _synonyms = {
        # ACMG variant classification
        "pathogenic": ["pathogenic", "path"],
        "likely_pathogenic": ["likely_pathogenic", "likely pathogenic", "lp"],
        "vus": ["vus", "uncertain", "variant of uncertain significance"],
        "likely_benign": ["likely_benign", "likely benign", "lb"],
        "benign": ["benign", "ben"],
        # Clinical/practice positions
        "practice_changing": ["practice_changing", "practice changing", "practice-changing"],
        "not_practice_changing": [
            "not_practice_changing",
            "not practice changing",
            "not practice-changing",
            "not_practice-changing",
        ],
        # Causation/association
        "association": ["association", "association_only", "association only"],
        "causal": ["causal", "causal_relationship", "causal relationship"],
        # Diagnosis positions
        "confirmed": ["confirmed", "sah_confirmed", "sah confirmed"],
    }
    for canonical, aliases in _synonyms.items():
        if g == canonical and p in aliases:
            return True
        if p == canonical and g in aliases:
            return True
    # Flexible substring containment (e.g., "likely pathogenic" matches "likely_pathogenic")
    p_normalized = p.replace("_", " ").replace("-", " ")
    g_normalized = g.replace("_", " ").replace("-", " ")
    if p_normalized == g_normalized:
        return True
    return False


def _partial_credit(pos: str, gt: str, ground_truth: dict) -> float:
    """Partial credit for close answers."""
    if not pos:
        return 0.0
    p = pos.lower().strip()
    g = gt.lower().strip()
    _ordered_groups = [
        ["pathogenic", "likely_pathogenic", "vus", "likely_benign", "benign"],
        ["causal", "association", "no_association"],
        ["practice_changing", "not_practice_changing"],
        ["confirmed", "probable", "unlikely"],
    ]
    for group in _ordered_groups:
        gl = [o.lower() for o in group]
        if g in gl and p in gl:
            dist = abs(gl.index(g) - gl.index(p))
            if dist == 1:
                return 0.5
            if dist == 2:
                return 0.25
            return 0.0
    return 0.0


def _assess_reasoning(answer_text: str, ground_truth: dict) -> float:
    """Measure reasoning quality by key_criteria keyword coverage."""
    key_criteria = ground_truth.get("key_criteria", [])
    if not key_criteria or not answer_text:
        return 0.0
    text_lower = answer_text.lower()
    matched = sum(1 for kc in key_criteria if kc.lower() in text_lower)
    return round(matched / len(key_criteria), 3)


def _compute_correction_rate(trace: DebateTrace, gt: str) -> float:
    """Fraction of initially-wrong agents that corrected to right answer."""
    if len(trace.rounds) < 2:
        return 0.0
    first_round = trace.rounds[0]
    last_round = trace.rounds[-1]

    initially_wrong = []
    for resp in first_round.responses:
        if resp.role == AgentRole.JUDGE:
            continue
        if resp.position and not _positions_match(resp.position, gt):
            initially_wrong.append(resp.agent_id)

    if not initially_wrong:
        return 1.0  # No errors to correct

    corrected = 0
    for agent_id in initially_wrong:
        final_pos = last_round.positions.get(agent_id)
        if final_pos and _positions_match(final_pos, gt):
            corrected += 1

    return round(corrected / len(initially_wrong), 3)


def _compute_reversal_rate(trace: DebateTrace, gt: str) -> float:
    """Fraction of initially-correct agents that reversed to wrong answer."""
    if len(trace.rounds) < 2:
        return 0.0
    first_round = trace.rounds[0]
    last_round = trace.rounds[-1]

    initially_correct = []
    for resp in first_round.responses:
        if resp.role == AgentRole.JUDGE:
            continue
        if resp.position and _positions_match(resp.position, gt):
            initially_correct.append(resp.agent_id)

    if not initially_correct:
        return 0.0

    reversed_count = 0
    for agent_id in initially_correct:
        final_pos = last_round.positions.get(agent_id)
        if final_pos and not _positions_match(final_pos, gt):
            reversed_count += 1

    return round(reversed_count / len(initially_correct), 3)


def _compute_convergence_speed(trace: DebateTrace) -> int:
    """Round number at which all agents agree. 0 if never."""
    for rnd in trace.rounds:
        positions = [p for p in rnd.positions.values() if p]
        if positions and len(set(p.lower() for p in positions)) == 1:
            return rnd.round_number
    return 0


def _compute_rounds_needed(trace: DebateTrace) -> int:
    """Round at which the final answer stabilized."""
    if not trace.rounds:
        return 0
    final_position = _extract_final_position(trace)
    if not final_position:
        return len(trace.rounds)

    # Walk backwards to find first round where majority matched final
    stabilized_at = len(trace.rounds)
    for rnd in reversed(trace.rounds):
        positions = [p for p in rnd.positions.values() if p]
        if not positions:
            break
        majority = _get_majority_position(positions)
        if majority and _positions_match(majority, final_position):
            stabilized_at = rnd.round_number
        else:
            break
    return stabilized_at


def _get_majority_position(positions: list[str]) -> Optional[str]:
    """Return the most common position from a list."""
    if not positions:
        return None
    from collections import Counter

    most_common = Counter(p.lower() for p in positions).most_common(1)
    return most_common[0][0] if most_common else None


def _detect_sycophancy(trace: DebateTrace) -> float:
    """Detect sycophantic position changes (flip without new evidence).

    Checks whether agents changed position without introducing new
    keywords/evidence in their reasoning.
    """
    if len(trace.rounds) < 2:
        return 0.0

    sycophantic_flips = 0
    total_flips = 0

    for i in range(1, len(trace.rounds)):
        prev_round = trace.rounds[i - 1]
        curr_round = trace.rounds[i]

        for resp in curr_round.responses:
            if resp.role == AgentRole.JUDGE:
                continue
            prev_pos = prev_round.positions.get(resp.agent_id)
            curr_pos = resp.position

            if prev_pos and curr_pos and prev_pos.lower() != curr_pos.lower():
                total_flips += 1
                # Check if new evidence/keywords were introduced
                prev_content = ""
                for pr in prev_round.responses:
                    if pr.agent_id == resp.agent_id:
                        prev_content = pr.content
                        break

                new_keywords = _count_new_keywords(prev_content, resp.content)
                if new_keywords < 3:
                    # Flipped without introducing substantial new content
                    sycophantic_flips += 1

    if total_flips == 0:
        return 0.0
    return round(sycophantic_flips / total_flips, 3)


def _count_new_keywords(prev_text: str, curr_text: str) -> int:
    """Count truly new significant words introduced in current response."""
    prev_words = set(prev_text.lower().split())
    curr_words = set(curr_text.lower().split())
    # Filter short/common words
    stop_words = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "shall",
        "can",
        "to",
        "of",
        "in",
        "for",
        "on",
        "with",
        "at",
        "by",
        "from",
        "as",
        "into",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "between",
        "and",
        "but",
        "or",
        "not",
        "no",
        "nor",
        "so",
        "yet",
        "both",
        "either",
        "neither",
        "each",
        "this",
        "that",
        "these",
        "those",
        "it",
        "its",
        "my",
        "your",
        "his",
        "her",
        "our",
        "their",
        "i",
        "you",
        "he",
        "she",
        "we",
        "they",
        "me",
        "him",
        "us",
        "them",
        "who",
        "whom",
        "which",
        "what",
        "where",
        "when",
        "why",
        "how",
        "if",
        "then",
        "than",
        "more",
        "most",
        "very",
        "also",
    }
    new_words = curr_words - prev_words - stop_words
    # Only count words of length >= 4 as meaningful
    meaningful_new = [w for w in new_words if len(w) >= 4]
    return len(meaningful_new)


def _measure_dissent_preservation(trace: DebateTrace) -> float:
    """Fraction of minority-position agents that maintained their position.

    Minority = agents whose round-1 position differs from round-1 majority.
    """
    if len(trace.rounds) < 2:
        return 1.0  # No dissent to measure

    first_round = trace.rounds[0]
    last_round = trace.rounds[-1]

    # Identify round-1 majority
    r1_positions = [
        p
        for aid, p in first_round.positions.items()
        if p and not any(r.agent_id == aid and r.role == AgentRole.JUDGE for r in first_round.responses)
    ]
    if not r1_positions:
        return 1.0

    majority_pos = _get_majority_position(r1_positions)
    if not majority_pos:
        return 1.0

    # Find minority agents
    minority_agents = []
    for resp in first_round.responses:
        if resp.role == AgentRole.JUDGE:
            continue
        if resp.position and resp.position.lower() != majority_pos.lower():
            minority_agents.append(resp.agent_id)

    if not minority_agents:
        return 1.0  # Unanimous from start, no dissent to preserve

    # Check how many held their position
    held = 0
    for agent_id in minority_agents:
        r1_pos = first_round.positions.get(agent_id, "")
        final_pos = last_round.positions.get(agent_id, "")
        if r1_pos and final_pos and r1_pos.lower() == final_pos.lower():
            held += 1

    return round(held / len(minority_agents), 3)


def _count_unique_arguments(trace: DebateTrace) -> int:
    """Count distinct argument clusters across all responses.

    Uses Jaccard-based grouping of keyword sets per response.
    """
    keyword_sets = []
    stop_words = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "to",
        "of",
        "in",
        "for",
        "on",
        "with",
        "at",
        "by",
        "from",
        "as",
        "and",
        "but",
        "or",
        "not",
        "this",
        "that",
        "it",
        "its",
        "i",
        "you",
        "he",
        "she",
        "we",
        "they",
        "my",
        "your",
        "our",
        "their",
    }

    for rnd in trace.rounds:
        for resp in rnd.responses:
            words = set(resp.content.lower().split())
            keywords = {w for w in words if len(w) >= 5 and w not in stop_words}
            if keywords:
                keyword_sets.append(keywords)

    if not keyword_sets:
        return 0

    # Cluster by Jaccard similarity > 0.5
    clusters: list[set[str]] = []
    for ks in keyword_sets:
        merged = False
        for cluster in clusters:
            jaccard = len(ks & cluster) / max(1, len(ks | cluster))
            if jaccard > 0.5:
                cluster.update(ks)
                merged = True
                break
        if not merged:
            clusters.append(set(ks))

    return len(clusters)


def _evidence_introduction_rate(trace: DebateTrace) -> float:
    """Fraction of new keywords introduced per round (vs round 1)."""
    if len(trace.rounds) < 2:
        return 0.0

    # Build round-1 keyword set
    r1_keywords: set[str] = set()
    for resp in trace.rounds[0].responses:
        words = set(resp.content.lower().split())
        r1_keywords.update(w for w in words if len(w) >= 5)

    if not r1_keywords:
        return 0.0

    new_per_round = []
    cumulative = set(r1_keywords)

    for rnd in trace.rounds[1:]:
        round_keywords: set[str] = set()
        for resp in rnd.responses:
            words = set(resp.content.lower().split())
            round_keywords.update(w for w in words if len(w) >= 5)
        new = round_keywords - cumulative
        ratio = len(new) / max(1, len(cumulative))
        new_per_round.append(ratio)
        cumulative.update(round_keywords)

    return round(sum(new_per_round) / len(new_per_round), 3) if new_per_round else 0.0


def _compute_comparison(
    debate_accuracy: float,
    single_baseline: Optional[str],
    gt_classification: str,
    trace: DebateTrace,
) -> ComparisonScore:
    """Compute comparison scores vs baselines."""
    single_acc = None
    sc_acc = None
    lift_single = None
    lift_sc = None

    if single_baseline is not None:
        single_match = _positions_match(single_baseline, gt_classification)
        single_acc = 1.0 if single_match else 0.0
        lift_single = round(debate_accuracy - single_acc, 3)

    if trace.self_consistency_answers:
        sc_correct = sum(1 for a in trace.self_consistency_answers if _positions_match(a, gt_classification))
        sc_acc = round(sc_correct / len(trace.self_consistency_answers), 3)
        lift_sc = round(debate_accuracy - sc_acc, 3)

    return ComparisonScore(
        single_model_accuracy=single_acc,
        self_consistency_accuracy=sc_acc,
        debate_accuracy=debate_accuracy,
        debate_lift_vs_single=lift_single,
        debate_lift_vs_sc=lift_sc,
    )
