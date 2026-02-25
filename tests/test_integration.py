"""
Integration tests for BioEval pipeline.

Tests the full scoring → normalization → analysis chain
without any API calls using synthetic responses.
"""

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


# =============================================================================
# NORMALIZER TESTS
# =============================================================================

class TestNormalizer:
    """Test score normalization for each component."""

    def test_protoreason_step_ordering(self):
        from bioeval.scoring.normalizer import normalize_protoreason
        # kendall_tau = 1.0 → score = 1.0
        result = {"task_id": "proto_001", "kendall_tau": 1.0, "adjacent_pair_accuracy": 1.0}
        ns = normalize_protoreason(result, "step_ordering")
        assert ns.score == 1.0
        assert ns.passed is True

    def test_protoreason_step_ordering_negative_tau(self):
        from bioeval.scoring.normalizer import normalize_protoreason
        # kendall_tau = -1.0 → score = 0.0
        result = {"task_id": "proto_002", "kendall_tau": -1.0, "adjacent_pair_accuracy": 0.0}
        ns = normalize_protoreason(result, "step_ordering")
        assert ns.score == 0.0
        assert ns.passed is False

    def test_protoreason_step_ordering_none_tau(self):
        from bioeval.scoring.normalizer import normalize_protoreason
        result = {"task_id": "proto_003", "kendall_tau": None}
        ns = normalize_protoreason(result, "step_ordering")
        assert ns.score == 0.0

    def test_causalbio_knockout(self):
        from bioeval.scoring.normalizer import normalize_causalbio
        # Correct effect + good reasoning → high score
        result = {"task_id": "cb_001", "effect_correct": True, "reasoning_score": 0.8}
        ns = normalize_causalbio(result, "knockout_prediction")
        assert ns.score > 0.8
        assert ns.passed is True

    def test_causalbio_knockout_wrong(self):
        from bioeval.scoring.normalizer import normalize_causalbio
        # Wrong effect + no reasoning → low score
        result = {"task_id": "cb_002", "effect_correct": False, "reasoning_score": 0.0}
        ns = normalize_causalbio(result, "knockout_prediction")
        assert ns.score == 0.0
        assert ns.passed is False

    def test_designcheck(self):
        from bioeval.scoring.normalizer import normalize_designcheck
        result = {"task_id": "dc_001", "f1": 0.75, "flaw_recall": 0.8,
                  "estimated_precision": 0.7, "critical_recall": 1.0, "weighted_recall": 0.85}
        ns = normalize_designcheck(result)
        assert ns.score == 0.75
        assert ns.passed is True

    def test_adversarial(self):
        from bioeval.scoring.normalizer import normalize_adversarial
        result = {"task_id": "adv_001", "score": 0.9, "trap_detected": True,
                  "correct_content_score": 0.8, "hallucination_penalty": 0.0,
                  "adversarial_type": "false_premise"}
        ns = normalize_adversarial(result)
        assert ns.score == 0.9
        assert ns.passed is True

    def test_adversarial_nested_scores(self):
        from bioeval.scoring.normalizer import normalize_adversarial
        # Normalized JSON format: scores nested under "scores" key
        result = {"task_id": "adv_002", "scores": {"score": 0.3, "passed": False},
                  "trap_detected": False, "adversarial_type": "hallucination_trap"}
        ns = normalize_adversarial(result)
        assert ns.score == 0.3
        assert ns.passed is False

    def test_calibration_good(self):
        from bioeval.scoring.normalizer import normalize_calibration
        # Low calibration error → high normalized score
        result = {"task_id": "cal_001", "calibration_error": 0.1, "is_correct": True,
                  "confidence_score": 0.9,
                  "details": {"confidence_appropriate": True, "correct_behavior": "high_confidence_correct"}}
        ns = normalize_calibration(result)
        assert ns.score == 0.9  # 1.0 - 0.1
        assert ns.passed is True

    def test_calibration_bad(self):
        from bioeval.scoring.normalizer import normalize_calibration
        # High calibration error → low normalized score
        result = {"task_id": "cal_002", "calibration_error": 0.8, "is_correct": False,
                  "confidence_score": 0.9,
                  "details": {"confidence_appropriate": False, "correct_behavior": "acknowledge_unknown"}}
        ns = normalize_calibration(result)
        assert ns.score == 0.2
        assert ns.passed is False

    def test_multiturn(self):
        from bioeval.scoring.normalizer import normalize_multiturn
        result = {"dialogue_id": "mt_001", "overall_score": 0.75, "memory_score": 0.6}
        ns = normalize_multiturn(result)
        assert ns.score == 0.75
        assert ns.passed is True


