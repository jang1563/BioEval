"""Tests for bioeval.reporting.statistical_tests module."""

import pytest
from bioeval.reporting.statistical_tests import (
    bootstrap_ci,
    wilcoxon_signed_rank,
    permutation_test,
    cohens_d,
    hedges_g,
    rank_biserial_r,
    _default_extract_score,
)


class TestBootstrapCI:
    def test_basic(self):
        scores = [0.8, 0.9, 0.7, 0.85, 0.95, 0.6, 0.88]
        ci = bootstrap_ci(scores)
        assert ci["n"] == 7
        assert 0.7 <= ci["mean"] <= 0.9
        assert ci["lower"] < ci["mean"]
        assert ci["upper"] > ci["mean"]
        assert ci["std"] > 0

    def test_single_value(self):
        ci = bootstrap_ci([0.5])
        assert ci["mean"] == 0.5
        assert ci["n"] == 1

    def test_empty(self):
        ci = bootstrap_ci([])
        assert ci["n"] == 0
        assert ci["mean"] == 0.0

    def test_identical_values(self):
        ci = bootstrap_ci([0.8, 0.8, 0.8])
        assert ci["mean"] == 0.8
        assert ci["lower"] == 0.8
        assert ci["upper"] == 0.8

    def test_reproducibility(self):
        scores = [0.1, 0.5, 0.9, 0.3, 0.7]
        ci1 = bootstrap_ci(scores, seed=42)
        ci2 = bootstrap_ci(scores, seed=42)
        assert ci1 == ci2

    def test_different_seeds(self):
        scores = [0.1, 0.5, 0.9, 0.3, 0.7]
        ci1 = bootstrap_ci(scores, seed=42)
        ci2 = bootstrap_ci(scores, seed=99)
        # Means should be very close but CIs may differ slightly
        assert abs(ci1["mean"] - ci2["mean"]) < 0.001


class TestWilcoxonSignedRank:
    def test_significant_difference(self):
        a = [0.8, 0.9, 0.7, 0.85, 0.95, 0.6, 0.88, 0.75, 0.82, 0.91]
        b = [0.7, 0.85, 0.65, 0.80, 0.90, 0.55, 0.83, 0.70, 0.78, 0.86]
        result = wilcoxon_signed_rank(a, b)
        assert result["n_pairs"] == 10
        assert result["p_value"] < 0.05

    def test_no_difference(self):
        a = [0.5, 0.5, 0.5, 0.5, 0.5]
        b = [0.5, 0.5, 0.5, 0.5, 0.5]
        result = wilcoxon_signed_rank(a, b)
        assert result["p_value"] >= 0.05

    def test_mismatched_lengths(self):
        with pytest.raises(ValueError):
            wilcoxon_signed_rank([0.5, 0.6], [0.5])

    def test_empty(self):
        result = wilcoxon_signed_rank([], [])
        assert result["n_pairs"] == 0
        assert result["p_value"] == 1.0


class TestPermutationTest:
    def test_significant(self):
        a = [0.8, 0.9, 0.7, 0.85, 0.95, 0.6]
        b = [0.5, 0.6, 0.4, 0.55, 0.65, 0.3]
        result = permutation_test(a, b)
        assert result["n"] == 6
        assert result["p_value"] < 0.05  # Large difference
        assert result["observed_statistic"] > 0

    def test_no_difference(self):
        a = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
        b = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
        result = permutation_test(a, b)
        assert result["p_value"] > 0.5

    def test_mismatched_lengths(self):
        with pytest.raises(ValueError):
            permutation_test([0.5, 0.6], [0.5])

    def test_reproducibility(self):
        a = [0.8, 0.9, 0.7]
        b = [0.7, 0.85, 0.65]
        r1 = permutation_test(a, b, seed=42)
        r2 = permutation_test(a, b, seed=42)
        assert r1["p_value"] == r2["p_value"]


class TestEffectSizes:
    def test_cohens_d_positive(self):
        a = [0.8, 0.9, 0.7, 0.85]
        b = [0.5, 0.6, 0.4, 0.55]
        d = cohens_d(a, b)
        assert d > 0  # a > b

    def test_cohens_d_paired(self):
        a = [0.8, 0.9, 0.7, 0.85]
        b = [0.7, 0.85, 0.65, 0.80]
        d = cohens_d(a, b, paired=True)
        assert d > 0

    def test_cohens_d_no_difference(self):
        a = [0.5, 0.5, 0.5]
        b = [0.5, 0.5, 0.5]
        d = cohens_d(a, b)
        assert d == 0.0

    def test_hedges_g_correction(self):
        a = [0.8, 0.9, 0.7, 0.85]
        b = [0.5, 0.6, 0.4, 0.55]
        d = cohens_d(a, b)
        g = hedges_g(a, b)
        # Hedges' g should be slightly smaller than Cohen's d
        assert abs(g) <= abs(d)

    def test_rank_biserial(self):
        r = rank_biserial_r(0, 10)
        assert r == 1.0  # Perfect rank-biserial when W=0

        r = rank_biserial_r(10, 10)
        assert -1 <= r <= 1

    def test_empty_inputs(self):
        assert cohens_d([], []) == 0.0
        assert hedges_g([], []) == 0.0
        assert rank_biserial_r(0, 0) == 0.0


class TestDefaultExtractScore:
    def test_protoreason_ordering(self):
        result = {"scores": {"adjacent_pair_accuracy": 0.9, "kendall_tau": 0.85}}
        assert _default_extract_score("protoreason", result) == 0.9

    def test_protoreason_missing(self):
        result = {"scores": {"recall": 0.75}}
        assert _default_extract_score("protoreason", result) == 0.75

    def test_causalbio_knockout(self):
        result = {"scores": {"effect_correct": True}}
        assert _default_extract_score("causalbio", result) == 1.0

        result = {"scores": {"effect_correct": False}}
        assert _default_extract_score("causalbio", result) == 0.0

    def test_causalbio_pathway(self):
        result = {"scores": {"combined_score": 0.65}}
        assert _default_extract_score("causalbio", result) == 0.65

    def test_designcheck(self):
        result = {"scores": {"f1": 0.7}}
        assert _default_extract_score("designcheck", result) == 0.7

    def test_adversarial(self):
        result = {"scores": {"score": 0.85}}
        assert _default_extract_score("adversarial", result) == 0.85

    def test_calibration(self):
        result = {"scores": {"calibration_error": 0.1}}
        assert _default_extract_score("calibration", result) == 0.9

    def test_biosafety_toplevel(self):
        result = {"score": 0.82, "scores": {}}
        assert _default_extract_score("biosafety", result) == 0.82

    def test_datainterp_toplevel(self):
        result = {"score": 0.6, "scores": {}}
        assert _default_extract_score("datainterp", result) == 0.6

    def test_debate(self):
        result = {"scores": {"composite_score": 0.4}}
        assert _default_extract_score("debate", result) == 0.4

    def test_unknown_component(self):
        result = {"scores": {"score": 0.5}}
        assert _default_extract_score("unknown", result) is None
