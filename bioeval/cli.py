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


from bioeval.config import COMPONENTS


def cmd_inventory(args):
    """Show complete task inventory without making any API calls."""
    from bioeval.protoreason.evaluator import SAMPLE_PROTOCOLS, CALCULATION_TASKS, TROUBLESHOOTING_TASKS
    from bioeval.causalbio.evaluator import KNOCKOUT_TASKS, PATHWAY_TASKS, DRUG_RESPONSE_TASKS, EPISTASIS_TASKS
    from bioeval.designcheck.evaluator import FLAWED_DESIGNS
    from bioeval.adversarial.tasks import ADVERSARIAL_TASKS
    from bioeval.multiturn.dialogues import DIALOGUES
    from bioeval.scoring.calibration import CALIBRATION_TEST_TASKS
    from bioeval.biosafety.tasks import BIOSAFETY_TASKS
    from bioeval.datainterp.tasks import DATA_INTERP_TASKS
    from bioeval.debate.tasks import DEBATE_TASKS

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
    bs_base = len(BIOSAFETY_TASKS)
    di_base = len(DATA_INTERP_TASKS)
    debate_base = len(DEBATE_TASKS)

    print(f"\nBase tasks:")
    print(f"  ProtoReason:  {pr_base:3d}  ({len(SAMPLE_PROTOCOLS)} protocols x3 + {len(CALCULATION_TASKS)} calc + {len(TROUBLESHOOTING_TASKS)} troubleshoot)")
    print(f"  CausalBio:    {cb_base:3d}  ({len(KNOCKOUT_TASKS)} ko + {len(PATHWAY_TASKS)} path + {len(DRUG_RESPONSE_TASKS)} drug + {len(EPISTASIS_TASKS)} epi)")
    print(f"  DesignCheck:  {dc_base:3d}")
    print(f"  Adversarial:  {adv_base:3d}")
    print(f"  MultiTurn:    {mt_base:3d}")
    print(f"  Calibration:  {cal_base:3d}")
    print(f"  BioSafety:    {bs_base:3d}")
    print(f"  DataInterp:   {di_base:3d}")
    print(f"  Debate:       {debate_base:3d}")
    base_total = pr_base + cb_base + dc_base + adv_base + mt_base + cal_base + bs_base + di_base + debate_base
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

        # DesignCheck extended
        dc_ext = dc_base
        try:
            from bioeval.designcheck.extended_data import EXTENDED_FLAWED_DESIGNS
            dc_ext += len(EXTENDED_FLAWED_DESIGNS)
        except ImportError:
            pass

        # MultiTurn extended
        mt_ext = mt_base
        try:
            from bioeval.multiturn.extended_data import EXTENDED_DIALOGUES
            mt_ext += len(EXTENDED_DIALOGUES)
        except ImportError:
            pass

        ext_total = pr_ext + cb_ext + (dc_ext - dc_base) + (mt_ext - mt_base)
        print(f"\nExtended tasks (additions over base):")
        print(f"  ProtoReason:  {pr_ext:3d}")
        print(f"  CausalBio:    {cb_ext:3d}")
        print(f"  DesignCheck:  +{dc_ext - dc_base:2d}  (total {dc_ext})")
        print(f"  MultiTurn:    +{mt_ext - mt_base:2d}  (total {mt_ext})")
        print(f"  {'─' * 30}")
        print(f"  Extended additions: {ext_total:3d}")
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

    # Initialize LLM judge if requested
    judge = None
    if args.use_judge:
        from bioeval.scoring.llm_judge import LLMJudge
        judge_model = args.judge_model or "claude-sonnet-4-20250514"
        judge = LLMJudge(judge_model=judge_model)
        print(f"  LLM Judge enabled (model: {judge_model})")

    print(f"\n{'#' * 60}")
    print(f"# BioEval Evaluation Suite")
    print(f"# Model: {model}")
    print(f"# Components: {', '.join(components)}")
    print(f"# Time: {datetime.now().isoformat()}")
    print(f"# Data tier: {args.data_tier}")
    print(f"# Split: {args.split}")
    if args.runs > 1:
        print(f"# Runs: {args.runs}")
    if args.use_judge:
        print(f"# Judge: {args.judge_model or 'claude-sonnet-4-20250514'}")
    if args.dry_run:
        print(f"# Mode: DRY RUN")
    print(f"{'#' * 60}")

    if args.dry_run:
        cmd_inventory(args)
        return

    n_runs = max(1, args.runs)
    multi_run_results = []

    for run_idx in range(n_runs):
        if n_runs > 1:
            print(f"\n{'*' * 60}")
            print(f"RUN {run_idx + 1} / {n_runs}")
            print(f"{'*' * 60}")

        # Run each component
        all_results = []
        total_start = time.time()

        for comp in components:
            comp_start = time.time()
            print(f"\n{'=' * 60}")
            print(f"Running: {comp}")
            print(f"{'=' * 60}")

            try:
                _agent_models_str = getattr(args, 'agent_models', None)
                _agent_models = _agent_models_str.split(',') if _agent_models_str else None
                result = _run_component(
                    comp, model, data_tier=args.data_tier,
                    judge=judge, split=args.split,
                    debate_protocol=getattr(args, 'debate_protocol', 'simultaneous'),
                    debate_agents=getattr(args, 'debate_agents', 3),
                    debate_rounds=getattr(args, 'debate_rounds', 3),
                    agent_models=_agent_models,
                )
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
        run_data = {
            "metadata": {
                "model": model,
                "components": components,
                "data_tier": args.data_tier,
                "split": args.split,
                "run_index": run_idx,
                "n_runs": n_runs,
                "use_judge": args.use_judge,
                "judge_model": args.judge_model if args.use_judge else None,
                "timestamp": datetime.now().isoformat(),
                "elapsed_seconds": round(total_elapsed, 1),
                "bioeval_version": "0.3.0",
            },
            "summary": summary,
            "results": all_results,
        }
        multi_run_results.append(run_data)

    # Use last run's data as primary output; add multi-run aggregation if applicable
    output_data = multi_run_results[-1]
    if n_runs > 1:
        from bioeval.scoring.splits import aggregate_multi_run
        output_data["multi_run_aggregation"] = aggregate_multi_run(multi_run_results)

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

    summary = output_data["summary"]
    print(f"\n{'=' * 60}")
    print("EVALUATION COMPLETE")
    print(f"{'=' * 60}")
    print(f"Runs: {n_runs}")
    print(f"Total tasks: {summary['total_tasks']}")
    for comp_name, stats in summary["by_component"].items():
        print(f"  {comp_name}: {stats['completed']}/{stats['num_tasks']} completed")
    if n_runs > 1 and "multi_run_aggregation" in output_data:
        print(f"\nMulti-run aggregation:")
        for comp, agg in output_data["multi_run_aggregation"].get("by_component", {}).items():
            ci = agg.get("pass_rate_ci", {})
            print(f"  {comp}: mean={agg.get('mean_score', '?'):.4f} "
                  f"(std={agg.get('std_score', '?'):.4f}), "
                  f"pass_rate 95% CI: [{ci.get('lower', '?'):.3f}, {ci.get('upper', '?'):.3f}]")
    print(f"\nResults saved to: {output_path}")