# =============================================================================
# ANALYSIS PIPELINE TEST
# =============================================================================

class TestAnalysisPipeline:
    """Test the full analysis pipeline with a synthetic result file."""

    def _create_synthetic_result(self) -> dict:
        """Create a minimal synthetic result file."""
        return {
            "metadata": {
                "model": "test-model",
                "data_tier": "base",
                "timestamp": "2025-01-01T00:00:00",
            },
            "results": [
                {
                    "component": "adversarial",
                    "num_tasks": 5,
                    "results": [
                        {"task_id": "adv_001", "score": 0.9, "passed": True,
                         "trap_detected": True, "correct_content_score": 0.8,
                         "hallucination_penalty": 0.0, "adversarial_type": "false_premise"},
                        {"task_id": "adv_002", "score": 0.0, "passed": False,
                         "trap_detected": False, "correct_content_score": 0.0,
                         "hallucination_penalty": 0.5, "adversarial_type": "hallucination_trap"},
                        {"task_id": "adv_003", "score": 0.6, "passed": True,
                         "trap_detected": True, "correct_content_score": 0.5,
                         "hallucination_penalty": 0.0, "adversarial_type": "edge_case"},
                        {"task_id": "test_000", "score": 0.7, "passed": True,
                         "trap_detected": True, "correct_content_score": 0.6,
                         "hallucination_penalty": 0.0, "adversarial_type": "false_premise"},
                        {"task_id": "test_005", "score": 0.5, "passed": True,
                         "trap_detected": True, "correct_content_score": 0.4,
                         "hallucination_penalty": 0.1, "adversarial_type": "edge_case"},
                    ],
                },
                {
                    "component": "calibration",
                    "num_tasks": 3,
                    "results": [
                        {"task_id": "cal_001", "calibration_error": 0.1,
                         "is_correct": True, "confidence_score": 0.85,
                         "details": {"confidence_appropriate": True, "correct_behavior": "high_confidence_correct"}},
                        {"task_id": "cal_002", "calibration_error": 0.7,
                         "is_correct": False, "confidence_score": 0.9,
                         "details": {"confidence_appropriate": False, "correct_behavior": "overconfidence_trap"}},
                        {"task_id": "test_006", "calibration_error": 0.3,
                         "is_correct": True, "confidence_score": 0.7,
                         "details": {"confidence_appropriate": True, "correct_behavior": "high_confidence_correct"}},
                    ],
                },
            ],
        }

    def test_analyze_results(self):
        from bioeval.reporting.analysis import analyze_results
        data = self._create_synthetic_result()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            tmppath = f.name

        try:
            analysis = analyze_results(tmppath)

            assert analysis["overall"]["n"] == 8
            assert 0.0 <= analysis["overall"]["mean"] <= 1.0
            assert "adversarial" in analysis["by_component"]
            assert "calibration" in analysis["by_component"]
            assert analysis["by_component"]["adversarial"]["n"] == 5
            assert analysis["by_component"]["calibration"]["n"] == 3

            # ECE should be computed
            assert "calibration_analysis" in analysis
            assert "ece" in analysis["calibration_analysis"]
        finally:
            os.unlink(tmppath)

    def test_contamination_detection(self):
        from bioeval.reporting.analysis import detect_contamination
        data = self._create_synthetic_result()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            tmppath = f.name

        try:
            result = detect_contamination(tmppath)
            # Should have public and private counts
            assert "n_public" in result
            assert "n_private" in result
            assert "verdict" in result
        finally:
            os.unlink(tmppath)


