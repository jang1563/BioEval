"""
Self-contained HTML dashboard generator for BioEval results.

Generates a single HTML file with inline CSS/JS (no external dependencies)
that visualizes evaluation results including:
- Overall score summary cards
- Per-component bar chart
- Score distribution histogram
- Calibration reliability diagram
- Task-level detail table
- Contamination check panel
- Ablation comparison (if available)
"""

import json
import html as html_mod
from pathlib import Path

from bioeval.reporting.analysis import analyze_results, detect_contamination
from bioeval.version import __version__


def generate_dashboard(result_path: str, output_path: str | None = None) -> str:
    """Generate an HTML dashboard from evaluation results.

    Args:
        result_path: Path to the evaluation result JSON file.
        output_path: Where to save the HTML. If None, uses result_path with .html suffix.

    Returns:
        Path to the generated HTML file.
    """
    analysis = analyze_results(result_path)
    contam = detect_contamination(result_path)

    # Load raw data for task-level detail
    with open(result_path) as f:
        raw_data = json.load(f)

    if output_path is None:
        output_path = str(Path(result_path).with_suffix(".html"))

    html = _render_html(analysis, contam, raw_data)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path


def _render_html(analysis: dict, contam: dict, raw_data: dict) -> str:
    """Render the full HTML dashboard."""
    meta = analysis.get("metadata", {})
    overall = analysis.get("overall", {})
    by_comp = analysis.get("by_component", {})
    cal_analysis = analysis.get("calibration_analysis", {})

    model_name = html_mod.escape(str(meta.get("model", "Unknown")))
    data_tier = html_mod.escape(str(meta.get("data_tier", "base")))
    timestamp = html_mod.escape(str(meta.get("timestamp", "")))

    # Component data for charts
    comp_names = sorted(by_comp.keys())
    comp_means = [by_comp[c].get("mean", 0) for c in comp_names]
    comp_pass_rates = [by_comp[c].get("pass_rate", 0) for c in comp_names]
    comp_ns = [by_comp[c].get("n", 0) for c in comp_names]

    # Score distribution bins
    all_scores_json = json.dumps(_collect_all_scores(raw_data, analysis))

    # Calibration bins
    cal_bins_json = json.dumps(cal_analysis.get("bins", []))

    # Task-level rows
    task_rows = _build_task_rows(raw_data, analysis)
    task_rows_json = json.dumps(task_rows)

    # Contamination
    contam_json = json.dumps(contam)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BioEval Dashboard - {model_name}</title>
<style>
{_CSS}
</style>
</head>
<body>
<div class="container">

<!-- Header -->
<header>
    <h1>BioEval Dashboard</h1>
    <div class="meta-bar">
        <span class="meta-item"><b>Model:</b> {model_name}</span>
        <span class="meta-item"><b>Tier:</b> {data_tier}</span>
        <span class="meta-item"><b>Date:</b> {timestamp}</span>
        <span class="meta-item"><b>Tasks:</b> {overall.get('n', 0)}</span>
    </div>
</header>

<!-- Summary Cards -->
<section class="cards">
    <div class="card">
        <div class="card-label">Overall Mean</div>
        <div class="card-value" id="overall-mean">{overall.get('mean', 0):.3f}</div>
        <div class="card-sub">std: {overall.get('std', 0):.3f}</div>
    </div>
    <div class="card">
        <div class="card-label">Pass Rate</div>
        <div class="card-value">{overall.get('pass_rate', 0):.1%}</div>
        <div class="card-sub">{overall.get('n_passed', 0)}/{overall.get('n', 0)} passed</div>
    </div>
    <div class="card">
        <div class="card-label">Median</div>
        <div class="card-value">{overall.get('median', 0):.3f}</div>
        <div class="card-sub">IQR: [{overall.get('p25', 0):.2f}, {overall.get('p75', 0):.2f}]</div>
    </div>
    <div class="card">
        <div class="card-label">Range</div>
        <div class="card-value">{overall.get('min', 0):.2f} - {overall.get('max', 0):.2f}</div>
        <div class="card-sub">{len(comp_names)} components</div>
    </div>
</section>

<!-- Component Bar Chart -->
<section class="panel">
    <h2>Per-Component Scores</h2>
    <div class="chart-container" id="comp-chart"></div>
    <table class="data-table" id="comp-table">
        <thead>
            <tr><th>Component</th><th>N</th><th>Mean</th><th>Std</th><th>Pass Rate</th><th>Median</th></tr>
        </thead>
        <tbody id="comp-tbody"></tbody>
    </table>
</section>

