"""
Error Annotator Module

Automatically annotates model responses with error taxonomy categories.
Integrates the taxonomy schema into the evaluation pipeline.
"""

import re
from typing import Optional
from dataclasses import dataclass

from bioeval.taxonomy.schema import (
    ErrorCategory,
    KnowledgeError,
    ReasoningError,
    ProceduralError,
    UncertaintyError,
    ErrorAnnotation,
    AnnotatedResponse,
    create_error_annotation,
)


# =============================================================================
# ERROR DETECTION PATTERNS
# =============================================================================

# Patterns that suggest hallucination
HALLUCINATION_PATTERNS = [
    r"the (?:well-known|famous|established) (\w+) gene",  # Made-up "famous" genes
    r"as shown in \w+ et al\. \(\d{4}\)",  # Fake citations
    r"the (\w+) pathway, discovered in \d{4}",  # Fake pathway discoveries
]

# Patterns suggesting overconfidence
OVERCONFIDENCE_PATTERNS = [
    r"(?:always|never|definitely|certainly|absolutely) (?:will|causes|results)",
    r"there is no doubt",
    r"it is certain that",
    r"100% (?:effective|accurate|correct)",
]

# Patterns suggesting causal confusion
CAUSAL_CONFUSION_PATTERNS = [
    r"(\w+) is caused by (?:high|increased|elevated) expression of (\w+)",  # May have causality backwards
    r"because (\w+) expression (?:is|was) (?:high|low)",  # Correlation as causation
]

# Patterns suggesting procedural errors
PROCEDURAL_ERROR_PATTERNS = [
    r"incubate (?:overnight|for \d+ hours?) at (?:room temperature|RT|37[°C]*) with (?:trypsin|protease)",  # Dangerous
    r"add \d+\s*[mM] (?:SDS|EDTA|DTT) to (?:live|growing) cells",  # Wrong order
    r"skip the (?:wash|blocking|fixation) step",  # Missing critical steps
]


# =============================================================================
# AUTOMATIC ERROR DETECTION
# =============================================================================


def detect_knowledge_errors(response: str, ground_truth: dict) -> list[ErrorAnnotation]:
    """Detect knowledge-related errors in response."""
    errors = []
    response_lower = response.lower()

    # Check for hallucination patterns
    for pattern in HALLUCINATION_PATTERNS:
        matches = re.findall(pattern, response, re.IGNORECASE)
        for match in matches:
            errors.append(
                create_error_annotation(
                    category="knowledge",
                    subcategory=KnowledgeError.FACTUAL_HALLUCINATION.value,
                    severity="major",
                    explanation=f"Potentially fabricated reference: {match}",
                    text_span=str(match),
                )
            )

    # Check for domain confusion (mixing species, cell types)
    species_mentioned = []
    from bioeval.scoring.matching import phrase_match

    for species in ["human", "mouse", "rat", "yeast", "drosophila", "zebrafish", "c. elegans"]:
        if phrase_match(species, response_lower):
            species_mentioned.append(species)

    if len(species_mentioned) > 2:
        errors.append(
            create_error_annotation(
                category="knowledge",
                subcategory=KnowledgeError.DOMAIN_CONFUSION.value,
                severity="minor",
                explanation=f"Multiple species mentioned ({', '.join(species_mentioned)}) - verify context appropriateness",
            )
        )

    return errors


def detect_reasoning_errors(response: str, ground_truth: dict) -> list[ErrorAnnotation]:
    """Detect reasoning-related errors."""
    errors = []

    # Check for causal confusion patterns
    for pattern in CAUSAL_CONFUSION_PATTERNS:
        matches = re.findall(pattern, response, re.IGNORECASE)
        if matches:
            errors.append(
                create_error_annotation(
                    category="reasoning",
                    subcategory=ReasoningError.CORRELATION_CAUSATION.value,
                    severity="major",
                    explanation="Statement may confuse correlation with causation",
                    text_span=str(matches[0]) if matches else None,
                )
            )

    # Check for overgeneralization
    overgeneralization_phrases = [
        "all cancers",
        "every cell",
        "always works",
        "never fails",
        "in all cases",
        "universally",
        "without exception",
    ]
    for phrase in overgeneralization_phrases:
        if phrase in response.lower():
            errors.append(
                create_error_annotation(
                    category="reasoning",
                    subcategory=ReasoningError.OVERGENERALIZATION.value,
                    severity="minor",
                    explanation=f"Overgeneralization: '{phrase}'",
                    text_span=phrase,
                )
            )
            break  # Only report once

    return errors


