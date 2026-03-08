"""
Tests for LongHorizon component (Component 10).

Covers:
- Task data loading and structure
- Scoring logic for all 5 task types
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


class TestLongHorizonDataLoading:
    """Test that task data loads correctly."""

    def test_task_data_imports(self):
        """Test that all task lists import from tasks.py."""
        from bioeval.longhorizon.tasks import (
            CONSTRAINT_TRACKING_TASKS,
            STATE_ACCUMULATION_TASKS,
            ERROR_PROPAGATION_TASKS,
            RESOURCE_MANAGEMENT_TASKS,
            ADAPTIVE_REPLANNING_TASKS,
        )
        assert len(CONSTRAINT_TRACKING_TASKS) >= 2
        assert len(STATE_ACCUMULATION_TASKS) >= 1
        assert len(ERROR_PROPAGATION_TASKS) >= 1
        assert len(RESOURCE_MANAGEMENT_TASKS) >= 1
        assert len(ADAPTIVE_REPLANNING_TASKS) >= 1

    def test_evaluator_load_tasks(self):
        """Test that LongHorizonEvaluator.load_tasks() returns EvalTask objects."""
        from bioeval.longhorizon.evaluator import LongHorizonEvaluator
        from bioeval.models.base import EvalTask

        evaluator = LongHorizonEvaluator()
        tasks = evaluator.load_tasks()

        assert len(tasks) >= 6, f"Expected >= 6 tasks, got {len(tasks)}"
        for task in tasks:
            assert isinstance(task, EvalTask)
            assert task.id.startswith("lh_")
            assert task.component == "longhorizon"
            assert task.task_type in [
                "constraint_tracking",
                "state_accumulation",
                "error_propagation",
                "resource_management",
                "adaptive_replanning",
            ]
            assert task.prompt, f"Task {task.id} has empty prompt"
            assert task.ground_truth, f"Task {task.id} has empty ground_truth"

    def test_task_ids_unique(self):
        """Verify all task IDs are unique."""
        from bioeval.longhorizon.evaluator import LongHorizonEvaluator

        evaluator = LongHorizonEvaluator()
        tasks = evaluator.load_tasks()
        ids = [t.id for t in tasks]
        assert len(ids) == len(set(ids)), f"Duplicate task IDs: {[x for x in ids if ids.count(x) > 1]}"

    def test_task_type_distribution(self):
        """Check that all 5 task types have at least 1 task."""
        from bioeval.longhorizon.evaluator import LongHorizonEvaluator

        evaluator = LongHorizonEvaluator()
        tasks = evaluator.load_tasks()

        type_counts = {}
        for t in tasks:
            type_counts[t.task_type] = type_counts.get(t.task_type, 0) + 1

        expected_types = [
            "constraint_tracking",
            "state_accumulation",
            "error_propagation",
            "resource_management",
            "adaptive_replanning",
        ]
        for tt in expected_types:
            assert tt in type_counts, f"Missing task type: {tt}"
            assert type_counts[tt] >= 1, f"Task type {tt} has 0 tasks"


# =============================================================================
# SCORING TESTS
# =============================================================================


class TestConstraintTrackingScoring:
    """Test scoring for constraint_tracking tasks."""

    def test_perfect_detection(self):
        """Response that mentions all violations should get high recall."""
        from bioeval.longhorizon.evaluator import LongHorizonEvaluator
        from bioeval.models.base import EvalTask

        evaluator = LongHorizonEvaluator()
        task = EvalTask(
            id="test_ct",
            component="longhorizon",
            task_type="constraint_tracking",
            prompt="test",
            ground_truth={
                "violations": ["cross_species_contamination", "sample_count_mismatch"],
                "min_violations_expected": 2,
            },
        )
        response = (
            "There is a critical risk of cross-species contamination due to multiplexing "
            "human and mouse libraries. Additionally, there is a sample count mismatch "
            "between the design requiring 3 replicates and only 4 crew available."
        )
        scores = evaluator.score_response(task, response)
        assert scores["violations_detected"] == 2
        assert scores["recall"] == 1.0
        assert scores["pass"] is True

    def test_no_detection(self):
        """Response missing violations should get zero recall."""
        from bioeval.longhorizon.evaluator import LongHorizonEvaluator
        from bioeval.models.base import EvalTask

        evaluator = LongHorizonEvaluator()
        task = EvalTask(
            id="test_ct_none",
            component="longhorizon",
            task_type="constraint_tracking",
            prompt="test",
            ground_truth={
                "violations": ["cross_species_contamination"],
                "min_violations_expected": 1,
            },
        )
        response = "The experimental plan looks well-designed and feasible."
        scores = evaluator.score_response(task, response)
        assert scores["violations_detected"] == 0
        assert scores["recall"] == 0.0
        assert scores["pass"] is False


class TestStateAccumulationScoring:
    """Test scoring for state_accumulation tasks."""

    def test_full_state_recall(self):
        """Response mentioning all targets and eliminations gets high score."""
        from bioeval.longhorizon.evaluator import LongHorizonEvaluator
        from bioeval.models.base import EvalTask

        evaluator = LongHorizonEvaluator()
        task = EvalTask(
            id="test_sa",
            component="longhorizon",
            task_type="state_accumulation",
            prompt="test",
            ground_truth={
                "final_active_targets": ["EGFR", "CDK4"],
                "all_eliminations": {
                    "MDM2": "insufficient expression",
                    "PTEN": "loss-of-function",
                    "PDGFRA": "no phenotype",
                },
            },
        )
        response = (
            "The remaining active targets are EGFR and CDK4. "
            "MDM2 was eliminated due to insufficient expression. "
            "PTEN was eliminated as loss-of-function. "
            "PDGFRA showed no significant phenotype and was eliminated."
        )
        scores = evaluator.score_response(task, response)
        assert scores["active_targets_correct"] == 2
        assert scores["target_recall"] == 1.0
        assert scores["eliminations_mentioned"] == 3
        assert scores["composite_score"] == 1.0


class TestErrorPropagationScoring:
    """Test scoring for error_propagation tasks."""

    def test_correct_identification(self):
        """Response identifying affected and unaffected stages."""
        from bioeval.longhorizon.evaluator import LongHorizonEvaluator
        from bioeval.models.base import EvalTask

        evaluator = LongHorizonEvaluator()
        task = EvalTask(
            id="test_ep",
            component="longhorizon",
            task_type="error_propagation",
            prompt="test",
            ground_truth={
                "affected": ["stage_5_normalization", "stage_6_pathway_analysis"],
                "unaffected": ["stage_1_sample_collection", "stage_4_sequencing"],
            },
        )
        response = (
            "The stage 5 normalization is affected since GAPDH was used as a reference. "
            "The stage 6 pathway analysis must be redone. "
            "Stage 1 sample collection is unaffected. "
            "Stage 4 sequencing data remains valid."
        )
        scores = evaluator.score_response(task, response)
        assert scores["affected_identified"] >= 1
        assert scores["unaffected_identified"] >= 1
        assert scores["composite_score"] > 0.0


class TestResourceManagementScoring:
    """Test scoring for resource_management tasks."""

    def test_infeasible_detection(self):
        """Response correctly identifying infeasible items."""
        from bioeval.longhorizon.evaluator import LongHorizonEvaluator
        from bioeval.models.base import EvalTask

        evaluator = LongHorizonEvaluator()
        task = EvalTask(
            id="test_rm",
            component="longhorizon",
            task_type="resource_management",
            prompt="test",
            ground_truth={
                "infeasible": {
                    "functional_immune_assay": {
                        "reason": "requires fresh sample, all samples are frozen",
                    },
                },
            },
        )
        response = (
            "The functional immune assay cannot be performed because it requires "
            "a fresh sample. All available samples are frozen, making this infeasible."
        )
        scores = evaluator.score_response(task, response)
        assert scores["infeasible_correctly_identified"] == 1
        assert scores["score"] == 1.0


class TestAdaptiveReplanningScoring:
    """Test scoring for adaptive_replanning tasks."""

    def test_required_elements(self):
        """Response with required elements and no prohibited ones."""
        from bioeval.longhorizon.evaluator import LongHorizonEvaluator
        from bioeval.models.base import EvalTask

        evaluator = LongHorizonEvaluator()
        task = EvalTask(
            id="test_ar",
            component="longhorizon",
            task_type="adaptive_replanning",
            prompt="test",
            ground_truth={
                "required_elements": [
                    "drop B cells from flight vs. ground comparison",
                    "proceed with T cells, monocytes, NK cells",
                ],
                "prohibited_elements": [
                    "restart from scratch",
                ],
                "bonus_elements": [
                    "use B cell data for within-condition analysis",
                ],
            },
        )
        response = (
            "We should drop B cells from the flight vs. ground comparison due to "
            "the batch effect. We can proceed with T cells, monocytes, and NK cells "
            "for the comparison analysis. The B cell data can still be used for "
            "within-condition analysis to explore processing sensitivity."
        )
        scores = evaluator.score_response(task, response)
        assert scores["required_elements_found"] >= 1
        assert scores["prohibited_elements_found"] == 0
        assert scores["penalty"] == 0.0
        assert scores["composite_score"] > 0.0


# =============================================================================
# REGISTRY TESTS
# =============================================================================


class TestRegistryIntegration:
    """Test that longhorizon is properly registered."""

    def test_in_registry(self):
        """longhorizon should be in the component registry."""
        from bioeval.registry import REGISTRY

        assert "longhorizon" in REGISTRY
        info = REGISTRY["longhorizon"]
        assert info.evaluator_class == "LongHorizonEvaluator"
        assert "constraint_tracking" in info.task_types
        assert len(info.task_types) == 5

    def test_in_config_components(self):
        """longhorizon should be in COMPONENTS list."""
        from bioeval.config import COMPONENTS, TASK_TYPES

        assert "longhorizon" in COMPONENTS
        assert "longhorizon" in TASK_TYPES
        assert len(TASK_TYPES["longhorizon"]) == 5

    def test_registry_load_tasks(self):
        """Registry should load tasks via create_evaluator."""
        from bioeval.registry import REGISTRY

        info = REGISTRY["longhorizon"]
        tasks = info.load_tasks()
        assert len(tasks) >= 6

    def test_in_package_init(self):
        """LongHorizonEvaluator should be importable from bioeval."""
        from bioeval import LongHorizonEvaluator

        assert LongHorizonEvaluator is not None


# =============================================================================
# NORMALIZER TESTS
# =============================================================================


class TestNormalizerIntegration:
    """Test that longhorizon normalizer works correctly."""

    def test_normalize_constraint_tracking(self):
        """Test normalization for constraint_tracking results."""
        from bioeval.scoring.normalizer import normalize_result

        result = {
            "task_id": "lh_ct_001",
            "recall": 0.75,
            "violations_detected": 2,
            "violations_total": 3,
        }
        ns = normalize_result(result, "longhorizon", "constraint_tracking")
        assert ns.component == "longhorizon"
        assert ns.task_type == "constraint_tracking"
        assert ns.score == 0.75
        assert ns.passed is True

    def test_normalize_state_accumulation(self):
        """Test normalization for state_accumulation results."""
        from bioeval.scoring.normalizer import normalize_result

        result = {
            "task_id": "lh_sa_001",
            "composite_score": 0.85,
            "target_recall": 1.0,
            "elimination_recall": 0.7,
        }
        ns = normalize_result(result, "longhorizon", "state_accumulation")
        assert ns.score == 0.85
        assert ns.subscores["target_recall"] == 1.0

    def test_normalize_adaptive_replanning(self):
        """Test normalization for adaptive_replanning results."""
        from bioeval.scoring.normalizer import normalize_result

        result = {
            "task_id": "lh_ar_001",
            "composite_score": 0.6,
            "required_score": 0.8,
            "penalty": 0.2,
            "bonus_elements_found": 2,
        }
        ns = normalize_result(result, "longhorizon", "adaptive_replanning")
        assert ns.score == 0.6
        assert ns.subscores["penalty"] == 0.2

    def test_normalize_resource_management(self):
        """Test normalization for resource_management results."""
        from bioeval.scoring.normalizer import normalize_result

        result = {
            "task_id": "lh_rm_001",
            "score": 1.0,
            "infeasible_correctly_identified": 1,
            "infeasible_total": 1,
        }
        ns = normalize_result(result, "longhorizon", "resource_management")
        assert ns.score == 1.0
        assert ns.passed is True

    def test_normalize_error_propagation(self):
        """Test normalization for error_propagation results."""
        from bioeval.scoring.normalizer import normalize_result

        result = {
            "task_id": "lh_ep_001",
            "composite_score": 0.75,
            "affected_recall": 1.0,
            "unaffected_recall": 0.5,
        }
        ns = normalize_result(result, "longhorizon", "error_propagation")
        assert ns.component == "longhorizon"
        assert ns.task_type == "error_propagation"
        assert ns.score == 0.75
        assert ns.passed is True  # 0.75 >= 0.5
        assert ns.subscores["affected_recall"] == 1.0
        assert ns.subscores["unaffected_recall"] == 0.5


# =============================================================================
# ADDITIONAL SCORING EDGE-CASE TESTS
# =============================================================================


class TestConstraintTrackingPartialDetection:
    """Test partial violation detection for constraint_tracking."""

    def test_partial_detection(self):
        """Response mentions only 1 of 3 violations: recall ~0.333, pass False."""
        from bioeval.longhorizon.evaluator import LongHorizonEvaluator
        from bioeval.models.base import EvalTask

        evaluator = LongHorizonEvaluator()
        task = EvalTask(
            id="test_ct_partial",
            component="longhorizon",
            task_type="constraint_tracking",
            prompt="test",
            ground_truth={
                "violations": [
                    "cross_species_contamination",
                    "sample_count_mismatch",
                    "reagent_expiry",
                ],
                "min_violations_expected": 3,
            },
        )
        # Response only mentions cross-species contamination
        response = (
            "There is a risk of cross-species contamination when multiplexing "
            "human and mouse samples on the same flow cell."
        )
        scores = evaluator.score_response(task, response)
        assert scores["violations_detected"] == 1
        assert scores["recall"] == pytest.approx(1 / 3, abs=0.01)
        assert scores["pass"] is False


class TestAdaptiveReplanningProhibitedPenalty:
    """Test prohibited element penalty for adaptive_replanning."""

    def test_prohibited_element_penalty(self):
        """2 required found + 1 prohibited: penalty 0.2, composite 0.8."""
        from bioeval.longhorizon.evaluator import LongHorizonEvaluator
        from bioeval.models.base import EvalTask

        evaluator = LongHorizonEvaluator()
        task = EvalTask(
            id="test_ar_penalty",
            component="longhorizon",
            task_type="adaptive_replanning",
            prompt="test",
            ground_truth={
                "required_elements": [
                    "switch to alternative antibody",
                    "validate with positive control",
                ],
                "prohibited_elements": [
                    "discard all previous data",
                    "restart from scratch",
                ],
                "bonus_elements": [],
            },
        )
        # Response includes both required elements and 1 prohibited element
        response = (
            "We should switch to an alternative antibody for the staining panel. "
            "We must validate the new antibody with a positive control sample. "
            "Given the severity of the issue, we should discard all previous data "
            "and begin the analysis fresh."
        )
        scores = evaluator.score_response(task, response)
        assert scores["required_elements_found"] == 2
        assert scores["prohibited_elements_found"] == 1
        assert scores["penalty"] == pytest.approx(0.2)
        # composite = required_score(2/2=1.0) - penalty(0.2) = 0.8
        assert scores["composite_score"] == pytest.approx(0.8)


class TestResourceManagementExpandedInfeasibility:
    """Test expanded infeasibility_terms for resource_management."""

    def test_out_for_repair_detection(self):
        """Infeasible item with 'out for repair' reason is correctly detected."""
        from bioeval.longhorizon.evaluator import LongHorizonEvaluator
        from bioeval.models.base import EvalTask

        evaluator = LongHorizonEvaluator()
        task = EvalTask(
            id="test_rm_repair",
            component="longhorizon",
            task_type="resource_management",
            prompt="test",
            ground_truth={
                "infeasible": {
                    "flow_cytometry_panel": {
                        "reason": "instrument is out for repair until next quarter",
                    },
                },
            },
        )
        response = (
            "The flow cytometry panel cannot be completed because the instrument "
            "is currently out for repair and will not be available until next quarter."
        )
        scores = evaluator.score_response(task, response)
        assert scores["infeasible_correctly_identified"] == 1
        assert scores["score"] == 1.0


class TestHyphenNormalization:
    """Test that hyphen normalization works in phrase matching."""

    def test_hyphenated_vs_underscore_term(self):
        """'cross-species contamination' in response matches 'cross_species_contamination' ground truth."""
        from bioeval.longhorizon.evaluator import LongHorizonEvaluator
        from bioeval.models.base import EvalTask

        evaluator = LongHorizonEvaluator()
        task = EvalTask(
            id="test_hyphen",
            component="longhorizon",
            task_type="constraint_tracking",
            prompt="test",
            ground_truth={
                "violations": ["cross_species_contamination"],
                "min_violations_expected": 1,
            },
        )
        # Response uses hyphens ("cross-species") while ground truth uses
        # underscores ("cross_species_contamination" -> "cross species contamination")
        response = (
            "There is a significant risk of cross-species contamination "
            "when multiplexing libraries from different organisms."
        )
        scores = evaluator.score_response(task, response)
        assert scores["violations_detected"] == 1
        assert scores["recall"] == 1.0
        assert scores["pass"] is True