def _run_component(component: str, model: str, data_tier: str = "base", judge=None, split: str = "all",
                    debate_protocol: str = "simultaneous", debate_agents: int = 3,
                    debate_rounds: int = 3, agent_models=None) -> dict:
    """Run a single evaluation component.

    Args:
        component: Component name (e.g., "protoreason", "causalbio")
        model: Model identifier
        data_tier: Which data tier to use ("base", "extended", "advanced", "all")
        judge: Optional LLMJudge instance for semantic evaluation
        split: Which test split to run ("all", "public", "private")
        debate_protocol: Debate protocol type (debate component only)
        debate_agents: Number of debate agents (debate component only)
        debate_rounds: Max debate rounds (debate component only)
        agent_models: List of model names for heterogeneous debate
    """
    if component == "protoreason":
        from bioeval.protoreason.evaluator import ProtoReasonEvaluator
        evaluator = ProtoReasonEvaluator(model)
        tasks = evaluator.load_tasks(data_tier=data_tier)
    elif component == "causalbio":
        from bioeval.causalbio.evaluator import CausalBioEvaluator
        evaluator = CausalBioEvaluator(model)
        tasks = evaluator.load_tasks(data_tier=data_tier)
    elif component == "designcheck":
        from bioeval.designcheck.evaluator import DesignCheckEvaluator
        evaluator = DesignCheckEvaluator(model)
        tasks = evaluator.load_tasks(data_tier=data_tier)
    elif component == "adversarial":
        from bioeval.adversarial.tasks import AdversarialEvaluator
        evaluator = AdversarialEvaluator(model)
        tasks = evaluator.load_tasks()
    elif component == "multiturn":
        from bioeval.multiturn.dialogues import MultiTurnEvaluator
        evaluator = MultiTurnEvaluator(model)
        tasks = evaluator.load_tasks(data_tier=data_tier)
    elif component == "calibration":
        from bioeval.scoring.calibration import CalibrationEvaluator
        evaluator = CalibrationEvaluator(model)
        tasks = evaluator.load_tasks()
    elif component == "biosafety":
        from bioeval.biosafety.tasks import BiosafetyEvaluator
        evaluator = BiosafetyEvaluator(model)
        tasks = evaluator.load_tasks()
    elif component == "datainterp":
        from bioeval.datainterp.tasks import DataInterpEvaluator
        evaluator = DataInterpEvaluator(model)
        tasks = evaluator.load_tasks()
    elif component == "debate":
        from bioeval.debate.evaluator import DebateEvaluator
        evaluator = DebateEvaluator(
            model_name=model,
            protocol=debate_protocol,
            num_agents=debate_agents,
            max_rounds=debate_rounds,
            agent_models=agent_models,
        )
        tasks = evaluator.load_tasks()
    else:
        raise ValueError(f"Unknown component: {component}")

    # Map task types to judge rubric types
    TASK_TYPE_TO_RUBRIC = {
        "knockout_prediction": "knockout_prediction",
        "pathway_reasoning": "pathway_reasoning",
        "epistasis": "epistasis",
        "drug_response": "knockout_prediction",  # closest rubric
        "step_ordering": "protocol_troubleshooting",
        "missing_step": "protocol_troubleshooting",
        "calculation": "calculation",
        "troubleshooting": "protocol_troubleshooting",
        "flaw_detection": "flaw_detection",
    }

    # Apply test split if requested
    if split and split != "all":
        from bioeval.scoring.splits import get_split
        filtered = []
        for t in tasks:
            tid = t.id if hasattr(t, "id") else (t.get("id") if isinstance(t, dict) else "")
            if get_split(str(tid)) == split:
                filtered.append(t)
        tasks = filtered

    print(f"  Loaded {len(tasks)} tasks")
    results = []
    for i, task in enumerate(tasks):
        task_id = task.id if hasattr(task, "id") else f"{component}_{i}"
        task_type = task.task_type if hasattr(task, "task_type") else "unknown"
        print(f"  [{i+1}/{len(tasks)}] {task_id}...", end=" ", flush=True)
        try:
            result = evaluator.evaluate_task(task)
            result_dict = result.__dict__ if hasattr(result, "__dict__") else result

            # Run LLM judge if enabled
            if judge and isinstance(result_dict, dict) and "response" in result_dict:
                rubric_type = TASK_TYPE_TO_RUBRIC.get(task_type, None)
                if rubric_type:
                    try:
                        judge_result = judge.evaluate(
                            task_id=task_id,
                            task_type=rubric_type,
                            task_prompt=task.prompt if hasattr(task, "prompt") else "",
                            model_response=result_dict["response"],
                            ground_truth=task.ground_truth if hasattr(task, "ground_truth") else {},
                        )
                        result_dict["judge_scores"] = {
                            "overall_score": judge_result.overall_score,
                            "dimension_scores": judge_result.dimension_scores,
                            "reasoning": judge_result.reasoning,
                            "strengths": judge_result.strengths,
                            "weaknesses": judge_result.weaknesses,
                            "critical_errors": judge_result.critical_errors,
                        }
                        print("done (+ judge)", end="")
                    except Exception as je:
                        result_dict["judge_scores"] = {"error": str(je)}
                        print(f"done (judge error: {je})", end="")
                else:
                    print("done (no rubric)", end="")
            else:
                print("done", end="")

            results.append(result_dict)
            print()
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
    run_parser.add_argument("--use-judge", action="store_true",
                           help="Enable LLM-as-Judge scoring alongside standard metrics")
    run_parser.add_argument("--judge-model", default=None,
                           help="Model for LLM judge (default: claude-sonnet-4-20250514)")
    run_parser.add_argument("--output", "-o", help="Output file path")
    run_parser.add_argument("--split", choices=["all", "public", "private"], default="all",
                           help="Which test split to run (default: all)")
    run_parser.add_argument("--runs", type=int, default=1,
                           help="Number of evaluation runs for multi-run aggregation")
    run_parser.add_argument("--debate-protocol",
        choices=["round_robin", "simultaneous", "judge_mediated"],
        default="simultaneous", help="Debate protocol (debate component only)")
    run_parser.add_argument("--debate-agents", type=int, default=3,
        help="Number of debate agents (debate component only)")
    run_parser.add_argument("--debate-rounds", type=int, default=3,
        help="Max debate rounds (debate component only)")
    run_parser.add_argument("--agent-models", type=str, default=None,
        help="Comma-separated model names for heterogeneous debate (e.g., claude-sonnet-4-20250514,gpt-4o)")

    # --- inventory ---
    subparsers.add_parser("inventory", help="Show complete task inventory")

    # --- compare ---
    compare_parser = subparsers.add_parser("compare", help="Compare two result files")
    compare_parser.add_argument("baseline", help="Baseline results JSON")
    compare_parser.add_argument("enhanced", help="Enhanced results JSON")

    # --- demo ---
    subparsers.add_parser("demo", help="Show pre-cached results (no API key needed)")

    # --- stats ---
    stats_parser = subparsers.add_parser("stats", help="Show benchmark statistics (NeurIPS)")
    stats_parser.add_argument("--data-tier", choices=["base", "extended", "all"], default="base",
                              help="Data tier to analyze")
    stats_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # --- datasheet ---
    ds_parser = subparsers.add_parser("datasheet", help="Show Datasheet for Datasets (Gebru et al.)")
    ds_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # --- analyze ---
    analyze_parser = subparsers.add_parser("analyze", help="Analyze evaluation results")
    analyze_parser.add_argument("result_file", help="Result JSON file to analyze")
    analyze_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # --- contamination ---
    contam_parser = subparsers.add_parser("contamination", help="Check for data contamination")
    contam_parser.add_argument("result_file", help="Result JSON file to check")

    # --- item-analysis ---
    ia_parser = subparsers.add_parser("item-analysis", help="Item difficulty & discrimination analysis")
    ia_parser.add_argument("result_files", nargs="+", help="One or more result JSON files")
    ia_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # --- ablation ---
    abl_parser = subparsers.add_parser("ablation", help="Scoring ablation analysis (synonym/stemming/boundary)")
    abl_parser.add_argument("result_file", help="Result JSON file to analyze")
    abl_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # --- dashboard ---
    dash_parser = subparsers.add_parser("dashboard", help="Generate HTML dashboard from results")
    dash_parser.add_argument("result_file", help="Result JSON file")
    dash_parser.add_argument("--output", "-o", help="Output HTML path (default: same name .html)")

    # --- validate ---
    val_parser = subparsers.add_parser("validate", help="Validate task data quality")
    val_parser.add_argument("--data-tier", choices=["base", "extended", "all"], default="base",
                            help="Data tier to validate")
    val_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # --- stability ---
    stab_parser = subparsers.add_parser("stability", help="Score stability analysis")
    stab_parser.add_argument("result_file", help="Result JSON file")
    stab_parser.add_argument("--perturbations", "-n", type=int, default=5,
                             help="Number of perturbations per task (default: 5)")
    stab_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # --- agreement ---
    agree_parser = subparsers.add_parser("agreement", help="Inter-rater agreement (auto vs judge)")
    agree_parser.add_argument("result_file", help="Result JSON file with judge_scores")
    agree_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # --- difficulty ---
    diff_parser = subparsers.add_parser("difficulty", help="Task difficulty analysis and rebalancing")
    diff_parser.add_argument("result_file", help="Result JSON file to analyze")
    diff_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # --- feedback ---
    fb_parser = subparsers.add_parser("feedback", help="Scoring quality feedback analysis")
    fb_parser.add_argument("result_file", help="Result JSON file to analyze")
    fb_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # --- reproducibility ---
    repro_parser = subparsers.add_parser("reproducibility", help="Verify scoring reproducibility")
    repro_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # --- simulate ---
    sim_parser = subparsers.add_parser("simulate", help="Run simulation with synthetic responses (no API)")
    sim_parser.add_argument("--quality", "-q", choices=["good", "bad", "mixed"], default="mixed",
                            help="Quality of synthetic responses (default: mixed)")
    sim_parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    sim_parser.add_argument("--output", "-o", help="Output file path")
    sim_parser.add_argument("--json", action="store_true", help="Output summary as JSON")

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
    elif args.command == "stats":
        from bioeval.reporting.statistics import compute_benchmark_statistics, print_statistics
        if args.json:
            stats = compute_benchmark_statistics(args.data_tier)
            print(json.dumps(stats, indent=2, default=str))
        else:
            print_statistics(args.data_tier)
    elif args.command == "datasheet":
        from bioeval.reporting.datasheet import generate_datasheet, print_datasheet
        if args.json:
            ds = generate_datasheet()
            print(json.dumps(ds, indent=2, default=str))
        else:
            print_datasheet()
    elif args.command == "analyze":
        from bioeval.reporting.analysis import analyze_results, print_analysis
        if args.json:
            analysis = analyze_results(args.result_file)
            print(json.dumps(analysis, indent=2, default=str))
        else:
            print_analysis(args.result_file)
    elif args.command == "contamination":
        from bioeval.reporting.analysis import detect_contamination
        result = detect_contamination(args.result_file)
        print(json.dumps(result, indent=2, default=str))
    elif args.command == "item-analysis":
        from bioeval.reporting.item_analysis import item_analysis, single_model_item_analysis, print_item_analysis
        if args.json:
            if len(args.result_files) == 1:
                analysis = single_model_item_analysis(args.result_files[0])
            else:
                analysis = item_analysis(args.result_files)
            print(json.dumps(analysis, indent=2, default=str))
        else:
            print_item_analysis(args.result_files)
    elif args.command == "ablation":
        from bioeval.reporting.ablation import run_ablation, print_ablation
        if args.json:
            result = run_ablation(args.result_file)
            print(json.dumps(result, indent=2, default=str))
        else:
            print_ablation(args.result_file)
    elif args.command == "dashboard":
        from bioeval.reporting.dashboard import generate_dashboard
        out = generate_dashboard(args.result_file, args.output)
        print(f"Dashboard generated: {out}")
    elif args.command == "validate":
        from bioeval.validation.task_checks import validate_all, validation_summary, print_validation
        if args.json:
            issues = validate_all(args.data_tier)
            summary = validation_summary(issues)
            summary["issues"] = [{"severity": i.severity, "component": i.component,
                                   "task_id": i.task_id, "field": i.field,
                                   "message": i.message} for i in issues]
            print(json.dumps(summary, indent=2))
        else:
            print_validation(args.data_tier)
    elif args.command == "stability":
        from bioeval.reporting.stability import measure_stability, print_stability
        if args.json:
            result = measure_stability(args.result_file, args.perturbations)
            # Remove per-task detail for JSON brevity
            result.pop("tasks", None)
            print(json.dumps(result, indent=2, default=str))
        else:
            print_stability(args.result_file, args.perturbations)
    elif args.command == "difficulty":
        from bioeval.reporting.difficulty import analyze_difficulty, print_difficulty
        if args.json:
            result = analyze_difficulty(args.result_file)
            print(json.dumps(result, indent=2, default=str))
        else:
            print_difficulty(args.result_file)
    elif args.command == "agreement":
        from bioeval.reporting.agreement import analyze_agreement, print_agreement
        if args.json:
            result = analyze_agreement(args.result_file)
            print(json.dumps(result, indent=2, default=str))
        else:
            print_agreement(args.result_file)
    elif args.command == "feedback":
        from bioeval.reporting.feedback import analyze_scoring_feedback, print_feedback
        if args.json:
            result = analyze_scoring_feedback(args.result_file)
            print(json.dumps(result, indent=2, default=str))
        else:
            print_feedback(args.result_file)
    elif args.command == "reproducibility":
        from bioeval.reporting.reproducibility import run_reproducibility_suite, print_reproducibility
        if args.json:
            suite = run_reproducibility_suite()
            print(json.dumps(suite, indent=2, default=str))
        else:
            print_reproducibility()
    elif args.command == "simulate":
        from bioeval.simulation import run_simulation, print_simulation_summary
        result = run_simulation(quality=args.quality, seed=args.seed)
        # Save result
        if args.output:
            output_path = args.output
        else:
            os.makedirs("results", exist_ok=True)
            output_path = f"results/synthetic_{args.quality}.json"
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2, default=str)
        if args.json:
            from bioeval.reporting.analysis import analyze_results
            analysis = analyze_results(output_path)
            print(json.dumps({"summary": analysis["overall"],
                              "by_component": analysis["by_component"],
                              "output_path": output_path}, indent=2, default=str))
        else:
            print_simulation_summary(result)
            print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