<!-- Score Distribution -->
<section class="panel">
    <h2>Score Distribution</h2>
    <div class="chart-container" id="dist-chart"></div>
</section>

<!-- Calibration -->
<section class="panel" id="cal-section" style="display:none;">
    <h2>Calibration Analysis</h2>
    <div class="cards" style="margin-bottom:1rem;">
        <div class="card card-sm">
            <div class="card-label">ECE</div>
            <div class="card-value">{cal_analysis.get('ece', 0):.4f}</div>
        </div>
        <div class="card card-sm">
            <div class="card-label">MCE</div>
            <div class="card-value">{cal_analysis.get('mce', 0):.4f}</div>
        </div>
        <div class="card card-sm">
            <div class="card-label">Overconfidence</div>
            <div class="card-value">{cal_analysis.get('overconfidence_rate', 0):.1%}</div>
        </div>
        <div class="card card-sm">
            <div class="card-label">Underconfidence</div>
            <div class="card-value">{cal_analysis.get('underconfidence_rate', 0):.1%}</div>
        </div>
    </div>
    <div class="chart-container" id="cal-chart"></div>
</section>

<!-- Contamination Check -->
<section class="panel" id="contam-section" style="display:none;">
    <h2>Contamination Check</h2>
    <div id="contam-content"></div>
</section>

<!-- Task Detail Table -->
<section class="panel">
    <h2>Task Details</h2>
    <div class="controls">
        <input type="text" id="task-search" placeholder="Filter by task ID or component..." oninput="filterTasks()">
        <select id="comp-filter" onchange="filterTasks()">
            <option value="">All Components</option>
            {''.join(f'<option value="{c}">{c}</option>' for c in comp_names)}
        </select>
    </div>
    <table class="data-table" id="task-table">
        <thead>
            <tr>
                <th onclick="sortTable('task_id')">Task ID</th>
                <th onclick="sortTable('component')">Component</th>
                <th onclick="sortTable('task_type')">Type</th>
                <th onclick="sortTable('score')">Score</th>
                <th onclick="sortTable('passed')">Passed</th>
            </tr>
        </thead>
        <tbody id="task-tbody"></tbody>
    </table>
    <div class="table-info" id="table-info"></div>
</section>

<footer>
    Generated by BioEval v{__version__}
</footer>

</div>

<script>
// ── Data ──
const compNames = {json.dumps(comp_names)};
const compMeans = {json.dumps(comp_means)};
const compPassRates = {json.dumps(comp_pass_rates)};
const compNs = {json.dumps(comp_ns)};
const byComp = {json.dumps(by_comp, default=str)};
const allScores = {all_scores_json};
const calBins = {cal_bins_json};
const taskRows = {task_rows_json};
const contam = {contam_json};

