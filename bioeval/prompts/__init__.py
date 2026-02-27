"""
BioEval Prompt Enhancement Module

This module provides enhanced prompt templates designed to improve model performance
on biological evaluation tasks by addressing common failure modes:

1. Calibration - Reduces overconfidence through evidence-based confidence scoring
2. Misleading Context Defense - Filters irrelevant information before reasoning
3. Edge Case Recognition - Explicitly checks boundary conditions
4. Nonsense Detection - Verifies biological entities exist before using them
5. Chain-of-Thought - Structured reasoning for causal biology tasks
"""

from .prompt_templates import (
    # System prompts
    CALIBRATED_SYSTEM_PROMPT,
    SCIENTIFIC_REASONING_SYSTEM_PROMPT,
    # Enhancement functions
    add_calibration_instructions,
    add_context_defense,
    add_edge_case_check,
    add_nonsense_detection,
    add_chain_of_thought,
    # Composite enhancers
    enhance_prompt,
    enhance_causal_prompt,
    enhance_adversarial_prompt,
    # Configuration
    PromptEnhancementConfig,
)

__all__ = [
    "CALIBRATED_SYSTEM_PROMPT",
    "SCIENTIFIC_REASONING_SYSTEM_PROMPT",
    "add_calibration_instructions",
    "add_context_defense",
    "add_edge_case_check",
    "add_nonsense_detection",
    "add_chain_of_thought",
    "enhance_prompt",
    "enhance_causal_prompt",
    "enhance_adversarial_prompt",
    "PromptEnhancementConfig",
]
