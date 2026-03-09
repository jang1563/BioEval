"""Tests for data tier consistency: base must be a subset of extended."""

from __future__ import annotations

import importlib

import pytest


# All evaluators that support data_tier argument
TIER_EVALUATORS = [
    "bioeval.protoreason.evaluator.ProtoReasonEvaluator",
    "bioeval.causalbio.evaluator.CausalBioEvaluator",
    "bioeval.designcheck.evaluator.DesignCheckEvaluator",
    "bioeval.multiturn.dialogues.MultiTurnEvaluator",
]


def _get_evaluator(cls_path):
    module_path, cls_name = cls_path.rsplit(".", 1)
    mod = importlib.import_module(module_path)
    return getattr(mod, cls_name)()


class TestBaseSubsetExtended:
    """Verify that every base task ID exists in the extended tier."""

    @pytest.mark.parametrize("cls_path", TIER_EVALUATORS)
    def test_base_ids_subset_of_extended(self, cls_path):
        e = _get_evaluator(cls_path)
        base_ids = {t.id for t in e.load_tasks("base")}
        ext_ids = {t.id for t in e.load_tasks("extended")}
        missing = base_ids - ext_ids
        assert not missing, f"base IDs not in extended: {sorted(missing)}"

    @pytest.mark.parametrize("cls_path", TIER_EVALUATORS)
    def test_no_duplicate_ids_in_extended(self, cls_path):
        e = _get_evaluator(cls_path)
        ext_tasks = e.load_tasks("extended")
        ids = [t.id for t in ext_tasks]
        dupes = [tid for tid in set(ids) if ids.count(tid) > 1]
        assert not dupes, f"duplicate IDs in extended: {sorted(dupes)}"

    def test_extended_count_protoreason(self):
        from bioeval.protoreason.evaluator import ProtoReasonEvaluator

        assert len(ProtoReasonEvaluator().load_tasks("extended")) == 59

    def test_extended_count_causalbio(self):
        from bioeval.causalbio.evaluator import CausalBioEvaluator

        assert len(CausalBioEvaluator().load_tasks("extended")) == 47

    def test_extended_count_designcheck(self):
        from bioeval.designcheck.evaluator import DesignCheckEvaluator

        assert len(DesignCheckEvaluator().load_tasks("extended")) == 30

    def test_extended_count_multiturn(self):
        from bioeval.multiturn.dialogues import MultiTurnEvaluator

        assert len(MultiTurnEvaluator().load_tasks("extended")) == 30

    def test_total_unique_301(self):
        """Total unique task IDs across all components must be 301."""
        from bioeval.protoreason.evaluator import ProtoReasonEvaluator
        from bioeval.causalbio.evaluator import CausalBioEvaluator
        from bioeval.designcheck.evaluator import DesignCheckEvaluator
        from bioeval.multiturn.dialogues import MultiTurnEvaluator
        from bioeval.adversarial.tasks import AdversarialEvaluator
        from bioeval.scoring.calibration import CalibrationEvaluator
        from bioeval.biosafety.tasks import BiosafetyEvaluator
        from bioeval.datainterp.tasks import DataInterpEvaluator
        from bioeval.debate.evaluator import DebateEvaluator
        from bioeval.longhorizon.evaluator import LongHorizonEvaluator
        from bioeval.agentic.evaluator import AgenticEvaluator
        from bioeval.bioambiguity.evaluator import BioAmbiguityEvaluator

        all_ids = set()
        for cls in [
            ProtoReasonEvaluator,
            CausalBioEvaluator,
            DesignCheckEvaluator,
            MultiTurnEvaluator,
        ]:
            for t in cls().load_tasks("extended"):
                all_ids.add(t.id)
        for cls in [
            AdversarialEvaluator,
            CalibrationEvaluator,
            BiosafetyEvaluator,
            DataInterpEvaluator,
            DebateEvaluator,
            LongHorizonEvaluator,
            AgenticEvaluator,
            BioAmbiguityEvaluator,
        ]:
            for t in cls().load_tasks():
                all_ids.add(t.id)
        assert len(all_ids) == 400, f"Expected 400, got {len(all_ids)}"


class TestExportCommand:
    """Test the bioeval export CLI command."""

    def test_export_base_jsonl(self, tmp_path):
        import json
        from bioeval.cli import cmd_export
        import argparse

        out = tmp_path / "base.jsonl"
        args = argparse.Namespace(data_tier="base", output=str(out))
        cmd_export(args)

        lines = out.read_text().strip().split("\n")
        assert len(lines) == 296, f"Expected 296, got {len(lines)}"
        for line in lines:
            record = json.loads(line)
            assert "component" in record
            assert "task_id" in record
            assert "prompt" in record
            assert record["prompt"], f"Empty prompt for {record['task_id']}"

    def test_export_extended_jsonl(self, tmp_path):
        import json
        from bioeval.cli import cmd_export
        import argparse

        out = tmp_path / "extended.jsonl"
        args = argparse.Namespace(data_tier="extended", output=str(out))
        cmd_export(args)

        lines = out.read_text().strip().split("\n")
        assert len(lines) == 400, f"Expected 400, got {len(lines)}"

        ids = [json.loads(line)["task_id"] for line in lines]
        assert len(ids) == len(set(ids)), "Duplicate task_ids in export"
