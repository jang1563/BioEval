"""
BioEval Test Suite

Tests for data loading, scoring, and evaluation components.
Run with: pytest tests/ -v
"""

import pytest
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# =============================================================================
# DATA LOADING TESTS
# =============================================================================


class TestProtoReasonData:
    """Tests for ProtoReason data loading."""

    def test_protocols_load(self):
        """Test that protocols load correctly."""
        from bioeval.protoreason.extended_data import PROTOCOLS

        assert len(PROTOCOLS) >= 10, "Should have at least 10 protocols"

        for protocol_id, protocol in PROTOCOLS.items():
            assert "name" in protocol, f"Protocol {protocol_id} missing name"
            assert "steps" in protocol, f"Protocol {protocol_id} missing steps"
            assert len(protocol["steps"]) >= 5, f"Protocol {protocol_id} has too few steps"

    def test_calculations_load(self):
        """Test that calculation tasks load correctly."""
        from bioeval.protoreason.extended_data import CALCULATION_TASKS

        assert len(CALCULATION_TASKS) >= 10, "Should have at least 10 calculation tasks"

        for task in CALCULATION_TASKS:
            assert "id" in task, "Task missing id"
            assert "question" in task, "Task missing question"
            assert "answer" in task, "Task missing answer"

    def test_troubleshooting_load(self):
        """Test that troubleshooting tasks load correctly."""
        from bioeval.protoreason.extended_data import TROUBLESHOOTING_TASKS

        assert len(TROUBLESHOOTING_TASKS) >= 5, "Should have at least 5 troubleshooting tasks"

        for task in TROUBLESHOOTING_TASKS:
            assert "id" in task
            assert "scenario" in task
            assert "possible_causes" in task

    def test_safety_tasks_load(self):
        """Test that safety tasks load correctly."""
        from bioeval.protoreason.extended_data import SAFETY_TASKS

        assert len(SAFETY_TASKS) >= 3, "Should have at least 3 safety tasks"

        for task in SAFETY_TASKS:
            assert "id" in task
            assert "scenario" in task


class TestCausalBioData:
    """Tests for CausalBio data loading."""

    def test_knockout_tasks_load(self):
        """Test knockout prediction tasks."""
        from bioeval.causalbio.extended_data import KNOCKOUT_TASKS

        assert len(KNOCKOUT_TASKS) >= 15, "Should have at least 15 knockout tasks"

        for task in KNOCKOUT_TASKS:
            assert "id" in task
            assert "gene" in task
            assert "cell_line" in task
            assert "ground_truth" in task

    def test_pathway_tasks_load(self):
        """Test pathway reasoning tasks."""
        from bioeval.causalbio.extended_data import PATHWAY_TASKS

        assert len(PATHWAY_TASKS) >= 5, "Should have at least 5 pathway tasks"

        for task in PATHWAY_TASKS:
            assert "id" in task
            assert "perturbation" in task
            assert "ground_truth" in task

    def test_drug_response_tasks_load(self):
        """Test drug response tasks."""
        from bioeval.causalbio.extended_data import DRUG_RESPONSE_TASKS

        assert len(DRUG_RESPONSE_TASKS) >= 5, "Should have at least 5 drug tasks"

        for task in DRUG_RESPONSE_TASKS:
            assert "id" in task
            assert "drug" in task

    def test_epistasis_tasks_load(self):
        """Test epistasis tasks."""
        from bioeval.causalbio.extended_data import EPISTASIS_TASKS

        assert len(EPISTASIS_TASKS) >= 5, "Should have at least 5 epistasis tasks"

        for task in EPISTASIS_TASKS:
            assert "id" in task
            assert "gene_a" in task
            assert "gene_b" in task


class TestDesignCheckData:
    """Tests for DesignCheck data loading."""

    def test_flawed_designs_load(self):
        """Test flawed experimental designs."""
        from bioeval.designcheck.evaluator import FLAWED_DESIGNS

        assert len(FLAWED_DESIGNS) >= 5, "Should have at least 5 designs"

        for design in FLAWED_DESIGNS:
            assert "id" in design
            assert "title" in design
            assert "description" in design
            assert "flaws" in design
            assert len(design["flaws"]) >= 1, f"Design {design['id']} has no flaws"


class TestAdversarialData:
    """Tests for adversarial tasks."""

    def test_adversarial_tasks_load(self):
        """Test adversarial tasks load."""
        from bioeval.adversarial.tasks import ADVERSARIAL_TASKS, AdversarialType

        assert len(ADVERSARIAL_TASKS) >= 20, "Should have at least 20 adversarial tasks"

        # Check coverage of adversarial types
        types_covered = set(task.adversarial_type for task in ADVERSARIAL_TASKS)
        assert len(types_covered) >= 5, "Should cover at least 5 adversarial types"

    def test_adversarial_task_structure(self):
        """Test adversarial task structure."""
        from bioeval.adversarial.tasks import ADVERSARIAL_TASKS

        for task in ADVERSARIAL_TASKS:
            assert task.id, "Task missing id"
            assert task.question, "Task missing question"
            assert task.correct_behavior, "Task missing correct_behavior"
            assert task.trap_description, "Task missing trap_description"


