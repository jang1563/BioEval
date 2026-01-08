"""
BioEval Enhanced Prompt Templates

This module contains prompt enhancements designed to address specific failure modes
identified in model evaluations:

- 58.8% overconfidence rate → Calibration Enhancement
- 0% pass on misleading_context → Context Defense
- 25% pass on edge_case → Edge Case Recognition
- 33% pass on plausible_nonsense → Nonsense Detection
- Causal reasoning errors → Chain-of-Thought

Usage:
    from bioeval.prompts import enhance_prompt, PromptEnhancementConfig

    config = PromptEnhancementConfig(
        calibration=True,
        context_defense=True,
        edge_case=True,
        nonsense_detection=True,
        chain_of_thought=True
    )

    enhanced = enhance_prompt(original_prompt, config)
"""

from dataclasses import dataclass, field
from typing import Optional, List


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class PromptEnhancementConfig:
    """Configuration for prompt enhancements."""
    calibration: bool = True
    context_defense: bool = True
    edge_case: bool = True
    nonsense_detection: bool = True
    chain_of_thought: bool = False  # Only for causal tasks

    # Fine-tuning options
    confidence_levels: List[str] = field(
        default_factory=lambda: ["high", "medium", "low"]
    )
    require_evidence_count: int = 2  # Min evidence pieces for high confidence


# =============================================================================
# SYSTEM PROMPTS
# =============================================================================

CALIBRATED_SYSTEM_PROMPT = """You are an expert biological scientist providing careful, well-calibrated responses.

CRITICAL GUIDELINES FOR CALIBRATION:
1. Your confidence MUST match your evidence strength
2. Say "I don't know" or "I'm uncertain" when appropriate
3. High confidence requires multiple independent pieces of evidence
4. Distinguish between what you know vs. what you're inferring
5. Acknowledge when a question is at the edge of current knowledge

CONFIDENCE SCALE:
- HIGH: Multiple verified facts, well-established mechanisms, textbook knowledge
- MEDIUM: Single strong evidence source, reasonable inference from known biology
- LOW: Speculation, limited evidence, novel/unusual scenarios, conflicting data

Never express high confidence unless you can cite specific biological mechanisms or established facts."""


SCIENTIFIC_REASONING_SYSTEM_PROMPT = """You are an expert biological scientist with rigorous analytical skills.

BEFORE ANSWERING ANY QUESTION:
1. VERIFY: Check that all mentioned genes, proteins, pathways, and mechanisms actually exist
2. FILTER: Identify which details in the question are relevant vs. irrelevant distractors
3. CONSIDER: Think about edge cases and boundary conditions
4. REASON: Work through the biology step-by-step before concluding
5. CALIBRATE: Match your confidence to your evidence strength

If something seems unfamiliar or made-up, explicitly say so rather than guessing."""


# =============================================================================
# 1. CALIBRATION ENHANCEMENT
# =============================================================================

CALIBRATION_INSTRUCTIONS = """
## Confidence Calibration Requirements

Before stating your confidence level, you MUST:

1. **List your evidence**: What specific facts support your answer?
2. **Evaluate evidence quality**: Is this from established biology or inference?
3. **Consider alternatives**: What other explanations are plausible?
4. **Identify uncertainties**: What don't you know that could change the answer?

CONFIDENCE ASSIGNMENT RULES:
- HIGH confidence: Only if you have 2+ independent, verified pieces of evidence AND the mechanism is well-established
- MEDIUM confidence: If you have good reasoning but limited direct evidence, OR if there are reasonable alternative explanations
- LOW confidence: If you are extrapolating, speculating, or the scenario is unusual

IMPORTANT: It is better to be correctly uncertain than incorrectly confident.
Overconfidence is a critical error. When in doubt, choose MEDIUM or LOW.

Format your confidence as:
```
Confidence: [HIGH/MEDIUM/LOW]
Evidence supporting this confidence:
- [Evidence 1]
- [Evidence 2]
Key uncertainties: [What could change this answer]
```
"""


def add_calibration_instructions(prompt: str, config: Optional[PromptEnhancementConfig] = None) -> str:
    """
    Add calibration instructions to reduce overconfidence.

    This addresses the 58.8% overconfidence rate by requiring:
    - Explicit evidence listing
    - Justification for confidence levels
    - Acknowledgment of uncertainties
    """
    if config is None:
        config = PromptEnhancementConfig()

    return f"{prompt}\n{CALIBRATION_INSTRUCTIONS}"


# =============================================================================
# 2. MISLEADING CONTEXT DEFENSE
# =============================================================================

