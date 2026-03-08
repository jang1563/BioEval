"""Tests for the agentic (pseudo-agentic multi-step reasoning) component."""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------


class TestAgenticDataLoading:
    """Verify task data imports and structure."""

    def test_task_data_imports(self):
        from bioeval.agentic.tasks import AGENTIC_TASKS, AgenticTask, AgenticStep

        assert len(AGENTIC_TASKS) == 24
        for t in AGENTIC_TASKS:
            assert isinstance(t, AgenticTask)
            assert t.id
            assert t.category
            assert t.title
            assert t.scenario
            assert len(t.steps) >= 3
            for s in t.steps:
                assert isinstance(s, AgenticStep)
                assert s.step_number >= 1
                assert s.name
                assert s.prompt
                assert s.milestone_name
                assert isinstance(s.milestone_criteria, list)
                assert len(s.milestone_criteria) >= 1

    def test_evaluator_load_tasks(self):
        from bioeval.agentic.evaluator import AgenticEvaluator

        evaluator = AgenticEvaluator()
        tasks = evaluator.load_tasks()
        assert len(tasks) == 24

    def test_task_ids_unique(self):
        from bioeval.agentic.tasks import AGENTIC_TASKS

        ids = [t.id for t in AGENTIC_TASKS]
        assert len(ids) == len(set(ids)), f"Duplicate IDs: {[x for x in ids if ids.count(x) > 1]}"

    def test_task_category_distribution(self):
        from bioeval.agentic.tasks import AGENTIC_TASKS
        from collections import Counter

        categories = Counter(t.category for t in AGENTIC_TASKS)
        assert categories["experimental_design"] == 6
        assert categories["bioinformatics_pipeline"] == 6
        assert categories["literature_research"] == 6
        assert categories["troubleshooting"] == 6

    def test_wrapper_has_required_attrs(self):
        """CLI compatibility: wrapper must have .id, .task_type, .prompt, .ground_truth."""
        from bioeval.agentic.evaluator import AgenticEvaluator

        evaluator = AgenticEvaluator()
        tasks = evaluator.load_tasks()
        for tw in tasks:
            assert hasattr(tw, "id")
            assert hasattr(tw, "task_type")
            assert hasattr(tw, "prompt")
            assert hasattr(tw, "ground_truth")
            assert hasattr(tw, "component")
            assert tw.component == "agentic"

    def test_step_numbers_sequential(self):
        """Step numbers should be 1, 2, 3, ..."""
        from bioeval.agentic.tasks import AGENTIC_TASKS

        for task in AGENTIC_TASKS:
            nums = [s.step_number for s in task.steps]
            expected = list(range(1, len(task.steps) + 1))
            assert nums == expected, f"{task.id}: steps not sequential: {nums}"


# ---------------------------------------------------------------
# Milestone scoring
# ---------------------------------------------------------------


class TestMilestoneScoring:
    """Test milestone scoring functions."""

    def test_perfect_detection(self):
        from bioeval.agentic.scoring import score_milestone

        ms = score_milestone(
            step_number=1,
            milestone_name="test_milestone",
            criteria=["CRISPR", "knockout", "sgRNA"],
            response="We will use CRISPR knockout with 6 sgRNA guides per gene.",
        )
        assert ms.achieved
        assert ms.confidence == 1.0
        assert ms.criteria_met == 3
        assert ms.criteria_total == 3

    def test_no_detection(self):
        from bioeval.agentic.scoring import score_milestone

        ms = score_milestone(
            step_number=1,
            milestone_name="test_milestone",
            criteria=["PCR", "thermocycler", "annealing"],
            response="We analyzed protein expression by Western blot.",
        )
        assert not ms.achieved
        assert ms.confidence == 0.0
        assert ms.criteria_met == 0

    def test_partial_detection_above_threshold(self):
        from bioeval.agentic.scoring import score_milestone

        ms = score_milestone(
            step_number=1,
            milestone_name="test_milestone",
            criteria=["CRISPR", "knockout", "lentivirus", "puromycin"],
            response="We use CRISPR knockout with lentivirus transduction.",
            threshold=0.5,
        )
        assert ms.achieved  # 3/4 = 0.75 >= 0.5
        assert ms.criteria_met == 3

    def test_partial_detection_below_threshold(self):
        from bioeval.agentic.scoring import score_milestone

        ms = score_milestone(
            step_number=1,
            milestone_name="test_milestone",
            criteria=["CRISPR", "knockout", "lentivirus", "puromycin"],
            response="We use CRISPR for gene editing.",
            threshold=0.5,
        )
        assert not ms.achieved  # 1/4 = 0.25 < 0.5
        assert ms.criteria_met == 1

    def test_empty_criteria(self):
        from bioeval.agentic.scoring import score_milestone

        ms = score_milestone(
            step_number=1,
            milestone_name="test_milestone",
            criteria=[],
            response="Any response.",
        )
        assert ms.achieved
        assert ms.confidence == 1.0

    def test_criteria_details_dict(self):
        from bioeval.agentic.scoring import score_milestone

        ms = score_milestone(
            step_number=1,
            milestone_name="test",
            criteria=["alpha", "beta"],
            response="This contains alpha but not the other.",
        )
        assert isinstance(ms.criteria_details, dict)
        assert ms.criteria_details["alpha"] is True
        assert ms.criteria_details["beta"] is False


