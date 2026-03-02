"""Tests for weight sensitivity analysis and random baselines."""

from __future__ import annotations

import pytest

from bioeval.reporting.sensitivity import (
    perturb_weights,
    WEIGHT_REGISTRY,
)
from bioeval.reporting.baselines import (
    compute_random_baselines,
    compute_naive_baselines,
)


class TestPerturbWeights:
    def test_sum_to_one(self):
        """All perturbed weight vectors must sum to 1.0."""
        weights = {"a": 0.5, "b": 0.3, "c": 0.2}
        samples = perturb_weights(weights, delta=0.1, n_samples=100, seed=42)
        for sample in samples:
            assert abs(sum(sample.values()) - 1.0) < 1e-9

    def test_non_negative(self):
        """All perturbed weights must be non-negative."""
        weights = {"a": 0.05, "b": 0.05, "c": 0.9}
        samples = perturb_weights(weights, delta=0.1, n_samples=200, seed=42)
        for sample in samples:
            for v in sample.values():
                assert v >= 0.0

    def test_keys_preserved(self):
        """Perturbed samples must have the same keys as the original."""
        weights = {"x": 0.6, "y": 0.4}
        samples = perturb_weights(weights, delta=0.1, n_samples=10, seed=42)
        for sample in samples:
            assert set(sample.keys()) == set(weights.keys())

    def test_reproducible(self):
        """Same seed produces same results."""
        weights = {"a": 0.5, "b": 0.5}
        s1 = perturb_weights(weights, seed=123, n_samples=5)
        s2 = perturb_weights(weights, seed=123, n_samples=5)
        for d1, d2 in zip(s1, s2):
            assert d1 == d2

    def test_registry_entries_valid(self):
        """All WEIGHT_REGISTRY entries must have weights summing to ~1.0."""
        for key, weights in WEIGHT_REGISTRY.items():
            total = sum(weights.values())
            assert abs(total - 1.0) < 0.01, f"WEIGHT_REGISTRY[{key}] sums to {total}"


class TestRandomBaselines:
    def test_all_nine_components(self):
        """Random baselines must cover all 9 components."""
        baselines = compute_random_baselines()
        expected = {
            "protoreason",
            "causalbio",
            "designcheck",
            "adversarial",
            "multiturn",
            "calibration",
            "biosafety",
            "datainterp",
            "debate",
        }
        assert set(baselines.keys()) == expected

    def test_baseline_range(self):
        """Random baselines must be in [0, 1]."""
        baselines = compute_random_baselines()
        for comp, info in baselines.items():
            score = info["random_baseline"]
            assert 0.0 <= score <= 1.0, f"{comp}: {score}"

    def test_has_method(self):
        """Each baseline must have a method description."""
        baselines = compute_random_baselines()
        for comp, info in baselines.items():
            assert "method" in info, f"{comp} missing method"
            assert len(info["method"]) > 0


class TestNaiveBaselines:
    def test_structure(self):
        """Naive baselines must be dict of dicts."""
        naive = compute_naive_baselines()
        assert isinstance(naive, dict)
        for comp, strategies in naive.items():
            assert isinstance(strategies, dict)
            for name, score in strategies.items():
                if score is not None:
                    assert 0.0 <= score <= 1.0, f"{comp}/{name}: {score}"
