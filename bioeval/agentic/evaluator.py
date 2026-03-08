"""
AgenticEvaluator: Pseudo-agentic multi-step scientific reasoning.

Standalone evaluator (does NOT inherit BaseEvaluator) following the
MultiTurnEvaluator pattern. Each task presents a multi-step scientific
workflow; the model reasons through each step, and milestone criteria
are checked via phrase_match.

No code execution — evaluates reasoning quality only.
Only works with API-backed models (requires generate_chat).
"""

from __future__ import annotations

import datetime

from bioeval.agentic.scoring import (
    score_milestone,
    compute_progress_rate,
    MilestoneScore,
)
from bioeval.agentic.tasks import AGENTIC_TASKS, AgenticTask


# ---------------------------------------------------------------
# Task wrapper for CLI compatibility
# ---------------------------------------------------------------


class _AgenticTaskWrapper:
    """Wraps AgenticTask for CLI compatibility (needs .id, .task_type, .prompt)."""

    def __init__(self, task: AgenticTask):
        self.id = task.id
        self.task_type = task.category
        self.component = "agentic"
        self.prompt = task.scenario  # CLI may display this
        self.ground_truth = task.ground_truth
        self.metadata = {"title": task.title, "n_steps": len(task.steps)}
        self._task = task  # Original task for evaluate_task


# ---------------------------------------------------------------
# Evaluator
# ---------------------------------------------------------------


class AgenticEvaluator:
    """Evaluator for pseudo-agentic multi-step scientific reasoning.

    Each task has multiple steps. For each step the model receives a prompt
    and generates a response. Milestone criteria are checked on each response
    using phrase_match. The overall score is a progress rate
    (milestones_achieved / total_milestones).

    This evaluator manages its own model client (like MultiTurnEvaluator).
    """

    COMPONENT = "agentic"

    def __init__(
        self,
        model_name: str = "claude-sonnet-4-20250514",
        temperature: float = 0.0,
    ):
        self.model_name = model_name
        self.temperature = temperature
        self._model_client = None

    @property
    def model_client(self):
        if self._model_client is None:
            from bioeval.models.base import init_model

            self._model_client = init_model(
                self.model_name, temperature=self.temperature
            )
        return self._model_client

    # ------------------------------------------------------------------
    # CLI interface
    # ------------------------------------------------------------------

    def load_tasks(self, data_tier: str = "base") -> list[_AgenticTaskWrapper]:
        """Load all agentic tasks wrapped for CLI compatibility."""
        return [_AgenticTaskWrapper(t) for t in AGENTIC_TASKS]

    def evaluate_task(self, task_wrapper) -> dict:
        """Evaluate a single agentic task (CLI entry point).

        Sends the scenario + first step as the initial message, then
        iterates through remaining steps. Each step prompt is sent once,
        scored against milestone criteria, and the conversation continues.
        """
        task: AgenticTask = task_wrapper._task

        system_prompt = (
            "You are a scientific research assistant working through a multi-step "
            "research workflow. For each step, provide detailed reasoning and "
            "concrete recommendations. Be specific about methods, parameters, "
            "controls, and potential issues. Think step by step."
        )

        messages = []
        step_scores: list[MilestoneScore] = []
        step_responses: list[str] = []

        for step in task.steps:
            if step.step_number == 1:
                # First step: combine scenario + step prompt
                messages.append({
                    "role": "user",
                    "content": (
                        f"{task.scenario}\n\n"
                        f"## Step {step.step_number}: {step.name}\n"
                        f"{step.prompt}"
                    ),
                })
            else:
                # Subsequent steps: add formatted step prompt
                messages.append({
                    "role": "user",
                    "content": (
                        f"## Step {step.step_number}: {step.name}\n"
                        f"{step.prompt}"
                    ),
                })

            # Get model response
            response = self.model_client.generate_chat(
                messages,
                max_tokens=3000,
                system=system_prompt,
            )
            if not response:
                response = "[No response generated]"

            messages.append({"role": "assistant", "content": response})
            step_responses.append(response)

            # Score milestone
            ms = score_milestone(
                step_number=step.step_number,
                milestone_name=step.milestone_name,
                criteria=step.milestone_criteria,
                response=response,
            )
            step_scores.append(ms)

        progress = compute_progress_rate(step_scores)

        return {
            "task_id": task.id,
            "category": task.category,
            "title": task.title,
            "scores": {
                "progress_rate": progress,
                "milestones_achieved": sum(1 for m in step_scores if m.achieved),
                "milestones_total": len(step_scores),
                "step_scores": [
                    {
                        "step": m.step_number,
                        "milestone": m.milestone_name,
                        "achieved": m.achieved,
                        "confidence": m.confidence,
                        "criteria_met": m.criteria_met,
                        "criteria_total": m.criteria_total,
                    }
                    for m in step_scores
                ],
            },
            "response": "\n\n".join(step_responses),
            "responses": step_responses,
            "timestamp": datetime.datetime.now().isoformat(),
        }

    # ------------------------------------------------------------------
    # Standalone evaluation
    # ------------------------------------------------------------------

    def run_evaluation(self, data_tier: str = "base") -> list[dict]:
        """Run evaluation on all tasks and return results."""
        tasks = self.load_tasks(data_tier)
        results = []
        for tw in tasks:
            result = self.evaluate_task(tw)
            results.append(result)
        return results

    # ------------------------------------------------------------------
    # Offline scoring (no model needed)
    # ------------------------------------------------------------------

    @staticmethod
    def score_response(task_wrapper, responses: list[str]) -> dict:
        """Score pre-collected responses against milestone criteria.

        This allows scoring existing responses without calling the model.

        Args:
            task_wrapper: An _AgenticTaskWrapper (or object with ._task).
            responses: List of response strings, one per step.

        Returns:
            Scoring dict compatible with evaluate_task output.
        """
        task: AgenticTask = task_wrapper._task

        if len(responses) != len(task.steps):
            return {
                "task_id": task.id,
                "error": (
                    f"Expected {len(task.steps)} responses, got {len(responses)}"
                ),
                "scores": {"progress_rate": 0.0},
            }

        step_scores = []
        for step, response in zip(task.steps, responses):
            ms = score_milestone(
                step_number=step.step_number,
                milestone_name=step.milestone_name,
                criteria=step.milestone_criteria,
                response=response,
            )
            step_scores.append(ms)

        progress = compute_progress_rate(step_scores)

        return {
            "task_id": task.id,
            "category": task.category,
            "title": task.title,
            "scores": {
                "progress_rate": progress,
                "milestones_achieved": sum(1 for m in step_scores if m.achieved),
                "milestones_total": len(step_scores),
                "step_scores": [
                    {
                        "step": m.step_number,
                        "milestone": m.milestone_name,
                        "achieved": m.achieved,
                        "confidence": m.confidence,
                        "criteria_met": m.criteria_met,
                        "criteria_total": m.criteria_total,
                    }
                    for m in step_scores
                ],
            },
        }
