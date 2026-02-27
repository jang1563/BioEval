#!/usr/bin/env python3
"""Quick test of statistical_tests module."""
import sys

sys.path.insert(0, "/Users/jak4013/Dropbox/Bioinformatics/Claude/Evaluation_model/BioEval")

from bioeval.reporting.statistical_tests import bootstrap_ci, wilcoxon_signed_rank, permutation_test, cohens_d, hedges_g

# Test bootstrap CI
scores = [0.8, 0.9, 0.7, 0.85, 0.95, 0.6, 0.88]
ci = bootstrap_ci(scores)
print("Bootstrap CI:", ci)
assert ci["n"] == 7
assert 0.7 <= ci["mean"] <= 0.9
assert ci["lower"] < ci["mean"] < ci["upper"]

# Test Wilcoxon
a = [0.8, 0.9, 0.7, 0.85, 0.95, 0.6, 0.88, 0.75, 0.82, 0.91]
b = [0.7, 0.85, 0.65, 0.80, 0.90, 0.55, 0.83, 0.70, 0.78, 0.86]
w = wilcoxon_signed_rank(a, b)
print("Wilcoxon:", w)
assert w["n_pairs"] == 10
assert w["p_value"] < 0.05  # Should be significant

# Test permutation (small N=6)
a_small = [0.8, 0.9, 0.7, 0.85, 0.95, 0.6]
b_small = [0.7, 0.85, 0.65, 0.80, 0.90, 0.55]
p = permutation_test(a_small, b_small)
print("Permutation:", p)
assert p["n"] == 6

# Test effect sizes
d = cohens_d(a, b, paired=True)
print("Cohen's d:", round(d, 4))
assert d > 0  # a > b on average

g = hedges_g(a, b)
print("Hedges' g:", round(g, 4))

print("\nAll statistical tests passed!")
