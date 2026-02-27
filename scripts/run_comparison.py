#!/usr/bin/env python3
"""
BioEval Comparison Script

Automatically runs evaluation with and without prompt enhancements,
then generates a comparison report.

Usage:
    python scripts/run_comparison.py
    python scripts/run_comparison.py --components adversarial causalbio
    python scripts/run_comparison.py --model claude-sonnet-4-20250514
"""

import argparse
import json
import sys
import os
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import after path setup
import bioeval.config as config

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds


def run_evaluation(components: list[str], model: str, enhanced: bool, output_path: str) -> dict:
    """Run evaluation with specified settings."""

    # Dynamically set the enhancement flag
    original_setting = config.PROMPT_ENHANCEMENTS_ENABLED
    config.PROMPT_ENHANCEMENTS_ENABLED = enhanced

    print(f"\n{'='*60}")
    print(f"Running {'ENHANCED' if enhanced else 'BASELINE'} evaluation")
    print(f"{'='*60}")
    print(f"Components: {', '.join(components)}")
    print(f"Model: {model}")
    print(f"Enhancements: {'ON' if enhanced else 'OFF'}")
    print(f"Output: {output_path}")
    print()

    results = {
        "metadata": {
            "model": model,
            "timestamp": datetime.now().isoformat(),
            "components": components,
            "enhanced_prompts": enhanced,
        },
        "summary": {
            "total_tasks": 0,
            "completed": 0,
            "errors": 0,
        },
        "results": [],
        "adversarial_summary": {},
        "calibration": {},
    }

    try:
        # Import evaluators (reimport to pick up config changes)
        if "adversarial" in components or "all" in components:
            # Force reimport to get updated config
            import importlib
            import bioeval.adversarial.tasks as adv_module

            importlib.reload(adv_module)
            from bioeval.adversarial.tasks import AdversarialEvaluator, ADVERSARIAL_TASKS, score_adversarial_response

            print("Running Adversarial evaluation...")
            adv_eval = AdversarialEvaluator(model_name=model, use_enhanced_prompts=enhanced)

            # Run with retry logic for each task
            adv_task_results = []
            for task in ADVERSARIAL_TASKS:
                for attempt in range(MAX_RETRIES):
                    try:
                        result = adv_eval.evaluate_task(task)
                        adv_task_results.append(result)
                        print(f"    Task {task.id}: {'PASS' if result['passed'] else 'FAIL'}")
                        break
                    except Exception as e:
                        if attempt < MAX_RETRIES - 1:
                            print(f"    Task {task.id}: Retry {attempt + 1}/{MAX_RETRIES} after error: {str(e)[:50]}...")
                            time.sleep(RETRY_DELAY * (attempt + 1))
                        else:
                            print(f"    Task {task.id}: FAILED after {MAX_RETRIES} retries")
                            adv_task_results.append(
                                {
                                    "task_id": task.id,
                                    "adversarial_type": task.adversarial_type.value,
                                    "passed": False,
                                    "failure_mode": f"API Error: {str(e)[:100]}",
                                    "error": True,
                                }
                            )

            # Aggregate adversarial results
            passed = sum(1 for r in adv_task_results if r.get("passed", False))
            by_type = {}
            for r in adv_task_results:
                t = r.get("adversarial_type", "unknown")
                if t not in by_type:
                    by_type[t] = {"passed": 0, "total": 0}
                by_type[t]["total"] += 1
                if r.get("passed", False):
                    by_type[t]["passed"] += 1

            adv_results = {
                "total_tasks": len(adv_task_results),
                "passed": passed,
                "pass_rate": passed / len(adv_task_results) if adv_task_results else 0,
                "by_type": {k: v["passed"] / v["total"] if v["total"] > 0 else 0 for k, v in by_type.items()},
                "results": adv_task_results,
            }

            results["adversarial_summary"] = {
                "total": adv_results["total_tasks"],
                "passed": adv_results["passed"],
                "pass_rate": adv_results["pass_rate"],
                "by_type": adv_results["by_type"],
            }
            results["summary"]["total_tasks"] += adv_results["total_tasks"]
            results["summary"]["completed"] += adv_results["total_tasks"]

            # Add individual results
            for r in adv_results["results"]:
                results["results"].append(
                    {
                        "component": "adversarial",
                        "task_id": r["task_id"],
                        "adversarial_type": r["adversarial_type"],
                        "passed": r["passed"],
                        "failure_mode": r.get("failure_mode"),
                        "enhanced_prompt_used": r.get("enhanced_prompt_used", enhanced),
                    }
                )

            print(f"  Adversarial pass rate: {adv_results['pass_rate']:.1%}")

        if "causalbio" in components or "all" in components:
            import importlib
            import bioeval.causalbio.evaluator as causal_module

            importlib.reload(causal_module)
            from bioeval.causalbio.evaluator import CausalBioEvaluator

            print("Running CausalBio evaluation...")
            causal_eval = CausalBioEvaluator(model_name=model, use_enhanced_prompts=enhanced)
            tasks = causal_eval.load_tasks()

            # Run with retry logic for each task
            causal_results = []
            for task in tasks:
                for attempt in range(MAX_RETRIES):
                    try:
                        result = causal_eval.evaluate_task(task)
                        causal_results.append(result)
                        print(f"    Task {task.id}: completed")
                        break
                    except Exception as e:
                        if attempt < MAX_RETRIES - 1:
                            print(f"    Task {task.id}: Retry {attempt + 1}/{MAX_RETRIES} after error: {str(e)[:50]}...")
                            time.sleep(RETRY_DELAY * (attempt + 1))
                        else:
                            print(f"    Task {task.id}: FAILED after {MAX_RETRIES} retries")
                            results["summary"]["errors"] += 1

            results["summary"]["total_tasks"] += len(causal_results)
            results["summary"]["completed"] += len(causal_results)

            for r in causal_results:
                results["results"].append(
                    {
                        "component": "causalbio",
                        "task_id": r.task_id,
                        "task_type": r.scores.get("task_type", "unknown") if hasattr(r, "scores") else "unknown",
                        "scores": r.scores if hasattr(r, "scores") else {},
                        "enhanced_prompt_used": enhanced,
                    }
                )

            print(f"  CausalBio tasks completed: {len(causal_results)}")

        # Save results
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\nResults saved to: {output_path}")

    finally:
        # Restore original setting
        config.PROMPT_ENHANCEMENTS_ENABLED = original_setting

    return results


