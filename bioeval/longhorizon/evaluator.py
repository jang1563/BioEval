"""
LongHorizon: Multi-step Scientific Reasoning Evaluation

Tests whether LLMs can sustain coherent reasoning across multi-step
experimental workflows: tracking constraints, accumulating state,
detecting error propagation, managing resources, and adaptively replanning.

Component 10 of BioEval. 5 task types x 6 tasks = 30 tasks (target).

See DESIGN.md for full architecture and rationale.
"""

from __future__ import annotations

from bioeval.models.base import BaseEvaluator, EvalTask, EvalResult
from bioeval.scoring.matching import phrase_match as _phrase_match

from bioeval.longhorizon.tasks import (
    CONSTRAINT_TRACKING_TASKS,
    STATE_ACCUMULATION_TASKS,
    ERROR_PROPAGATION_TASKS,
    RESOURCE_MANAGEMENT_TASKS,
    ADAPTIVE_REPLANNING_TASKS,
)


def _normalize_hyphens(text: str) -> str:
    """Replace hyphens with spaces for matching scientific terms.

    Models often write 'cross-species' while ground truth keys use
    'cross_species' (which becomes 'cross species' after underscore replacement).
    """
    return text.replace("-", " ")


def phrase_match(query: str, text: str) -> bool:
    """phrase_match with hyphen normalization for scientific terms."""
    if _phrase_match(query, text):
        return True
    return _phrase_match(_normalize_hyphens(query), _normalize_hyphens(text))