CONTEXT_DEFENSE_INSTRUCTIONS = """
## Critical: Filter Irrelevant Information

BEFORE answering, perform this relevance check:

1. **Identify the core question**: What is actually being asked?
2. **List all details provided**: Write out each piece of information given
3. **Classify each detail**:
   - RELEVANT: Directly affects the answer
   - IRRELEVANT: Does not impact the biological mechanism or answer
   - DISTRACTOR: Seems relevant but actually isn't
4. **Ignore distractors**: Base your answer ONLY on relevant information

Common irrelevant distractors to watch for:
- Lab environmental conditions (temperature, humidity) unless specifically about temperature-sensitive processes
- Researcher names, dates, or lab locations
- Equipment brands or specific catalog numbers (unless relevant to the problem)
- Procedural details that don't affect the outcome being asked about

Format your relevance analysis as:
```
Core question: [What is actually being asked]
Relevant details: [List only what matters]
Ignored distractors: [What you're filtering out and why]
```

Then proceed to answer based ONLY on the relevant details.
"""


def add_context_defense(prompt: str, config: Optional[PromptEnhancementConfig] = None) -> str:
    """
    Add context defense to filter misleading/irrelevant information.

    This addresses the 0% pass rate on misleading_context adversarial tests
    by forcing explicit relevance filtering.
    """
    return f"{CONTEXT_DEFENSE_INSTRUCTIONS}\n\n---\n\n{prompt}"


# =============================================================================
# 3. EDGE CASE RECOGNITION
# =============================================================================

EDGE_CASE_INSTRUCTIONS = """
## Edge Case Analysis Required

Before finalizing your answer, explicitly consider:

1. **Boundary conditions**:
   - What if concentrations are very high or very low?
   - What if time scales are very short or very long?
   - What if cell types or organisms are unusual?

2. **Exception scenarios**:
   - Are there known exceptions to the general rule you're applying?
   - Could this be a special case where normal biology doesn't apply?
   - Are there tissue-specific or context-specific variations?

3. **Assumption validation**:
   - What assumptions are you making?
   - Under what conditions would these assumptions break down?
   - Is this scenario one where standard assumptions apply?

4. **Red flags for edge cases**:
   - Unusual cell types (stem cells, cancer cells, specialized tissues)
   - Extreme conditions (hypoxia, heat shock, starvation)
   - Knockout/overexpression scenarios
   - Drug combinations or high doses
   - Developmental stages or aging

If this appears to be an edge case, explicitly state:
```
Edge case consideration: [Why this might be unusual]
Standard expectation: [What would normally happen]
Edge case possibility: [What might differ and why]
My assessment: [Which applies here and confidence level]
```
"""


def add_edge_case_check(prompt: str, config: Optional[PromptEnhancementConfig] = None) -> str:
    """
    Add edge case recognition to catch boundary conditions.

    This addresses the 25% pass rate on edge_case adversarial tests
    by forcing explicit consideration of unusual scenarios.
    """
    return f"{prompt}\n\n{EDGE_CASE_INSTRUCTIONS}"


# =============================================================================
# 4. NONSENSE DETECTION
# =============================================================================

NONSENSE_DETECTION_INSTRUCTIONS = """
## Entity Verification Required

BEFORE incorporating any biological entity into your answer, verify it exists:

1. **Gene/Protein names**:
   - Is this a real gene? (Watch for made-up names like "ONCORIX", "TUMORSUPPRESS1")
   - Real genes have standard nomenclature (e.g., TP53, BRCA1, EGFR)
   - Be suspicious of overly descriptive names that sound too convenient

2. **Pathway names**:
   - Is this a real signaling pathway?
   - Watch for fictional pathways that sound plausible

3. **Mechanism claims**:
   - Is this a real biological mechanism?
   - Be wary of claims that seem too perfectly aligned with the question

4. **Drug/compound names**:
   - Is this a real compound?
   - Verify before discussing its mechanism

If you encounter an entity you don't recognize:
```
Verification check: I am not familiar with [ENTITY].
- If this is a real but uncommon entity, I may have limited information
- If this is a fictional entity, I cannot provide accurate information about it
- Please verify this entity exists before I proceed
```

CRITICAL: Never make up functions or mechanisms for entities you don't recognize.
It is far better to say "I don't recognize this entity" than to hallucinate an answer.
"""


def add_nonsense_detection(prompt: str, config: Optional[PromptEnhancementConfig] = None) -> str:
    """
    Add nonsense detection to catch hallucination traps.

    This addresses the 33% pass rate on plausible_nonsense tests
    by requiring verification of biological entities.
    """
    return f"{NONSENSE_DETECTION_INSTRUCTIONS}\n\n---\n\n{prompt}"


# =============================================================================
# 5. CHAIN-OF-THOUGHT FOR CAUSAL REASONING
# =============================================================================