class TestMultiTurnData:
    """Tests for multi-turn dialogues."""

    def test_dialogues_load(self):
        """Test dialogues load."""
        from bioeval.multiturn.dialogues import DIALOGUES

        assert len(DIALOGUES) >= 5, "Should have at least 5 dialogues"

        for dialogue in DIALOGUES:
            assert dialogue.id
            assert dialogue.title
            assert len(dialogue.turns) >= 2, f"Dialogue {dialogue.id} needs at least 2 turns"

    def test_dialogue_turn_structure(self):
        """Test dialogue turn structure."""
        from bioeval.multiturn.dialogues import DIALOGUES

        for dialogue in DIALOGUES:
            for turn in dialogue.turns:
                assert turn.user_message, f"Turn {turn.turn_number} missing message"
                assert turn.expected_behaviors, f"Turn {turn.turn_number} missing expected behaviors"


# =============================================================================
# SCORING TESTS
# =============================================================================


class TestConfidenceExtraction:
    """Tests for confidence extraction."""

    def test_high_confidence_detection(self):
        """Test detection of high confidence language."""
        from bioeval.scoring.calibration import extract_confidence

        high_conf_texts = [
            "I am highly confident that KRAS is essential.",
            "This will definitely cause cell death.",
            "The mechanism is certainly through MAPK.",
        ]

        for text in high_conf_texts:
            result = extract_confidence(text)
            assert result.confidence_score >= 0.7, f"Should detect high confidence in: {text[:50]}"

    def test_low_confidence_detection(self):
        """Test detection of low confidence language."""
        from bioeval.scoring.calibration import extract_confidence

        low_conf_texts = [
            "I'm not sure about this.",
            "This might work, but I don't know.",
            "I'm uncertain about the mechanism.",
        ]

        for text in low_conf_texts:
            result = extract_confidence(text)
            assert result.confidence_score <= 0.4, f"Should detect low confidence in: {text[:50]}"

    def test_explicit_confidence_extraction(self):
        """Test extraction of explicit confidence statements."""
        from bioeval.scoring.calibration import extract_confidence

        result = extract_confidence("Confidence: HIGH. The gene is essential.")
        assert result.stated_confidence == "high"

        result = extract_confidence("I have low confidence in this prediction.")
        assert result.stated_confidence == "low"


class TestAdversarialScoring:
    """Tests for adversarial task scoring."""

    def test_false_premise_scoring(self):
        """Test scoring of false premise detection."""
        from bioeval.adversarial.tasks import score_adversarial_response, ADVERSARIAL_TASKS, AdversarialType

        # Get a false premise task
        fp_task = next(t for t in ADVERSARIAL_TASKS if t.adversarial_type == AdversarialType.FALSE_PREMISE)

        # Good response that corrects premise
        good_response = "Actually, this premise is incorrect. KRAS is an oncogene, not a tumor suppressor."
        result = score_adversarial_response(fp_task, good_response)
        assert result["passed"], "Should pass when premise is corrected"

        # Bad response that accepts premise
        bad_response = "Restoring KRAS function would help suppress the tumor growth."
        result = score_adversarial_response(fp_task, bad_response)
        assert not result["passed"], "Should fail when premise is accepted"

    def test_hallucination_trap_scoring(self):
        """Test scoring of hallucination trap detection."""
        from bioeval.adversarial.tasks import score_adversarial_response, ADVERSARIAL_TASKS, AdversarialType

        # Get a hallucination trap task
        ht_task = next(t for t in ADVERSARIAL_TASKS if t.adversarial_type == AdversarialType.HALLUCINATION_TRAP)

        # Good response expressing uncertainty
        good_response = "I'm not familiar with this gene. It doesn't appear to be a recognized gene name."
        result = score_adversarial_response(ht_task, good_response)
        assert result["passed"], "Should pass when uncertainty is expressed"


class TestCalibrationMetrics:
    """Tests for calibration metrics computation."""

    def test_calibration_metrics_computation(self):
        """Test that calibration metrics compute correctly."""
        from bioeval.scoring.calibration import compute_calibration_metrics, CalibrationResult

        # Create sample results
        results = [
            CalibrationResult(
                task_id="1", confidence_score=0.9, is_correct=True, confidence_bucket="high", calibration_error=0.1
            ),
            CalibrationResult(
                task_id="2", confidence_score=0.9, is_correct=False, confidence_bucket="high", calibration_error=0.9
            ),
            CalibrationResult(
                task_id="3", confidence_score=0.3, is_correct=True, confidence_bucket="low", calibration_error=0.7
            ),
            CalibrationResult(
                task_id="4", confidence_score=0.5, is_correct=True, confidence_bucket="medium", calibration_error=0.5
            ),
        ]

        metrics = compute_calibration_metrics(results)

        assert 0 <= metrics.expected_calibration_error <= 1
        assert 0 <= metrics.overconfidence_rate <= 1
        assert "high" in metrics.bucket_counts
        assert "low" in metrics.bucket_counts