class TestProgressRate:
    """Test progress rate computation."""

    def test_all_achieved(self):
        from bioeval.agentic.scoring import compute_progress_rate, MilestoneScore

        scores = [
            MilestoneScore(step_number=1, milestone_name="m1", criteria_total=3, criteria_met=3, achieved=True, confidence=1.0),
            MilestoneScore(step_number=2, milestone_name="m2", criteria_total=2, criteria_met=2, achieved=True, confidence=1.0),
        ]
        assert compute_progress_rate(scores) == 1.0

    def test_none_achieved(self):
        from bioeval.agentic.scoring import compute_progress_rate, MilestoneScore

        scores = [
            MilestoneScore(step_number=1, milestone_name="m1", criteria_total=3, criteria_met=0, achieved=False, confidence=0.0),
            MilestoneScore(step_number=2, milestone_name="m2", criteria_total=2, criteria_met=0, achieved=False, confidence=0.0),
        ]
        assert compute_progress_rate(scores) == 0.0

    def test_partial_achieved(self):
        from bioeval.agentic.scoring import compute_progress_rate, MilestoneScore

        scores = [
            MilestoneScore(step_number=1, milestone_name="m1", criteria_total=3, criteria_met=3, achieved=True, confidence=1.0),
            MilestoneScore(step_number=2, milestone_name="m2", criteria_total=3, criteria_met=0, achieved=False, confidence=0.0),
            MilestoneScore(step_number=3, milestone_name="m3", criteria_total=3, criteria_met=3, achieved=True, confidence=1.0),
        ]
        rate = compute_progress_rate(scores)
        assert abs(rate - 0.667) < 0.01

    def test_empty_scores(self):
        from bioeval.agentic.scoring import compute_progress_rate

        assert compute_progress_rate([]) == 0.0


# ---------------------------------------------------------------
# Offline scoring (score_response)
# ---------------------------------------------------------------


class TestOfflineScoring:
    """Test score_response without a model."""

    def test_score_response_correct_length(self):
        from bioeval.agentic.evaluator import AgenticEvaluator

        evaluator = AgenticEvaluator()
        tasks = evaluator.load_tasks()
        tw = tasks[0]  # ag_ed_001
        n_steps = len(tw._task.steps)

        # Generate dummy responses
        responses = ["This is a response about CRISPR knockout screening."] * n_steps
        result = AgenticEvaluator.score_response(tw, responses)
        assert "error" not in result
        assert "scores" in result
        assert result["scores"]["milestones_total"] == n_steps

    def test_score_response_wrong_length(self):
        from bioeval.agentic.evaluator import AgenticEvaluator

        evaluator = AgenticEvaluator()
        tasks = evaluator.load_tasks()
        tw = tasks[0]

        result = AgenticEvaluator.score_response(tw, ["only one response"])
        assert "error" in result
        assert result["scores"]["progress_rate"] == 0.0


# ---------------------------------------------------------------
# Registry integration
# ---------------------------------------------------------------


class TestRegistryIntegration:
    """Test that agentic is properly registered."""

    def test_in_registry(self):
        from bioeval.registry import REGISTRY

        assert "agentic" in REGISTRY

    def test_in_config_components(self):
        from bioeval.config import COMPONENTS, TASK_TYPES

        assert "agentic" in COMPONENTS
        assert "agentic" in TASK_TYPES
        assert "experimental_design" in TASK_TYPES["agentic"]

    def test_registry_load_tasks(self):
        from bioeval.registry import REGISTRY

        info = REGISTRY["agentic"]
        tasks = info.load_tasks()
        assert len(tasks) >= 6

    def test_in_package_init(self):
        import bioeval

        assert hasattr(bioeval, "AgenticEvaluator")


# ---------------------------------------------------------------
# Normalizer integration
# ---------------------------------------------------------------


class TestNormalizerIntegration:
    """Test normalizer for agentic results."""

    def test_normalize_agentic_full(self):
        from bioeval.scoring.normalizer import normalize_agentic

        result = {
            "task_id": "ag_ed_001",
            "category": "experimental_design",
            "title": "CRISPR screen",
            "scores": {
                "progress_rate": 0.8,
                "milestones_achieved": 4,
                "milestones_total": 5,
            },
        }
        ns = normalize_agentic(result)
        assert ns.component == "agentic"
        assert ns.task_type == "experimental_design"
        assert ns.score == 0.8
        assert ns.passed is True
        assert ns.subscores["milestones_achieved"] == 4
        assert ns.subscores["milestones_total"] == 5

    def test_normalize_agentic_zero(self):
        from bioeval.scoring.normalizer import normalize_agentic

        result = {
            "task_id": "ag_ed_002",
            "category": "experimental_design",
            "scores": {"progress_rate": 0.0, "milestones_achieved": 0, "milestones_total": 5},
        }
        ns = normalize_agentic(result)
        assert ns.score == 0.0
        assert ns.passed is False

    def test_normalize_via_dispatcher(self):
        from bioeval.scoring.normalizer import normalize_result

        result = {
            "task_id": "ag_ed_001",
            "category": "experimental_design",
            "scores": {"progress_rate": 0.6, "milestones_achieved": 3, "milestones_total": 5},
        }
        ns = normalize_result(result, "agentic", "experimental_design")
        assert ns.component == "agentic"
        assert ns.score == 0.6

    def test_task_type_inference(self):
        from bioeval.scoring.normalizer import normalize_component_results

        results = [
            {"task_id": "ag_ed_001", "category": "experimental_design", "scores": {"progress_rate": 0.8, "milestones_achieved": 4, "milestones_total": 5}},
            {"task_id": "ag_bp_001", "category": "bioinformatics_pipeline", "scores": {"progress_rate": 0.6, "milestones_achieved": 3, "milestones_total": 5}},
        ]
        normalized = normalize_component_results("agentic", results)
        assert len(normalized) == 2
        # Check that task_type was inferred from prefix
        types = {ns.task_type for ns in normalized}
        assert "experimental_design" in types
