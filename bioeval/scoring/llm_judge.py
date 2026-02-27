"""
LLM-as-Judge Scoring Module

Uses a separate LLM call to evaluate response quality with structured rubrics.
This provides semantic evaluation rather than simple string matching.
"""

import json
from typing import Optional
from dataclasses import dataclass, field
from enum import Enum


# =============================================================================
# SCORING RUBRICS
# =============================================================================


class ScoreDimension(Enum):
    """Dimensions for evaluating biological reasoning."""

    FACTUAL_ACCURACY = "factual_accuracy"
    MECHANISTIC_DEPTH = "mechanistic_depth"
    COMPLETENESS = "completeness"
    SCIENTIFIC_REASONING = "scientific_reasoning"
    PRACTICAL_APPLICABILITY = "practical_applicability"
    APPROPRIATE_UNCERTAINTY = "appropriate_uncertainty"


@dataclass
class RubricCriteria:
    """Single criterion within a rubric."""

    dimension: ScoreDimension
    weight: float
    description: str
    score_5: str  # What constitutes a 5
    score_3: str  # What constitutes a 3
    score_1: str  # What constitutes a 1


@dataclass
class JudgeResult:
    """Result from LLM judge evaluation."""

    task_id: str
    overall_score: float  # 1-5 scale
    dimension_scores: dict[str, float]
    reasoning: str
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    critical_errors: list[str] = field(default_factory=list)
    raw_judge_response: str = ""


# =============================================================================
# TASK-SPECIFIC RUBRICS
# =============================================================================