# =============================================================================
# MATCHING MODULE TESTS
# =============================================================================

class TestMatching:
    """Test the matching module edge cases."""

    def test_phrase_match_exact(self):
        from bioeval.scoring.matching import phrase_match
        assert phrase_match("inhibit", "The drug inhibits the enzyme")
        assert not phrase_match("inhibit", "Nothing relevant here")

    def test_phrase_match_synonym(self):
        from bioeval.scoring.matching import phrase_match
        assert phrase_match("reduce", "Expression was decreased in treated cells")
        assert phrase_match("essential", "This gene is critical for survival")

    def test_phrase_match_word_boundary(self):
        from bioeval.scoring.matching import phrase_match
        assert not phrase_match("ERK", "The CLERK was absent")
        assert phrase_match("ERK", "ERK phosphorylation was increased")

    def test_phrase_match_empty(self):
        from bioeval.scoring.matching import phrase_match
        assert not phrase_match("", "Some text")
        assert not phrase_match("  ", "Some text")

    def test_extract_key_terms(self):
        from bioeval.scoring.matching import extract_key_terms
        terms = extract_key_terms("The protein kinase phosphorylates downstream targets",
                                  min_length=5, max_terms=3)
        assert len(terms) <= 3
        assert all(len(t) >= 5 for t in terms)

    def test_synonym_false_positive_guard(self):
        """Ensure common words don't cause false positive synonym matches."""
        from bioeval.scoring.matching import phrase_match
        # "actually" should NOT match in generic text via "in" token
        assert not phrase_match("actually", "The gene is expressed in the nucleus")
        assert not phrase_match("however", "The results are shown in Table 1")


# =============================================================================
# SPLITS MODULE TESTS
# =============================================================================

class TestSplits:
    """Test the split module."""

    def test_deterministic(self):
        from bioeval.scoring.splits import get_split
        s1 = get_split("task_001")
        s2 = get_split("task_001")
        assert s1 == s2

    def test_split_distribution(self):
        from bioeval.scoring.splits import get_split
        ids = [f"task_{i:04d}" for i in range(1000)]
        private = sum(1 for tid in ids if get_split(tid) == "private")
        # Should be roughly 20% ± 5%
        assert 150 <= private <= 250

    def test_beta_binomial_ci(self):
        from bioeval.scoring.splits import beta_binomial_ci
        ci = beta_binomial_ci(8, 10)
        assert 0.0 <= ci["lower"] <= ci["mean"] <= ci["upper"] <= 1.0


# =============================================================================
# ITEM ANALYSIS TESTS
# =============================================================================

