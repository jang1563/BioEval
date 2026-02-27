#!/usr/bin/env python3
"""Run a local quality check suite for BioEval.

This script aggregates common checks used in CI:
- release consistency
- test suite
- black (optional)
- ruff (optional)
- mypy (optional)
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


@dataclass
class CheckResult:
    name: str
    status: str  # PASS | FAIL | SKIP
    detail: str = ""


def _run(name: str, cmd: list[str]) -> CheckResult:
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if proc.returncode == 0:
        return CheckResult(name=name, status="PASS")
    output = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    output = output.strip()
    tail = "\n".join(output.splitlines()[-20:]) if output else "No output"
    return CheckResult(name=name, status="FAIL", detail=tail)


def _tool_exists(tool: str) -> bool:
    return shutil.which(tool) is not None


def main() -> int:
    parser = argparse.ArgumentParser(description="Run BioEval quality checks")
    parser.add_argument("--require-tools", action="store_true",
                        help="Fail if black/ruff/mypy are missing")
    args = parser.parse_args()

    results: list[CheckResult] = []

    # Always-run checks
    results.append(_run("release-consistency", [sys.executable, "scripts/check_release_consistency.py"]))
    results.append(_run("pytest", [sys.executable, "-m", "pytest", "-q"]))

    # Optional tool checks
    optional = [
        ("black", ["black", "--check", "bioeval", "scripts", "tests"]),
        ("ruff", ["ruff", "check", "bioeval", "scripts", "tests"]),
        ("mypy", ["mypy", "bioeval", "--ignore-missing-imports"]),
    ]
    missing_tools = []
    for tool, cmd in optional:
        if _tool_exists(tool):
            results.append(_run(tool, cmd))
        else:
            results.append(CheckResult(name=tool, status="SKIP", detail=f"{tool} not installed"))
            missing_tools.append(tool)

    # Summary
    print("== BioEval Quality Check Summary ==")
    for r in results:
        print(f"- {r.name}: {r.status}")
        if r.detail and r.status != "PASS":
            print(r.detail)

    failed = [r for r in results if r.status == "FAIL"]
    if failed:
        return 1

    if args.require_tools and missing_tools:
        print(f"\nMissing required tools: {', '.join(missing_tools)}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