{_JS}
</script>
</body>
</html>"""


def _collect_all_scores(raw_data: dict, analysis: dict) -> list[float]:
    """Collect all normalized scores for the distribution chart."""
    from bioeval.reporting.analysis import load_and_normalize
    # We'll reconstruct from analysis by_component
    scores = []
    for comp, comp_data in analysis.get("by_component", {}).items():
        # We don't have individual scores in analysis, so estimate from raw data
        pass

    # Fallback: extract from raw results
    for comp_result in raw_data.get("results", []):
        for r in comp_result.get("results", []):
            if isinstance(r, dict):
                s = r.get("score", r.get("f1", r.get("overall_score")))
                if s is not None:
                    try:
                        scores.append(float(s))
                    except (ValueError, TypeError):
                        pass
                elif "calibration_error" in r:
                    scores.append(max(0, min(1, 1.0 - r["calibration_error"])))
    return scores


def _build_task_rows(raw_data: dict, analysis: dict) -> list[dict]:
    """Build task-level rows for the detail table."""
    rows = []
    for comp_result in raw_data.get("results", []):
        component = comp_result.get("component", "unknown")
        for r in comp_result.get("results", []):
            if not isinstance(r, dict):
                continue
            tid = r.get("task_id", r.get("dialogue_id", ""))
            task_type = r.get("task_type", r.get("adversarial_type",
                        r.get("details", {}).get("correct_behavior", "")))

            # Score
            score = r.get("score")
            if isinstance(r.get("scores"), dict):
                score = r["scores"].get("score", score)
            if score is None:
                if "calibration_error" in r:
                    score = max(0, min(1, 1.0 - r["calibration_error"]))
                elif "f1" in r:
                    score = r["f1"]
                elif "overall_score" in r:
                    score = r["overall_score"]
                else:
                    score = 0

            passed = r.get("passed", score >= 0.5 if score is not None else False)

            rows.append({
                "task_id": str(tid),
                "component": component,
                "task_type": str(task_type),
                "score": round(float(score), 4) if score is not None else 0,
                "passed": bool(passed),
            })
    return rows


# =============================================================================
# INLINE CSS
# =============================================================================

_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    background: #f5f6f8; color: #1a1a2e; line-height: 1.5;
}
.container { max-width: 1100px; margin: 0 auto; padding: 1.5rem; }
header { margin-bottom: 2rem; }
header h1 { font-size: 1.6rem; font-weight: 700; color: #1a1a2e; }
.meta-bar { display: flex; gap: 1.5rem; flex-wrap: wrap; margin-top: 0.5rem; font-size: 0.85rem; color: #555; }

.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
.card {
    background: #fff; border-radius: 10px; padding: 1.2rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08); text-align: center;
}
.card-sm { padding: 0.8rem; }
.card-label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #888; margin-bottom: 0.3rem; }
.card-value { font-size: 1.5rem; font-weight: 700; color: #1a1a2e; }
.card-sm .card-value { font-size: 1.1rem; }
.card-sub { font-size: 0.75rem; color: #999; margin-top: 0.2rem; }

.panel {
    background: #fff; border-radius: 10px; padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08); margin-bottom: 1.5rem;
}
.panel h2 { font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem; color: #333; }

.chart-container { width: 100%; min-height: 200px; margin-bottom: 1rem; }

/* Bar chart (CSS-only) */
.bar-chart { display: flex; align-items: flex-end; gap: 6px; height: 200px; padding: 0 0.5rem; }
.bar-group { flex: 1; display: flex; flex-direction: column; align-items: center; height: 100%; justify-content: flex-end; }
.bar {
    width: 100%; min-width: 30px; max-width: 80px; border-radius: 4px 4px 0 0;
    transition: height 0.4s ease;
    position: relative;
}
.bar:hover { opacity: 0.85; }
.bar-label { font-size: 0.65rem; color: #666; margin-top: 4px; text-align: center; word-break: break-all; }
.bar-value { font-size: 0.65rem; color: #333; font-weight: 600; margin-bottom: 2px; text-align: center; }

/* Histogram */
.histogram { display: flex; align-items: flex-end; gap: 2px; height: 160px; }
.hist-bar {
    flex: 1; background: #6366f1; border-radius: 2px 2px 0 0; min-width: 8px;
    transition: height 0.3s ease; position: relative;
}
.hist-bar:hover { background: #4f46e5; }
.hist-bar .tooltip {
    display: none; position: absolute; bottom: 100%; left: 50%; transform: translateX(-50%);
    background: #333; color: #fff; padding: 2px 6px; border-radius: 3px; font-size: 0.65rem;
    white-space: nowrap;
}
.hist-bar:hover .tooltip { display: block; }

/* Calibration diagram */
.cal-diagram { display: flex; align-items: flex-end; gap: 4px; height: 180px; position: relative; }
.cal-bar-group { flex: 1; display: flex; flex-direction: column; align-items: center; height: 100%; justify-content: flex-end; }
.cal-bar {
    width: 80%; border-radius: 3px 3px 0 0; position: relative;
}
.cal-conf { background: #93c5fd; }
.cal-acc { background: #6366f1; }
.cal-label { font-size: 0.6rem; color: #666; margin-top: 2px; }
.cal-legend { display: flex; gap: 1rem; font-size: 0.75rem; margin-top: 0.5rem; justify-content: center; }
.cal-legend span::before { content: ''; display: inline-block; width: 12px; height: 12px; border-radius: 2px; margin-right: 4px; vertical-align: middle; }
.cal-legend .leg-conf::before { background: #93c5fd; }
.cal-legend .leg-acc::before { background: #6366f1; }
.diagonal-line { position: absolute; bottom: 0; left: 0; width: 100%; height: 100%; pointer-events: none; }

/* Table */
.data-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
.data-table th {
    text-align: left; padding: 0.5rem; border-bottom: 2px solid #e5e7eb;
    font-weight: 600; color: #555; cursor: pointer; user-select: none;
}
.data-table th:hover { color: #1a1a2e; }
.data-table td { padding: 0.4rem 0.5rem; border-bottom: 1px solid #f0f0f0; }
.data-table tbody tr:hover { background: #f8f9fb; }

.score-cell { font-weight: 600; font-variant-numeric: tabular-nums; }
.pass-badge { display: inline-block; padding: 1px 8px; border-radius: 10px; font-size: 0.7rem; font-weight: 600; }
.pass-yes { background: #dcfce7; color: #166534; }
.pass-no { background: #fef2f2; color: #991b1b; }

.controls { display: flex; gap: 0.75rem; margin-bottom: 1rem; }
.controls input, .controls select {
    padding: 0.4rem 0.75rem; border: 1px solid #d1d5db; border-radius: 6px;
    font-size: 0.8rem; background: #fff;
}
.controls input { flex: 1; }
.table-info { font-size: 0.75rem; color: #888; margin-top: 0.5rem; }

/* Contamination */
.contam-verdict { font-size: 1rem; font-weight: 600; padding: 0.5rem 0; }
.contam-ok { color: #166534; }
.contam-warn { color: #991b1b; }
.contam-mild { color: #92400e; }
.contam-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-size: 0.85rem; }
.contam-stats dt { color: #666; }
.contam-stats dd { font-weight: 600; }

footer { text-align: center; font-size: 0.7rem; color: #aaa; margin-top: 2rem; padding: 1rem; }

/* Color palette for components */
.c0 { background: #6366f1; } .c1 { background: #8b5cf6; }
.c2 { background: #a78bfa; } .c3 { background: #f59e0b; }
.c4 { background: #10b981; } .c5 { background: #ec4899; }
.c6 { background: #06b6d4; } .c7 { background: #f97316; }
"""


