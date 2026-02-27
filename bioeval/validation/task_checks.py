"""
Task data validation framework for BioEval.

Automatically checks all task data for quality issues:
- Missing required fields
- Duplicate task IDs
- Empty strings / zero-length lists
- Ground truth completeness
- ID format consistency
- Cross-component integrity

Run: bioeval validate [--data-tier base]
"""

import re
from collections import Counter
from dataclasses import dataclass


@dataclass
class ValidationIssue:
    """A single validation issue."""
    severity: str  # "error", "warning", "info"
    component: str
    task_id: str
    field: str
    message: str

    def __str__(self):
        icon = {"error": "ERROR", "warning": "WARN", "info": "INFO"}[self.severity]
        return f"[{icon}] {self.component}/{self.task_id}: {self.field} - {self.message}"


def validate_all(data_tier: str = "base") -> list[ValidationIssue]:
    """Run all validation checks across all components.

    Returns list of ValidationIssue sorted by severity.
    """
    issues: list[ValidationIssue] = []
    all_ids: list[str] = []

    issues.extend(_validate_adversarial(all_ids))
    issues.extend(_validate_calibration(all_ids))
    issues.extend(_validate_protoreason(all_ids, data_tier))
    issues.extend(_validate_causalbio(all_ids, data_tier))
    issues.extend(_validate_designcheck(all_ids, data_tier))
    issues.extend(_validate_multiturn(all_ids, data_tier))

    # Cross-component: duplicate IDs
    id_counts = Counter(all_ids)
    for tid, count in id_counts.items():
        if count > 1:
            issues.append(ValidationIssue(
                "error", "global", tid, "id",
                f"Duplicate task ID (appears {count} times)"))

    # Sort: errors first, then warnings, then info
    order = {"error": 0, "warning": 1, "info": 2}
    issues.sort(key=lambda i: (order[i.severity], i.component, i.task_id))
    return issues


# =============================================================================
# HELPER VALIDATORS
# =============================================================================

def _check_required_str(d: dict, field: str, comp: str, tid: str,
                        issues: list[ValidationIssue], min_len: int = 1):
    """Check a required string field exists and is non-empty."""
    val = d.get(field)
    if val is None:
        issues.append(ValidationIssue("error", comp, tid, field, "Missing required field"))
    elif not isinstance(val, str):
        issues.append(ValidationIssue("error", comp, tid, field,
                                      f"Expected str, got {type(val).__name__}"))
    elif len(val.strip()) < min_len:
        issues.append(ValidationIssue("warning", comp, tid, field, "Empty or too short"))


def _check_required_list(d: dict, field: str, comp: str, tid: str,
                         issues: list[ValidationIssue], min_len: int = 1):
    """Check a required list field exists and is non-empty."""
    val = d.get(field)
    if val is None:
        issues.append(ValidationIssue("error", comp, tid, field, "Missing required field"))
    elif not isinstance(val, list):
        issues.append(ValidationIssue("error", comp, tid, field,
                                      f"Expected list, got {type(val).__name__}"))
    elif len(val) < min_len:
        issues.append(ValidationIssue("warning", comp, tid, field,
                                      f"List too short ({len(val)} < {min_len})"))


def _check_id_format(tid: str, pattern: str, comp: str,
                     issues: list[ValidationIssue]):
    """Check that a task ID matches an expected pattern."""
    if not re.match(pattern, tid):
        issues.append(ValidationIssue("warning", comp, tid, "id",
                                      f"ID does not match expected pattern: {pattern}"))


# =============================================================================
# ADVERSARIAL VALIDATION
# =============================================================================

