#!/usr/bin/env python3
"""
BioEval: Run evaluation suite

Usage:
    python run_evaluation.py --model claude-sonnet-4-20250514 --component all
    python run_evaluation.py --model claude-sonnet-4-20250514 --component protoreason
    python run_evaluation.py --model gpt-4 --component causalbio --output results/gpt4_causalbio.json
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_protoreason(model_name: str) -> dict:
    """Run ProtoReason evaluation."""
    from bioeval.protoreason.evaluator import ProtoReasonEvaluator
    
    print(f"\n{'='*60}")
    print("Running ProtoReason: Protocol Procedural Reasoning")
    print(f"{'='*60}")
    
    evaluator = ProtoReasonEvaluator(model_name)
    tasks = evaluator.load_tasks()
    print(f"Loaded {len(tasks)} tasks")
    
    results = []
    for i, task in enumerate(tasks):
        print(f"  [{i+1}/{len(tasks)}] {task.id}...", end=" ")
        try:
            result = evaluator.evaluate_task(task)
            results.append(result)
            print("✓")
        except Exception as e:
            print(f"✗ Error: {e}")
            results.append({"task_id": task.id, "error": str(e)})
    
    return {
        "component": "protoreason",
        "model": model_name,
        "num_tasks": len(tasks),
        "results": [r.__dict__ if hasattr(r, '__dict__') else r for r in results]
    }


def run_causalbio(model_name: str) -> dict:
    """Run CausalBio evaluation."""
    from bioeval.causalbio.evaluator import CausalBioEvaluator
    
    print(f"\n{'='*60}")
    print("Running CausalBio: Causal Perturbation Prediction")
    print(f"{'='*60}")
    
    evaluator = CausalBioEvaluator(model_name)
    tasks = evaluator.load_tasks()
    print(f"Loaded {len(tasks)} tasks")
    
    results = []
    for i, task in enumerate(tasks):
        print(f"  [{i+1}/{len(tasks)}] {task.id}...", end=" ")
        try:
            result = evaluator.evaluate_task(task)
            results.append(result)
            print("✓")
        except Exception as e:
            print(f"✗ Error: {e}")
            results.append({"task_id": task.id, "error": str(e)})
    
    return {
        "component": "causalbio",
        "model": model_name,
        "num_tasks": len(tasks),
        "results": [r.__dict__ if hasattr(r, '__dict__') else r for r in results]
    }


def run_designcheck(model_name: str) -> dict:
    """Run DesignCheck evaluation."""
    from bioeval.designcheck.evaluator import DesignCheckEvaluator
    
    print(f"\n{'='*60}")
    print("Running DesignCheck: Experimental Design Critique")
    print(f"{'='*60}")
    
    evaluator = DesignCheckEvaluator(model_name)
    tasks = evaluator.load_tasks()
    print(f"Loaded {len(tasks)} tasks")
    
    results = []
    for i, task in enumerate(tasks):
        print(f"  [{i+1}/{len(tasks)}] {task.id}...", end=" ")
        try:
            result = evaluator.evaluate_task(task)
            results.append(result)
            print("✓")
        except Exception as e:
            print(f"✗ Error: {e}")
            results.append({"task_id": task.id, "error": str(e)})
    
    return {
        "component": "designcheck",
        "model": model_name,
        "num_tasks": len(tasks),
        "results": [r.__dict__ if hasattr(r, '__dict__') else r for r in results]
    }


def aggregate_results(all_results: list[dict]) -> dict:
    """Aggregate results across components."""
    summary = {
        "total_tasks": 0,
        "by_component": {}
    }
    
    for component_result in all_results:
        component = component_result["component"]
        num_tasks = component_result["num_tasks"]
        
        summary["total_tasks"] += num_tasks
        summary["by_component"][component] = {
            "num_tasks": num_tasks,
            "completed": len([r for r in component_result.get("results", []) 
                            if "error" not in r])
        }
    
    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Run BioEval evaluation suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Run all components with Claude:
    python run_evaluation.py --model claude-sonnet-4-20250514 --component all
    
  Run specific component:
    python run_evaluation.py --model claude-sonnet-4-20250514 --component protoreason
    
  Compare models:
    python run_evaluation.py --model claude-sonnet-4-20250514 --output results/claude.json
    python run_evaluation.py --model gpt-4 --output results/gpt4.json
        """
    )
    
    parser.add_argument(
        "--model", "-m",
        default="claude-sonnet-4-20250514",
        help="Model to evaluate (default: claude-sonnet-4-20250514)"
    )
    
    parser.add_argument(
        "--component", "-c",
        choices=["all", "protoreason", "causalbio", "designcheck"],
        default="all",
        help="Component to run (default: all)"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: results/<model>_<timestamp>.json)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Load tasks but don't run evaluation"
    )
    
    args = parser.parse_args()
    
    # Check for API key
    if "claude" in args.model.lower() and not os.environ.get("ANTHROPIC_API_KEY"):
        print("Warning: ANTHROPIC_API_KEY not set. Set it with:")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
        if not args.dry_run:
            sys.exit(1)
    
    print(f"\n{'#'*60}")
    print(f"# BioEval Evaluation Suite")
    print(f"# Model: {args.model}")
    print(f"# Component: {args.component}")
    print(f"# Time: {datetime.now().isoformat()}")
    print(f"{'#'*60}")
    
    if args.dry_run:
        print("\n[DRY RUN MODE - Loading tasks only]")
    
    # Run components
    all_results = []
    
    if args.component in ["all", "protoreason"]:
        if args.dry_run:
            from bioeval.protoreason.extended_data import get_task_statistics
            stats = get_task_statistics()
            total = stats['protocols'] * 3 + stats['calculation_tasks'] + stats['troubleshooting_tasks'] + stats['safety_tasks']
            print(f"\nProtoReason: ~{total} tasks available")
            print(f"  - {stats['protocols']} protocols ({stats['total_protocol_steps']} steps)")
            print(f"  - {stats['calculation_tasks']} calculation tasks")
            print(f"  - {stats['troubleshooting_tasks']} troubleshooting tasks")
            print(f"  - {stats['safety_tasks']} safety tasks")
        else:
            result = run_protoreason(args.model)
            all_results.append(result)
    
    if args.component in ["all", "causalbio"]:
        if args.dry_run:
            from bioeval.causalbio.extended_data import get_task_statistics
            stats = get_task_statistics()
            print(f"\nCausalBio: {stats['total_tasks']} tasks available")
            print(f"  - {stats['knockout_tasks']} knockout predictions")
            print(f"  - {stats['pathway_tasks']} pathway reasoning")
            print(f"  - {stats['drug_response_tasks']} drug response")
            print(f"  - {stats['epistasis_tasks']} epistasis tasks")
        else:
            result = run_causalbio(args.model)
            all_results.append(result)
    
    if args.component in ["all", "designcheck"]:
        if args.dry_run:
            from bioeval.designcheck.evaluator import get_task_statistics
            stats = get_task_statistics()
            print(f"\nDesignCheck: {stats['total_designs']} designs ({stats['total_flaws']} flaws)")
            print(f"  - By severity: {stats['flaws_by_severity']}")
            print(f"  - By category: {stats['flaws_by_category']}")
        else:
            result = run_designcheck(args.model)
            all_results.append(result)
    
    if args.dry_run:
        print("\n[DRY RUN COMPLETE]")
        return
    
    # Aggregate and save results
    summary = aggregate_results(all_results)
    
    output = {
        "metadata": {
            "model": args.model,
            "component": args.component,
            "timestamp": datetime.now().isoformat(),
            "bioeval_version": "0.1.0"
        },
        "summary": summary,
        "results": all_results
    }
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        os.makedirs("results", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_safe = args.model.replace("/", "_").replace(":", "_")
        output_path = f"results/{model_safe}_{timestamp}.json"
    
    # Save results
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\n{'='*60}")
    print("EVALUATION COMPLETE")
    print(f"{'='*60}")
    print(f"Total tasks: {summary['total_tasks']}")
    for component, stats in summary['by_component'].items():
        print(f"  {component}: {stats['completed']}/{stats['num_tasks']} completed")
    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
