#!/usr/bin/env python3
"""
BioEval Results Visualization

Quick visualization of evaluation results from the command line.

Usage:
    python visualize_results.py results/evaluation_results.json
    python visualize_results.py results/evaluation_results.json --output report.html
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def load_results(filepath: str) -> dict:
    """Load results from JSON file."""
    with open(filepath) as f:
        return json.load(f)


def print_summary(results: dict):
    """Print summary statistics to console."""
    print("\n" + "=" * 60)
    print("BIOEVAL RESULTS SUMMARY")
    print("=" * 60)
    
    # Metadata
    meta = results.get("metadata", {})
    print(f"\nModel: {meta.get('model', 'Unknown')}")
    print(f"Timestamp: {meta.get('timestamp', 'Unknown')}")
    print(f"Components: {', '.join(meta.get('components', []))}")
    
    # Summary stats
    summary = results.get("summary", {})
    print(f"\n--- Task Summary ---")
    print(f"Total tasks: {summary.get('total_tasks', 0)}")
    print(f"Completed: {summary.get('completed', 0)}")
    print(f"Errors: {summary.get('errors', 0)}")
    
    # Component breakdown
    print(f"\n--- By Component ---")
    for key, value in summary.items():
        if key.endswith("_tasks"):
            component = key.replace("_tasks", "")
            print(f"  {component}: {value}")
    
    # Calibration
    cal = results.get("calibration", {})
    if cal:
        print(f"\n--- Calibration Metrics ---")
        print(f"Expected Calibration Error: {cal.get('expected_calibration_error', 0):.3f}")
        print(f"Overconfidence Rate: {cal.get('overconfidence_rate', 0):.1%}")
        print(f"Underconfidence Rate: {cal.get('underconfidence_rate', 0):.1%}")
        print(f"Brier Score: {cal.get('brier_score', 0):.3f}")
        
        buckets = cal.get("bucket_accuracies", {})
        if buckets:
            print(f"\nAccuracy by confidence bucket:")
            for bucket, acc in buckets.items():
                count = cal.get("bucket_counts", {}).get(bucket, 0)
                print(f"  {bucket}: {acc:.1%} (n={count})")
    
    # Adversarial
    adv = results.get("adversarial_summary", {})
    if adv:
        print(f"\n--- Adversarial Robustness ---")
        print(f"Pass Rate: {adv.get('pass_rate', 0):.1%}")
        print(f"Passed: {adv.get('passed', 0)}/{adv.get('total', 0)}")
        
        by_type = adv.get("by_type", {})
        if by_type:
            print(f"\nBy adversarial type:")
            for atype, data in by_type.items():
                rate = data['passed'] / data['total'] if data['total'] > 0 else 0
                print(f"  {atype}: {rate:.0%} ({data['passed']}/{data['total']})")
    
    # Execution stats
    exec_stats = results.get("execution_stats", {})
    if exec_stats:
        print(f"\n--- Execution Stats ---")
        print(f"API calls: {exec_stats.get('api_calls', 0)}")
        print(f"Cache hits: {exec_stats.get('cache_hits', 0)}")
        print(f"Cache hit rate: {exec_stats.get('cache_hit_rate', 0):.1%}")
        print(f"Total tokens: {exec_stats.get('total_tokens', 0):,}")
    
    print("\n" + "=" * 60)


def generate_html_report(results: dict, output_path: str):
    """Generate HTML report with visualizations."""
    meta = results.get("metadata", {})
    summary = results.get("summary", {})
    cal = results.get("calibration", {})
    adv = results.get("adversarial_summary", {})
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>BioEval Results - {meta.get('model', 'Unknown')}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .card {{ background: white; border-radius: 8px; padding: 24px; margin-bottom: 24px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 2px solid #eee; padding-bottom: 8px; }}
        .metric {{ display: inline-block; margin: 16px; text-align: center; }}
        .metric-value {{ font-size: 32px; font-weight: bold; color: #2196F3; }}
        .metric-label {{ font-size: 14px; color: #666; }}
        .chart {{ height: 300px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #f9f9f9; }}
        .pass {{ color: #4CAF50; }}
        .fail {{ color: #f44336; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧬 BioEval Results</h1>
        
        <div class="card">
            <h2>Overview</h2>
            <p><strong>Model:</strong> {meta.get('model', 'Unknown')}</p>
            <p><strong>Date:</strong> {meta.get('timestamp', 'Unknown')[:19]}</p>
            <p><strong>Components:</strong> {', '.join(meta.get('components', []))}</p>
            
            <div style="display: flex; justify-content: space-around; margin-top: 24px;">
                <div class="metric">
                    <div class="metric-value">{summary.get('total_tasks', 0)}</div>
                    <div class="metric-label">Total Tasks</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{summary.get('completed', 0)}</div>
                    <div class="metric-label">Completed</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{cal.get('expected_calibration_error', 0):.3f}</div>
                    <div class="metric-label">ECE</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{adv.get('pass_rate', 0):.0%}</div>
                    <div class="metric-label">Adversarial Pass</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>Calibration</h2>
            <div id="calibration-chart" class="chart"></div>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Expected Calibration Error</td><td>{cal.get('expected_calibration_error', 0):.4f}</td></tr>
                <tr><td>Overconfidence Rate</td><td>{cal.get('overconfidence_rate', 0):.1%}</td></tr>
                <tr><td>Underconfidence Rate</td><td>{cal.get('underconfidence_rate', 0):.1%}</td></tr>
                <tr><td>Brier Score</td><td>{cal.get('brier_score', 0):.4f}</td></tr>
            </table>
        </div>
        
        <div class="card">
            <h2>Adversarial Robustness</h2>
            <div id="adversarial-chart" class="chart"></div>
        </div>
        
        <div class="card">
            <h2>Component Breakdown</h2>
            <div id="component-chart" class="chart"></div>
        </div>
    </div>
    
    <script>
        // Calibration chart
        var calBuckets = {json.dumps(list(cal.get('bucket_accuracies', {}).keys()))};
        var calAccuracies = {json.dumps(list(cal.get('bucket_accuracies', {}).values()))};
        var calCounts = {json.dumps(list(cal.get('bucket_counts', {}).values()))};
        
        Plotly.newPlot('calibration-chart', [{{
            x: calBuckets,
            y: calAccuracies,
            type: 'bar',
            text: calCounts.map(c => 'n=' + c),
            textposition: 'auto',
            marker: {{ color: ['#FFC107', '#2196F3', '#4CAF50'] }}
        }}], {{
            title: 'Accuracy by Confidence Bucket',
            yaxis: {{ title: 'Accuracy', range: [0, 1] }},
            xaxis: {{ title: 'Confidence Level' }}
        }});
        
        // Adversarial chart
        var advTypes = {json.dumps(list(adv.get('by_type', {}).keys()))};
        var advRates = {json.dumps([d['passed']/d['total'] if d['total'] > 0 else 0 for d in adv.get('by_type', {}).values()])};
        
        Plotly.newPlot('adversarial-chart', [{{
            x: advTypes,
            y: advRates,
            type: 'bar',
            marker: {{ color: advRates.map(r => r > 0.7 ? '#4CAF50' : r > 0.4 ? '#FFC107' : '#f44336') }}
        }}], {{
            title: 'Pass Rate by Adversarial Type',
            yaxis: {{ title: 'Pass Rate', range: [0, 1] }},
            xaxis: {{ title: 'Type', tickangle: -45 }}
        }});
        
        // Component chart
        var components = [];
        var taskCounts = [];
        {chr(10).join(f"components.push('{k.replace('_tasks', '')}'); taskCounts.push({v});" for k, v in summary.items() if k.endswith('_tasks'))}
        
        Plotly.newPlot('component-chart', [{{
            labels: components,
            values: taskCounts,
            type: 'pie',
            hole: 0.4
        }}], {{
            title: 'Tasks by Component'
        }});
    </script>
</body>
</html>"""
    
    with open(output_path, 'w') as f:
        f.write(html)
    
    print(f"HTML report saved to: {output_path}")