def compare_results(enhanced_results: dict, baseline_results: dict) -> dict:
    """Compare enhanced vs baseline results."""

    comparison = {
        "timestamp": datetime.now().isoformat(),
        "enhanced": {
            "total_tasks": enhanced_results["summary"]["total_tasks"],
        },
        "baseline": {
            "total_tasks": baseline_results["summary"]["total_tasks"],
        },
        "improvements": [],
        "regressions": [],
    }

    # Compare adversarial results
    if enhanced_results.get("adversarial_summary") and baseline_results.get("adversarial_summary"):
        enh_adv = enhanced_results["adversarial_summary"]
        base_adv = baseline_results["adversarial_summary"]

        comparison["adversarial"] = {
            "enhanced_pass_rate": enh_adv.get("pass_rate", 0),
            "baseline_pass_rate": base_adv.get("pass_rate", 0),
            "improvement": enh_adv.get("pass_rate", 0) - base_adv.get("pass_rate", 0),
        }

        # Compare by type
        comparison["adversarial"]["by_type"] = {}
        all_types = set(enh_adv.get("by_type", {}).keys()) | set(base_adv.get("by_type", {}).keys())

        for adv_type in all_types:
            enh_rate = enh_adv.get("by_type", {}).get(adv_type, 0)
            base_rate = base_adv.get("by_type", {}).get(adv_type, 0)
            diff = enh_rate - base_rate

            comparison["adversarial"]["by_type"][adv_type] = {
                "enhanced": enh_rate,
                "baseline": base_rate,
                "improvement": diff,
            }

            if diff > 0:
                comparison["improvements"].append(f"{adv_type}: +{diff:.0%}")
            elif diff < 0:
                comparison["regressions"].append(f"{adv_type}: {diff:.0%}")

    return comparison