# =============================================================================
# INLINE JS
# =============================================================================

_JS = """
const COLORS = ['#6366f1','#8b5cf6','#a78bfa','#f59e0b','#10b981','#ec4899','#06b6d4','#f97316'];

// ── Component Bar Chart ──
function renderCompChart() {
    const container = document.getElementById('comp-chart');
    const maxVal = Math.max(...compMeans, 0.01);
    let html = '<div class="bar-chart">';
    compNames.forEach((name, i) => {
        const h = (compMeans[i] / 1.0) * 100;  // scale to 0-1
        const color = COLORS[i % COLORS.length];
        html += `<div class="bar-group">
            <div class="bar-value">${compMeans[i].toFixed(3)}</div>
            <div class="bar" style="height:${Math.max(h, 2)}%;background:${color};"></div>
            <div class="bar-label">${name}</div>
        </div>`;
    });
    html += '</div>';
    container.innerHTML = html;

    // Table
    const tbody = document.getElementById('comp-tbody');
    tbody.innerHTML = '';
    compNames.forEach((name, i) => {
        const c = byComp[name] || {};
        tbody.innerHTML += `<tr>
            <td><b>${name}</b></td>
            <td>${c.n || 0}</td>
            <td class="score-cell">${(c.mean || 0).toFixed(3)}</td>
            <td>${(c.std || 0).toFixed(3)}</td>
            <td>${((c.pass_rate || 0) * 100).toFixed(1)}%</td>
            <td>${(c.median || 0).toFixed(3)}</td>
        </tr>`;
    });
}

// ── Score Distribution ──
function renderDistChart() {
    const container = document.getElementById('dist-chart');
    if (!allScores.length) { container.innerHTML = '<p style="color:#999;">No scores available</p>'; return; }

    const nBins = 20;
    const bins = new Array(nBins).fill(0);
    allScores.forEach(s => {
        const idx = Math.min(Math.floor(s * nBins), nBins - 1);
        bins[idx]++;
    });
    const maxBin = Math.max(...bins, 1);

    let html = '<div class="histogram">';
    bins.forEach((count, i) => {
        const h = (count / maxBin) * 100;
        const lo = (i / nBins).toFixed(2);
        const hi = ((i + 1) / nBins).toFixed(2);
        html += `<div class="hist-bar" style="height:${Math.max(h, 1)}%;">
            <span class="tooltip">[${lo}, ${hi}): ${count}</span>
        </div>`;
    });
    html += '</div>';
    html += `<div style="display:flex;justify-content:space-between;font-size:0.65rem;color:#999;"><span>0.0</span><span>0.5</span><span>1.0</span></div>`;
    container.innerHTML = html;
}

// ── Calibration Diagram ──
function renderCalChart() {
    if (!calBins.length) return;
    document.getElementById('cal-section').style.display = 'block';

    const container = document.getElementById('cal-chart');
    let html = '<div class="cal-diagram">';
    calBins.forEach((b, i) => {
        if (b.n === 0) {
            html += `<div class="cal-bar-group">
                <div style="height:2%;width:80%;background:#eee;border-radius:3px 3px 0 0;"></div>
                <div class="cal-label">${b.bin_range}</div>
            </div>`;
            return;
        }
        const confH = (b.avg_confidence * 100);
        const accH = (b.avg_accuracy * 100);
        html += `<div class="cal-bar-group">
            <div style="display:flex;gap:2px;align-items:flex-end;height:100%;width:100%;">
                <div class="cal-bar cal-conf" style="height:${Math.max(confH, 1)}%;flex:1;" title="Conf: ${b.avg_confidence}"></div>
                <div class="cal-bar cal-acc" style="height:${Math.max(accH, 1)}%;flex:1;" title="Acc: ${b.avg_accuracy}"></div>
            </div>
            <div class="cal-label">${b.bin_range} (n=${b.n})</div>
        </div>`;
    });
    html += '</div>';
    html += '<div class="cal-legend"><span class="leg-conf">Confidence</span><span class="leg-acc">Accuracy</span></div>';
    container.innerHTML = html;
}

// ── Contamination ──
function renderContam() {
    if (contam.error) return;
    document.getElementById('contam-section').style.display = 'block';

    const el = document.getElementById('contam-content');
    let cls = 'contam-ok';
    if (contam.verdict && contam.verdict.startsWith('WARNING')) cls = 'contam-warn';
    else if (contam.verdict && contam.verdict.startsWith('MILD')) cls = 'contam-mild';

    el.innerHTML = `
        <div class="contam-verdict ${cls}">${contam.verdict || 'N/A'}</div>
        <div class="contam-stats">
            <dt>Public mean</dt><dd>${(contam.public_mean || 0).toFixed(3)} (n=${contam.n_public || 0})</dd>
            <dt>Private mean</dt><dd>${(contam.private_mean || 0).toFixed(3)} (n=${contam.n_private || 0})</dd>
            <dt>Gap</dt><dd>${(contam.gap || 0).toFixed(3)}</dd>
            <dt>t-statistic</dt><dd>${(contam.t_statistic || 0).toFixed(2)}</dd>
        </div>`;
}

// ── Task Table ──
let currentSort = { key: 'score', asc: false };
let filteredRows = [...taskRows];

function renderTasks() {
    const tbody = document.getElementById('task-tbody');
    tbody.innerHTML = '';
    filteredRows.forEach(r => {
        const passClass = r.passed ? 'pass-yes' : 'pass-no';
        const passText = r.passed ? 'Pass' : 'Fail';
        const scoreColor = r.score >= 0.7 ? '#166534' : r.score >= 0.4 ? '#92400e' : '#991b1b';
        tbody.innerHTML += `<tr>
            <td>${r.task_id}</td>
            <td>${r.component}</td>
            <td>${r.task_type}</td>
            <td class="score-cell" style="color:${scoreColor}">${r.score.toFixed(4)}</td>
            <td><span class="pass-badge ${passClass}">${passText}</span></td>
        </tr>`;
    });
    document.getElementById('table-info').textContent = `Showing ${filteredRows.length} of ${taskRows.length} tasks`;
}

function filterTasks() {
    const search = document.getElementById('task-search').value.toLowerCase();
    const comp = document.getElementById('comp-filter').value;
    filteredRows = taskRows.filter(r => {
        if (comp && r.component !== comp) return false;
        if (search && !r.task_id.toLowerCase().includes(search) && !r.component.includes(search) && !r.task_type.includes(search)) return false;
        return true;
    });
    applySorting();
    renderTasks();
}

function sortTable(key) {
    if (currentSort.key === key) { currentSort.asc = !currentSort.asc; }
    else { currentSort = { key, asc: true }; }
    applySorting();
    renderTasks();
}

function applySorting() {
    const { key, asc } = currentSort;
    filteredRows.sort((a, b) => {
        let va = a[key], vb = b[key];
        if (typeof va === 'string') { va = va.toLowerCase(); vb = vb.toLowerCase(); }
        if (typeof va === 'boolean') { va = va ? 1 : 0; vb = vb ? 1 : 0; }
        if (va < vb) return asc ? -1 : 1;
        if (va > vb) return asc ? 1 : -1;
        return 0;
    });
}

// ── Overall mean color ──
function colorOverall() {
    const el = document.getElementById('overall-mean');
    const val = parseFloat(el.textContent);
    if (val >= 0.7) el.style.color = '#166534';
    else if (val >= 0.4) el.style.color = '#92400e';
    else el.style.color = '#991b1b';
}

// ── Init ──
document.addEventListener('DOMContentLoaded', () => {
    renderCompChart();
    renderDistChart();
    renderCalChart();
    renderContam();
    applySorting();
    renderTasks();
    colorOverall();
});
"""
