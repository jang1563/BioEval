"""
BioAmbiguity: Context-Dependent Biological Reasoning Evaluation

Tests whether LLMs can recognize that the same biological concept
(gene, pathway, compound, process) behaves differently depending
on context — tissue type, disease state, species, concentration,
or developmental stage.
"""

from bioeval.bioambiguity.evaluator import BioAmbiguityEvaluator

__all__ = ["BioAmbiguityEvaluator"]
