#!/usr/bin/env python3
"""Release consistency checks for BioEval."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from bioeval.version import __version__

ROOT = Path(__file__).resolve().parent.parent


def _fail(msg: str):
    print(f"[FAIL] {msg}")
    sys.exit(1)


def _ok(msg: str):
    print(f"[OK] {msg}")


def check_version_badge():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    m = re.search(r"badge/version-([0-9]+\.[0-9]+\.[0-9]+)-", readme)
    if not m:
        _fail("README version badge not found")
    if m.group(1) != __version__:
        _fail(f"README badge version {m.group(1)} != package version {__version__}")
    _ok(f"README badge version matches {__version__}")


def check_version_imports():
    setup_py = (ROOT / "setup.py").read_text(encoding="utf-8")
    if 'version=version_ns["__version__"]' not in setup_py:
        _fail("setup.py is not reading version from bioeval/version.py")
    _ok("setup.py uses version.py")


def check_inventory_counts():
    """Verify README task counts match actual load_tasks() output."""
    from bioeval.protoreason.evaluator import ProtoReasonEvaluator
    from bioeval.causalbio.evaluator import CausalBioEvaluator
    from bioeval.designcheck.evaluator import DesignCheckEvaluator
    from bioeval.adversarial.tasks import AdversarialEvaluator
    from bioeval.multiturn.dialogues import MultiTurnEvaluator
    from bioeval.scoring.calibration import CalibrationEvaluator
    from bioeval.biosafety.tasks import BiosafetyEvaluator
    from bioeval.datainterp.tasks import DataInterpEvaluator
    from bioeval.debate.evaluator import DebateEvaluator

    # Count base tasks from actual evaluator load_tasks()
    base_counts = {}
    evaluators = {
        "protoreason": (ProtoReasonEvaluator, "base"),
        "causalbio": (CausalBioEvaluator, "base"),
        "designcheck": (DesignCheckEvaluator, "base"),
        "multiturn": (MultiTurnEvaluator, "base"),
    }
    # These evaluators' load_tasks() takes no tier argument
    no_tier_evaluators = {
        "adversarial": AdversarialEvaluator,
        "calibration": CalibrationEvaluator,
        "biosafety": BiosafetyEvaluator,
        "datainterp": DataInterpEvaluator,
        "debate": DebateEvaluator,
    }

    for name, (cls, tier) in evaluators.items():
        e = cls()
        base_counts[name] = len(e.load_tasks(tier))

    for name, cls in no_tier_evaluators.items():
        e = cls()
        base_counts[name] = len(e.load_tasks())

    base_total = sum(base_counts.values())

    # Count extended additions (unique tasks not in base)
    ext_additions = 0
    for name, (cls, _) in evaluators.items():
        e = cls()
        try:
            base_tasks = e.load_tasks("base")
            ext_tasks = e.load_tasks("extended")
            base_ids = {t.id for t in base_tasks}
            ext_ids = {t.id for t in ext_tasks}
            ext_additions += len(ext_ids - base_ids)
        except Exception:
            pass

    total_unique = base_total + ext_additions

    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    # Check base count
    m_base = re.search(r"\|\s+\*\*Base\*\*\s+\|\s+(\d+)\s+\|", readme)
    if not m_base:
        _fail("README base task count not found")
    doc_base = int(m_base.group(1))
    if doc_base != base_total:
        _fail(f"README base count {doc_base} != computed {base_total}")

    # Check extended count
    m_ext = re.search(r"\|\s+\*\*Extended\*\*\s+\|\s+(\d+)\s+\|", readme)
    if not m_ext:
        _fail("README extended task count not found")
    doc_ext = int(m_ext.group(1))
    if doc_ext != ext_additions:
        _fail(f"README extended count {doc_ext} != computed {ext_additions}")

    # Check total count
    m_total = re.search(r"\|\s+\*\*Total Unique\*\*\s+\|\s+\*\*(\d+)\*\*\s+\|", readme)
    if not m_total:
        _fail("README total unique task count not found")
    doc_total = int(m_total.group(1))
    if doc_total != total_unique:
        _fail(f"README total count {doc_total} != computed {total_unique}")

    _ok(f"README inventory counts match: base={base_total}, extended=+{ext_additions}, total={total_unique}")


def check_no_hardcoded_legacy_versions():
    bad_patterns = ("0.1.0", "0.2.0", "0.4.0")
    paths = list((ROOT / "bioeval").rglob("*.py")) + list((ROOT / "scripts").rglob("*.py")) + [ROOT / "README.md"]
    offenders = []
    for p in paths:
        if not p.exists():
            continue
        if p.name == "check_release_consistency.py":
            continue
        txt = p.read_text(encoding="utf-8")
        for pat in bad_patterns:
            if pat in txt:
                offenders.append(f"{p.relative_to(ROOT)}: contains {pat}")
    if offenders:
        _fail("Legacy version strings found:\n" + "\n".join(offenders[:20]))
    _ok("No legacy version strings in code/scripts/README")


def main():
    check_version_badge()
    check_version_imports()
    check_inventory_counts()
    check_no_hardcoded_legacy_versions()
    print("[OK] Release consistency checks passed")


if __name__ == "__main__":
    main()
