"""Tests for reporting modules: baselines and datasheet."""

from __future__ import annotations


class TestBaselines:
    def test_random_baselines_structure(self):
        from bioeval.reporting.baselines import compute_random_baselines

        baselines = compute_random_baselines()
        assert len(baselines) == 9
        for comp, info in baselines.items():
            assert "random_baseline" in info, f"{comp}: missing random_baseline"
            assert 0.0 <= info["random_baseline"] <= 1.0, f"{comp}: out of range"

    def test_baselines_deterministic(self):
        from bioeval.reporting.baselines import compute_random_baselines

        a = compute_random_baselines(seed=42)
        b = compute_random_baselines(seed=42)
        for comp in a:
            assert a[comp]["random_baseline"] == b[comp]["random_baseline"]

    def test_print_baselines_runs(self, capsys):
        from bioeval.reporting.baselines import print_baselines

        print_baselines()
        captured = capsys.readouterr()
        assert "protoreason" in captured.out.lower() or "ProtoReason" in captured.out


class TestDatasheet:
    def test_datasheet_generation(self):
        from bioeval.reporting.datasheet import generate_datasheet

        ds = generate_datasheet()
        for section in ["title", "motivation", "composition", "collection", "uses"]:
            assert section in ds, f"Missing section: {section}"
        assert "197 base tasks" in ds["composition"]["total_instances"]

    def test_print_datasheet_runs(self, capsys):
        from bioeval.reporting.datasheet import print_datasheet

        print_datasheet()
        captured = capsys.readouterr()
        assert "BioEval" in captured.out
