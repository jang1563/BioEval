"""
BioEval: Multi-dimensional Evaluation of LLMs for Biological Research
"""

from bioeval.version import __version__

# Default model for evaluation
DEFAULT_MODEL = "claude-sonnet-4-20250514"

# Core exports
from bioeval.models.base import BaseEvaluator, EvalTask, EvalResult

# Component evaluators
from bioeval.protoreason.evaluator import ProtoReasonEvaluator
from bioeval.causalbio.evaluator import CausalBioEvaluator
from bioeval.designcheck.evaluator import DesignCheckEvaluator
from bioeval.adversarial.tasks import AdversarialEvaluator
from bioeval.multiturn.dialogues import MultiTurnEvaluator
from bioeval.scoring.calibration import CalibrationEvaluator
from bioeval.biosafety.tasks import BiosafetyEvaluator
from bioeval.datainterp.tasks import DataInterpEvaluator
from bioeval.debate.evaluator import DebateEvaluator
from bioeval.longhorizon.evaluator import LongHorizonEvaluator
from bioeval.agentic.evaluator import AgenticEvaluator

# Scoring
from bioeval.scoring.calibration import extract_confidence, compute_calibration_metrics
from bioeval.scoring.llm_judge import LLMJudge

# Execution
from bioeval.execution.async_runner import AsyncBioEvalClient, ExecutionConfig, ResponseCache

__all__ = [
    # Version
    "__version__",
    "DEFAULT_MODEL",
    # Base
    "BaseEvaluator",
    "EvalTask",
    "EvalResult",
    # Evaluators
    "ProtoReasonEvaluator",
    "CausalBioEvaluator",
    "DesignCheckEvaluator",
    "AdversarialEvaluator",
    "MultiTurnEvaluator",
    "CalibrationEvaluator",
    "BiosafetyEvaluator",
    "DataInterpEvaluator",
    "DebateEvaluator",
    "LongHorizonEvaluator",
    "AgenticEvaluator",
    # Scoring
    "extract_confidence",
    "compute_calibration_metrics",
    "LLMJudge",
    # Execution
    "AsyncBioEvalClient",
    "ExecutionConfig",
    "ResponseCache",
]