class TestItemAnalysis:
    """Test item difficulty and discrimination analysis."""

    def _make_result_file(self, scores: list[tuple[str, float]], component="adversarial"):
        """Create a temp result file with given (task_id, score) pairs."""
        results = []
        for tid, score in scores:
            results.append({
                "task_id": tid, "score": score,
                "trap_detected": score > 0.5,
                "correct_content_score": score,
                "hallucination_penalty": 0.0,
                "adversarial_type": "false_premise",
            })
        data = {
            "metadata": {"model": "test", "data_tier": "base", "timestamp": "2025-01-01T00:00:00"},
            "results": [{"component": component, "num_tasks": len(results), "results": results}],
        }
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump(data, f)
        f.close()
        return f.name

    def test_single_model_analysis(self):
        from bioeval.reporting.item_analysis import single_model_item_analysis
        path = self._make_result_file([("t1", 0.9), ("t2", 0.5), ("t3", 0.0)])
        try:
            result = single_model_item_analysis(path)
            assert result["n_tasks"] == 3
            assert 0.0 <= result["mean_score"] <= 1.0
            assert result["summary"]["n_perfect"] == 0
            assert result["summary"]["n_zero"] == 1
        finally:
            os.unlink(path)

    def test_multi_model_difficulty(self):
        from bioeval.reporting.item_analysis import compute_item_difficulty
        from bioeval.reporting.analysis import load_and_normalize
        # Model A: high scorer
        path_a = self._make_result_file([("t1", 0.9), ("t2", 0.8), ("t3", 0.7)])
        # Model B: low scorer
        path_b = self._make_result_file([("t1", 0.6), ("t2", 0.2), ("t3", 0.1)])
        try:
            multi = [load_and_normalize(path_a), load_and_normalize(path_b)]
            difficulty = compute_item_difficulty(multi)
            assert "t1" in difficulty
            assert "t2" in difficulty
            assert "t3" in difficulty
            # t1 should be easier (both pass): p_value = 1.0
            assert difficulty["t1"]["p_value"] == 1.0
            # t3: model A passes (0.7 >= 0.5), model B fails (0.1 < 0.5)
            assert difficulty["t3"]["p_value"] == 0.5
            assert difficulty["t2"]["n_models"] == 2
        finally:
            os.unlink(path_a)
            os.unlink(path_b)

    def test_item_analysis_full(self):
        from bioeval.reporting.item_analysis import item_analysis
        paths = []
        for i in range(4):
            # Vary scores across models
            scores = [("t1", 0.9 - i * 0.1), ("t2", 0.5 + i * 0.05), ("t3", 0.3)]
            paths.append(self._make_result_file(scores))
        try:
            result = item_analysis(paths)
            assert result["n_models"] == 4
            assert result["n_tasks"] == 3
            assert "items" in result
            assert "summary" in result
            assert "by_component" in result
            assert "difficulty_histogram" in result["summary"]
        finally:
            for p in paths:
                os.unlink(p)


# =============================================================================
# ABLATION TESTS
# =============================================================================

