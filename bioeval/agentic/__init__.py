"""
Agentic: Pseudo-agentic multi-step scientific reasoning evaluation.

Tests whether LLMs can sustain coherent reasoning across multi-step
scientific workflows: planning experiments, executing bioinformatics
pipelines, conducting literature-based research, and troubleshooting.

Component 11 of BioEval. 4 categories x 6 tasks = 24 tasks.
"""

from bioeval.agentic.evaluator import AgenticEvaluator

__all__ = ["AgenticEvaluator"]