# =============================================================================
# CACHING TESTS
# =============================================================================


class TestResponseCache:
    """Tests for response caching."""

    def test_cache_set_get(self, tmp_path):
        """Test cache set and get operations."""
        from bioeval.execution.async_runner import ResponseCache

        cache = ResponseCache(str(tmp_path / "test_cache"))

        # Set a value
        cache.set(
            model="test-model", prompt="test prompt", response="test response", usage={"input_tokens": 10, "output_tokens": 20}
        )

        # Get it back
        result = cache.get(model="test-model", prompt="test prompt")

        assert result is not None
        assert result["response"] == "test response"
        assert result["cached"] is True

    def test_cache_miss(self, tmp_path):
        """Test cache miss returns None."""
        from bioeval.execution.async_runner import ResponseCache

        cache = ResponseCache(str(tmp_path / "test_cache"))

        result = cache.get(model="nonexistent", prompt="nonexistent")
        assert result is None

    def test_cache_with_system_prompt(self, tmp_path):
        """Test caching with system prompts."""
        from bioeval.execution.async_runner import ResponseCache

        cache = ResponseCache(str(tmp_path / "test_cache"))

        # Same prompt, different system prompts should be different cache keys
        cache.set("model", "prompt", "response1", system="system1")
        cache.set("model", "prompt", "response2", system="system2")

        result1 = cache.get("model", "prompt", system="system1")
        result2 = cache.get("model", "prompt", system="system2")

        assert result1["response"] == "response1"
        assert result2["response"] == "response2"


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestTaskLoading:
    """Integration tests for task loading in run_enhanced.py."""

    def test_all_task_loaders_work(self):
        """Test that all task loaders execute without error."""
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

        from run_enhanced import (
            load_protoreason_tasks,
            load_causalbio_tasks,
            load_designcheck_tasks,
            load_calibration_tasks,
            load_adversarial_tasks,
        )

        proto_tasks = load_protoreason_tasks()
        assert len(proto_tasks) >= 50, f"ProtoReason should have 50+ tasks, got {len(proto_tasks)}"

        causal_tasks = load_causalbio_tasks()
        assert len(causal_tasks) >= 40, f"CausalBio should have 40+ tasks, got {len(causal_tasks)}"

        design_tasks = load_designcheck_tasks()
        assert len(design_tasks) >= 5, f"DesignCheck should have 5+ tasks, got {len(design_tasks)}"

        cal_tasks = load_calibration_tasks()
        assert len(cal_tasks) >= 5, f"Calibration should have 5+ tasks, got {len(cal_tasks)}"

        adv_tasks = load_adversarial_tasks()
        assert len(adv_tasks) >= 20, f"Adversarial should have 20+ tasks, got {len(adv_tasks)}"

    def test_task_structure_consistency(self):
        """Test that all tasks have consistent structure."""
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

        from run_enhanced import (
            load_protoreason_tasks,
            load_causalbio_tasks,
            load_designcheck_tasks,
        )

        all_tasks = load_protoreason_tasks() + load_causalbio_tasks() + load_designcheck_tasks()

        for task in all_tasks:
            assert "task_id" in task, f"Task missing task_id: {task}"
            assert "task_type" in task, f"Task missing task_type: {task}"
            assert "component" in task, f"Task missing component: {task}"
            assert "prompt" in task, f"Task missing prompt: {task}"
            assert "ground_truth" in task, f"Task missing ground_truth: {task}"


class TestStatisticsFunctions:
    """Test statistics helper functions."""

    def test_protoreason_statistics(self):
        """Test ProtoReason statistics function."""
        from bioeval.protoreason.extended_data import get_task_statistics

        stats = get_task_statistics()
        assert stats["protocols"] >= 10
        assert stats["total_protocol_steps"] >= 100
        assert stats["calculation_tasks"] >= 10

    def test_causalbio_statistics(self):
        """Test CausalBio statistics function."""
        from bioeval.causalbio.extended_data import get_task_statistics

        stats = get_task_statistics()
        assert stats["total_tasks"] >= 40
        assert stats["knockout_tasks"] >= 15

    def test_adversarial_statistics(self):
        """Test adversarial statistics function."""
        from bioeval.adversarial.tasks import get_statistics

        stats = get_statistics()
        assert stats["total"] >= 20
        assert len(stats["by_type"]) >= 5


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
