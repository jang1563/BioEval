"""
Tests for BioAmbiguity component (Component 12).

Covers:
- Task data loading and structure
- Scoring logic (context_awareness, distinction_quality, evidence_support)
- Registry integration
- Normalizer integration
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


# =============================================================================
# DATA LOADING TESTS
# =============================================================================


class TestBioAmbiguityDataLoading:
    """Test that task data loads correctly."""

    def test_task_data_imports(self):
        """Test that all task lists import from tasks.py."""
        from bioeval.bioambiguity.tasks import (
            GENE_CONTEXT_TASKS,
            PATHWAY_CROSSTALK_TASKS,
            DOSE_RESPONSE_TASKS,
            TEMPORAL_SHIFT_TASKS,
            SPECIES_TRANSLATION_TASKS,
        )
        assert len(GENE_CONTEXT_TASKS) == 9
        # Stage 2 types are empty until populated
        assert isinstance(PATHWAY_CROSSTALK_TASKS, list)
        assert isinstance(DOSE_RESPONSE_TASKS, list)
        assert isinstance(TEMPORAL_SHIFT_TASKS, list)
        assert isinstance(SPECIES_TRANSLATION_TASKS, list)

    def test_evaluator_load_tasks(self):
        """Test that BioAmbiguityEvaluator.load_tasks() returns EvalTask objects."""
        from bioeval.bioambiguity.evaluator import BioAmbiguityEvaluator
        from bioeval.models.base import EvalTask

        evaluator = BioAmbiguityEvaluator()
        tasks = evaluator.load_tasks()

        assert len(tasks) >= 9, f"Expected >= 9 tasks, got {len(tasks)}"
        for task in tasks:
            assert isinstance(task, EvalTask)
            assert task.id.startswith("ba_")
            assert task.component == "bioambiguity"
            assert task.task_type in [
                "gene_context",
                "pathway_crosstalk",
                "dose_response",
                "temporal_shift",
                "species_translation",
            ]
            assert task.prompt, f"Task {task.id} has empty prompt"
            assert task.ground_truth, f"Task {task.id} has empty ground_truth"

    def test_task_ids_unique(self):
        """Verify all task IDs are unique."""
        from bioeval.bioambiguity.evaluator import BioAmbiguityEvaluator

        evaluator = BioAmbiguityEvaluator()
        tasks = evaluator.load_tasks()
        ids = [t.id for t in tasks]
        assert len(ids) == len(set(ids)), f"Duplicate task IDs: {[x for x in ids if ids.count(x) > 1]}"

    def test_gene_context_tasks_have_contexts(self):
        """Each gene_context task must have 'contexts' in ground_truth."""
        from bioeval.bioambiguity.tasks import GENE_CONTEXT_TASKS

        for t in GENE_CONTEXT_TASKS:
            gt = t["ground_truth"]
            assert "contexts" in gt, f"Task {t['id']} missing 'contexts' in ground_truth"
            assert len(gt["contexts"]) >= 2, f"Task {t['id']} needs >=2 contexts, got {len(gt['contexts'])}"
            for ctx_name, ctx_info in gt["contexts"].items():
                assert "role" in ctx_info, f"Task {t['id']} context '{ctx_name}' missing 'role'"
                assert "key_terms" in ctx_info, f"Task {t['id']} context '{ctx_name}' missing 'key_terms'"
                assert len(ctx_info["key_terms"]) >= 2, f"Task {t['id']} context '{ctx_name}' needs >=2 key_terms"

    def test_ground_truth_has_distinction_key(self):
        """Each task must have a distinction_key explaining the ambiguity."""
        from bioeval.bioambiguity.tasks import GENE_CONTEXT_TASKS

        for t in GENE_CONTEXT_TASKS:
            gt = t["ground_truth"]
            assert "distinction_key" in gt, f"Task {t['id']} missing 'distinction_key'"
            assert len(gt["distinction_key"]) > 20, f"Task {t['id']} distinction_key too short"


# =============================================================================
# SCORING TESTS
# =============================================================================


class TestBioAmbiguityScoring:
    """Test scoring logic."""

    def _get_evaluator(self):
        from bioeval.bioambiguity.evaluator import BioAmbiguityEvaluator
        return BioAmbiguityEvaluator()

    def _get_first_task(self):
        evaluator = self._get_evaluator()
        tasks = evaluator.load_tasks()
        return tasks[0], evaluator

    def test_perfect_response_scores_high(self):
        """A response mentioning all key terms should score well."""
        task, evaluator = self._get_first_task()
        gt = task.ground_truth

        # Build perfect response from ground truth
        lines = []
        for ctx_name, ctx_info in gt["contexts"].items():
            terms = ctx_info.get("key_terms", [])
            role = ctx_info.get("role", "")
            lines.append(f"In {ctx_name}: {role}. Involves {', '.join(terms)}.")
        lines.append(gt.get("distinction_key", ""))
        response = "\n".join(lines)

        result = evaluator.score_response(task, response)
        assert result["score"] > 0.3, f"Perfect response scored too low: {result['score']}"
        assert result["context_awareness"] > 0.3
        assert result["n_contexts"] >= 2

    def test_empty_response_scores_zero(self):
        """Empty response should score near zero."""
        task, evaluator = self._get_first_task()
        result = evaluator.score_response(task, "")
        assert result["score"] == 0.0
        assert result["context_awareness"] == 0.0

    def test_single_context_response(self):
        """Response mentioning only one context should score lower than all contexts."""
        task, evaluator = self._get_first_task()
        gt = task.ground_truth

        # Only mention first context
        first_ctx = list(gt["contexts"].values())[0]
        terms = first_ctx.get("key_terms", [])
        partial_response = f"This involves {', '.join(terms)}."

        result_partial = evaluator.score_response(task, partial_response)

        # Build full response
        lines = []
        for ctx_name, ctx_info in gt["contexts"].items():
            t = ctx_info.get("key_terms", [])
            lines.append(f"{', '.join(t)}")
        full_response = "\n".join(lines)

        result_full = evaluator.score_response(task, full_response)
        assert result_full["context_awareness"] >= result_partial["context_awareness"]

    def test_score_output_format(self):
        """Verify score output has required fields."""
        task, evaluator = self._get_first_task()
        result = evaluator.score_response(task, "Some response about biology.")

        required_fields = [
            "score", "context_awareness", "distinction_quality",
            "evidence_support", "context_details", "n_contexts",
            "terms_found", "terms_total",
        ]
        for field in required_fields:
            assert field in result, f"Missing field: {field}"

        assert 0.0 <= result["score"] <= 1.0
        assert 0.0 <= result["context_awareness"] <= 1.0
        assert 0.0 <= result["distinction_quality"] <= 1.0
        assert 0.0 <= result["evidence_support"] <= 1.0

    def test_all_tasks_scoreable(self):
        """All loaded tasks should be scoreable without errors."""
        evaluator = self._get_evaluator()
        tasks = evaluator.load_tasks()

        for task in tasks:
            result = evaluator.score_response(task, "Test response mentioning apoptosis and senescence.")
            assert "score" in result, f"Task {task.id} scoring failed"
            assert "error" not in result, f"Task {task.id} returned error: {result.get('error')}"


# =============================================================================
# REGISTRY TESTS
# =============================================================================


class TestBioAmbiguityRegistry:
    """Test component registry integration."""

    def test_component_in_registry(self):
        """BioAmbiguity must be in the component registry."""
        from bioeval.registry import REGISTRY
        assert "bioambiguity" in REGISTRY

    def test_registry_metadata(self):
        """Registry entry should have correct metadata."""
        from bioeval.registry import REGISTRY
        info = REGISTRY["bioambiguity"]
        assert info.name == "bioambiguity"
        assert "context" in info.description.lower() or "ambiguity" in info.description.lower()
        assert info.evaluator_class == "BioAmbiguityEvaluator"
        assert "gene_context" in info.task_types
        assert len(info.task_types) == 5
        assert "base" in info.supports_data_tiers

    def test_registry_load_tasks(self):
        """Registry should be able to load tasks."""
        from bioeval.registry import REGISTRY
        info = REGISTRY["bioambiguity"]
        tasks = info.load_tasks()
        assert len(tasks) >= 9

    def test_config_includes_bioambiguity(self):
        """Config COMPONENTS and TASK_TYPES should include bioambiguity."""
        from bioeval.config import COMPONENTS, TASK_TYPES
        assert "bioambiguity" in COMPONENTS
        assert "bioambiguity" in TASK_TYPES
        assert len(TASK_TYPES["bioambiguity"]) == 5


# =============================================================================
# NORMALIZER TESTS
# =============================================================================


class TestBioAmbiguityNormalizer:
    """Test normalizer integration."""

    def test_normalize_result(self):
        """Normalizer should handle bioambiguity results."""
        from bioeval.scoring.normalizer import normalize_result

        result = {
            "task_id": "ba_gc_001",
            "score": 0.65,
            "context_awareness": 0.8,
            "distinction_quality": 0.5,
            "evidence_support": 0.6,
        }
        normalized = normalize_result(result, "bioambiguity")
        assert normalized.component == "bioambiguity"
        assert normalized.task_type == "gene_context"
        assert normalized.score == 0.65
        assert normalized.passed is True
        assert "context_awareness" in normalized.subscores

    def test_normalize_failing_score(self):
        """Score below 0.5 should not pass."""
        from bioeval.scoring.normalizer import normalize_result

        result = {
            "task_id": "ba_gc_002",
            "score": 0.3,
            "context_awareness": 0.4,
            "distinction_quality": 0.2,
            "evidence_support": 0.3,
        }
        normalized = normalize_result(result, "bioambiguity")
        assert normalized.passed is False
        assert normalized.score == 0.3

    def test_normalize_task_type_inference(self):
        """Task type should be inferred from task ID prefix."""
        from bioeval.scoring.normalizer import normalize_bioambiguity

        for prefix, expected_type in [
            ("ba_gc_001", "gene_context"),
            ("ba_pc_001", "pathway_crosstalk"),
            ("ba_dr_001", "dose_response"),
            ("ba_ts_001", "temporal_shift"),
            ("ba_st_001", "species_translation"),
        ]:
            result = {"task_id": prefix, "score": 0.5}
            normalized = normalize_bioambiguity(result)
            assert normalized.task_type == expected_type, f"Expected {expected_type} for {prefix}"


# =============================================================================
# SIMULATION TESTS
# =============================================================================


class TestBioAmbiguitySimulation:
    """Test simulation generator."""

    def test_gen_good_quality(self):
        """Good quality simulation should produce scoreable responses."""
        import random
        from bioeval.simulation import _gen_bioambiguity
        from bioeval.bioambiguity.evaluator import BioAmbiguityEvaluator

        evaluator = BioAmbiguityEvaluator()
        tasks = evaluator.load_tasks()
        rng = random.Random(42)

        for task in tasks[:3]:
            response = _gen_bioambiguity(task, "good", rng)
            assert len(response) > 50, f"Good response too short for {task.id}"
            result = evaluator.score_response(task, response)
            assert result["score"] > 0.2, f"Good quality scored too low for {task.id}: {result['score']}"

    def test_gen_bad_quality(self):
        """Bad quality simulation should produce low-scoring responses."""
        import random
        from bioeval.simulation import _gen_bioambiguity
        from bioeval.bioambiguity.evaluator import BioAmbiguityEvaluator

        evaluator = BioAmbiguityEvaluator()
        tasks = evaluator.load_tasks()
        rng = random.Random(42)

        for task in tasks[:3]:
            response = _gen_bioambiguity(task, "bad", rng)
            result = evaluator.score_response(task, response)
            assert result["score"] < 0.3, f"Bad quality scored too high for {task.id}: {result['score']}"

    def test_simulate_bioambiguity(self):
        """Full simulation should produce results for all tasks."""
        import random
        from bioeval.simulation import _simulate_bioambiguity
        from bioeval.bioambiguity.evaluator import BioAmbiguityEvaluator

        evaluator = BioAmbiguityEvaluator()
        rng = random.Random(42)

        result = _simulate_bioambiguity(evaluator, "good", rng)
        assert result["component"] == "bioambiguity"
        assert result["num_tasks"] >= 9
        for r in result["results"]:
            assert "task_id" in r
            assert "score" in r or "error" in r


# =============================================================================
# STATISTICS TESTS
# =============================================================================


class TestBioAmbiguityStatistics:
    """Test statistics integration."""

    def test_benchmark_statistics_includes_bioambiguity(self):
        """compute_benchmark_statistics should include bioambiguity."""
        from bioeval.reporting.statistics import compute_benchmark_statistics

        stats = compute_benchmark_statistics()
        assert "bioambiguity" in stats["components"]
        ba_stats = stats["components"]["bioambiguity"]
        assert ba_stats["n_tasks"] >= 9
        assert "gene_context" in ba_stats["by_type"]