CHAIN_OF_THOUGHT_TEMPLATE = """
## Structured Causal Reasoning Required

For this causal biology question, work through your reasoning step-by-step:

### Step 1: Identify the Perturbation
- What is being changed? (gene knockout, drug treatment, mutation, etc.)
- What is the normal function of this component?

### Step 2: Map the Direct Effects
- What does this component directly interact with?
- What immediate molecular changes occur?

### Step 3: Trace the Pathway
- What signaling pathways are affected?
- Draw the causal chain: A → B → C → D
- Note any feedback loops or compensatory mechanisms

### Step 4: Consider the Cellular Context
- How does the cell type affect the outcome?
- Are there redundant pathways that could compensate?
- What is the baseline state of relevant pathways?

### Step 5: Predict the Phenotype
- Based on the pathway analysis, what phenotype do you expect?
- What is your confidence in this prediction?

### Step 6: Validate Your Reasoning
- Does this match known biology?
- Are there published examples of similar perturbations?
- What experiments would test your prediction?

Format your response as:
```
PERTURBATION: [What is changed]
NORMAL FUNCTION: [What this component normally does]

CAUSAL CHAIN:
[Component] --[effect]--> [Next component] --[effect]--> [Outcome]

KEY CONSIDERATIONS:
- [Relevant pathway details]
- [Compensatory mechanisms]
- [Context-specific factors]

PREDICTION: [Your predicted outcome]
CONFIDENCE: [HIGH/MEDIUM/LOW with justification]
VALIDATION: [What evidence supports this]
```
"""


def add_chain_of_thought(prompt: str, config: Optional[PromptEnhancementConfig] = None) -> str:
    """
    Add chain-of-thought reasoning structure for causal biology.

    This improves causal reasoning by enforcing systematic analysis
    of perturbations and their downstream effects.
    """
    return f"{CHAIN_OF_THOUGHT_TEMPLATE}\n\n---\n\nQUESTION:\n{prompt}"


# =============================================================================
# COMPOSITE ENHANCERS
# =============================================================================

def enhance_prompt(
    prompt: str,
    config: Optional[PromptEnhancementConfig] = None,
    task_type: Optional[str] = None
) -> str:
    """
    Apply all relevant enhancements to a prompt based on configuration.

    Args:
        prompt: Original prompt text
        config: Enhancement configuration
        task_type: Type of task (for task-specific enhancements)

    Returns:
        Enhanced prompt with all applicable improvements
    """
    if config is None:
        config = PromptEnhancementConfig()

    enhanced = prompt

    # Apply enhancements in order
    if config.nonsense_detection:
        enhanced = add_nonsense_detection(enhanced, config)

    if config.context_defense:
        enhanced = add_context_defense(enhanced, config)

    if config.edge_case:
        enhanced = add_edge_case_check(enhanced, config)

    if config.calibration:
        enhanced = add_calibration_instructions(enhanced, config)

    return enhanced


def enhance_causal_prompt(
    prompt: str,
    config: Optional[PromptEnhancementConfig] = None
) -> str:
    """
    Enhance a causal biology prompt with chain-of-thought reasoning.

    This applies:
    1. Chain-of-thought structure
    2. Calibration instructions
    3. Edge case recognition
    """
    if config is None:
        config = PromptEnhancementConfig(chain_of_thought=True)

    enhanced = add_chain_of_thought(prompt, config)
    enhanced = add_edge_case_check(enhanced, config)
    enhanced = add_calibration_instructions(enhanced, config)

    return enhanced


def enhance_adversarial_prompt(
    prompt: str,
    adversarial_type: Optional[str] = None,
    config: Optional[PromptEnhancementConfig] = None
) -> str:
    """
    Enhance a prompt with defenses specific to adversarial type.

    Args:
        prompt: Original prompt
        adversarial_type: Type of adversarial test (e.g., 'misleading_context')
        config: Enhancement configuration
    """
    if config is None:
        config = PromptEnhancementConfig()

    enhanced = prompt

    # Apply type-specific defenses
    if adversarial_type in ['misleading_context', 'plausible_nonsense']:
        enhanced = add_context_defense(enhanced, config)

    if adversarial_type in ['hallucination_trap', 'plausible_nonsense', 'false_premise']:
        enhanced = add_nonsense_detection(enhanced, config)

    if adversarial_type == 'edge_case':
        enhanced = add_edge_case_check(enhanced, config)

    # Always add calibration
    if config.calibration:
        enhanced = add_calibration_instructions(enhanced, config)

    return enhanced


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_system_prompt(enhanced: bool = True) -> str:
    """
    Get the appropriate system prompt.

    Args:
        enhanced: If True, return the full scientific reasoning prompt

    Returns:
        System prompt string
    """
    if enhanced:
        return SCIENTIFIC_REASONING_SYSTEM_PROMPT
    return CALIBRATED_SYSTEM_PROMPT


def format_confidence_output(
    confidence: str,
    evidence: List[str],
    uncertainties: List[str]
) -> str:
    """
    Format a properly calibrated confidence statement.

    Args:
        confidence: HIGH, MEDIUM, or LOW
        evidence: List of supporting evidence
        uncertainties: List of key uncertainties

    Returns:
        Formatted confidence block
    """
    evidence_str = "\n".join(f"- {e}" for e in evidence)
    uncertainty_str = ", ".join(uncertainties) if uncertainties else "None identified"

    return f"""
Confidence: {confidence}
Evidence supporting this confidence:
{evidence_str}
Key uncertainties: {uncertainty_str}
"""