RUBRICS = {
    "knockout_prediction": [
        RubricCriteria(
            dimension=ScoreDimension.FACTUAL_ACCURACY,
            weight=0.3,
            description="Correctness of the predicted fitness effect",
            score_5="Correct prediction with accurate CRISPR score interpretation",
            score_3="Correct direction but imprecise magnitude",
            score_1="Incorrect prediction or fundamentally wrong understanding",
        ),
        RubricCriteria(
            dimension=ScoreDimension.MECHANISTIC_DEPTH,
            weight=0.3,
            description="Quality of biological mechanism explanation",
            score_5="Explains pathway dependencies, genetic context, and molecular basis",
            score_3="Mentions relevant pathways but lacks mechanistic detail",
            score_1="No mechanism or incorrect biological reasoning",
        ),
        RubricCriteria(
            dimension=ScoreDimension.SCIENTIFIC_REASONING,
            weight=0.2,
            description="Logical flow from evidence to conclusion",
            score_5="Clear reasoning chain connecting genotype, context, and phenotype",
            score_3="Reasonable logic but some gaps or unsupported claims",
            score_1="Illogical or contradictory reasoning",
        ),
        RubricCriteria(
            dimension=ScoreDimension.APPROPRIATE_UNCERTAINTY,
            weight=0.2,
            description="Calibration of confidence to evidence strength",
            score_5="Confidence matches evidence; acknowledges context-dependency",
            score_3="Mostly appropriate but over/under-confident in places",
            score_1="Highly confident when wrong, or uncertain about established facts",
        ),
    ],
    "pathway_reasoning": [
        RubricCriteria(
            dimension=ScoreDimension.COMPLETENESS,
            weight=0.25,
            description="Coverage of affected pathways and downstream effects",
            score_5="Identifies all major pathways, feedback loops, and compensatory mechanisms",
            score_3="Covers main pathways but misses secondary effects",
            score_1="Incomplete or misses critical pathways",
        ),
        RubricCriteria(
            dimension=ScoreDimension.MECHANISTIC_DEPTH,
            weight=0.3,
            description="Molecular detail of pathway effects",
            score_5="Names specific nodes, explains signal flow, predicts gene expression changes",
            score_3="General pathway knowledge without specific molecular details",
            score_1="Vague or incorrect pathway understanding",
        ),
        RubricCriteria(
            dimension=ScoreDimension.SCIENTIFIC_REASONING,
            weight=0.25,
            description="Logic of pathway predictions",
            score_5="Correctly traces cause-effect relationships through signaling cascade",
            score_3="Generally logical but some causal steps unclear",
            score_1="Confuses cause and effect or makes illogical predictions",
        ),
        RubricCriteria(
            dimension=ScoreDimension.PRACTICAL_APPLICABILITY,
            weight=0.2,
            description="Clinical/experimental relevance of predictions",
            score_5="Mentions resistance mechanisms, therapeutic implications, experimental validation",
            score_3="Some practical context but limited",
            score_1="Purely theoretical with no practical grounding",
        ),
    ],
    "protocol_troubleshooting": [
        RubricCriteria(
            dimension=ScoreDimension.COMPLETENESS,
            weight=0.3,
            description="Coverage of possible causes",
            score_5="Identifies >80% of common causes, ranked by likelihood",
            score_3="Identifies major causes but misses some common issues",
            score_1="Misses critical causes or provides irrelevant suggestions",
        ),
        RubricCriteria(
            dimension=ScoreDimension.PRACTICAL_APPLICABILITY,
            weight=0.35,
            description="Actionability of diagnostic steps",
            score_5="Provides specific, executable diagnostic steps in logical order",
            score_3="General troubleshooting advice but lacks specificity",
            score_1="Vague or impractical suggestions",
        ),
        RubricCriteria(
            dimension=ScoreDimension.SCIENTIFIC_REASONING,
            weight=0.2,
            description="Logic of differential diagnosis",
            score_5="Systematic approach, rules out causes efficiently",
            score_3="Reasonable logic but not optimally organized",
            score_1="Random or illogical troubleshooting order",
        ),
        RubricCriteria(
            dimension=ScoreDimension.FACTUAL_ACCURACY,
            weight=0.15,
            description="Technical correctness of advice",
            score_5="All suggestions are technically sound",
            score_3="Mostly correct with minor inaccuracies",
            score_1="Contains incorrect or potentially harmful advice",
        ),
    ],
    "calculation": [
        RubricCriteria(
            dimension=ScoreDimension.FACTUAL_ACCURACY,
            weight=0.5,
            description="Numerical correctness of final answer",
            score_5="Correct answer with proper units",
            score_3="Minor calculation error but correct method",
            score_1="Wrong answer due to fundamental error",
        ),
        RubricCriteria(
            dimension=ScoreDimension.SCIENTIFIC_REASONING,
            weight=0.3,
            description="Clarity of calculation steps",
            score_5="Clear step-by-step work, formulas shown, units tracked",
            score_3="Shows work but some steps unclear",
            score_1="No work shown or incorrect formula application",
        ),
        RubricCriteria(
            dimension=ScoreDimension.PRACTICAL_APPLICABILITY,
            weight=0.2,
            description="Practical considerations mentioned",
            score_5="Notes assumptions, practical tips, potential pitfalls",
            score_3="Some practical context",
            score_1="Pure calculation with no practical guidance",
        ),
    ],
    "flaw_detection": [
        RubricCriteria(
            dimension=ScoreDimension.COMPLETENESS,
            weight=0.35,
            description="Coverage of actual flaws in the design",
            score_5="Identifies all critical and major flaws",
            score_3="Identifies most critical flaws but misses some major ones",
            score_1="Misses critical flaws",
        ),
        RubricCriteria(
            dimension=ScoreDimension.FACTUAL_ACCURACY,
            weight=0.25,
            description="Accuracy of flaw identification (precision)",
            score_5="All identified flaws are real problems, no false positives",
            score_3="Mostly accurate but some minor false positives",
            score_1="Many false positives or mischaracterized flaws",
        ),
        RubricCriteria(
            dimension=ScoreDimension.SCIENTIFIC_REASONING,
            weight=0.2,
            description="Quality of explanation for why each is a flaw",
            score_5="Clear explanation of why each issue compromises validity",
            score_3="Identifies flaws but explanations lack depth",
            score_1="Poor or incorrect explanations",
        ),
        RubricCriteria(
            dimension=ScoreDimension.PRACTICAL_APPLICABILITY,
            weight=0.2,
            description="Quality of suggested fixes",
            score_5="Specific, actionable fixes that would resolve issues",
            score_3="General suggestions for improvement",
            score_1="No fixes or impractical suggestions",
        ),
    ],
    "epistasis": [
        RubricCriteria(
            dimension=ScoreDimension.FACTUAL_ACCURACY,
            weight=0.3,
            description="Correct identification of interaction type",
            score_5="Correctly identifies synthetic lethal/suppressive/enhancing",
            score_3="Partially correct or correct with wrong terminology",
            score_1="Incorrect interaction type",
        ),
        RubricCriteria(
            dimension=ScoreDimension.MECHANISTIC_DEPTH,
            weight=0.35,
            description="Explanation of interaction mechanism",
            score_5="Detailed molecular explanation of why genes interact",
            score_3="General explanation without molecular details",
            score_1="No mechanism or incorrect explanation",
        ),
        RubricCriteria(
            dimension=ScoreDimension.PRACTICAL_APPLICABILITY,
            weight=0.2,
            description="Clinical/therapeutic relevance",
            score_5="Correctly explains clinical implications and therapeutic opportunities",
            score_3="Mentions clinical relevance but lacks specificity",
            score_1="No practical context",
        ),
        RubricCriteria(
            dimension=ScoreDimension.APPROPRIATE_UNCERTAINTY,
            weight=0.15,
            description="Acknowledgment of context-dependency",
            score_5="Notes that interactions can vary by cell type/context",
            score_3="Some acknowledgment of complexity",
            score_1="Overly definitive claims",
        ),
    ],
}