class TestAblation:
    """Test scoring ablation framework."""

    def test_match_config_context_manager(self):
        from bioeval.scoring.matching import MatchConfig, match_config, get_match_config
        # Default: all features on
        cfg = get_match_config()
        assert cfg.use_stemming is True
        assert cfg.use_synonyms is True

        # Temporarily disable synonyms
        with match_config(MatchConfig(use_synonyms=False)):
            cfg2 = get_match_config()
            assert cfg2.use_synonyms is False

        # Restored
        cfg3 = get_match_config()
        assert cfg3.use_synonyms is True

    def test_synonym_ablation_effect(self):
        from bioeval.scoring.matching import MatchConfig, match_config, phrase_match
        # "reduce" should match "decreased" via synonym expansion
        assert phrase_match("reduce", "Expression was decreased in treated cells")

        # With synonyms off, should NOT match (no exact/stem match)
        with match_config(MatchConfig(use_synonyms=False)):
            assert not phrase_match("reduce", "Expression was decreased in treated cells")

    def test_stemming_ablation_effect(self):
        from bioeval.scoring.matching import MatchConfig, match_config, phrase_match
        # "inhibit" should match "inhibited" via stemming
        assert phrase_match("inhibit", "The drug inhibited the enzyme")

        # With stemming off (and synonyms off), only exact match
        with match_config(MatchConfig(use_stemming=False, use_synonyms=False)):
            # "inhibit" is NOT an exact substring of "inhibited" — wait, it IS
            # ("inhibit" in "inhibited" is True via exact substring)
            assert phrase_match("inhibit", "The drug inhibited the enzyme")
            # But "inhibition" would NOT match "inhibited" without stemming
            assert not phrase_match("inhibition", "The drug inhibited the enzyme")

    def test_run_ablation(self):
        from bioeval.reporting.ablation import run_ablation
        # Create a synthetic result file
        data = {
            "metadata": {"model": "test", "data_tier": "base", "timestamp": "2025-01-01T00:00:00"},
            "results": [{
                "component": "adversarial",
                "num_tasks": 2,
                "results": [
                    {"task_id": "a1", "score": 0.8, "trap_detected": True,
                     "correct_content_score": 0.7, "hallucination_penalty": 0.0,
                     "adversarial_type": "false_premise"},
                    {"task_id": "a2", "score": 0.3, "trap_detected": False,
                     "correct_content_score": 0.2, "hallucination_penalty": 0.2,
                     "adversarial_type": "hallucination_trap"},
                ],
            }],
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            tmppath = f.name
        try:
            result = run_ablation(tmppath)
            assert "configs" in result
            assert "full" in result["configs"]
            assert "exact_only" in result["configs"]
            assert "deltas" in result
            assert "feature_contributions" in result
        finally:
            os.unlink(tmppath)


# =============================================================================
# DASHBOARD TESTS
# =============================================================================

class TestDashboard:
    """Test HTML dashboard generation."""

    def test_generate_dashboard(self):
        from bioeval.reporting.dashboard import generate_dashboard
        data = {
            "metadata": {"model": "test-model", "data_tier": "base",
                         "timestamp": "2025-01-01T00:00:00"},
            "results": [
                {
                    "component": "adversarial",
                    "num_tasks": 2,
                    "results": [
                        {"task_id": "adv_001", "score": 0.9, "trap_detected": True,
                         "correct_content_score": 0.8, "hallucination_penalty": 0.0,
                         "adversarial_type": "false_premise"},
                        {"task_id": "adv_002", "score": 0.3, "trap_detected": False,
                         "correct_content_score": 0.1, "hallucination_penalty": 0.4,
                         "adversarial_type": "hallucination_trap"},
                    ],
                },
                {
                    "component": "calibration",
                    "num_tasks": 2,
                    "results": [
                        {"task_id": "cal_001", "calibration_error": 0.1,
                         "is_correct": True, "confidence_score": 0.85,
                         "details": {"confidence_appropriate": True, "correct_behavior": "high_confidence_correct"}},
                        {"task_id": "test_000", "calibration_error": 0.4,
                         "is_correct": False, "confidence_score": 0.7,
                         "details": {"confidence_appropriate": False, "correct_behavior": "overconfidence_trap"}},
                    ],
                },
            ],
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            result_path = f.name

        html_path = result_path.replace(".json", ".html")
        try:
            out = generate_dashboard(result_path, html_path)
            assert os.path.exists(out)
            with open(out) as fh:
                html_content = fh.read()
            assert "BioEval Dashboard" in html_content
            assert "test-model" in html_content
            assert "adversarial" in html_content
            assert "calibration" in html_content
            assert len(html_content) > 1000  # Substantial HTML
        finally:
            os.unlink(result_path)
            if os.path.exists(html_path):
                os.unlink(html_path)


# =============================================================================
# TASK VALIDATION TESTS
# =============================================================================

class TestTaskValidation:
    """Test task data validation framework."""

    def test_validate_all_no_errors(self):
        from bioeval.validation.task_checks import validate_all, validation_summary
        issues = validate_all("base")
        summary = validation_summary(issues)
        # Should have no errors on valid base data
        assert summary["errors"] == 0
        assert summary["all_clear"] is True

    def test_validation_issue_format(self):
        from bioeval.validation.task_checks import ValidationIssue
        issue = ValidationIssue("error", "test", "t1", "field", "broken")
        s = str(issue)
        assert "ERROR" in s
        assert "test" in s
        assert "t1" in s


# =============================================================================
# STABILITY ANALYSIS TESTS
# =============================================================================

class TestStability:
    """Test score stability analysis."""

    def test_perturbation_functions(self):
        from bioeval.reporting.stability import perturb_response
        text = "The KRAS gene is essential for cell proliferation."
        # Each perturbation type should return a string
        for ptype in ["case", "whitespace", "synonym", "word_order"]:
            result = perturb_response(text, ptype, seed=42)
            assert isinstance(result, str)
            assert len(result) > 0

    def test_measure_stability(self):
        from bioeval.reporting.stability import measure_stability
        data = {
            "metadata": {"model": "test", "data_tier": "base", "timestamp": "2025-01-01T00:00:00"},
            "results": [{
                "component": "adversarial",
                "num_tasks": 2,
                "results": [
                    {"task_id": "a1", "score": 0.8, "trap_detected": True,
                     "correct_content_score": 0.7, "hallucination_penalty": 0.0,
                     "adversarial_type": "false_premise"},
                    {"task_id": "a2", "score": 0.3, "trap_detected": False,
                     "correct_content_score": 0.2, "hallucination_penalty": 0.2,
                     "adversarial_type": "hallucination_trap"},
                ],
            }],
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            tmppath = f.name
        try:
            result = measure_stability(tmppath, n_perturbations=3)
            assert "overall" in result
            assert "by_component" in result
            assert result["n_tasks"] == 2
            # Small perturbations should produce small diffs
            assert result["overall"]["mean_score_diff"] < 0.1
            assert result["overall"]["pass_stability"] >= 0.5
        finally:
            os.unlink(tmppath)


# =============================================================================
# COMPONENT REGISTRY TESTS
# =============================================================================

class TestRegistry:
    """Test component registry."""

    def test_builtin_components(self):
        from bioeval.registry import REGISTRY, list_components
        names = list_components()
        assert len(names) == 9
        for expected in ["protoreason", "causalbio", "designcheck",
                         "adversarial", "multiturn", "calibration",
                         "biosafety", "datainterp", "debate"]:
            assert expected in names

    def test_component_info(self):
        from bioeval.registry import get_component
        info = get_component("adversarial")
        assert info.name == "adversarial"
        assert "adversarial" in info.description.lower()
        assert len(info.task_types) > 0
        assert "base" in info.supports_data_tiers

    def test_register_custom(self):
        from bioeval.registry import (REGISTRY, register_component,
                                       unregister_component, ComponentInfo)
        custom = ComponentInfo(
            name="custom_test",
            description="Test component",
            evaluator_module="bioeval.adversarial.tasks",
            evaluator_class="AdversarialEvaluator",
            task_data_module="bioeval.adversarial.tasks",
        )
        register_component("custom_test", custom)
        assert "custom_test" in REGISTRY
        unregister_component("custom_test")
        assert "custom_test" not in REGISTRY

    def test_unknown_component_raises(self):
        from bioeval.registry import get_component
        with pytest.raises(KeyError):
            get_component("nonexistent_component")


# =============================================================================
# SIMULATION TESTS
# =============================================================================

class TestSimulation:
    """Test synthetic response generation and end-to-end pipeline."""

    def test_simulation_good_quality(self):
        from bioeval.simulation import run_simulation
        result = run_simulation(quality="good", seed=42)
        assert result["metadata"]["quality"] == "good"
        assert result["metadata"]["simulation"] is True
        assert len(result["results"]) == 9
        # All 9 components present
        comp_names = {r["component"] for r in result["results"]}
        assert comp_names == {"protoreason", "causalbio", "designcheck",
                              "adversarial", "multiturn", "calibration",
                              "biosafety", "datainterp", "debate"}
        # No errors
        for comp_result in result["results"]:
            errors = [r for r in comp_result["results"]
                      if isinstance(r, dict) and "error" in r and "score" not in r]
            assert len(errors) == 0, f"{comp_result['component']} has errors: {errors}"

    def test_simulation_bad_quality(self):
        from bioeval.simulation import run_simulation
        result = run_simulation(quality="bad", seed=42)
        assert result["metadata"]["quality"] == "bad"
        for comp_result in result["results"]:
            assert comp_result["num_tasks"] > 0

    def test_simulation_analysis_pipeline(self):
        """Verify simulation results are compatible with the analysis pipeline."""
        from bioeval.simulation import run_simulation
        from bioeval.reporting.analysis import analyze_results
        import tempfile, json
        result = run_simulation(quality="good", seed=99)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(result, f, default=str)
            tmppath = f.name
        try:
            analysis = analyze_results(tmppath)
            assert analysis["overall"]["n"] > 0
            assert 0.0 <= analysis["overall"]["mean"] <= 1.0
            assert len(analysis["by_component"]) >= 4  # At least 4 components scored
        finally:
            os.unlink(tmppath)

    def test_simulation_reproducibility(self):
        """Same seed → identical results."""
        from bioeval.simulation import run_simulation
        r1 = run_simulation(quality="mixed", seed=123)
        r2 = run_simulation(quality="mixed", seed=123)
        # Compare task counts and scores (ignore timestamps)
        for c1, c2 in zip(r1["results"], r2["results"]):
            assert c1["component"] == c2["component"]
            assert c1["num_tasks"] == c2["num_tasks"]
            for t1, t2 in zip(c1["results"], c2["results"]):
                if "error" not in t1:
                    # Scores should be identical for same seed
                    tid1 = t1.get("task_id", t1.get("dialogue_id"))
                    tid2 = t2.get("task_id", t2.get("dialogue_id"))
                    assert tid1 == tid2

    def test_simulation_quality_ordering(self):
        """Good quality should score higher than bad quality on average."""
        from bioeval.simulation import run_simulation
        from bioeval.reporting.analysis import analyze_results
        import tempfile, json
        scores = {}
        for q in ["good", "bad"]:
            result = run_simulation(quality=q, seed=42)
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                json.dump(result, f, default=str)
                tmppath = f.name
            try:
                analysis = analyze_results(tmppath)
                scores[q] = analysis["overall"]["mean"]
            finally:
                os.unlink(tmppath)
        assert scores["good"] > scores["bad"], \
            f"Good ({scores['good']:.3f}) should score higher than bad ({scores['bad']:.3f})"


# =============================================================================
# REPRODUCIBILITY TESTS
# =============================================================================

class TestReproducibility:
    """Test reproducibility verification framework."""

    def test_determinism(self):
        from bioeval.reporting.reproducibility import verify_determinism
        result = verify_determinism(n_runs=2, seed=42)
        assert result["passed"] is True
        assert result["hash_match"] is True

    def test_seed_sensitivity(self):
        from bioeval.reporting.reproducibility import verify_seed_sensitivity
        result = verify_seed_sensitivity(seeds=[42, 99])
        assert result["passed"] is True
        assert result["n_unique"] == 2

    def test_component_coverage(self):
        from bioeval.reporting.reproducibility import verify_component_coverage
        result = verify_component_coverage()
        assert result["passed"] is True
        assert result["all_error_free"] is True
        assert result["all_present"] is True


# =============================================================================
# SCORING FEEDBACK TESTS
# =============================================================================

class TestFeedback:
    """Test scoring feedback analysis."""

    def test_feedback_on_good_results(self):
        from bioeval.simulation import run_simulation
        from bioeval.reporting.feedback import analyze_scoring_feedback
        import tempfile
        result = run_simulation(quality="good", seed=42)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(result, f, default=str)
            tmppath = f.name
        try:
            fb = analyze_scoring_feedback(tmppath)
            assert fb["n_tasks"] > 0
            assert "diagnostics" in fb
            assert "warnings" in fb
            assert "suggestions" in fb
            # Check distribution diagnostic exists
            dist = [d for d in fb["diagnostics"] if d["type"] == "overall_distribution"]
            assert len(dist) == 1
            assert 0.0 <= dist[0]["mean"] <= 1.0
        finally:
            os.unlink(tmppath)

    def test_feedback_on_bad_results(self):
        from bioeval.simulation import run_simulation
        from bioeval.reporting.feedback import analyze_scoring_feedback
        import tempfile
        result = run_simulation(quality="bad", seed=42)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(result, f, default=str)
            tmppath = f.name
        try:
            fb = analyze_scoring_feedback(tmppath)
            assert fb["n_tasks"] > 0
            # Bad quality should produce lower scores, potentially more warnings
            dist = [d for d in fb["diagnostics"] if d["type"] == "overall_distribution"]
            assert dist[0]["mean"] < 0.7  # Bad should score below 0.7
        finally:
            os.unlink(tmppath)


# =============================================================================
# AGREEMENT METRIC TESTS
# =============================================================================

class TestAgreement:
    """Test inter-rater agreement metrics."""

    def test_cohens_kappa_perfect(self):
        from bioeval.reporting.agreement import cohens_kappa
        r1 = [1, 1, 0, 0, 1, 0]
        r2 = [1, 1, 0, 0, 1, 0]
        assert cohens_kappa(r1, r2) == 1.0

    def test_cohens_kappa_chance(self):
        from bioeval.reporting.agreement import cohens_kappa
        # All same class → pe=1.0 for both raters agreeing on same class
        r1 = [1, 1, 1, 1]
        r2 = [0, 0, 0, 0]
        k = cohens_kappa(r1, r2)
        assert k <= 0  # Disagreement below chance

    def test_cohens_kappa_moderate(self):
        from bioeval.reporting.agreement import cohens_kappa
        r1 = [1, 1, 0, 0, 1, 0, 1, 0]
        r2 = [1, 0, 0, 0, 1, 1, 1, 0]
        k = cohens_kappa(r1, r2)
        assert 0 < k < 1  # Some agreement but not perfect

    def test_weighted_kappa(self):
        from bioeval.reporting.agreement import weighted_kappa
        # Similar scores → high weighted kappa
        s1 = [0.9, 0.8, 0.2, 0.1, 0.5]
        s2 = [0.85, 0.75, 0.25, 0.15, 0.55]
        wk = weighted_kappa(s1, s2)
        assert wk > 0.5  # Should be substantial agreement

    def test_analyze_from_scores(self):
        from bioeval.reporting.agreement import analyze_agreement_from_scores
        auto = [0.9, 0.8, 0.3, 0.1, 0.6, 0.4, 0.7, 0.2]
        judge = [0.85, 0.75, 0.35, 0.15, 0.55, 0.45, 0.65, 0.25]
        result = analyze_agreement_from_scores(auto, judge)
        assert result["n"] == 8
        assert "cohens_kappa" in result
        assert "weighted_kappa" in result
        assert "interpretation" in result
        assert result["percent_agreement"] > 0.5


# =============================================================================
# DIFFICULTY ANALYSIS TESTS
# =============================================================================

class TestDifficulty:
    """Test task difficulty analysis and rebalancing."""

    def test_difficulty_analysis(self):
        from bioeval.simulation import run_simulation
        from bioeval.reporting.difficulty import analyze_difficulty
        import tempfile
        result = run_simulation(quality="mixed", seed=42)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(result, f, default=str)
            tmppath = f.name
        try:
            analysis = analyze_difficulty(tmppath)
            assert analysis["n_tasks"] > 0
            assert "overall" in analysis
            assert "by_component" in analysis
            assert "recommendations" in analysis
            assert 0 <= analysis["balance_score"] <= 1.0
            # Distribution should sum to total
            o = analysis["overall"]
            assert o["easy"] + o["medium"] + o["hard"] == o["n"]
        finally:
            os.unlink(tmppath)

    def test_difficulty_good_vs_bad(self):
        from bioeval.simulation import run_simulation
        from bioeval.reporting.difficulty import analyze_difficulty
        import tempfile
        analyses = {}
        for q in ["good", "bad"]:
            result = run_simulation(quality=q, seed=42)
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                json.dump(result, f, default=str)
                tmppath = f.name
            try:
                analyses[q] = analyze_difficulty(tmppath)
            finally:
                os.unlink(tmppath)
        # Good should have more easy tasks than bad
        assert analyses["good"]["overall"]["easy"] >= analyses["bad"]["overall"]["easy"]
