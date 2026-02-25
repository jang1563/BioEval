#!/usr/bin/env python3
"""
BioEval: Unified CLI entry point

Usage:
    bioeval run --all                    Run all components
    bioeval run -c adversarial           Run specific component
    bioeval run --all --dry-run          Show task inventory without API calls
    bioeval compare results_a.json results_b.json   Compare two runs
    bioeval demo                         Show pre-cached results (no API key needed)
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path


COMPONENTS = [
    "protoreason", "causalbio", "designcheck",
    "adversarial", "multiturn", "calibration",
]


def cmd_inventory(args):
    """Show complete task inventory without making any API calls."""
    from bioeval.protoreason.evaluator import SAMPLE_PROTOCOLS, CALCULATION_TASKS, TROUBLESHOOTING_TASKS
    from bioeval.causalbio.evaluator import KNOCKOUT_TASKS, PATHWAY_TASKS, DRUG_RESPONSE_TASKS, EPISTASIS_TASKS
    from bioeval.designcheck.evaluator import FLAWED_DESIGNS
    from bioeval.adversarial.tasks import ADVERSARIAL_TASKS
    from bioeval.multiturn.dialogues import DIALOGUES
    from bioeval.scoring.calibration import CALIBRATION_TEST_TASKS

    print("=" * 60)
    print("BioEval Task Inventory")
    print("=" * 60)

    # Base data
    pr_base = len(SAMPLE_PROTOCOLS) * 3 + len(CALCULATION_TASKS) + len(TROUBLESHOOTING_TASKS)
    cb_base = len(KNOCKOUT_TASKS) + len(PATHWAY_TASKS) + len(DRUG_RESPONSE_TASKS) + len(EPISTASIS_TASKS)
    dc_base = len(FLAWED_DESIGNS)
    adv_base = len(ADVERSARIAL_TASKS)
    mt_base = len(DIALOGUES)
    cal_base = len(CALIBRATION_TEST_TASKS)

    print(f"\nBase tasks:")
    print(f"  ProtoReason:  {pr_base:3d}  ({len(SAMPLE_PROTOCOLS)} protocols x3 + {len(CALCULATION_TASKS)} calc + {len(TROUBLESHOOTING_TASKS)} troubleshoot)")
    print(f"  CausalBio:    {cb_base:3d}  ({len(KNOCKOUT_TASKS)} ko + {len(PATHWAY_TASKS)} path + {len(DRUG_RESPONSE_TASKS)} drug + {len(EPISTASIS_TASKS)} epi)")
    print(f"  DesignCheck:  {dc_base:3d}")
    print(f"  Adversarial:  {adv_base:3d}")
    print(f"  MultiTurn:    {mt_base:3d}")
    print(f"  Calibration:  {cal_base:3d}")
    base_total = pr_base + cb_base + dc_base + adv_base + mt_base + cal_base
    print(f"  {'─' * 30}")
    print(f"  Base total:   {base_total:3d}")

    # Extended data
    try:
        from bioeval.protoreason.extended_data import PROTOCOLS as EXT_PR, CALCULATION_TASKS as EXT_CALC
        from bioeval.protoreason.extended_data import TROUBLESHOOTING_TASKS as EXT_TS, SAFETY_TASKS as EXT_SAFETY
        from bioeval.causalbio.extended_data import KNOCKOUT_TASKS as EXT_KO, PATHWAY_TASKS as EXT_PATH
        from bioeval.causalbio.extended_data import DRUG_RESPONSE_TASKS as EXT_DRUG, EPISTASIS_TASKS as EXT_EPI

        pr_ext = len(EXT_PR) * 3 + len(EXT_CALC) + len(EXT_TS) + len(EXT_SAFETY)
        cb_ext = len(EXT_KO) + len(EXT_PATH) + len(EXT_DRUG) + len(EXT_EPI)
        ext_total = pr_ext + cb_ext
        print(f"\nExtended tasks:")
        print(f"  ProtoReason:  {pr_ext:3d}")
        print(f"  CausalBio:    {cb_ext:3d}")
        print(f"  {'─' * 30}")
        print(f"  Extended total: {ext_total:3d}")
    except ImportError:
        ext_total = 0
        print("\nExtended data: not available")

    # Advanced data
    try:
        from bioeval.protoreason.advanced_data import ADVANCED_PROTOCOLS, ADVANCED_CALCULATIONS, ADVANCED_TROUBLESHOOTING
        from bioeval.causalbio.advanced_data import BIOMARKER_TASKS, COMBINATION_TASKS, MULTI_OMIC_TASKS, RESISTANCE_TASKS
        from bioeval.designcheck.advanced_data import ANIMAL_DESIGNS, CLINICAL_DESIGNS, MULTICENTER_DESIGNS, SEQUENCING_DESIGNS

        pr_adv = len(ADVANCED_PROTOCOLS) * 3 + len(ADVANCED_CALCULATIONS) + len(ADVANCED_TROUBLESHOOTING)
        cb_adv = len(BIOMARKER_TASKS) + len(COMBINATION_TASKS) + len(MULTI_OMIC_TASKS) + len(RESISTANCE_TASKS)
        dc_adv = len(ANIMAL_DESIGNS) + len(CLINICAL_DESIGNS) + len(MULTICENTER_DESIGNS) + len(SEQUENCING_DESIGNS)
        adv_total = pr_adv + cb_adv + dc_adv
        print(f"\nAdvanced tasks:")
        print(f"  ProtoReason:  {pr_adv:3d}")
        print(f"  CausalBio:    {cb_adv:3d}")
        print(f"  DesignCheck:  {dc_adv:3d}")
        print(f"  {'─' * 30}")
        print(f"  Advanced total: {adv_total:3d}")
    except ImportError:
        adv_total = 0
        print("\nAdvanced data: not available")

    grand = base_total + ext_total + adv_total
    print(f"\n{'=' * 40}")
    print(f"GRAND TOTAL: {grand} tasks")
    print(f"  Base:     {base_total}")
    print(f"  Extended: {ext_total}")
    print(f"  Advanced: {adv_total}")
    print(f"{'=' * 40}")

    # Adversarial breakdown
    from collections import Counter
    type_counts = Counter(t.adversarial_type.value for t in ADVERSARIAL_TASKS)
    print(f"\nAdversarial breakdown:")
    for t, c in sorted(type_counts.items()):
        print(f"  {t}: {c}")


def cmd_run(args):
    """Run evaluation on specified components."""
    model = args.model

    # Determine which components to run
    if args.all:
        components = COMPONENTS
    elif args.component:
        components = args.component
    else:
        print("Error: specify --all or -c <component>")
        sys.exit(1)

    # Check API key
    if "claude" in model.lower() and not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not set.")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
        if not args.dry_run:
            sys.exit(1)

    if "gpt" in model.lower() and not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not set.")
        print("  export OPENAI_API_KEY='your-key-here'")
        if not args.dry_run:
            sys.exit(1)

    print(f"\n{'#' * 60}")
    print(f"# BioEval Evaluation Suite")
    print(f"# Model: {model}")
    print(f"# Components: {', '.join(components)}")
    print(f"# Time: {datetime.now().isoformat()}")
    print(f"# Data tier: {args.data_tier}")
    if args.dry_run:
        print(f"# Mode: DRY RUN")
    print(f"{'#' * 60}")

    if args.dry_run:
        cmd_inventory(args)
        return

    # Run each component
    all_results = []
    total_start = time.time()

    for comp in components:
        comp_start = time.time()
        print(f"\n{'=' * 60}")
        print(f"Running: {comp}")
        print(f"{'=' * 60}")

        try:
            result = _run_component(comp, model, data_tier=args.data_tier)
            all_results.append(result)
            elapsed = time.time() - comp_start
            n_tasks = result.get("num_tasks", 0)
            n_completed = len([r for r in result.get("results", []) if "error" not in (r if isinstance(r, dict) else {})])
            print(f"  Completed: {n_completed}/{n_tasks} tasks ({elapsed:.1f}s)")
        except Exception as e:
            print(f"  ERROR: {e}")
            all_results.append({"component": comp, "error": str(e), "num_tasks": 0, "results": []})

    total_elapsed = time.time() - total_start

    # Aggregate and save
    summary = _aggregate(all_results)
    output_data = {
        "metadata": {
            "model": model,
            "components": components,
            "data_tier": args.data_tier,
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": round(total_elapsed, 1),
            "bioeval_version": "0.2.0",
        },
        "summary": summary,
        "results": all_results,
    }

    # Output path
    if args.output:
        output_path = args.output
    else:
        os.makedirs("results", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_safe = model.replace("/", "_").replace(":", "_")
        output_path = f"results/{model_safe}_{timestamp}.json"

    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2, default=str)

    print(f"\n{'=' * 60}")
    print("EVALUATION COMPLETE")
    print(f"{'=' * 60}")
    print(f"Time: {total_elapsed:.1f}s")
    print(f"Total tasks: {summary['total_tasks']}")
    for comp_name, stats in summary["by_component"].items():
        print(f"  {comp_name}: {stats['completed']}/{stats['num_tasks']} completed")
    print(f"\nResults saved to: {output_path}")


def _run_component(component: str, model: str, data_tier: str = "base") -> dict:
    """Run a single evaluation component."""
    if component == "protoreason":
        from bioeval.protoreason.evaluator import ProtoReasonEvaluator
        evaluator = ProtoReasonEvaluator(model)
        tasks = evaluator.load_tasks()
    elif component == "causalbio":
        from bioeval.causalbio.evaluator import CausalBioEvaluator
        evaluator = CausalBioEvaluator(model)
        tasks = evaluator.load_tasks()
    elif component == "designcheck":
        from bioeval.designcheck.evaluator import DesignCheckEvaluator
        evaluator = DesignCheckEvaluator(model)
        tasks = evaluator.load_tasks()
    elif component == "adversarial":
        from bioeval.adversarial.tasks import AdversarialEvaluator
        evaluator = AdversarialEvaluator(model)
        tasks = evaluator.load_tasks()
    elif component == "multiturn":
        from bioeval.multiturn.dialogues import MultiTurnEvaluator
        evaluator = MultiTurnEvaluator(model)
        tasks = evaluator.load_tasks()
    elif component == "calibration":
        from bioeval.scoring.calibration import CalibrationEvaluator
        evaluator = CalibrationEvaluator(model)
        tasks = evaluator.load_tasks()
    else:
        raise ValueError(f"Unknown component: {component}")

    print(f"  Loaded {len(tasks)} tasks")
    results = []
    for i, task in enumerate(tasks):
        task_id = task.id if hasattr(task, "id") else f"{component}_{i}"
        print(f"  [{i+1}/{len(tasks)}] {task_id}...", end=" ", flush=True)
        try:
            result = evaluator.evaluate_task(task)
            results.append(result.__dict__ if hasattr(result, "__dict__") else result)
            print("done")
        except Exception as e:
            print(f"error: {e}")
            results.append({"task_id": task_id, "error": str(e)})

    return {
        "component": component,
        "model": model,
        "num_tasks": len(tasks),
        "results": results,
    }


def _aggregate(all_results: list[dict]) -> dict:
    """Aggregate results across components."""
    summary = {"total_tasks": 0, "by_component": {}}
    for cr in all_results:
        comp = cr.get("component", "unknown")
        n = cr.get("num_tasks", 0)
        completed = len([
            r for r in cr.get("results", [])
            if not (isinstance(r, dict) and "error" in r)
        ])
        summary["total_tasks"] += n
        summary["by_component"][comp] = {"num_tasks": n, "completed": completed}
    return summary


def cmd_compare(args):
    """Compare two evaluation result files."""
    with open(args.baseline) as f:
        baseline = json.load(f)
    with open(args.enhanced) as f:
        enhanced = json.load(f)

    print(f"\n{'=' * 60}")
    print("BioEval Comparison")
    print(f"{'=' * 60}")
    print(f"Baseline: {args.baseline}")
    print(f"  Model: {baseline.get('metadata', {}).get('model', 'unknown')}")
    print(f"Enhanced: {args.enhanced}")
    print(f"  Model: {enhanced.get('metadata', {}).get('model', 'unknown')}")
    print()

    # Compare by component
    b_components = {r["component"]: r for r in baseline.get("results", [])}
    e_components = {r["component"]: r for r in enhanced.get("results", [])}

    all_components = sorted(set(list(b_components.keys()) + list(e_components.keys())))
    for comp in all_components:
        b = b_components.get(comp, {})
        e = e_components.get(comp, {})
        b_tasks = b.get("num_tasks", 0)
        e_tasks = e.get("num_tasks", 0)
        print(f"{comp}:")
        print(f"  Baseline: {b_tasks} tasks")
        print(f"  Enhanced: {e_tasks} tasks")
        print()

    print("(Detailed statistical comparison available after Phase 2)")


def cmd_demo(args):
    """Show pre-cached results without requiring API key."""
    results_dir = Path(__file__).parent.parent / "results"
    result_files = sorted(results_dir.glob("*.json")) if results_dir.exists() else []

    if not result_files:
        print("No cached results found in results/ directory.")
        print("Run 'bioeval run --all' first to generate results.")
        return

    print(f"\n{'=' * 60}")
    print("BioEval Demo Mode (Pre-cached Results)")
    print(f"{'=' * 60}")
    print(f"\nFound {len(result_files)} result file(s):")

    for f in result_files:
        with open(f) as fh:
            try:
                data = json.load(fh)
                meta = data.get("metadata", {})
                summary = data.get("summary", {})
                print(f"\n  {f.name}")
                print(f"    Model: {meta.get('model', 'unknown')}")
                print(f"    Date: {meta.get('timestamp', 'unknown')}")
                print(f"    Total tasks: {summary.get('total_tasks', 'unknown')}")
                for comp, stats in summary.get("by_component", {}).items():
                    print(f"      {comp}: {stats.get('completed', '?')}/{stats.get('num_tasks', '?')}")
            except json.JSONDecodeError:
                print(f"\n  {f.name} (invalid JSON)")

    print("\n(HTML dashboard available after Phase 3)")


def main():
    parser = argparse.ArgumentParser(
        prog="bioeval",
        description="BioEval: LLM Biology Evaluation Benchmark",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- run ---
    run_parser = subparsers.add_parser("run", help="Run evaluation")
    run_parser.add_argument("--model", "-m", default="claude-sonnet-4-20250514", help="Model to evaluate")
    run_parser.add_argument("--all", action="store_true", help="Run all components")
    run_parser.add_argument(
        "--component", "-c", nargs="+", choices=COMPONENTS,
        help="Specific component(s) to run",
    )
    run_parser.add_argument("--data-tier", choices=["base", "extended", "advanced", "all"], default="base",
                           help="Data tier to use (default: base)")
    run_parser.add_argument("--dry-run", action="store_true", help="Show task inventory, no API calls")
    run_parser.add_argument("--output", "-o", help="Output file path")

    # --- inventory ---
    subparsers.add_parser("inventory", help="Show complete task inventory")

    # --- compare ---
    compare_parser = subparsers.add_parser("compare", help="Compare two result files")
    compare_parser.add_argument("baseline", help="Baseline results JSON")
    compare_parser.add_argument("enhanced", help="Enhanced results JSON")

    # --- demo ---
    subparsers.add_parser("demo", help="Show pre-cached results (no API key needed)")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)
    elif args.command == "run":
        cmd_run(args)
    elif args.command == "inventory":
        cmd_inventory(args)
    elif args.command == "compare":
        cmd_compare(args)
    elif args.command == "demo":
        cmd_demo(args)


if __name__ == "__main__":
    main()