def detect_procedural_errors(response: str, task_type: str) -> list[ErrorAnnotation]:
    """Detect procedural errors (mostly for protocol tasks)."""
    errors = []

    if task_type not in ["step_ordering", "missing_step", "troubleshooting", "safety", "calculation"]:
        return errors

    # Check for dangerous procedural patterns
    for pattern in PROCEDURAL_ERROR_PATTERNS:
        matches = re.findall(pattern, response, re.IGNORECASE)
        if matches:
            errors.append(
                create_error_annotation(
                    category="procedural",
                    subcategory=ProceduralError.SAFETY_OVERSIGHT.value,
                    severity="critical",
                    explanation="Potentially dangerous procedural suggestion",
                    text_span=str(matches[0]),
                )
            )

    # Check for missing safety mentions in safety tasks
    if task_type == "safety":
        safety_terms = ["ppe", "gloves", "goggles", "hood", "ventilation", "dispose", "hazard"]
        if not any(term in response.lower() for term in safety_terms):
            errors.append(
                create_error_annotation(
                    category="procedural",
                    subcategory=ProceduralError.SAFETY_OVERSIGHT.value,
                    severity="major",
                    explanation="Safety task response lacks safety precautions",
                )
            )

    return errors


def detect_uncertainty_errors(response: str, confidence_score: float, is_correct: bool) -> list[ErrorAnnotation]:
    """Detect uncertainty calibration errors."""
    errors = []

    # Check for overconfidence
    for pattern in OVERCONFIDENCE_PATTERNS:
        if re.search(pattern, response, re.IGNORECASE):
            if not is_correct:
                errors.append(
                    create_error_annotation(
                        category="uncertainty",
                        subcategory=UncertaintyError.OVERCONFIDENCE.value,
                        severity="major",
                        explanation="High confidence language used but answer appears incorrect",
                    )
                )
            break

    # Check calibration
    if confidence_score > 0.8 and not is_correct:
        errors.append(
            create_error_annotation(
                category="uncertainty",
                subcategory=UncertaintyError.OVERCONFIDENCE.value,
                severity="major",
                explanation=f"Confidence ({confidence_score:.0%}) much higher than accuracy",
            )
        )
    elif confidence_score < 0.3 and is_correct:
        errors.append(
            create_error_annotation(
                category="uncertainty",
                subcategory=UncertaintyError.FALSE_HEDGING.value,
                severity="minor",
                explanation=f"Unnecessary uncertainty ({confidence_score:.0%}) on correct answer",
            )
        )

    return errors


# =============================================================================
# MAIN ANNOTATOR
# =============================================================================


@dataclass
class AnnotationResult:
    """Result of automatic annotation."""

    task_id: str
    errors: list[ErrorAnnotation]
    error_count: int
    errors_by_category: dict[str, int]
    errors_by_severity: dict[str, int]
    overall_quality: str


def annotate_response(
    task_id: str, task_type: str, response: str, ground_truth: dict, confidence_score: float = 0.5, is_correct: bool = True
) -> AnnotationResult:
    """
    Automatically annotate a model response with error taxonomy.

    Args:
        task_id: Task identifier
        task_type: Type of task
        response: Model response text
        ground_truth: Ground truth information
        confidence_score: Model's confidence (0-1)
        is_correct: Whether response is correct

    Returns:
        AnnotationResult with detected errors
    """
    all_errors = []

    # Detect different error types
    all_errors.extend(detect_knowledge_errors(response, ground_truth))
    all_errors.extend(detect_reasoning_errors(response, ground_truth))
    all_errors.extend(detect_procedural_errors(response, task_type))
    all_errors.extend(detect_uncertainty_errors(response, confidence_score, is_correct))

    # Count by category
    by_category = {}
    for error in all_errors:
        cat = error.category.value
        by_category[cat] = by_category.get(cat, 0) + 1

    # Count by severity
    by_severity = {}
    for error in all_errors:
        sev = error.severity
        by_severity[sev] = by_severity.get(sev, 0) + 1

    # Determine overall quality
    critical_count = by_severity.get("critical", 0)
    major_count = by_severity.get("major", 0)

    if critical_count > 0:
        overall_quality = "poor"
    elif major_count > 2:
        overall_quality = "poor"
    elif major_count > 0:
        overall_quality = "acceptable"
    elif len(all_errors) > 0:
        overall_quality = "good"
    else:
        overall_quality = "excellent"

    return AnnotationResult(
        task_id=task_id,
        errors=all_errors,
        error_count=len(all_errors),
        errors_by_category=by_category,
        errors_by_severity=by_severity,
        overall_quality=overall_quality,
    )


def summarize_annotations(annotations: list[AnnotationResult]) -> dict:
    """Summarize annotations across multiple responses."""
    total_errors = 0
    by_category = {}
    by_severity = {}
    quality_dist = {}

    for ann in annotations:
        total_errors += ann.error_count

        for cat, count in ann.errors_by_category.items():
            by_category[cat] = by_category.get(cat, 0) + count

        for sev, count in ann.errors_by_severity.items():
            by_severity[sev] = by_severity.get(sev, 0) + count

        quality_dist[ann.overall_quality] = quality_dist.get(ann.overall_quality, 0) + 1

    return {
        "total_responses": len(annotations),
        "total_errors": total_errors,
        "avg_errors_per_response": total_errors / len(annotations) if annotations else 0,
        "errors_by_category": by_category,
        "errors_by_severity": by_severity,
        "quality_distribution": quality_dist,
    }