# Default rubric for tasks without specific rubric
DEFAULT_RUBRIC = [
    RubricCriteria(
        dimension=ScoreDimension.FACTUAL_ACCURACY,
        weight=0.3,
        description="Correctness of factual claims",
        score_5="All facts correct and verifiable",
        score_3="Mostly correct with minor errors",
        score_1="Significant factual errors",
    ),
    RubricCriteria(
        dimension=ScoreDimension.COMPLETENESS,
        weight=0.25,
        description="Coverage of relevant aspects",
        score_5="Comprehensive coverage of topic",
        score_3="Covers main points but misses some",
        score_1="Incomplete or superficial",
    ),
    RubricCriteria(
        dimension=ScoreDimension.SCIENTIFIC_REASONING,
        weight=0.25,
        description="Quality of reasoning",
        score_5="Clear, logical, well-supported arguments",
        score_3="Generally logical but some gaps",
        score_1="Poor reasoning or logical errors",
    ),
    RubricCriteria(
        dimension=ScoreDimension.APPROPRIATE_UNCERTAINTY,
        weight=0.2,
        description="Calibration of confidence",
        score_5="Confidence matches evidence strength",
        score_3="Mostly appropriate confidence",
        score_1="Miscalibrated confidence",
    ),
]


# =============================================================================
# JUDGE PROMPT TEMPLATE
# =============================================================================

JUDGE_SYSTEM_PROMPT = """You are an expert scientific evaluator assessing AI responses to biology tasks.
Your role is to provide rigorous, objective evaluation based on the provided rubric.

You must:
1. Evaluate each dimension separately with a score from 1-5
2. Provide specific reasoning for each score
3. Identify concrete strengths and weaknesses
4. Flag any critical errors (factual mistakes that could cause harm)
5. Be calibrated: a score of 3 means "acceptable", 5 means "excellent", 1 means "poor"

Respond in JSON format only."""


def create_judge_prompt(
    task_type: str, task_prompt: str, model_response: str, ground_truth: dict, rubric: Optional[list[RubricCriteria]] = None
) -> str:
    """Create the prompt for the LLM judge."""

    if rubric is None:
        rubric = RUBRICS.get(task_type, DEFAULT_RUBRIC)

    rubric_text = "\n".join(
        [
            f"""
Dimension: {c.dimension.value}
Weight: {c.weight}
Description: {c.description}
- Score 5: {c.score_5}
- Score 3: {c.score_3}
- Score 1: {c.score_1}
"""
            for c in rubric
        ]
    )

    # Simplify ground truth for judge
    gt_summary = json.dumps(ground_truth, indent=2, default=str)[:2000]

    prompt = f"""## Task Type
{task_type}

## Original Task Prompt
{task_prompt}

## Model Response to Evaluate
{model_response}

## Reference Information (Ground Truth)
{gt_summary}

## Evaluation Rubric
{rubric_text}

## Instructions
Evaluate the model response against the rubric. For each dimension, provide:
1. A score from 1-5
2. Brief reasoning (1-2 sentences)

Then provide:
- Overall weighted score
- List of strengths (specific quotes/examples)
- List of weaknesses (specific issues)
- Critical errors (factual mistakes that could cause experimental failure or harm)

## Response Format (JSON only)
{{
    "dimension_scores": {{
        "<dimension_name>": {{
            "score": <1-5>,
            "reasoning": "<brief explanation>"
        }}
    }},
    "overall_score": <weighted average>,
    "strengths": ["<specific strength 1>", "<specific strength 2>"],
    "weaknesses": ["<specific weakness 1>", "<specific weakness 2>"],
    "critical_errors": ["<error 1 if any>"],
    "summary_reasoning": "<2-3 sentence overall assessment>"
}}"""

    return prompt


