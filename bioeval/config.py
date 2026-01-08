"""
BioEval Configuration Constants

Centralized configuration to avoid hardcoded values throughout the codebase.
"""

# =============================================================================
# MODEL CONFIGURATION
# =============================================================================

# Default models for evaluation
DEFAULT_MODEL = "claude-sonnet-4-20250514"
DEFAULT_JUDGE_MODEL = "claude-sonnet-4-20250514"

# Supported models
SUPPORTED_MODELS = {
    "claude": [
        "claude-sonnet-4-20250514",
        "claude-opus-4-20250514", 
        "claude-haiku-3-5-20241022",
    ],
    "openai": [
        "gpt-4",
        "gpt-4-turbo",
        "gpt-4o",
        "gpt-3.5-turbo",
    ]
}

# =============================================================================
# EXECUTION CONFIGURATION
# =============================================================================

# Rate limits (conservative defaults)
DEFAULT_RPM = 50  # Requests per minute
DEFAULT_TPM = 40000  # Tokens per minute
DEFAULT_MAX_CONCURRENT = 5
DEFAULT_TIMEOUT = 120.0  # Seconds

# Retry configuration
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_RETRY_DELAY = 1.0  # Seconds

# Cache configuration
DEFAULT_CACHE_DIR = ".bioeval_cache"
CACHE_ENABLED_DEFAULT = True

# =============================================================================
# SCORING CONFIGURATION
# =============================================================================

# Score ranges
MIN_SCORE = 1.0
MAX_SCORE = 5.0

# Confidence thresholds
HIGH_CONFIDENCE_THRESHOLD = 0.7
LOW_CONFIDENCE_THRESHOLD = 0.4

# Calibration buckets
CONFIDENCE_BUCKETS = {
    "high": (0.7, 1.0),
    "medium": (0.4, 0.7),
    "low": (0.0, 0.4)
}

# =============================================================================
# TASK CONFIGURATION
# =============================================================================

# Component names
COMPONENTS = [
    "protoreason",
    "causalbio", 
    "designcheck",
    "adversarial",
    "multiturn",
    "calibration"
]

# Task types by component
TASK_TYPES = {
    "protoreason": [
        "step_ordering",
        "missing_step",
        "calculation",
        "troubleshooting",
        "safety"
    ],
    "causalbio": [
        "knockout_prediction",
        "pathway_reasoning",
        "drug_response",
        "epistasis"
    ],
    "designcheck": [
        "flaw_detection"
    ],
    "adversarial": [
        "false_premise",
        "hallucination_trap",
        "misleading_context",
        "edge_case",
        "contradictory",
        "plausible_nonsense",
        "overly_specific"
    ],
    "calibration": [
        "acknowledge_unknown",
        "high_confidence_correct",
        "partial_knowledge",
        "context_dependent",
        "moderate_confidence"
    ]
}

# =============================================================================
# OUTPUT CONFIGURATION
# =============================================================================

# Default output directory
DEFAULT_OUTPUT_DIR = "results"

# File formats
RESULTS_FORMAT = "json"
REPORT_FORMAT = "html"

# =============================================================================
# PROMPT ENHANCEMENT CONFIGURATION
# =============================================================================

# Enable/disable prompt enhancements globally
PROMPT_ENHANCEMENTS_ENABLED = True

# Individual enhancement toggles
ENHANCEMENT_CALIBRATION = True  # Reduces overconfidence
ENHANCEMENT_CONTEXT_DEFENSE = True  # Filters misleading context
ENHANCEMENT_EDGE_CASE = True  # Checks boundary conditions
ENHANCEMENT_NONSENSE_DETECTION = True  # Verifies entities exist
ENHANCEMENT_CHAIN_OF_THOUGHT = True  # Structured reasoning for causal tasks

# Enhancement configuration
CALIBRATION_MIN_EVIDENCE = 2  # Minimum evidence for high confidence
CALIBRATION_CONFIDENCE_LEVELS = ["high", "medium", "low"]

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_LOG_LEVEL = "INFO"
