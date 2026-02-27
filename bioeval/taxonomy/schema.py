"""
BioEval Error Taxonomy

Systematic categorization of how LLMs fail in biological reasoning.
Used for annotating errors and analyzing failure modes.
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class ErrorCategory(Enum):
    """Top-level error categories."""

    KNOWLEDGE = "knowledge"
    REASONING = "reasoning"
    PROCEDURAL = "procedural"
    UNCERTAINTY = "uncertainty"
    COMMUNICATION = "communication"


class KnowledgeError(Enum):
    """Knowledge-related errors."""

    FACTUAL_HALLUCINATION = "factual_hallucination"  # Invented genes, pathways, mechanisms
    OUTDATED_INFO = "outdated_info"  # Superseded nomenclature, old understanding
    DOMAIN_CONFUSION = "domain_confusion"  # Mixing species, cell types, contexts
    INCORRECT_FACT = "incorrect_fact"  # Wrong but real information


class ReasoningError(Enum):
    """Reasoning-related errors."""

    CAUSAL_REVERSAL = "causal_reversal"  # Effect→cause confusion
    PATHWAY_TRUNCATION = "pathway_truncation"  # Incomplete mechanism
    SCALE_CONFUSION = "scale_confusion"  # Molecule vs cell vs organism
    TEMPORAL_CONFUSION = "temporal_confusion"  # Order of biological events
    OVERGENERALIZATION = "overgeneralization"  # Applying rule beyond valid context
    CORRELATION_CAUSATION = "correlation_causation"  # Treating correlation as causation


class ProceduralError(Enum):
    """Procedural/protocol errors."""

    STEP_OMISSION = "step_omission"  # Missing critical steps
    STEP_HALLUCINATION = "step_hallucination"  # Invented procedures
    REAGENT_CONFUSION = "reagent_confusion"  # Wrong chemicals/concentrations
    ORDER_ERROR = "order_error"  # Wrong step sequence
    SAFETY_OVERSIGHT = "safety_oversight"  # Missing hazard warnings


class UncertaintyError(Enum):
    """Uncertainty calibration errors."""

    OVERCONFIDENCE = "overconfidence"  # High confidence, wrong answer
    FALSE_HEDGING = "false_hedging"  # Unnecessary uncertainty on known facts
    MISSING_UNCERTAINTY = "missing_uncertainty"  # No acknowledgment of unknowns
    MISCALIBRATED = "miscalibrated"  # Confidence doesn't match accuracy


class CommunicationError(Enum):
    """Communication/presentation errors."""

    JARGON_MISUSE = "jargon_misuse"  # Incorrect technical terms
    PRECISION_LOSS = "precision_loss"  # Vague where specificity needed
    AUDIENCE_MISMATCH = "audience_mismatch"  # Wrong level of detail
    AMBIGUITY = "ambiguity"  # Unclear meaning


@dataclass
class ErrorAnnotation:
    """Single error annotation for a model response."""

    error_id: str
    category: ErrorCategory
    subcategory: str  # One of the specific error types
    severity: str  # "critical", "major", "minor"
    text_span: Optional[str] = None  # The problematic text
    explanation: str = ""  # Why this is an error
    correct_info: Optional[str] = None  # What should have been said


@dataclass
class AnnotatedResponse:
    """Model response with error annotations."""

    task_id: str
    model: str
    response: str
    errors: list[ErrorAnnotation] = field(default_factory=list)
    overall_quality: str = ""  # "good", "acceptable", "poor", "harmful"
    annotator: str = ""
    notes: str = ""


# Error severity guidelines
SEVERITY_GUIDELINES = {
    "critical": """
    Errors that could cause:
    - Experimental failure or safety issues
    - Wrong scientific conclusions
    - Waste of significant resources (time, reagents, samples)
    - Patient harm in clinical contexts
    
    Examples:
    - Missing safety step with hazardous reagents
    - Completely wrong mechanism that would mislead research
    - Calculation error that affects experimental design
    """,
    "major": """
    Errors that could cause:
    - Suboptimal experimental results
    - Confusion or misunderstanding
    - Minor resource waste
    - Incomplete understanding
    
    Examples:
    - Missing non-critical step
    - Incomplete pathway explanation
    - Outdated but not harmful information
    """,
    "minor": """
    Errors that:
    - Don't affect experimental outcome
    - Are stylistic or presentational
    - Represent small imprecisions
    
    Examples:
    - Slightly imprecise terminology
    - Unnecessary hedging
    - Minor formatting issues
    """,
}


# Annotation schema for export
ANNOTATION_SCHEMA = {
    "task_id": "string - unique task identifier",
    "model": "string - model name/version",
    "response": "string - full model response",
    "errors": [
        {
            "error_id": "string - unique error identifier",
            "category": "enum - ErrorCategory value",
            "subcategory": "string - specific error type",
            "severity": "string - critical/major/minor",
            "text_span": "string - problematic text (optional)",
            "explanation": "string - why this is an error",
            "correct_info": "string - what should have been said (optional)",
        }
    ],
    "overall_quality": "string - good/acceptable/poor/harmful",
    "annotator": "string - annotator identifier",
    "notes": "string - additional observations",
}


def create_error_annotation(
    category: str,
    subcategory: str,
    severity: str,
    explanation: str,
    text_span: Optional[str] = None,
    correct_info: Optional[str] = None,
) -> ErrorAnnotation:
    """Helper to create error annotations."""
    import uuid

    category_enum = ErrorCategory(category.lower())

    return ErrorAnnotation(
        error_id=str(uuid.uuid4())[:8],
        category=category_enum,
        subcategory=subcategory,
        severity=severity,
        text_span=text_span,
        explanation=explanation,
        correct_info=correct_info,
    )


def export_annotation_template(output_path: str = "annotation_template.json"):
    """Export JSON template for manual annotation."""
    import json

    template = {
        "schema_version": "1.0",
        "annotation_guidelines": SEVERITY_GUIDELINES,
        "error_categories": {
            "knowledge": [e.value for e in KnowledgeError],
            "reasoning": [e.value for e in ReasoningError],
            "procedural": [e.value for e in ProceduralError],
            "uncertainty": [e.value for e in UncertaintyError],
            "communication": [e.value for e in CommunicationError],
        },
        "annotations": [
            {
                "task_id": "TASK_ID_HERE",
                "model": "MODEL_NAME_HERE",
                "response": "RESPONSE_TEXT_HERE",
                "errors": [],
                "overall_quality": "",
                "annotator": "",
                "notes": "",
            }
        ],
    }

    with open(output_path, "w") as f:
        json.dump(template, f, indent=2)

    return template


if __name__ == "__main__":
    # Generate annotation template
    template = export_annotation_template("annotation_template.json")
    print("Generated annotation template")
    print("\nError categories:")
    for cat in ErrorCategory:
        print(f"  {cat.value}")