def analyze_errors(results: dict):
    """Analyze common error patterns."""
    task_results = results.get("results", [])
    
    print("\n--- Error Analysis ---")
    
    # Count task types with issues
    low_scores = {}
    for result in task_results:
        task_type = result.get("task_type", "unknown")
        
        # Check various score indicators
        conf = result.get("confidence", {})
        if conf.get("score", 0.5) > 0.8:
            # High confidence - check if correct
            if result.get("effect_mentioned") == False or result.get("passed") == False:
                low_scores[task_type] = low_scores.get(task_type, 0) + 1
    
    if low_scores:
        print("\nTask types with potential overconfidence:")
        for task_type, count in sorted(low_scores.items(), key=lambda x: -x[1]):
            print(f"  {task_type}: {count} issues")
    
    # Adversarial failures
    adv_failures = [r for r in task_results 
                    if r.get("component") == "adversarial" and not r.get("passed", True)]
    if adv_failures:
        print(f"\nAdversarial failures ({len(adv_failures)}):")
        for fail in adv_failures[:5]:
            print(f"  - {fail.get('task_id')}: {fail.get('failure_mode', 'unknown')}")


def main():
    parser = argparse.ArgumentParser(
        description="Visualize BioEval results",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("results_file", help="Path to results JSON file")
    parser.add_argument("--output", "-o", help="Output HTML report path")
    parser.add_argument("--analyze", "-a", action="store_true", help="Run error analysis")
    
    args = parser.parse_args()
    
    # Load results
    if not Path(args.results_file).exists():
        print(f"Error: File not found: {args.results_file}")
        sys.exit(1)
    
    results = load_results(args.results_file)
    
    # Print summary
    print_summary(results)
    
    # Error analysis
    if args.analyze:
        analyze_errors(results)
    
    # Generate HTML report
    if args.output:
        generate_html_report(results, args.output)
    else:
        # Default output path
        output_path = args.results_file.replace('.json', '_report.html')
        generate_html_report(results, output_path)


if __name__ == "__main__":
    main()