class LongHorizonEvaluator(BaseEvaluator):
    """Evaluator for long-horizon multi-step scientific reasoning."""

    COMPONENT = "longhorizon"

    def load_tasks(self, data_tier: str = "base") -> list[EvalTask]:
        """Load all long-horizon evaluation tasks.

        Args:
            data_tier: Data tier to load ("base" only for now).

        Returns:
            List of EvalTask objects across all 5 task types.
        """
        tasks = []

        # constraint_tracking
        for t in CONSTRAINT_TRACKING_TASKS:
            stage_text = "\n\n".join(
                f"**Stage {s['stage']}: {s['name']}**\n{s['content']}"
                for s in t["stages"]
            )
            prompt = (
                f"# Long-Horizon Experiment Review: {t['title']}\n\n"
                f"The following multi-stage experiment has been planned. "
                f"Review the entire plan and answer the question at the end.\n\n"
                f"{stage_text}\n\n"
                f"## Question\n{t['question']}"
            )
            tasks.append(EvalTask(
                id=t["id"],
                component=self.COMPONENT,
                task_type="constraint_tracking",
                prompt=prompt,
                ground_truth=t["ground_truth"],
                metadata={"title": t["title"], "n_stages": len(t["stages"])},
            ))

        # state_accumulation
        for t in STATE_ACCUMULATION_TASKS:
            stage_text = "\n\n".join(
                f"**Stage {s['stage']}: {s['name']}**\n{s['content']}"
                for s in t["stages"]
            )
            final_q = t["stages"][-1]["checkpoint_question"]
            prompt = (
                f"# Long-Horizon Campaign: {t['title']}\n\n"
                f"You are reviewing a multi-stage research campaign. Read all stages "
                f"carefully, tracking which candidates/items remain active and which "
                f"have been eliminated at each stage.\n\n"
                f"{stage_text}\n\n"
                f"## Final Question\n{final_q}"
            )
            tasks.append(EvalTask(
                id=t["id"],
                component=self.COMPONENT,
                task_type="state_accumulation",
                prompt=prompt,
                ground_truth=t["ground_truth"],
                metadata={"title": t["title"], "n_stages": len(t["stages"])},
            ))

        # error_propagation
        for t in ERROR_PROPAGATION_TASKS:
            prompt = (
                f"# Error Propagation Analysis: {t['title']}\n\n"
                f"## Completed Study\n{t['completed_plan']}\n\n"
                f"## Revealed Error\n{t['revealed_error']}\n\n"
                f"## Question\n{t['question']}"
            )
            tasks.append(EvalTask(
                id=t["id"],
                component=self.COMPONENT,
                task_type="error_propagation",
                prompt=prompt,
                ground_truth=t["ground_truth"],
                metadata={"title": t["title"]},
            ))

        # resource_management
        for t in RESOURCE_MANAGEMENT_TASKS:
            prompt = (
                f"# Resource Management: {t['title']}\n\n"
                f"## Scenario\n{t['scenario']}\n\n"
                f"## Question\n{t['question']}"
            )
            tasks.append(EvalTask(
                id=t["id"],
                component=self.COMPONENT,
                task_type="resource_management",
                prompt=prompt,
                ground_truth=t["ground_truth"],
                metadata={"title": t["title"]},
            ))

        # adaptive_replanning
        for t in ADAPTIVE_REPLANNING_TASKS:
            prompt = (
                f"# Adaptive Replanning: {t['title']}\n\n"
                f"## Original Plan\n{t['original_plan']}\n\n"
                f"## Unexpected Result\n{t['unexpected_result']}\n\n"
                f"## Question\n{t['question']}"
            )
            tasks.append(EvalTask(
                id=t["id"],
                component=self.COMPONENT,
                task_type="adaptive_replanning",
                prompt=prompt,
                ground_truth=t["ground_truth"],
                metadata={"title": t["title"]},
            ))

        return tasks

    def score_response(self, task: EvalTask, response: str) -> dict:
        """Score a model response for a long-horizon task.

        Dispatches to task-type-specific scoring methods.
        Uses phrase_match() for robust keyword detection.
        """
        if task.task_type == "constraint_tracking":
            return self._score_constraint_tracking(task, response)
        elif task.task_type == "state_accumulation":
            return self._score_state_accumulation(task, response)
        elif task.task_type == "error_propagation":
            return self._score_error_propagation(task, response)
        elif task.task_type == "resource_management":
            return self._score_resource_management(task, response)
        elif task.task_type == "adaptive_replanning":
            return self._score_adaptive_replanning(task, response)
        else:
            return {"error": f"Unknown task type: {task.task_type}", "score": 0.0}

    # ------------------------------------------------------------------
    # Task-type-specific scoring
    # ------------------------------------------------------------------

    def _score_constraint_tracking(self, task: EvalTask, response: str) -> dict:
        """Score constraint tracking: check if violations are identified.

        Each violation key (e.g. "cross_species_contamination") is converted
        to a human-readable phrase and matched via phrase_match().
        """
        gt = task.ground_truth
        violations_found = 0
        violation_details = {}

        for v in gt.get("violations", []):
            query = v.replace("_", " ")
            found = phrase_match(query, response)
            violation_details[v] = found
            if found:
                violations_found += 1

        total = len(gt.get("violations", []))
        recall = violations_found / total if total > 0 else 0.0

        return {
            "violations_detected": violations_found,
            "violations_total": total,
            "violation_details": violation_details,
            "recall": round(recall, 3),
            "pass": violations_found >= gt.get("min_violations_expected", 1),
        }

    def _score_state_accumulation(self, task: EvalTask, response: str) -> dict:
        """Score state accumulation: check final state accuracy.

        Checks whether the model correctly reports:
        1. Final active targets
        2. All elimination decisions with reasons
        """
        gt = task.ground_truth

        final_targets = gt.get("final_active_targets", [])
        targets_found = {}
        for t in final_targets:
            targets_found[t] = phrase_match(t, response)
        targets_mentioned = sum(1 for v in targets_found.values() if v)

        eliminations = gt.get("all_eliminations", {})
        elims_found = {}
        for name in eliminations:
            query = name.replace("Compound_", "Compound ").replace("_", " ")
            elims_found[name] = phrase_match(query, response)
        elims_mentioned = sum(1 for v in elims_found.values() if v)

        target_recall = targets_mentioned / len(final_targets) if final_targets else 0.0
        elim_recall = elims_mentioned / len(eliminations) if eliminations else 0.0

        return {
            "active_targets_correct": targets_mentioned,
            "active_targets_total": len(final_targets),
            "target_details": targets_found,
            "eliminations_mentioned": elims_mentioned,
            "eliminations_total": len(eliminations),
            "elimination_details": elims_found,
            "target_recall": round(target_recall, 3),
            "elimination_recall": round(elim_recall, 3),
            "composite_score": round((target_recall + elim_recall) / 2, 3),
        }

    def _score_error_propagation(self, task: EvalTask, response: str) -> dict:
        """Score error propagation: check affected/unaffected identification.

        Each ground truth key (e.g. "stage_5_normalization") is converted
        to a phrase and matched.
        """
        gt = task.ground_truth

        affected = gt.get("affected", [])
        unaffected = gt.get("unaffected", [])

        affected_details = {}
        for a in affected:
            query = a.replace("_", " ")
            affected_details[a] = phrase_match(query, response)
        affected_found = sum(1 for v in affected_details.values() if v)

        unaffected_details = {}
        for u in unaffected:
            query = u.replace("_", " ")
            unaffected_details[u] = phrase_match(query, response)
        unaffected_found = sum(1 for v in unaffected_details.values() if v)

        affected_recall = affected_found / len(affected) if affected else 0.0
        unaffected_recall = unaffected_found / len(unaffected) if unaffected else 0.0

        return {
            "affected_identified": affected_found,
            "affected_total": len(affected),
            "affected_details": affected_details,
            "unaffected_identified": unaffected_found,
            "unaffected_total": len(unaffected),
            "unaffected_details": unaffected_details,
            "affected_recall": round(affected_recall, 3),
            "unaffected_recall": round(unaffected_recall, 3),
            "composite_score": round((affected_recall + unaffected_recall) / 2, 3),
        }

    def _score_resource_management(self, task: EvalTask, response: str) -> dict:
        """Score resource management: check feasibility assessments."""
        gt = task.ground_truth

        infeasible = gt.get("infeasible", {})
        infeasible_correct = 0
        infeasible_details = {}

        for name, info in infeasible.items():
            item_query = name.replace("_", " ")
            item_mentioned = phrase_match(item_query, response)

            reason_detected = False
            if item_mentioned:
                infeasibility_terms = [
                    "infeasible", "not feasible", "cannot be", "not possible",
                    "cannot accommodate", "not enough", "insufficient",
                    "shortage", "expired", "expires", "expiry",
                    "unavailable", "not available", "out for repair",
                    "over budget", "exceed", "exceeds",
                    "not submitted", "pending approval",
                    "fresh sample", "frozen", "incompatible",
                ]
                reason_detected = any(
                    phrase_match(term, response) for term in infeasibility_terms
                )

            correct = item_mentioned and reason_detected
            infeasible_details[name] = {
                "item_mentioned": item_mentioned,
                "reason_detected": reason_detected,
                "correct": correct,
            }
            if correct:
                infeasible_correct += 1

        total_infeasible = len(infeasible)
        score = infeasible_correct / total_infeasible if total_infeasible else 1.0

        return {
            "infeasible_correctly_identified": infeasible_correct,
            "infeasible_total": total_infeasible,
            "infeasible_details": infeasible_details,
            "score": round(score, 3),
        }

    def _score_adaptive_replanning(self, task: EvalTask, response: str) -> dict:
        """Score adaptive replanning: check required/prohibited elements.

        Uses phrase_match() for each required/prohibited/bonus element.
        Prohibited elements incur a penalty.
        """
        gt = task.ground_truth

        required = gt.get("required_elements", [])
        prohibited = gt.get("prohibited_elements", [])
        bonus = gt.get("bonus_elements", [])

        required_details = {}
        for r in required:
            required_details[r] = phrase_match(r, response)
        required_found = sum(1 for v in required_details.values() if v)

        prohibited_details = {}
        for p in prohibited:
            prohibited_details[p] = phrase_match(p, response)
        prohibited_found = sum(1 for v in prohibited_details.values() if v)

        bonus_details = {}
        for b in bonus:
            bonus_details[b] = phrase_match(b, response)
        bonus_found = sum(1 for v in bonus_details.values() if v)

        required_score = required_found / len(required) if required else 0.0
        penalty = prohibited_found * 0.2

        return {
            "required_elements_found": required_found,
            "required_elements_total": len(required),
            "required_details": required_details,
            "prohibited_elements_found": prohibited_found,
            "prohibited_details": prohibited_details,
            "bonus_elements_found": bonus_found,
            "bonus_details": bonus_details,
            "required_score": round(required_score, 3),
            "penalty": round(penalty, 3),
            "composite_score": round(max(0.0, required_score - penalty), 3),
        }