# =============================================================================
# JUDGE CLASS
# =============================================================================


class LLMJudge:
    """LLM-based evaluation judge."""

    def __init__(self, judge_model: str = "claude-sonnet-4-20250514"):
        """Initialize judge with specified model."""
        self.judge_model = judge_model
        self._client = None

    @property
    def client(self):
        """Lazy load Anthropic client."""
        if self._client is None:
            from anthropic import Anthropic

            self._client = Anthropic()
        return self._client

    def evaluate(self, task_id: str, task_type: str, task_prompt: str, model_response: str, ground_truth: dict) -> JudgeResult:
        """Evaluate a single model response."""

        judge_prompt = create_judge_prompt(
            task_type=task_type, task_prompt=task_prompt, model_response=model_response, ground_truth=ground_truth
        )

        response = self.client.messages.create(
            model=self.judge_model,
            max_tokens=2000,
            temperature=0.0,
            system=JUDGE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": judge_prompt}],
        )

        raw_response = response.content[0].text

        # Parse JSON response
        try:
            # Handle potential markdown code blocks
            json_str = raw_response
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]

            result_dict = json.loads(json_str.strip())

            return JudgeResult(
                task_id=task_id,
                overall_score=result_dict.get("overall_score", 0),
                dimension_scores={
                    k: v.get("score", 0) if isinstance(v, dict) else v
                    for k, v in result_dict.get("dimension_scores", {}).items()
                },
                reasoning=result_dict.get("summary_reasoning", ""),
                strengths=result_dict.get("strengths", []),
                weaknesses=result_dict.get("weaknesses", []),
                critical_errors=result_dict.get("critical_errors", []),
                raw_judge_response=raw_response,
            )

        except json.JSONDecodeError as e:
            # Return error result if parsing fails
            return JudgeResult(
                task_id=task_id,
                overall_score=0,
                dimension_scores={},
                reasoning=f"Failed to parse judge response: {e}",
                raw_judge_response=raw_response,
            )

    def batch_evaluate(self, evaluations: list[dict]) -> list[JudgeResult]:
        """Evaluate multiple responses."""
        results = []
        for eval_item in evaluations:
            result = self.evaluate(
                task_id=eval_item["task_id"],
                task_type=eval_item["task_type"],
                task_prompt=eval_item["task_prompt"],
                model_response=eval_item["model_response"],
                ground_truth=eval_item["ground_truth"],
            )
            results.append(result)
        return results


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_rubric_for_task(task_type: str) -> list[RubricCriteria]:
    """Get the appropriate rubric for a task type."""
    return RUBRICS.get(task_type, DEFAULT_RUBRIC)


def calculate_weighted_score(dimension_scores: dict, task_type: str) -> float:
    """Calculate weighted overall score from dimension scores."""
    rubric = get_rubric_for_task(task_type)

    total_weight = 0
    weighted_sum = 0

    for criterion in rubric:
        dim_name = criterion.dimension.value
        if dim_name in dimension_scores:
            weighted_sum += dimension_scores[dim_name] * criterion.weight
            total_weight += criterion.weight

    return weighted_sum / total_weight if total_weight > 0 else 0


if __name__ == "__main__":
    # Print available rubrics
    print("Available task-specific rubrics:")
    for task_type in RUBRICS:
        rubric = RUBRICS[task_type]
        print(f"\n{task_type}:")
        for criterion in rubric:
            print(f"  - {criterion.dimension.value} (weight: {criterion.weight})")