def print_comparison_report(comparison: dict):
    """Print a formatted comparison report."""

    print("\n" + "=" * 70)
    print("COMPARISON REPORT: Enhanced vs Baseline")
    print("=" * 70)

    if "adversarial" in comparison:
        adv = comparison["adversarial"]
        print("\n--- Adversarial Robustness ---")
        print(f"  Enhanced pass rate:  {adv['enhanced_pass_rate']:.1%}")
        print(f"  Baseline pass rate:  {adv['baseline_pass_rate']:.1%}")

        improvement = adv["improvement"]
        if improvement > 0:
            print(f"  Improvement:         +{improvement:.1%} ✓")
        elif improvement < 0:
            print(f"  Regression:          {improvement:.1%} ✗")
        else:
            print(f"  Change:              No change")

        print("\n  By adversarial type:")
        for adv_type, data in adv.get("by_type", {}).items():
            diff = data["improvement"]
            symbol = "✓" if diff > 0 else ("✗" if diff < 0 else "=")
            print(f"    {adv_type:25} {data['baseline']:.0%} → {data['enhanced']:.0%} ({diff:+.0%}) {symbol}")

    if comparison.get("improvements"):
        print("\n--- Improvements ---")
        for imp in comparison["improvements"]:
            print(f"  ✓ {imp}")

    if comparison.get("regressions"):
        print("\n--- Regressions ---")
        for reg in comparison["regressions"]:
            print(f"  ✗ {reg}")

    print("\n" + "=" * 70)


