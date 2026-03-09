"""
BioAmbiguity: Context-Dependent Biological Reasoning Evaluation

Tests whether LLMs recognize that the same biological concept behaves
differently depending on context (tissue type, disease state, species,
concentration, developmental stage).

Component 12 of BioEval. 5 task types x 9 tasks = 45 tasks (target).
"""

from __future__ import annotations

from bioeval.models.base import BaseEvaluator, EvalTask
from bioeval.scoring.matching import phrase_match

from bioeval.bioambiguity.tasks import (
    GENE_CONTEXT_TASKS,
    PATHWAY_CROSSTALK_TASKS,
    DOSE_RESPONSE_TASKS,
    TEMPORAL_SHIFT_TASKS,
    SPECIES_TRANSLATION_TASKS,
)


class BioAmbiguityEvaluator(BaseEvaluator):
    """Evaluator for context-dependent biological reasoning."""

    COMPONENT = "bioambiguity"

    def load_tasks(self, data_tier: str = "base") -> list[EvalTask]:
        """Load all bioambiguity evaluation tasks.

        Args:
            data_tier: Data tier to load ("base" only for now).

        Returns:
            List of EvalTask objects across all task types.
        """
        tasks = []

        for task_type, task_list in [
            ("gene_context", GENE_CONTEXT_TASKS),
            ("pathway_crosstalk", PATHWAY_CROSSTALK_TASKS),
            ("dose_response", DOSE_RESPONSE_TASKS),
            ("temporal_shift", TEMPORAL_SHIFT_TASKS),
            ("species_translation", SPECIES_TRANSLATION_TASKS),
        ]:
            for t in task_list:
                tasks.append(EvalTask(
                    id=t["id"],
                    component=self.COMPONENT,
                    task_type=task_type,
                    prompt=t["prompt"],
                    ground_truth=t["ground_truth"],
                    metadata={"title": t["title"]},
                ))

        return tasks

    def score_response(self, task: EvalTask, response: str) -> dict:
        """Score a model response for a bioambiguity task.

        Evaluates three dimensions:
        1. context_awareness: Does the response mention correct context-specific terms?
        2. distinction_quality: Does it distinguish between contexts?
        3. evidence_support: Does it provide mechanistic evidence?

        Returns dict with composite score and per-dimension scores.
        """
        gt = task.ground_truth
        contexts = gt.get("contexts", {})

        if not contexts:
            return {
                "score": 0.0,
                "context_awareness": 0.0,
                "distinction_quality": 0.0,
                "evidence_support": 0.0,
                "error": "No contexts defined in ground truth",
            }

        # 1. Context awareness: check if key_terms are mentioned per context
        context_scores = {}
        total_terms = 0
        found_terms = 0

        for ctx_name, ctx_info in contexts.items():
            key_terms = ctx_info.get("key_terms", [])
            ctx_found = {}
            for term in key_terms:
                matched = phrase_match(term, response)
                ctx_found[term] = matched
                total_terms += 1
                if matched:
                    found_terms += 1
            context_scores[ctx_name] = ctx_found

        context_awareness = found_terms / total_terms if total_terms > 0 else 0.0

        # 2. Distinction quality: check if the distinction key is reflected
        distinction_key = gt.get("distinction_key", "")
        distinction_words = [w.strip(",:;—()-/") for w in distinction_key.split() if len(w.strip(",:;—()-/")) > 4]
        dist_found = 0
        for word in distinction_words:
            if phrase_match(word, response):
                dist_found += 1
        distinction_quality = dist_found / len(distinction_words) if distinction_words else 0.0

        # 3. Evidence support: check role descriptions and mechanism keywords
        evidence_total = 0
        evidence_found = 0
        for ctx_name, ctx_info in contexts.items():
            role = ctx_info.get("role", "")
            role_words = [w for w in role.split() if len(w) > 3]
            for word in role_words:
                evidence_total += 1
                if phrase_match(word, response):
                    evidence_found += 1

        evidence_support = evidence_found / evidence_total if evidence_total > 0 else 0.0

        # Composite: 0.4 * context + 0.35 * distinction + 0.25 * evidence
        composite = (
            0.40 * context_awareness
            + 0.35 * distinction_quality
            + 0.25 * evidence_support
        )

        return {
            "score": round(composite, 4),
            "context_awareness": round(context_awareness, 4),
            "distinction_quality": round(distinction_quality, 4),
            "evidence_support": round(evidence_support, 4),
            "context_details": context_scores,
            "n_contexts": len(contexts),
            "terms_found": found_terms,
            "terms_total": total_terms,
        }
