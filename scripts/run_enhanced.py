#!/usr/bin/env python3
"""
BioEval Enhanced Runner

Features:
- Async execution for 10x faster evaluation
- Response caching to avoid redundant API calls
- LLM-as-Judge scoring for semantic evaluation
- Confidence calibration metrics
- Progress tracking and resumability

Usage:
    python run_enhanced.py --model claude-sonnet-4-20250514 --component all
    python run_enhanced.py --model claude-sonnet-4-20250514 --component causalbio --use-judge
    python run_enhanced.py --cache-stats
    python run_enhanced.py --clear-cache
"""

import argparse
import asyncio
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bioeval.execution.async_runner import (
    AsyncBioEvalClient,
    ExecutionConfig,
    run_async_evaluation,
    ResponseCache,
    ProgressTracker,
)
from bioeval.scoring.calibration import (
    extract_confidence,
    compute_calibration_metrics,
    CalibrationResult,
    add_confidence_prompt,
)

# =============================================================================
# TASK LOADERS
# =============================================================================


def load_protoreason_tasks() -> list[dict]:
    """Load ProtoReason tasks."""
    from bioeval.protoreason.extended_data import PROTOCOLS, CALCULATION_TASKS, TROUBLESHOOTING_TASKS, SAFETY_TASKS
    import random

    tasks = []

    # Step ordering tasks (shuffled protocol reconstruction)
    for protocol_id, protocol in PROTOCOLS.items():
        steps = protocol["steps"].copy()
        original_steps = steps.copy()
        random.shuffle(steps)

        tasks.append(
            {
                "task_id": f"ordering_{protocol_id}",
                "task_type": "step_ordering",
                "component": "protoreason",
                "prompt": f"""The following steps for {protocol['name']} are in random order. 
Please reorder them into the correct sequence.

Shuffled steps:
{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(steps))}

Provide your answer as a numbered list in the correct order.
Then briefly explain the reasoning for critical ordering decisions.""",
                "ground_truth": {"correct_steps": original_steps, "shuffled_steps": steps, "protocol_name": protocol["name"]},
            }
        )

    # Missing step detection tasks
    for protocol_id, protocol in PROTOCOLS.items():
        steps = protocol["steps"].copy()
        # Remove 1-2 critical steps
        critical_indices = protocol.get("critical_steps", [0, len(steps) // 2])[:2]
        removed_steps = []
        for idx in sorted(critical_indices, reverse=True):
            if idx < len(steps):
                removed_steps.append(steps.pop(idx))

        tasks.append(
            {
                "task_id": f"missing_{protocol_id}",
                "task_type": "missing_step",
                "component": "protoreason",
                "prompt": f"""The following protocol for {protocol['name']} is missing critical steps.
Identify what is missing and explain why each missing step is important.

Protocol steps:
{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(steps))}

What steps are missing? Why are they critical?""",
                "ground_truth": {
                    "removed_steps": removed_steps,
                    "complete_steps": protocol["steps"],
                    "protocol_name": protocol["name"],
                },
            }
        )

    # Calculation tasks
    for calc in CALCULATION_TASKS:
        tasks.append(
            {
                "task_id": calc["id"],
                "task_type": "calculation",
                "component": "protoreason",
                "prompt": f"""Solve this laboratory calculation problem. Show your work step by step.

{calc['question']}

Provide:
1. The calculation steps
2. The final answer with units
3. Any important considerations""",
                "ground_truth": calc,
            }
        )

    # Troubleshooting tasks
    for trouble in TROUBLESHOOTING_TASKS:
        tasks.append(
            {
                "task_id": trouble["id"],
                "task_type": "troubleshooting",
                "component": "protoreason",
                "prompt": f"""You are troubleshooting an experimental problem.

Scenario: {trouble['scenario']}
Details: {trouble['details']}

Provide:
1. Ranked list of possible causes (most likely first)
2. Diagnostic steps to identify the root cause
3. Recommended solutions""",
                "ground_truth": trouble,
            }
        )

    # Safety tasks
    for safety in SAFETY_TASKS:
        tasks.append(
            {
                "task_id": safety["id"],
                "task_type": "safety",
                "component": "protoreason",
                "prompt": f"""Safety assessment:

Scenario: {safety['scenario']}

{safety['question']}

List all relevant safety precautions, PPE requirements, and hazard mitigations.""",
                "ground_truth": safety,
            }
        )

    return tasks


def load_causalbio_tasks() -> list[dict]:
    """Load CausalBio tasks."""
    from bioeval.causalbio.extended_data import KNOCKOUT_TASKS, PATHWAY_TASKS, DRUG_RESPONSE_TASKS, EPISTASIS_TASKS

    tasks = []

    # Knockout predictions
    for ko in KNOCKOUT_TASKS:
        tasks.append(
            {
                "task_id": ko["id"],
                "task_type": "knockout_prediction",
                "component": "causalbio",
                "prompt": f"""Predict the fitness effect of a gene knockout.

Gene: {ko['gene']}
Cell line: {ko['cell_line']} ({ko['cell_type']})

Provide:
1. Prediction: Is this gene essential, non-essential, or context-dependent?
2. Confidence level (HIGH/MEDIUM/LOW)
3. Biological reasoning for your prediction
4. What experimental evidence would you expect?""",
                "ground_truth": ko,
            }
        )

    # Pathway reasoning
    for pathway in PATHWAY_TASKS:
        tasks.append(
            {
                "task_id": pathway["id"],
                "task_type": "pathway_reasoning",
                "component": "causalbio",
                "prompt": f"""Predict downstream pathway effects.

Perturbation: {pathway['perturbation']}
Cell context: {pathway['cell_context']}

Provide:
1. Affected pathways and direction of change
2. Molecular mechanism for each effect
3. Expected cellular phenotype
4. Compensatory or resistance mechanisms""",
                "ground_truth": pathway,
            }
        )

    # Drug responses
    for drug in DRUG_RESPONSE_TASKS:
        tasks.append(
            {
                "task_id": drug["id"],
                "task_type": "drug_response",
                "component": "causalbio",
                "prompt": f"""Predict transcriptional and cellular response to drug treatment.

Drug: {drug['drug']}
Cell type: {drug['cell_type']}
Concentration: {drug.get('concentration', 'standard')}
Duration: {drug.get('duration', '24 hours')}

Provide:
1. Key genes expected to be upregulated
2. Key genes expected to be downregulated  
3. Mechanism of drug action
4. Expected cellular phenotype""",
                "ground_truth": drug,
            }
        )

    # Epistasis
    for epi in EPISTASIS_TASKS:
        single_effects = epi.get("ground_truth", {}).get("single_effects", {})
        tasks.append(
            {
                "task_id": epi["id"],
                "task_type": "epistasis",
                "component": "causalbio",
                "prompt": f"""Predict the genetic interaction between two genes.

Gene A: {epi['gene_a']}
Gene B: {epi['gene_b']}
Context: {epi['context']}

Known single-gene effects:
{json.dumps(single_effects, indent=2)}

Provide:
1. Type of genetic interaction (synthetic lethal, suppressive, enhancing, no interaction)
2. Combined phenotypic effect
3. Molecular mechanism of interaction
4. Clinical or therapeutic relevance""",
                "ground_truth": epi,
            }
        )

    return tasks


def load_designcheck_tasks() -> list[dict]:
    """Load DesignCheck tasks."""
    from bioeval.designcheck.evaluator import FLAWED_DESIGNS

    tasks = []
    for design in FLAWED_DESIGNS:
        tasks.append(
            {
                "task_id": design["id"],
                "task_type": "flaw_detection",
                "component": "designcheck",
                "prompt": f"""Review this experimental design for methodological flaws.

Title: {design['title']}

{design['description']}

Identify:
1. Specific flaws (controls, statistics, confounders, technical, interpretation)
2. Severity of each flaw (critical, major, minor)
3. Why each is a problem
4. Suggested fixes""",
                "ground_truth": design,
            }
        )

    return tasks


def load_calibration_tasks() -> list[dict]:
    """Load calibration test tasks."""
    from bioeval.scoring.calibration import CALIBRATION_TEST_TASKS

    tasks = []
    for cal in CALIBRATION_TEST_TASKS:
        tasks.append(
            {
                "task_id": cal["id"],
                "task_type": cal["task_type"],
                "component": "calibration",
                "prompt": cal["question"],
                "ground_truth": cal,
                "is_calibration_test": True,
            }
        )

    return tasks


def load_adversarial_tasks() -> list[dict]:
    """Load adversarial robustness tasks."""
    from bioeval.adversarial.tasks import ADVERSARIAL_TASKS

    tasks = []
    for adv in ADVERSARIAL_TASKS:
        tasks.append(
            {
                "task_id": adv.id,
                "task_type": adv.adversarial_type.value,
                "component": "adversarial",
                "prompt": adv.question,
                "ground_truth": {
                    "trap_description": adv.trap_description,
                    "correct_behavior": adv.correct_behavior,
                    "incorrect_behaviors": adv.incorrect_behaviors,
                    "difficulty": adv.difficulty,
                },
                "adversarial_task": adv,
            }
        )

    return tasks


# =============================================================================
# SCORING
# =============================================================================


def score_response_basic(task: dict, response: str) -> dict:
    """Basic scoring (string matching + confidence extraction)."""
    gt = task.get("ground_truth", {})
    task_type = task.get("task_type", "")
    response_lower = response.lower()

    scores = {"task_id": task["task_id"], "task_type": task_type}

    # Extract confidence
    confidence = extract_confidence(response)
    scores["confidence"] = {
        "score": confidence.confidence_score,
        "stated": confidence.stated_confidence,
        "uncertainty_phrases": len(confidence.uncertainty_phrases),
        "certainty_phrases": len(confidence.certainty_phrases),
    }

    # Task-specific scoring
    if task_type == "knockout_prediction":
        expected_effect = gt.get("ground_truth", {}).get("effect", "")
        scores["effect_mentioned"] = expected_effect in response_lower
        scores["has_reasoning"] = any(
            word in response_lower for word in ["because", "since", "therefore", "mechanism", "pathway"]
        )

    elif task_type == "calculation":
        answer = gt.get("answer", {})
        # Check if key numbers appear
        numbers_found = 0
        for key, value in answer.items():
            if any(c.isdigit() for c in str(value)):
                nums = "".join(c for c in str(value) if c.isdigit() or c == ".")
                if nums and nums in response:
                    numbers_found += 1
        scores["numerical_accuracy"] = numbers_found / len(answer) if answer else 0
        scores["shows_work"] = "=" in response or "×" in response or "*" in response

    elif task_type == "flaw_detection":
        flaws = gt.get("flaws", [])
        detected = 0
        for flaw in flaws:
            flaw_terms = flaw.get("type", "").replace("_", " ").split()
            if any(term in response_lower for term in flaw_terms if len(term) > 3):
                detected += 1
        scores["flaw_recall"] = detected / len(flaws) if flaws else 0
        scores["flaws_detected"] = detected

    elif task_type == "epistasis":
        interaction = gt.get("ground_truth", {}).get("interaction_type", "")
        scores["interaction_correct"] = interaction in response_lower

    elif task_type == "pathway_reasoning":
        pathways = gt.get("ground_truth", {}).get("affected_pathways", [])
        mentioned = 0
        for p in pathways:
            pathway_name = p.get("pathway", "").lower()
            if any(term in response_lower for term in pathway_name.split("/") + pathway_name.split("-")):
                mentioned += 1
        scores["pathway_coverage"] = mentioned / len(pathways) if pathways else 0

    elif task_type == "troubleshooting":
        causes = gt.get("possible_causes", [])
        mentioned = sum(
            1 for cause in causes if any(term in response_lower for term in cause.lower().split()[:3] if len(term) > 4)
        )
        scores["cause_coverage"] = mentioned / len(causes) if causes else 0

    elif task_type == "safety":
        # Check if required precautions are mentioned
        required = gt.get("required_precautions", [])
        if not required:
            # Fallback: check for common safety terms
            safety_terms = [
                "ppe",
                "gloves",
                "goggles",
                "fume hood",
                "biosafety",
                "disposal",
                "hazard",
                "protection",
                "ventilation",
                "shield",
            ]
            scores["safety_awareness"] = sum(1 for term in safety_terms if term in response_lower) / len(safety_terms)
        else:
            mentioned = sum(
                1 for prec in required if any(word in response_lower for word in prec.lower().split() if len(word) > 3)
            )
            scores["precaution_coverage"] = mentioned / len(required) if required else 0

    elif task_type == "drug_response":
        # Check predicted genes
        expected_up = gt.get("expected_upregulated", gt.get("ground_truth", {}).get("upregulated", []))
        expected_down = gt.get("expected_downregulated", gt.get("ground_truth", {}).get("downregulated", []))

        up_mentioned = sum(1 for gene in expected_up if gene.lower() in response_lower)
        down_mentioned = sum(1 for gene in expected_down if gene.lower() in response_lower)

        total_genes = len(expected_up) + len(expected_down)
        scores["gene_coverage"] = (up_mentioned + down_mentioned) / total_genes if total_genes > 0 else 0
        scores["mechanism_mentioned"] = any(
            word in response_lower for word in ["mechanism", "pathway", "target", "inhibit", "activate", "bind"]
        )

    elif task_type == "step_ordering":
        # Check if response contains numbered steps in reasonable order
        import re

        # Extract numbers from response
        numbers = re.findall(r"\b(\d+)\b", response)
        scores["has_ordering"] = len(numbers) >= 3
        scores["response_structured"] = any(
            marker in response_lower for marker in ["first", "then", "next", "finally", "before", "after"]
        )

    elif task_type == "missing_step":
        removed_steps = gt.get("removed_steps", [])
        # Check if removed concepts are identified
        identified = 0
        for step in removed_steps:
            key_words = [w for w in step.lower().split() if len(w) > 4][:3]
            if any(word in response_lower for word in key_words):
                identified += 1
        scores["missing_step_recall"] = identified / len(removed_steps) if removed_steps else 0
        scores["explains_importance"] = any(
            word in response_lower for word in ["important", "critical", "essential", "necessary", "required", "must"]
        )

    # Adversarial task scoring
    elif task.get("component") == "adversarial":
        from bioeval.adversarial.tasks import score_adversarial_response

        adv_task = task.get("adversarial_task")
        if adv_task:
            adv_scores = score_adversarial_response(adv_task, response)
            scores.update(adv_scores)

    scores["response_length"] = len(response)

    return scores


async def score_with_judge(task: dict, response: str, judge_client: AsyncBioEvalClient) -> dict:
    """Score using LLM-as-Judge."""
    from bioeval.scoring.llm_judge import create_judge_prompt, JUDGE_SYSTEM_PROMPT

    judge_prompt = create_judge_prompt(
        task_type=task["task_type"],
        task_prompt=task["prompt"],
        model_response=response,
        ground_truth=task.get("ground_truth", {}),
    )

    result = await judge_client.generate(prompt=judge_prompt, system=JUDGE_SYSTEM_PROMPT, task_id=f"judge_{task['task_id']}")

    # Parse judge response
    try:
        judge_response = result["response"]
        # Handle markdown code blocks
        if "```json" in judge_response:
            judge_response = judge_response.split("```json")[1].split("```")[0]
        elif "```" in judge_response:
            judge_response = judge_response.split("```")[1].split("```")[0]

        judge_scores = json.loads(judge_response.strip())
        return {
            "judge_overall": judge_scores.get("overall_score", 0),
            "judge_dimensions": judge_scores.get("dimension_scores", {}),
            "judge_strengths": judge_scores.get("strengths", []),
            "judge_weaknesses": judge_scores.get("weaknesses", []),
            "judge_critical_errors": judge_scores.get("critical_errors", []),
            "judge_reasoning": judge_scores.get("summary_reasoning", ""),
        }
    except (json.JSONDecodeError, KeyError) as e:
        return {"judge_error": str(e), "judge_raw": result["response"][:500]}


# =============================================================================
# MAIN EVALUATION
# =============================================================================


async def run_evaluation(
    components: list[str], model: str, use_judge: bool = False, config: Optional[ExecutionConfig] = None
) -> dict:
    """Run full evaluation."""

    config = config or ExecutionConfig()

    # Load tasks
    all_tasks = []
    if "protoreason" in components or "all" in components:
        all_tasks.extend(load_protoreason_tasks())
    if "causalbio" in components or "all" in components:
        all_tasks.extend(load_causalbio_tasks())
    if "designcheck" in components or "all" in components:
        all_tasks.extend(load_designcheck_tasks())
    if "calibration" in components or "all" in components:
        all_tasks.extend(load_calibration_tasks())
    if "adversarial" in components or "all" in components:
        all_tasks.extend(load_adversarial_tasks())

    print(f"Loaded {len(all_tasks)} tasks")

    # Create evaluation ID for tracking
    eval_id = f"{model.replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Run async evaluation
    print(f"\n{'='*60}")
    print(f"Running evaluation: {eval_id}")
    print(f"Model: {model}")
    print(f"Tasks: {len(all_tasks)}")
    print(f"Use Judge: {use_judge}")
    print(f"{'='*60}\n")

    results, stats = await run_async_evaluation(tasks=all_tasks, model=model, config=config, evaluation_id=eval_id)

    # Score responses
    print("\nScoring responses...")
    scored_results = []

    for result in results:
        task_id = result.get("task_id")
        task = next((t for t in all_tasks if t["task_id"] == task_id), None)

        if not task or result.get("error"):
            scored_results.append({"task_id": task_id, "error": result.get("error", "Task not found")})
            continue

        response = result.get("response", "")

        # Basic scoring
        basic_scores = score_response_basic(task, response)

        scored_result = {
            "task_id": task_id,
            "component": task.get("component"),
            "task_type": task.get("task_type"),
            "response_preview": response[:200] + "..." if len(response) > 200 else response,
            "cached": result.get("cached", False),
            **basic_scores,
        }

        scored_results.append(scored_result)

    # Run LLM-as-Judge if requested
    if use_judge:
        print("\nRunning LLM-as-Judge evaluation...")
        judge_client = AsyncBioEvalClient(model=model, config=config)

        judge_tasks = []
        for result in results:
            if not result.get("error"):
                task_id = result.get("task_id")
                task = next((t for t in all_tasks if t["task_id"] == task_id), None)
                if task:
                    judge_tasks.append((task, result.get("response", "")))

        for i, (task, response) in enumerate(judge_tasks):
            print(f"\rJudging: {i+1}/{len(judge_tasks)}", end="")
            judge_scores = await score_with_judge(task, response, judge_client)

            # Update scored result
            for sr in scored_results:
                if sr.get("task_id") == task["task_id"]:
                    sr.update(judge_scores)
                    break
        print()

    # Compute calibration metrics
    print("\nComputing calibration metrics...")
    calibration_results = []
    for sr in scored_results:
        if "confidence" in sr:
            conf = sr["confidence"]
            # Determine correctness based on available scores
            is_correct = (
                sr.get("effect_mentioned", False)
                or sr.get("numerical_accuracy", 0) > 0.8
                or sr.get("flaw_recall", 0) > 0.5
                or sr.get("pathway_coverage", 0) > 0.5
            )

            if conf["score"] >= 0.7:
                bucket = "high"
            elif conf["score"] >= 0.4:
                bucket = "medium"
            else:
                bucket = "low"

            calibration_results.append(
                CalibrationResult(
                    task_id=sr["task_id"],
                    confidence_score=conf["score"],
                    is_correct=is_correct,
                    confidence_bucket=bucket,
                    calibration_error=abs(conf["score"] - (1.0 if is_correct else 0.0)),
                )
            )

    calibration_metrics = compute_calibration_metrics(calibration_results)

    # Run error taxonomy annotation
    print("\nAnnotating errors with taxonomy...")
    from bioeval.taxonomy.annotator import annotate_response, summarize_annotations

    annotations = []
    for sr in scored_results:
        if "error" not in sr:
            conf = sr.get("confidence", {})
            is_correct = (
                sr.get("effect_mentioned", False)
                or sr.get("numerical_accuracy", 0) > 0.8
                or sr.get("flaw_recall", 0) > 0.5
                or sr.get("passed", False)
            )

            # Get response from results
            result = next((r for r in results if r.get("task_id") == sr["task_id"]), {})
            response = result.get("response", "")

            # Get ground truth from task
            task = next((t for t in all_tasks if t["task_id"] == sr["task_id"]), {})

            annotation = annotate_response(
                task_id=sr["task_id"],
                task_type=sr.get("task_type", ""),
                response=response,
                ground_truth=task.get("ground_truth", {}),
                confidence_score=conf.get("score", 0.5),
                is_correct=is_correct,
            )
            annotations.append(annotation)

            # Add annotation summary to scored result
            sr["error_annotation"] = {
                "error_count": annotation.error_count,
                "by_category": annotation.errors_by_category,
                "by_severity": annotation.errors_by_severity,
                "quality": annotation.overall_quality,
            }

    annotation_summary = summarize_annotations(annotations)

    # Aggregate results
    output = {
        "metadata": {
            "model": model,
            "timestamp": datetime.now().isoformat(),
            "evaluation_id": eval_id,
            "components": components,
            "use_judge": use_judge,
        },
        "summary": {
            "total_tasks": len(all_tasks),
            "completed": len([r for r in scored_results if "error" not in r]),
            "errors": len([r for r in scored_results if "error" in r]),
        },
        "execution_stats": stats,
        "calibration": {
            "expected_calibration_error": calibration_metrics.expected_calibration_error,
            "maximum_calibration_error": calibration_metrics.maximum_calibration_error,
            "overconfidence_rate": calibration_metrics.overconfidence_rate,
            "underconfidence_rate": calibration_metrics.underconfidence_rate,
            "brier_score": calibration_metrics.brier_score,
            "bucket_accuracies": calibration_metrics.bucket_accuracies,
            "bucket_counts": calibration_metrics.bucket_counts,
        },
        "error_taxonomy": annotation_summary,
        "results": scored_results,
    }

    # Compute component summaries
    for component in ["protoreason", "causalbio", "designcheck", "calibration", "adversarial"]:
        component_results = [r for r in scored_results if r.get("component") == component]
        if component_results:
            output["summary"][f"{component}_tasks"] = len(component_results)

    # Handle adversarial summary
    adversarial_results = [r for r in scored_results if r.get("component") == "adversarial"]
    if adversarial_results:
        passed = sum(1 for r in adversarial_results if r.get("passed", False))
        output["adversarial_summary"] = {
            "total": len(adversarial_results),
            "passed": passed,
            "pass_rate": passed / len(adversarial_results),
            "by_type": {},
        }
        for r in adversarial_results:
            t = r.get("adversarial_type", "unknown")
            if t not in output["adversarial_summary"]["by_type"]:
                output["adversarial_summary"]["by_type"][t] = {"passed": 0, "total": 0}
            output["adversarial_summary"]["by_type"][t]["total"] += 1
            if r.get("passed", False):
                output["adversarial_summary"]["by_type"][t]["passed"] += 1

    # Run multi-turn dialogues if requested (separate from async pipeline)
    if "multiturn" in components:
        print("\nRunning multi-turn dialogues...")
        from bioeval.multiturn.dialogues import MultiTurnEvaluator, DIALOGUES

        try:
            mt_evaluator = MultiTurnEvaluator(model_name=model)
            mt_results = mt_evaluator.run_all_dialogues()
            output["multiturn"] = mt_results
            print(f"  Completed {mt_results['total_dialogues']} dialogues")
            print(f"  Average score: {mt_results['average_score']:.2f}")
        except Exception as e:
            output["multiturn_error"] = str(e)
            print(f"  Error running multi-turn: {e}")
    elif "all" in components:
        # Just note it's available but don't run automatically (too slow)
        from bioeval.multiturn.dialogues import DIALOGUES

        output["multiturn_note"] = f"{len(DIALOGUES)} dialogues available - run with --component multiturn"

    return output


# =============================================================================
# CLI
# =============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="BioEval Enhanced Runner with async, caching, and LLM judge",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--model", "-m", default="claude-sonnet-4-20250514", help="Model to evaluate")
    parser.add_argument(
        "--component",
        "-c",
        nargs="+",
        choices=["all", "protoreason", "causalbio", "designcheck", "calibration", "adversarial", "multiturn"],
        default=["all"],
        help="Components to run",
    )
    parser.add_argument("--use-judge", "-j", action="store_true", help="Use LLM-as-Judge for semantic scoring")
    parser.add_argument("--max-concurrent", type=int, default=5, help="Max concurrent API calls")
    parser.add_argument("--no-cache", action="store_true", help="Disable response caching")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--run-multiturn", action="store_true", help="Actually run multi-turn dialogues (slow, sequential)")
    parser.add_argument("--cache-stats", action="store_true", help="Show cache statistics and exit")
    parser.add_argument("--clear-cache", action="store_true", help="Clear cache and exit")

    args = parser.parse_args()

    # Handle cache commands
    if args.cache_stats:
        cache = ResponseCache()
        stats = cache.get_stats()
        print("Cache Statistics:")
        print(f"  Total cached: {stats['total_cached']}")
        print(f"  By model: {stats['by_model']}")
        print(f"  Path: {stats['cache_path']}")
        return

    if args.clear_cache:
        cache = ResponseCache()
        cache.clear()
        print("Cache cleared")
        return

    # Check API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set")
        print("Run: export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)

    # Configure execution
    config = ExecutionConfig(max_concurrent=args.max_concurrent, cache_enabled=not args.no_cache)

    # Run evaluation
    output = asyncio.run(run_evaluation(components=args.component, model=args.model, use_judge=args.use_judge, config=config))

    # Save results
    if args.output:
        output_path = args.output
    else:
        os.makedirs("results", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_safe = args.model.replace("/", "_").replace(":", "_")
        output_path = f"results/{model_safe}_{timestamp}.json"

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2, default=str)

    # Print summary
    print(f"\n{'='*60}")
    print("EVALUATION COMPLETE")
    print(f"{'='*60}")
    print(f"Total tasks: {output['summary']['total_tasks']}")
    print(f"Completed: {output['summary']['completed']}")
    print(f"Errors: {output['summary']['errors']}")
    print(f"\nCalibration:")
    print(f"  ECE: {output['calibration']['expected_calibration_error']:.3f}")
    print(f"  Overconfidence rate: {output['calibration']['overconfidence_rate']:.1%}")
    print(f"  Bucket accuracies: {output['calibration']['bucket_accuracies']}")

    if "adversarial_summary" in output:
        print(f"\nAdversarial Robustness:")
        print(f"  Pass rate: {output['adversarial_summary']['pass_rate']:.1%}")
        print(f"  Passed: {output['adversarial_summary']['passed']}/{output['adversarial_summary']['total']}")

    if "error_taxonomy" in output:
        et = output["error_taxonomy"]
        print(f"\nError Taxonomy:")
        print(f"  Total errors detected: {et.get('total_errors', 0)}")
        print(f"  Avg errors/response: {et.get('avg_errors_per_response', 0):.2f}")
        if et.get("errors_by_severity"):
            print(f"  By severity: {et['errors_by_severity']}")

    if "multiturn" in output:
        mt = output["multiturn"]
        print(f"\nMulti-Turn Dialogues:")
        print(f"  Dialogues: {mt.get('total_dialogues', 0)}")
        print(f"  Avg score: {mt.get('average_score', 0):.2f}")
        print(f"  Memory score: {mt.get('average_memory_score', 0):.2f}")

    print(f"\nExecution:")
    print(f"  API calls: {output['execution_stats']['api_calls']}")
    print(f"  Cache hits: {output['execution_stats']['cache_hits']}")
    print(f"  Cache hit rate: {output['execution_stats']['cache_hit_rate']:.1%}")
    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