def generate_html_report(comparison: dict, enhanced_results: dict, baseline_results: dict, output_path: str):
    """Generate an HTML comparison report."""

    adv = comparison.get("adversarial", {})

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>BioEval Comparison Report</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .card {{ background: white; border-radius: 8px; padding: 24px; margin-bottom: 24px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 2px solid #eee; padding-bottom: 8px; }}
        .metric {{ display: inline-block; margin: 16px 32px 16px 0; text-align: center; }}
        .metric-value {{ font-size: 36px; font-weight: bold; }}
        .metric-label {{ font-size: 14px; color: #666; }}
        .improved {{ color: #4CAF50; }}
        .regressed {{ color: #f44336; }}
        .neutral {{ color: #9E9E9E; }}
        .chart {{ height: 400px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #f9f9f9; }}
        .badge {{ padding: 4px 8px; border-radius: 4px; font-size: 12px; }}
        .badge-improved {{ background: #E8F5E9; color: #2E7D32; }}
        .badge-regressed {{ background: #FFEBEE; color: #C62828; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>BioEval Comparison Report</h1>
        <p>Generated: {comparison['timestamp']}</p>

        <div class="card">
            <h2>Overall Results</h2>
            <div class="metric">
                <div class="metric-value">{adv.get('baseline_pass_rate', 0):.0%}</div>
                <div class="metric-label">Baseline Pass Rate</div>
            </div>
            <div class="metric">
                <div class="metric-value">{adv.get('enhanced_pass_rate', 0):.0%}</div>
                <div class="metric-label">Enhanced Pass Rate</div>
            </div>
            <div class="metric">
                <div class="metric-value {'improved' if adv.get('improvement', 0) > 0 else 'regressed' if adv.get('improvement', 0) < 0 else 'neutral'}">{adv.get('improvement', 0):+.0%}</div>
                <div class="metric-label">Improvement</div>
            </div>
        </div>

        <div class="card">
            <h2>Adversarial Robustness by Type</h2>
            <div id="comparison-chart" class="chart"></div>
            <table>
                <tr><th>Type</th><th>Baseline</th><th>Enhanced</th><th>Change</th></tr>
"""

    for adv_type, data in adv.get("by_type", {}).items():
        diff = data["improvement"]
        badge_class = "badge-improved" if diff > 0 else "badge-regressed" if diff < 0 else ""
        badge_text = f"+{diff:.0%}" if diff > 0 else f"{diff:.0%}"
        html += f"""                <tr>
                    <td>{adv_type}</td>
                    <td>{data['baseline']:.0%}</td>
                    <td>{data['enhanced']:.0%}</td>
                    <td><span class="badge {badge_class}">{badge_text}</span></td>
                </tr>
"""

    # Prepare chart data
    types = list(adv.get("by_type", {}).keys())
    baseline_vals = [adv["by_type"][t]["baseline"] for t in types]
    enhanced_vals = [adv["by_type"][t]["enhanced"] for t in types]

    html += f"""            </table>
        </div>

        <div class="card">
            <h2>Summary</h2>
            <h3>Improvements ({len(comparison.get('improvements', []))})</h3>
            <ul>
"""
    for imp in comparison.get("improvements", []):
        html += f"                <li class='improved'>{imp}</li>\n"

    html += """            </ul>
            <h3>Regressions</h3>
            <ul>
"""
    for reg in comparison.get("regressions", []):
        html += f"                <li class='regressed'>{reg}</li>\n"

    html += f"""            </ul>
        </div>
    </div>

    <script>
        var types = {json.dumps(types)};
        var baseline = {json.dumps(baseline_vals)};
        var enhanced = {json.dumps(enhanced_vals)};

        Plotly.newPlot('comparison-chart', [
            {{
                x: types,
                y: baseline,
                name: 'Baseline',
                type: 'bar',
                marker: {{ color: '#9E9E9E' }}
            }},
            {{
                x: types,
                y: enhanced,
                name: 'Enhanced',
                type: 'bar',
                marker: {{ color: '#2196F3' }}
            }}
        ], {{
            title: 'Pass Rate by Adversarial Type',
            yaxis: {{ title: 'Pass Rate', range: [0, 1], tickformat: '.0%' }},
            xaxis: {{ tickangle: -45 }},
            barmode: 'group'
        }});
    </script>
</body>
</html>"""

    with open(output_path, "w") as f:
        f.write(html)

    print(f"HTML report saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Run comparison between enhanced and baseline BioEval",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--components",
        "-c",
        nargs="+",
        default=["adversarial", "causalbio"],
        help="Components to evaluate (default: adversarial causalbio)",
    )
    parser.add_argument(
        "--model", "-m", default="claude-sonnet-4-20250514", help="Model to use (default: claude-sonnet-4-20250514)"
    )
    parser.add_argument("--output-dir", "-o", default="results", help="Output directory for results (default: results)")
    parser.add_argument("--skip-baseline", action="store_true", help="Skip baseline run (use existing baseline results)")
    parser.add_argument("--skip-enhanced", action="store_true", help="Skip enhanced run (use existing enhanced results)")

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # File paths
    enhanced_path = output_dir / f"enhanced_{timestamp}.json"
    baseline_path = output_dir / f"baseline_{timestamp}.json"
    comparison_path = output_dir / f"comparison_{timestamp}.json"
    report_path = output_dir / f"comparison_report_{timestamp}.html"

    print("=" * 70)
    print("BioEval Comparison: Enhanced vs Baseline Prompts")
    print("=" * 70)
    print(f"Model: {args.model}")
    print(f"Components: {', '.join(args.components)}")
    print(f"Output directory: {output_dir}")

    # Run enhanced evaluation
    if not args.skip_enhanced:
        enhanced_results = run_evaluation(
            components=args.components, model=args.model, enhanced=True, output_path=str(enhanced_path)
        )
    else:
        # Load existing results
        existing = list(output_dir.glob("enhanced_*.json"))
        if existing:
            with open(sorted(existing)[-1]) as f:
                enhanced_results = json.load(f)
            print(f"Using existing enhanced results: {sorted(existing)[-1]}")
        else:
            print("ERROR: No existing enhanced results found")
            sys.exit(1)

    # Run baseline evaluation
    if not args.skip_baseline:
        baseline_results = run_evaluation(
            components=args.components, model=args.model, enhanced=False, output_path=str(baseline_path)
        )
    else:
        existing = list(output_dir.glob("baseline_*.json"))
        if existing:
            with open(sorted(existing)[-1]) as f:
                baseline_results = json.load(f)
            print(f"Using existing baseline results: {sorted(existing)[-1]}")
        else:
            print("ERROR: No existing baseline results found")
            sys.exit(1)

    # Compare results
    print("\nComparing results...")
    comparison = compare_results(enhanced_results, baseline_results)

    # Save comparison
    with open(comparison_path, "w") as f:
        json.dump(comparison, f, indent=2)

    # Print report
    print_comparison_report(comparison)

    # Generate HTML report
    generate_html_report(comparison, enhanced_results, baseline_results, str(report_path))

    print(f"\nAll results saved to: {output_dir}/")
    print(f"  - Enhanced: {enhanced_path.name}")
    print(f"  - Baseline: {baseline_path.name}")
    print(f"  - Comparison: {comparison_path.name}")
    print(f"  - HTML Report: {report_path.name}")


if __name__ == "__main__":
    main()
