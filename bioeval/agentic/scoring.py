"""
Milestone scoring for agentic tasks.

Evaluates each step's response against milestone criteria using phrase_match.
Computes a progress rate (milestones achieved / total milestones).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from bioeval.scoring.matching import phrase_match


@dataclass
class MilestoneScore:
    """Score for a single milestone (one step)."""

    step_number: int
    milestone_name: str
    criteria_total: int
    criteria_met: int
    criteria_details: dict = field(default_factory=dict)
    achieved: bool = False
    confidence: float = 0.0


def score_milestone(
    step_number: int,
    milestone_name: str,
    criteria: list[str],
    response: str,
    threshold: float = 0.5,
) -> MilestoneScore:
    """Score a single milestone against a model response.

    A milestone is achieved if >= threshold fraction of its criteria
    are detected in the response via phrase_match.

    Args:
        step_number: Which step this milestone belongs to.
        milestone_name: Human-readable name for the milestone.
        criteria: List of phrases to match.
        response: The model's response text.
        threshold: Fraction of criteria that must match (default 0.5).

    Returns:
        MilestoneScore with details.
    """
    if not criteria:
        return MilestoneScore(
            step_number=step_number,
            milestone_name=milestone_name,
            criteria_total=0,
            criteria_met=0,
            achieved=True,
            confidence=1.0,
        )

    details = {}
    met = 0
    for c in criteria:
        found = phrase_match(c, response)
        details[c] = found
        if found:
            met += 1

    total = len(criteria)
    confidence = met / total
    achieved = confidence >= threshold

    return MilestoneScore(
        step_number=step_number,
        milestone_name=milestone_name,
        criteria_total=total,
        criteria_met=met,
        criteria_details=details,
        achieved=achieved,
        confidence=round(confidence, 3),
    )


def compute_progress_rate(milestone_scores: list[MilestoneScore]) -> float:
    """Compute overall progress rate from milestone scores.

    progress_rate = milestones_achieved / total_milestones
    """
    if not milestone_scores:
        return 0.0
    achieved = sum(1 for m in milestone_scores if m.achieved)
    return round(achieved / len(milestone_scores), 3)