def _validate_adversarial(all_ids: list[str]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    try:
        from bioeval.adversarial.tasks import ADVERSARIAL_TASKS
    except ImportError:
        issues.append(ValidationIssue("error", "adversarial", "", "import",
                                      "Cannot import ADVERSARIAL_TASKS"))
        return issues

    valid_difficulties = {"easy", "medium", "hard"}

    for t in ADVERSARIAL_TASKS:
        tid = t.id
        all_ids.append(tid)
        _check_id_format(tid, r"^adv_", "adversarial", issues)

        if not t.question or len(t.question.strip()) < 20:
            issues.append(ValidationIssue("warning", "adversarial", tid, "question",
                                          "Question too short (< 20 chars)"))

        if not t.trap_description:
            issues.append(ValidationIssue("error", "adversarial", tid, "trap_description",
                                          "Missing trap description"))

        if not t.correct_behavior:
            issues.append(ValidationIssue("error", "adversarial", tid, "correct_behavior",
                                          "Missing correct behavior"))

        if not t.incorrect_behaviors:
            issues.append(ValidationIssue("warning", "adversarial", tid, "incorrect_behaviors",
                                          "No incorrect behaviors specified"))

        if t.difficulty not in valid_difficulties:
            issues.append(ValidationIssue("warning", "adversarial", tid, "difficulty",
                                          f"Unknown difficulty: {t.difficulty}"))

    return issues


# =============================================================================
# CALIBRATION VALIDATION
# =============================================================================

def _validate_calibration(all_ids: list[str]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    try:
        from bioeval.scoring.calibration import CALIBRATION_TEST_TASKS
    except ImportError:
        issues.append(ValidationIssue("error", "calibration", "", "import",
                                      "Cannot import CALIBRATION_TEST_TASKS"))
        return issues

    valid_behaviors = {"acknowledge_unknown", "high_confidence_correct",
                       "partial_knowledge", "context_dependent",
                       "moderate_confidence", "overconfidence_trap"}

    for t in CALIBRATION_TEST_TASKS:
        tid = t.get("id", "")
        all_ids.append(tid)
        _check_id_format(tid, r"^cal_", "calibration", issues)
        _check_required_str(t, "question", "calibration", tid, issues, min_len=20)
        _check_required_str(t, "explanation", "calibration", tid, issues)

        behavior = t.get("correct_behavior", "")
        if behavior not in valid_behaviors:
            issues.append(ValidationIssue("warning", "calibration", tid, "correct_behavior",
                                          f"Unknown behavior: {behavior}"))

        # High-confidence tasks should have expected_answer
        if behavior == "high_confidence_correct" and not t.get("expected_answer"):
            issues.append(ValidationIssue("warning", "calibration", tid, "expected_answer",
                                          "high_confidence_correct task missing expected_answer"))

        # Overconfidence traps should have nuance_indicators
        if behavior == "overconfidence_trap" and not t.get("nuance_indicators"):
            issues.append(ValidationIssue("info", "calibration", tid, "nuance_indicators",
                                          "overconfidence_trap task missing nuance_indicators"))

    return issues


# =============================================================================
# PROTOREASON VALIDATION
# =============================================================================

def _validate_protoreason(all_ids: list[str], data_tier: str) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    try:
        from bioeval.protoreason.evaluator import SAMPLE_PROTOCOLS, CALCULATION_TASKS, TROUBLESHOOTING_TASKS
    except ImportError:
        issues.append(ValidationIssue("error", "protoreason", "", "import",
                                      "Cannot import protoreason data"))
        return issues

    # Protocols
    for name, proto in SAMPLE_PROTOCOLS.items():
        tid = f"proto_{name}"
        all_ids.extend([f"{tid}_ordering", f"{tid}_missing", f"{tid}_reagent"])

        if not proto.get("steps"):
            issues.append(ValidationIssue("error", "protoreason", tid, "steps",
                                          "Protocol has no steps"))
        elif len(proto["steps"]) < 3:
            issues.append(ValidationIssue("warning", "protoreason", tid, "steps",
                                          f"Only {len(proto['steps'])} steps (min 3 recommended)"))

        if not proto.get("name"):
            issues.append(ValidationIssue("warning", "protoreason", tid, "name",
                                          "Protocol missing name"))

    # Calculation tasks
    for t in CALCULATION_TASKS:
        tid = t.get("id", f"calc_unknown")
        all_ids.append(tid)
        _check_id_format(tid, r"^calc_", "protoreason", issues)
        _check_required_str(t, "question", "protoreason", tid, issues, min_len=10)

        answer = t.get("answer")
        if not answer:
            issues.append(ValidationIssue("error", "protoreason", tid, "answer",
                                          "Missing answer"))
        elif isinstance(answer, dict) and not answer:
            issues.append(ValidationIssue("error", "protoreason", tid, "answer",
                                          "Empty answer dict"))

    # Troubleshooting tasks
    for t in TROUBLESHOOTING_TASKS:
        tid = t.get("id", f"trouble_unknown")
        all_ids.append(tid)
        _check_id_format(tid, r"^trouble_", "protoreason", issues)
        _check_required_str(t, "scenario", "protoreason", tid, issues, min_len=10)
        _check_required_list(t, "possible_causes", "protoreason", tid, issues, min_len=2)
        _check_required_list(t, "diagnostic_steps", "protoreason", tid, issues, min_len=1)

    return issues


# =============================================================================
# CAUSALBIO VALIDATION
# =============================================================================

def _validate_causalbio(all_ids: list[str], data_tier: str) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    try:
        from bioeval.causalbio.evaluator import (
            KNOCKOUT_TASKS, PATHWAY_TASKS, DRUG_RESPONSE_TASKS, EPISTASIS_TASKS,
            ensure_task_provenance, PROVENANCE_CURATED, PROVENANCE_EXTERNAL
        )
    except ImportError:
        issues.append(ValidationIssue("error", "causalbio", "", "import",
                                      "Cannot import causalbio data"))
        return issues

    valid_source_types = {PROVENANCE_CURATED, PROVENANCE_EXTERNAL}

    def _check_provenance(task: dict, tid: str):
        normalized = ensure_task_provenance(task, "bioeval.causalbio.evaluator")
        prov = normalized.get("provenance", {})
        if not isinstance(prov, dict):
            issues.append(ValidationIssue("error", "causalbio", tid, "provenance",
                                          "Missing provenance metadata dict"))
            return
        source_type = prov.get("source_type")
        if source_type not in valid_source_types:
            issues.append(ValidationIssue("warning", "causalbio", tid, "provenance.source_type",
                                          f"Unexpected source_type: {source_type}"))
        if not prov.get("source_id"):
            issues.append(ValidationIssue("error", "causalbio", tid, "provenance.source_id",
                                          "Missing source_id"))
        if not prov.get("release"):
            issues.append(ValidationIssue("warning", "causalbio", tid, "provenance.release",
                                          "Missing release tag"))

    # Knockout tasks
    for t in KNOCKOUT_TASKS:
        tid = t.get("id", "ko_unknown")
        all_ids.append(tid)
        _check_id_format(tid, r"^ko_", "causalbio", issues)
        _check_required_str(t, "gene", "causalbio", tid, issues)
        _check_required_str(t, "question", "causalbio", tid, issues, min_len=10)
        _check_provenance(t, tid)

        gt = t.get("ground_truth", {})
        if not gt:
            issues.append(ValidationIssue("error", "causalbio", tid, "ground_truth",
                                          "Missing ground truth"))
        else:
            if gt.get("effect") not in ("essential", "non-essential"):
                issues.append(ValidationIssue("warning", "causalbio", tid, "ground_truth.effect",
                                              f"Unexpected effect: {gt.get('effect')}"))

    # Pathway tasks
    for t in PATHWAY_TASKS:
        tid = t.get("id", "pathway_unknown")
        all_ids.append(tid)
        _check_id_format(tid, r"^pathway_", "causalbio", issues)
        _check_required_str(t, "question", "causalbio", tid, issues, min_len=10)
        _check_provenance(t, tid)

        gt = t.get("ground_truth", {})
        pathways = gt.get("affected_pathways", [])
        if not pathways:
            issues.append(ValidationIssue("error", "causalbio", tid, "ground_truth.affected_pathways",
                                          "No affected pathways"))
        for i, p in enumerate(pathways):
            valid_directions = {"up", "down", "variable",
                                "increased", "decreased", "arrested", "inhibited",
                                "activated", "suppressed", "enhanced"}
            if p.get("direction") not in valid_directions:
                issues.append(ValidationIssue("warning", "causalbio", tid,
                                              f"affected_pathways[{i}].direction",
                                              f"Unexpected direction: {p.get('direction')}"))

    # Drug response tasks
    for t in DRUG_RESPONSE_TASKS:
        tid = t.get("id", "drug_unknown")
        all_ids.append(tid)
        _check_id_format(tid, r"^drug_", "causalbio", issues)
        _check_required_str(t, "drug", "causalbio", tid, issues)
        _check_provenance(t, tid)

        gt = t.get("ground_truth", {})
        if not gt.get("upregulated") and not gt.get("downregulated"):
            issues.append(ValidationIssue("warning", "causalbio", tid, "ground_truth",
                                          "No upregulated or downregulated genes"))

    # Epistasis tasks
    for t in EPISTASIS_TASKS:
        tid = t.get("id", "epistasis_unknown")
        all_ids.append(tid)
        _check_id_format(tid, r"^epistasis_", "causalbio", issues)
        _check_required_str(t, "gene_a", "causalbio", tid, issues)
        _check_required_str(t, "gene_b", "causalbio", tid, issues)
        _check_provenance(t, tid)

        gt = t.get("ground_truth", {})
        valid_interactions = {"enhancing", "suppressive", "synergistic", "synthetic_lethal"}
        interaction = gt.get("interaction", "")
        if interaction not in valid_interactions:
            issues.append(ValidationIssue("warning", "causalbio", tid,
                                          "ground_truth.interaction",
                                          f"Unexpected interaction: {interaction}"))

    return issues


# =============================================================================
# DESIGNCHECK VALIDATION
# =============================================================================

def _validate_designcheck(all_ids: list[str], data_tier: str) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    try:
        from bioeval.designcheck.evaluator import FLAWED_DESIGNS
    except ImportError:
        issues.append(ValidationIssue("error", "designcheck", "", "import",
                                      "Cannot import designcheck data"))
        return issues

    valid_severities = {"critical", "major", "minor"}
    valid_categories = {"controls", "statistics", "confounders", "technical", "interpretation"}

    for d in FLAWED_DESIGNS:
        tid = d.get("id", "design_unknown")
        all_ids.append(tid)
        _check_id_format(tid, r"^design_", "designcheck", issues)
        _check_required_str(d, "title", "designcheck", tid, issues)
        _check_required_str(d, "description", "designcheck", tid, issues, min_len=50)

        flaws = d.get("flaws", [])
        if not flaws:
            issues.append(ValidationIssue("error", "designcheck", tid, "flaws",
                                          "No flaws defined for flawed design"))
        for i, flaw in enumerate(flaws):
            if flaw.get("severity") not in valid_severities:
                issues.append(ValidationIssue("warning", "designcheck", tid,
                                              f"flaws[{i}].severity",
                                              f"Unknown severity: {flaw.get('severity')}"))
            if flaw.get("category") not in valid_categories:
                issues.append(ValidationIssue("info", "designcheck", tid,
                                              f"flaws[{i}].category",
                                              f"Non-standard category: {flaw.get('category')}"))
            if not flaw.get("explanation"):
                issues.append(ValidationIssue("warning", "designcheck", tid,
                                              f"flaws[{i}].explanation",
                                              "Flaw missing explanation"))

    return issues


# =============================================================================
# MULTITURN VALIDATION
# =============================================================================

def _validate_multiturn(all_ids: list[str], data_tier: str) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    try:
        from bioeval.multiturn.dialogues import DIALOGUES
    except ImportError:
        issues.append(ValidationIssue("error", "multiturn", "", "import",
                                      "Cannot import multiturn data"))
        return issues

    for d in DIALOGUES:
        tid = d.id
        all_ids.append(tid)
        _check_id_format(tid, r"^mt_", "multiturn", issues)

        if not d.title:
            issues.append(ValidationIssue("warning", "multiturn", tid, "title", "Missing title"))

        if not d.turns:
            issues.append(ValidationIssue("error", "multiturn", tid, "turns", "No turns defined"))
        elif len(d.turns) < 2:
            issues.append(ValidationIssue("warning", "multiturn", tid, "turns",
                                          "Only 1 turn (multi-turn needs >= 2)"))

        for i, turn in enumerate(d.turns):
            if turn.turn_number != i + 1:
                issues.append(ValidationIssue("warning", "multiturn", tid,
                                              f"turns[{i}].turn_number",
                                              f"Expected {i+1}, got {turn.turn_number}"))
            if not turn.user_message:
                issues.append(ValidationIssue("error", "multiturn", tid,
                                              f"turns[{i}].user_message",
                                              "Empty user message"))
            if not turn.expected_behaviors:
                issues.append(ValidationIssue("warning", "multiturn", tid,
                                              f"turns[{i}].expected_behaviors",
                                              "No expected behaviors"))

        if not d.overall_objective:
            issues.append(ValidationIssue("warning", "multiturn", tid, "overall_objective",
                                          "Missing overall objective"))

    return issues


# =============================================================================
# SUMMARY & OUTPUT
# =============================================================================

def validation_summary(issues: list[ValidationIssue]) -> dict:
    """Compute summary statistics from validation issues."""
    by_severity = Counter(i.severity for i in issues)
    by_component = Counter(i.component for i in issues)
    return {
        "total_issues": len(issues),
        "errors": by_severity.get("error", 0),
        "warnings": by_severity.get("warning", 0),
        "info": by_severity.get("info", 0),
        "by_component": dict(by_component),
        "all_clear": by_severity.get("error", 0) == 0,
    }


def print_validation(data_tier: str = "base"):
    """Run validation and print results."""
    issues = validate_all(data_tier)
    summary = validation_summary(issues)

    print(f"\n{'=' * 60}")
    print(f"BioEval Task Validation (tier: {data_tier})")
    print(f"{'=' * 60}")

    if not issues:
        print("\nAll checks passed. No issues found.")
        return summary

    print(f"\nTotal issues: {summary['total_issues']}")
    print(f"  Errors:   {summary['errors']}")
    print(f"  Warnings: {summary['warnings']}")
    print(f"  Info:     {summary['info']}")

    if summary["errors"] > 0:
        print(f"\n--- ERRORS ---")
        for i in issues:
            if i.severity == "error":
                print(f"  {i}")

    if summary["warnings"] > 0:
        print(f"\n--- WARNINGS ---")
        for i in issues:
            if i.severity == "warning":
                print(f"  {i}")

    if summary["info"] > 0:
        print(f"\n--- INFO ---")
        for i in issues:
            if i.severity == "info":
                print(f"  {i}")

    print(f"\nBy component:")
    for comp, count in sorted(summary["by_component"].items()):
        print(f"  {comp:<15} {count} issues")

    verdict = "PASS" if summary["all_clear"] else "FAIL"
    print(f"\nVerdict: {verdict}")
    return summary
