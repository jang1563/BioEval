"""
LongHorizon: Multi-step Scientific Reasoning Evaluation

Tests whether LLMs can sustain coherent scientific reasoning across
multi-step experimental workflows, tracking constraints, accumulating
state, detecting error propagation, and adaptively replanning when
intermediate results are unexpected.
"""

from bioeval.longhorizon.evaluator import LongHorizonEvaluator

__all__ = ["LongHorizonEvaluator"]
