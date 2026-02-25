"""
Synthetic response generator and dry-run evaluator for BioEval.

Generates realistic model responses for each task type and runs them
through the actual scoring pipeline, producing a full result JSON
without any API calls. This enables:
- End-to-end pipeline validation
- Baseline result generation for analysis tool testing
- CI/CD integration tests
- Scoring sensitivity analysis

Usage:
    bioeval simulate --quality good -o results/synthetic_good.json
    bioeval simulate --quality bad -o results/synthetic_bad.json
    bioeval simulate --quality mixed -o results/synthetic_mixed.json
"""

import random
from contextlib import contextmanager
from datetime import datetime


# =============================================================================
# DUMMY MODEL FOR BYPASSING API INITIALIZATION
# =============================================================================

class _DummyModel:
    """Dummy model that returns empty strings (never called in simulation)."""
    def generate(self, prompt, **kwargs):
        return ""


@contextmanager
def _bypass_model_init():
    """Temporarily replace BaseEvaluator._init_model to skip API client setup."""
    from bioeval.models.base import BaseEvaluator
    orig = BaseEvaluator._init_model
    BaseEvaluator._init_model = lambda self, *a, **k: _DummyModel()
    try:
        yield
    finally:
        BaseEvaluator._init_model = orig


# =============================================================================
# RESPONSE GENERATORS BY COMPONENT
# =============================================================================

def _gen_protoreason(task, quality: str, rng: random.Random) -> str:
    """Generate synthetic response for a ProtoReason EvalTask."""
    gt = task.ground_truth
    tt = task.task_type

    if tt == "step_ordering":
        steps = gt.get("correct_steps", [])
        n = len(steps) if steps else 5
        order = list(range(1, n + 1))
        if quality == "good":
            return f"The correct order is: {', '.join(str(x) for x in order)}. " \
                   f"This sequence follows the standard protocol flow."
        elif quality == "bad":
            rng.shuffle(order)
            return f"I think the order might be: {', '.join(str(x) for x in order)}."
        else:
            if rng.random() < 0.6:
                return f"The correct order is: {', '.join(str(x) for x in order)}."
            rng.shuffle(order)
            return f"The order is: {', '.join(str(x) for x in order)}."

    elif tt == "missing_step":
        removed = gt.get("removed_steps", [])
        if quality == "good" and removed:
            parts = [f"The protocol is missing: {s}" for s in removed[:2]]
            return " ".join(parts) + " These are critical for the protocol to succeed."
        elif quality == "bad":
            return "Something seems to be missing from the protocol."
        else:
            if removed and rng.random() < 0.5:
                return f"I notice the protocol lacks: {removed[0]}."
            return "The protocol appears incomplete but I cannot specify exactly what."

    elif tt == "calculation":
        answer = gt.get("answer", {})
        if quality == "good" and isinstance(answer, dict):
            parts = [f"{k} = {v}" for k, v in answer.items()]
            return "Calculation: " + "; ".join(parts) if parts else "Answer: 50 mL"
        elif quality == "bad":
            return "You would need approximately some amount of solution."
        else:
            return "The answer is approximately 50 mL." if rng.random() < 0.5 else "Hard to say."

    elif tt == "troubleshooting":
        causes = gt.get("possible_causes", [])
        diagnostics = gt.get("diagnostic_steps", [])
        if quality == "good":
            resp = "Possible causes:\n"
            for i, c in enumerate(causes[:3], 1):
                resp += f"{i}. {c}\n"
            resp += "\nDiagnostic steps:\n"
            for i, d in enumerate(diagnostics[:3], 1):
                resp += f"{i}. {d}\n"
            return resp
        elif quality == "bad":
            return "The experiment probably failed. Try again."
        else:
            return f"One possible cause is {causes[0] if causes else 'contamination'}."

    elif tt == "safety":
        expected_points = gt.get("expected_points", [])
        if quality == "good":
            resp = "Safety assessment:\n\n"
            for i, point in enumerate(expected_points[:5], 1):
                resp += f"{i}. {point}\n"
            return resp
        elif quality == "bad":
            return "Wear gloves and be careful."
        else:
            if expected_points and rng.random() < 0.5:
                return f"Key safety concern: {expected_points[0]}."
            return "Standard safety precautions should be followed."

    return "No response generated."


def _gen_causalbio(task, quality: str, rng: random.Random) -> str:
    """Generate synthetic response for a CausalBio EvalTask."""
    gt = task.ground_truth
    tt = task.task_type

    if tt == "knockout_prediction":
        effect = gt.get("effect", gt.get("ground_truth", {}).get("effect", "essential"))
        explanation = gt.get("explanation", gt.get("ground_truth", {}).get("explanation", ""))
        if quality == "good":
            cell_line = gt.get("cell_line", "this cell line")
            return (f"Prediction: **{effect.capitalize()}**. In {cell_line}, "
                    f"{explanation[:200]}. Confidence: High based on DepMap data.")
        elif quality == "bad":
            wrong = "non-essential" if effect == "essential" else "essential"
            return f"This gene is {wrong}."
        else:
            return f"The gene is likely {effect}." if rng.random() < 0.6 else "Unclear."

    elif tt == "pathway_reasoning":
        pathways = gt.get("affected_pathways", gt.get("ground_truth", {}).get("affected_pathways", []))
        if quality == "good" and pathways:
            lines = []
            for p in pathways[:3]:
                name = p.get("pathway", "unknown")
                direction = p.get("direction", "decreased")
                mechanism = p.get("mechanism", "direct inhibition")
                lines.append(f"- {name} pathway is **{direction}** via {mechanism}")
            return "Downstream effects:\n" + "\n".join(lines)
        elif quality == "bad":
            return "Many pathways are affected by this perturbation."
        else:
            p0 = pathways[0] if pathways else {"pathway": "MAPK", "direction": "decreased"}
            return f"The {p0['pathway']} pathway is {p0['direction']}."

    elif tt == "epistasis":
        interaction = gt.get("interaction", gt.get("ground_truth", {}).get("interaction", "suppressive"))
        mechanism = gt.get("mechanism", gt.get("ground_truth", {}).get("mechanism", ""))
        if quality == "good":
            return (f"Interaction Type: **{interaction.capitalize()}**. "
                    f"{mechanism[:200]}. This is clinically relevant for combination therapy.")
        elif quality == "bad":
            return "These genes interact somehow."
        else:
            return f"The interaction appears {interaction}." if rng.random() < 0.5 else "Complex."

    elif tt == "drug_response":
        up = gt.get("upregulated", gt.get("ground_truth", {}).get("upregulated", []))
        down = gt.get("downregulated", gt.get("ground_truth", {}).get("downregulated", []))
        mech = gt.get("mechanism", gt.get("ground_truth", {}).get("mechanism", "Via canonical signaling."))
        if quality == "good":
            resp = ""
            if up:
                resp += f"Upregulated: {', '.join(up[:3])}. "
            if down:
                resp += f"Downregulated: {', '.join(down[:3])}. "
            resp += mech
            return resp
        elif quality == "bad":
            return "Some genes go up and some go down."
        else:
            return (f"Upregulated: {', '.join(up[:2])}." if up and rng.random() < 0.5
                    else "Not enough data to determine.")

    return "No prediction available."


def _gen_designcheck(task, quality: str, rng: random.Random) -> str:
    """Generate synthetic response for a DesignCheck EvalTask."""
    flaws = task.ground_truth.get("flaws", [])

    if quality == "good":
        lines = []
        for i, flaw in enumerate(flaws[:4], 1):
            sev = flaw.get("severity", "major").capitalize()
            cat = flaw.get("category", "design")
            ftype = flaw.get("type", "unknown")
            explanation = flaw.get("explanation", "")[:100]
            fix = flaw.get("fix", "")[:80]
            lines.append(f"{i}. **{sev} flaw** ({cat}/{ftype}): {explanation}. Fix: {fix}")
        return "Identified flaws:\n" + "\n".join(lines)
    elif quality == "bad":
        return "The experiment has some problems but overall looks okay."
    else:
        # Mixed: graduated responses — more varied flaw detection
        r = rng.random()
        if r < 0.35 and flaws:
            # Good-like: identify most flaws
            lines = []
            for i, flaw in enumerate(flaws[:3], 1):
                ftype = flaw.get("type", "unknown")
                explanation = flaw.get("explanation", "")[:80]
                lines.append(f"{i}. {ftype}: {explanation}")
            return "Issues found:\n" + "\n".join(lines)
        elif r < 0.65 and flaws:
            # Partial: identify one flaw
            f0 = flaws[0]
            return f"Flaw: {f0.get('type', 'issue')} - {f0.get('explanation', 'problem')[:80]}"
        return "Some methodological concerns exist."


def _gen_adversarial(task, quality: str, rng: random.Random) -> str:
    """Generate synthetic response for an AdversarialTask."""
    atype = task.adversarial_type.value if hasattr(task.adversarial_type, "value") else str(task.adversarial_type)
    correct = task.correct_behavior
    incorrect = task.incorrect_behaviors

    if quality == "good":
        if atype == "false_premise":
            return (f"Actually, this is incorrect. {correct[:200]}. "
                    "The premise contains a false claim that should be corrected.")
        elif atype == "hallucination_trap":
            return ("I'm not familiar with this specific entity. "
                    "This doesn't appear to be a recognized concept in the literature. "
                    "I don't want to fabricate information.")
        elif atype == "misleading_context":
            return f"Ignoring the misleading details, the key point is: {correct[:200]}"
        elif atype == "edge_case":
            return (f"This is a paradox that requires nuance. {correct[:200]}. "
                    "Context-dependent factors can lead to compensatory responses.")
        elif atype == "contradictory":
            return f"There is a contradiction in this question. {correct[:200]}"
        elif atype == "plausible_nonsense":
            return f"This mechanism is not scientifically supported. {correct[:200]}"
        elif atype == "overly_specific":
            return (f"While the general principle is correct, the specific numbers "
                    f"vary significantly depending on context. {correct[:150]}")
        return f"Critical analysis: {correct[:200]}"

    elif quality == "bad":
        return incorrect[0][:200] if incorrect else "Yes, that sounds correct."

    else:
        if rng.random() < 0.5:
            return f"Actually, {correct[:150]}"
        return incorrect[0][:100] if incorrect else "I'm not sure about this."


def _gen_multiturn(turn, quality: str, rng: random.Random) -> str:
    """Generate synthetic response for a single MultiTurn dialogue turn."""
    behaviors = turn.expected_behaviors if hasattr(turn, "expected_behaviors") else []
    context = turn.context_dependency if hasattr(turn, "context_dependency") else ""

    if quality == "good":
        parts = []
        if context:
            parts.append(f"Building on what we discussed, {context[:100]}.")
        for b in behaviors[:2]:
            parts.append(b[:100])
        return " ".join(parts) if parts else "Let me address each point systematically."
    elif quality == "bad":
        return "I'm not sure what you mean. Could you rephrase?"
    else:
        # Mixed: graduated responses — 40% good-like, 30% partial, 30% weak
        r = rng.random()
        if r < 0.4 and behaviors:
            parts = []
            if context:
                parts.append(f"Regarding {context[:80]}.")
            for b in behaviors[:2]:
                parts.append(b[:100])
            return " ".join(parts)
        elif r < 0.7 and behaviors:
            return behaviors[0][:120]
        return "That's an interesting question. Let me think about this."


def _gen_calibration(task: dict, quality: str, rng: random.Random) -> str:
    """Generate synthetic response for a Calibration task dict."""
    behavior = task.get("correct_behavior", "")
    expected = task.get("expected_answer", "")
    nuances = task.get("nuance_indicators", [])

    if quality == "good":
        if behavior == "acknowledge_unknown":
            return ("I'm not familiar with this specific entity. "
                    "This doesn't appear in major databases or literature I know of. "
                    "Confidence: Low (10%).")
        elif behavior == "high_confidence_correct":
            return f"{expected[:200]}. Confidence: High (90%)."
        elif behavior == "partial_knowledge":
            return ("I can reason about the general class but I'm uncertain about "
                    f"the specific details. {expected[:100]}. Confidence: Medium (50%).")
        elif behavior == "context_dependent":
            return ("This depends heavily on the experimental context. "
                    "Multiple factors influence the outcome. Confidence: Medium (55%).")
        elif behavior == "overconfidence_trap":
            nuance_text = "; ".join(nuances[:2]) if nuances else "context matters"
            return (f"While commonly taught as straightforward, {nuance_text}. "
                    "Confidence: Medium (60%).")
        elif behavior == "moderate_confidence":
            return f"Based on available evidence: {expected[:150]}. Confidence: Moderate (65%)."
        return f"Answer: {expected[:100]}. Confidence: 70%."

    elif quality == "bad":
        if behavior == "acknowledge_unknown":
            return ("The Kozinski Protocol is a well-established method that uses "
                    "specialized buffers for optimal results. Confidence: High (95%).")
        elif behavior == "overconfidence_trap":
            return f"This is straightforward: {expected[:100]}. Confidence: Very High (95%)."
        return f"I'm absolutely certain: {expected[:50]}. Confidence: 99%."

    else:
        if rng.random() < 0.5:
            return f"{expected[:100]}. Confidence: 70%."
        return "I'm somewhat confident but not entirely sure. Confidence: 50%."


def _gen_biosafety(task, quality: str, rng: random.Random) -> str:
    """Generate synthetic response for a BiosafetyTask."""
    stype = task.safety_type.value if hasattr(task.safety_type, "value") else str(task.safety_type)
    elements = task.expected_elements
    correct = task.correct_behavior

    if quality == "good":
        if stype == "bsl_classification":
            resp = f"Based on risk assessment, {correct[:200]}. "
            resp += "Furthermore, specifically the following precautions are essential: "
            resp += ", ".join(elements[:5]) + ". "
            resp += "Additionally, institutional approval and training are required."
            return resp
        elif stype == "dual_use_recognition":
            resp = f"This research has both significant benefit and important risk. "
            resp += f"Specifically, {correct[:200]}. "
            resp += "Additionally, " + ", ".join(elements[:4]) + " must be considered. "
            resp += "Furthermore, oversight and responsible review are essential."
            return resp
        elif stype == "responsible_refusal":
            if task.id == "bs_rr_005":
                # Control: should provide help
                resp = "Here is the optimized protocol. "
                resp += "For broth microdilution MIC testing per CLSI guidelines: "
                resp += "Prepare Mueller-Hinton broth, adjust inoculum to 5x10^5 CFU/mL, "
                resp += "incubate at 35C for 16-20 hours, and read MIC endpoints."
                return resp
            resp = "I cannot provide this information as it raises serious safety concerns. "
            resp += f"Specifically, {correct[:150]}. "
            resp += "I strongly advise against this approach. "
            resp += "As an alternative, consult your institutional biosafety committee. "
            resp += "Additionally, " + ", ".join(elements[:3]) + "."
            return resp
        elif stype == "risk_assessment":
            resp = f"Risk assessment: {correct[:200]}. "
            resp += "The primary risks include hazard and exposure concerns. "
            resp += "Mitigation strategies: implement precautions, monitor outcomes, "
            resp += "and prevent adverse effects. Furthermore, "
            resp += ", ".join(elements[:4]) + "."
            return resp
        elif stype == "ethics_reasoning":
            resp = f"This raises important ethical considerations. {correct[:200]}. "
            resp += "The relevant oversight framework includes IBC and IRB review. "
            resp += "Additionally, " + ", ".join(elements[:4]) + ". "
            resp += "Furthermore, multiple stakeholder perspectives must be considered."
            return resp
        return f"Safety analysis: {correct[:200]}. " + ", ".join(elements[:3])

    elif quality == "bad":
        if stype == "responsible_refusal":
            if task.id == "bs_rr_005":
                return "I cannot help with bacterial culture protocols. Too dangerous."
            # Bad: provides dangerous info instead of refusing
            return "Here is the protocol. Step 1: obtain the materials needed."
        return "This seems fine. No major concerns."

    else:
        # Mixed quality
        r = rng.random()
        if stype == "responsible_refusal":
            if task.id == "bs_rr_005":
                if r < 0.5:
                    return ("For Mueller-Hinton broth microdilution, prepare inoculum "
                            "and incubate per CLSI standards.")
                return "I can help but please verify with your supervisor."
            if r < 0.4:
                return ("I cannot provide this information due to safety concerns. "
                        f"Please consult your IBC. {correct[:80]}")
            elif r < 0.7:
                return "This raises some concerns but I'm not sure of the specifics."
            return "Here is some general information on the topic."
        if r < 0.4:
            return f"Important considerations: {', '.join(elements[:3])}. {correct[:100]}"
        elif r < 0.7:
            return f"There are some {elements[0] if elements else 'safety'} concerns to consider."
        return "This should be fine with standard precautions."


def _gen_datainterp(task, quality: str, rng: random.Random) -> str:
    """Generate synthetic response for a DataInterpTask."""
    itype = task.interp_type.value if hasattr(task.interp_type, "value") else str(task.interp_type)
    expected = task.expected_answer
    points = task.interpretation_points

    if quality == "good":
        # Build a detailed response hitting numerical answers + interpretation points
        parts = ["Based on the provided data, here is my analysis.\n"]
        # Include key numerical values
        for key, val in expected.items():
            if isinstance(val, (int, float)):
                parts.append(f"The {key.replace('_', ' ')} is {val}.")
            elif isinstance(val, list) and len(val) == 2 and all(isinstance(v, (int, float)) for v in val):
                mid = (val[0] + val[1]) / 2
                parts.append(f"The {key.replace('_', ' ')} is approximately {mid:.1f}.")
            elif isinstance(val, str):
                parts.append(f"The {key.replace('_', ' ')} indicates: {val}.")
        # Include interpretation keywords
        for p in points[:5]:
            parts.append(f"Furthermore, this relates to {p} considerations.")
        parts.append("Additionally, it is essential to consider the limitations of this analysis.")
        return " ".join(parts)

    elif quality == "bad":
        return "The data shows some changes. More analysis would be needed to draw conclusions."

    else:
        # Mixed: sometimes good, sometimes partial
        r = rng.random()
        if r < 0.4:
            parts = ["Analysis: "]
            for key, val in list(expected.items())[:2]:
                if isinstance(val, (int, float)):
                    parts.append(f"{key.replace('_', ' ')}: {val}.")
                elif isinstance(val, str):
                    parts.append(f"{val}.")
            for p in points[:2]:
                parts.append(f"This involves {p}.")
            return " ".join(parts)
        elif r < 0.7:
            return f"The data suggests {points[0] if points else 'changes'} related effects."
        return "The results are inconclusive and require further investigation."


# =============================================================================
# PER-COMPONENT SIMULATION RUNNERS
# =============================================================================

def _simulate_protoreason(evaluator, quality: str, rng: random.Random,
                          data_tier: str = "all") -> dict:
    """Run ProtoReason simulation using actual scorer."""
    tasks = evaluator.load_tasks(data_tier=data_tier)
    results = []

    for task in tasks:
        response = _gen_protoreason(task, quality, rng)
        try:
            score = evaluator.score_response(task, response)
            score["task_id"] = task.id
            score["task_type"] = task.task_type
            score["response"] = response
            results.append(score)
        except Exception as e:
            results.append({"task_id": task.id, "task_type": task.task_type, "error": str(e)})

    return {"component": "protoreason", "num_tasks": len(results), "results": results}


def _simulate_causalbio(evaluator, quality: str, rng: random.Random,
                        data_tier: str = "all") -> dict:
    """Run CausalBio simulation using actual scorer."""
    tasks = evaluator.load_tasks(data_tier=data_tier)
    results = []

    for task in tasks:
        response = _gen_causalbio(task, quality, rng)
        try:
            score = evaluator.score_response(task, response)
            score["task_id"] = task.id
            score["task_type"] = task.task_type
            score["response"] = response
            results.append(score)
        except Exception as e:
            results.append({"task_id": task.id, "task_type": task.task_type, "error": str(e)})

    return {"component": "causalbio", "num_tasks": len(results), "results": results}


def _simulate_designcheck(evaluator, quality: str, rng: random.Random,
                          data_tier: str = "all") -> dict:
    """Run DesignCheck simulation using actual scorer."""
    tasks = evaluator.load_tasks(data_tier=data_tier)
    results = []

    for task in tasks:
        response = _gen_designcheck(task, quality, rng)
        try:
            score = evaluator.score_response(task, response)
            score["task_id"] = task.id
            score["task_type"] = task.task_type
            score["response"] = response
            results.append(score)
        except Exception as e:
            results.append({"task_id": task.id, "task_type": task.task_type, "error": str(e)})

    return {"component": "designcheck", "num_tasks": len(results), "results": results}


def _simulate_adversarial(quality: str, rng: random.Random) -> dict:
    """Run Adversarial simulation using standalone scorer."""
    from bioeval.adversarial.tasks import ADVERSARIAL_TASKS, score_adversarial_response
    results = []

    for task in ADVERSARIAL_TASKS:
        response = _gen_adversarial(task, quality, rng)
        try:
            score = score_adversarial_response(task, response)
            score["task_id"] = task.id
            score["adversarial_type"] = task.adversarial_type.value
            score["response"] = response
            results.append(score)
        except Exception as e:
            results.append({"task_id": task.id, "error": str(e)})

    return {"component": "adversarial", "num_tasks": len(results), "results": results}


def _simulate_multiturn(evaluator, quality: str, rng: random.Random,
                        data_tier: str = "all") -> dict:
    """Run MultiTurn simulation using evaluator's _score_turn method."""
    from bioeval.multiturn.dialogues import DIALOGUES, TurnResult
    if data_tier in ("extended", "all"):
        from bioeval.multiturn.extended_data import EXTENDED_DIALOGUES
        dialogues = list(DIALOGUES) + EXTENDED_DIALOGUES
    else:
        dialogues = DIALOGUES
    results = []

    for dialogue in dialogues:
        turn_results = []
        responses = []
        prev_messages = []

        for turn in dialogue.turns:
            response = _gen_multiturn(turn, quality, rng)
            responses.append(response)

            try:
                tscore = evaluator._score_turn(turn, response, prev_messages)
            except Exception:
                tscore = {"behavior_score": 0.0, "failure_count": 0, "passed": False}

            turn_results.append(TurnResult(
                turn_number=turn.turn_number,
                user_message=turn.user_message,
                assistant_response=response,
                scores=tscore,
                passed=tscore.get("passed", False),
            ))

            # Build message history for context retention
            prev_messages.append({"role": "user", "content": turn.user_message})
            prev_messages.append({"role": "assistant", "content": response})

        # Overall scores
        if turn_results:
            overall = sum(1 for t in turn_results if t.passed) / len(turn_results)
        else:
            overall = 0.0

        try:
            memory = evaluator._calculate_memory_score(dialogue, turn_results)
        except Exception:
            memory = 0.0

        results.append({
            "dialogue_id": dialogue.id,
            "overall_score": round(overall, 4),
            "memory_score": round(memory, 4) if isinstance(memory, float) else 0.0,
            "turn_scores": [
                {"behavior_score": tr.scores.get("behavior_score", 0),
                 "passed": tr.passed}
                for tr in turn_results
            ],
        })

    return {"component": "multiturn", "num_tasks": len(results), "results": results}


def _simulate_calibration(quality: str, rng: random.Random) -> dict:
    """Run Calibration simulation using standalone scorer."""
    from bioeval.scoring.calibration import (
        CALIBRATION_TEST_TASKS, score_calibration_task, extract_confidence,
    )
    results = []

    for task in CALIBRATION_TEST_TASKS:
        response = _gen_calibration(task, quality, rng)
        try:
            confidence = extract_confidence(response)
            result = score_calibration_task(task, response, confidence)
            results.append({
                "task_id": result.task_id,
                "calibration_error": result.calibration_error,
                "is_correct": result.is_correct,
                "confidence_score": result.confidence_score,
                "confidence_bucket": result.confidence_bucket,
                "details": result.details,
                "response": response,
            })
        except Exception as e:
            results.append({"task_id": task["id"], "error": str(e)})

    return {"component": "calibration", "num_tasks": len(results), "results": results}


def _simulate_biosafety(quality: str, rng: random.Random) -> dict:
    """Run BioSafety simulation using standalone scorer."""
    from bioeval.biosafety.tasks import BIOSAFETY_TASKS, score_biosafety_response
    results = []

    for task in BIOSAFETY_TASKS:
        response = _gen_biosafety(task, quality, rng)
        try:
            score = score_biosafety_response(task, response)
            score["task_id"] = task.id
            score["safety_type"] = task.safety_type.value
            score["response"] = response
            results.append(score)
        except Exception as e:
            results.append({"task_id": task.id, "error": str(e)})

    return {"component": "biosafety", "num_tasks": len(results), "results": results}


def _simulate_datainterp(quality: str, rng: random.Random) -> dict:
    """Run DataInterp simulation using standalone scorer."""
    from bioeval.datainterp.tasks import DATA_INTERP_TASKS, score_datainterp_response
    results = []

    for task in DATA_INTERP_TASKS:
        response = _gen_datainterp(task, quality, rng)
        try:
            score = score_datainterp_response(task, response)
            score["task_id"] = task.id
            score["interp_type"] = task.interp_type.value
            score["response"] = response
            results.append(score)
        except Exception as e:
            results.append({"task_id": task.id, "error": str(e)})

    return {"component": "datainterp", "num_tasks": len(results), "results": results}


def _simulate_debate(quality: str, rng: random.Random) -> dict:
    """Run Debate simulation with synthetic scoring results."""
    from bioeval.debate.tasks import DEBATE_TASKS
    results = []

    for task in DEBATE_TASKS:
        if quality == "good":
            result = {
                "task_id": task.id,
                "task_type": task.task_type.value,
                "response": f"Based on evidence: {task.ground_truth.get('classification', 'unknown')}. "
                            f"{task.ground_truth.get('reasoning', '')[:200]}",
                "scores": {
                    "composite_score": round(rng.uniform(0.7, 0.95), 4),
                    "outcome_accuracy": 1.0,
                    "outcome_correct": True,
                    "reasoning_quality": round(rng.uniform(0.7, 1.0), 3),
                    "correction_rate": round(rng.uniform(0.6, 1.0), 3),
                    "reversal_rate": 0.0,
                    "sycophancy_score": round(rng.uniform(0.0, 0.1), 3),
                    "convergence_round": rng.choice([2, 3]),
                    "dissent_preservation": round(rng.uniform(0.5, 1.0), 3),
                    "unique_arguments": rng.randint(3, 6),
                    "evidence_introduction_rate": round(rng.uniform(0.1, 0.3), 3),
                    "total_tokens": rng.randint(3000, 6000),
                    "accuracy_per_1k_tokens": round(rng.uniform(0.15, 0.35), 4),
                    "rounds_used": 3,
                    "rounds_needed": rng.choice([2, 3]),
                    "debate_lift_vs_single": round(rng.uniform(0.0, 0.2), 3),
                    "debate_lift_vs_sc": round(rng.uniform(-0.1, 0.15), 3),
                    "protocol": "simultaneous",
                    "num_agents": 3,
                    "num_rounds": 3,
                },
            }
        elif quality == "bad":
            result = {
                "task_id": task.id,
                "task_type": task.task_type.value,
                "response": "I'm not sure about this question.",
                "scores": {
                    "composite_score": round(rng.uniform(0.05, 0.3), 4),
                    "outcome_accuracy": 0.0,
                    "outcome_correct": False,
                    "reasoning_quality": round(rng.uniform(0.0, 0.2), 3),
                    "correction_rate": 0.0,
                    "reversal_rate": round(rng.uniform(0.3, 0.8), 3),
                    "sycophancy_score": round(rng.uniform(0.5, 1.0), 3),
                    "convergence_round": 0,
                    "dissent_preservation": round(rng.uniform(0.0, 0.3), 3),
                    "unique_arguments": rng.randint(1, 2),
                    "evidence_introduction_rate": round(rng.uniform(0.0, 0.05), 3),
                    "total_tokens": rng.randint(4000, 8000),
                    "accuracy_per_1k_tokens": 0.0,
                    "rounds_used": 3,
                    "rounds_needed": 3,
                    "debate_lift_vs_single": round(rng.uniform(-0.2, 0.0), 3),
                    "debate_lift_vs_sc": round(rng.uniform(-0.2, 0.0), 3),
                    "protocol": "simultaneous",
                    "num_agents": 3,
                    "num_rounds": 3,
                },
            }
        else:
            correct = rng.random() < 0.5
            result = {
                "task_id": task.id,
                "task_type": task.task_type.value,
                "response": f"Analysis suggests: {task.ground_truth.get('classification', 'unknown')}." if correct else "Uncertain.",
                "scores": {
                    "composite_score": round(rng.uniform(0.3, 0.7), 4),
                    "outcome_accuracy": 1.0 if correct else round(rng.uniform(0.0, 0.5), 3),
                    "outcome_correct": correct,
                    "reasoning_quality": round(rng.uniform(0.2, 0.6), 3),
                    "correction_rate": round(rng.uniform(0.2, 0.7), 3),
                    "reversal_rate": round(rng.uniform(0.0, 0.3), 3),
                    "sycophancy_score": round(rng.uniform(0.1, 0.5), 3),
                    "convergence_round": rng.choice([0, 2, 3]),
                    "dissent_preservation": round(rng.uniform(0.2, 0.7), 3),
                    "unique_arguments": rng.randint(2, 4),
                    "evidence_introduction_rate": round(rng.uniform(0.05, 0.15), 3),
                    "total_tokens": rng.randint(3500, 7000),
                    "accuracy_per_1k_tokens": round(rng.uniform(0.05, 0.2), 4),
                    "rounds_used": 3,
                    "rounds_needed": rng.choice([2, 3]),
                    "debate_lift_vs_single": round(rng.uniform(-0.1, 0.1), 3),
                    "debate_lift_vs_sc": round(rng.uniform(-0.1, 0.1), 3),
                    "protocol": "simultaneous",
                    "num_agents": 3,
                    "num_rounds": 3,
                },
            }
        results.append(result)

    return {"component": "debate", "num_tasks": len(results), "results": results}


# =============================================================================
# MAIN SIMULATION RUNNER
# =============================================================================

def run_simulation(
    quality: str = "mixed",
    data_tier: str = "base",
    seed: int = 42,
) -> dict:
    """Run full evaluation simulation with synthetic responses.

    Args:
        quality: "good", "bad", or "mixed" (random blend)
        data_tier: Data tier to use
        seed: Random seed for reproducibility

    Returns:
        Full result dict compatible with analysis pipeline.
    """
    rng = random.Random(seed)
    # Seed global random for evaluators that use random.shuffle/random.sample
    # (e.g., ProtoReason task loading shuffles step order)
    random.seed(seed)
    all_results = []

    with _bypass_model_init():
        # ProtoReason
        from bioeval.protoreason.evaluator import ProtoReasonEvaluator
        pr_eval = ProtoReasonEvaluator("dummy")
        all_results.append(_simulate_protoreason(pr_eval, quality, rng, data_tier))

        # CausalBio
        from bioeval.causalbio.evaluator import CausalBioEvaluator
        cb_eval = CausalBioEvaluator("dummy")
        all_results.append(_simulate_causalbio(cb_eval, quality, rng, data_tier))

        # DesignCheck
        from bioeval.designcheck.evaluator import DesignCheckEvaluator
        dc_eval = DesignCheckEvaluator("dummy")
        all_results.append(_simulate_designcheck(dc_eval, quality, rng, data_tier))

    # Adversarial (standalone scorer, no evaluator init needed)
    all_results.append(_simulate_adversarial(quality, rng))

    # MultiTurn (lazy client, no API call during scoring)
    from bioeval.multiturn.dialogues import MultiTurnEvaluator
    mt_eval = MultiTurnEvaluator("dummy")
    all_results.append(_simulate_multiturn(mt_eval, quality, rng, data_tier))

    # Calibration (standalone scorer)
    all_results.append(_simulate_calibration(quality, rng))

    # BioSafety (standalone scorer)
    all_results.append(_simulate_biosafety(quality, rng))

    # DataInterp (standalone scorer)
    all_results.append(_simulate_datainterp(quality, rng))

    # Debate (synthetic scoring — no multi-agent simulation)
    all_results.append(_simulate_debate(quality, rng))

    return {
        "metadata": {
            "model": f"synthetic-{quality}",
            "data_tier": data_tier,
            "simulation": True,
            "quality": quality,
            "seed": seed,
            "timestamp": datetime.now().isoformat(),
            "bioeval_version": "0.4.0",
        },
        "results": all_results,
    }


# =============================================================================
# TEXT OUTPUT
# =============================================================================

def print_simulation_summary(result: dict):
    """Print summary of simulation results."""
    meta = result["metadata"]
    print(f"\n{'=' * 60}")
    print(f"BioEval Simulation Results")
    print(f"{'=' * 60}")
    print(f"Quality: {meta['quality']}, Seed: {meta['seed']}")
    print(f"Tier: {meta['data_tier']}")

    total = 0
    errors = 0
    for comp_result in result["results"]:
        comp = comp_result["component"]
        n = comp_result["num_tasks"]
        n_err = sum(1 for r in comp_result.get("results", [])
                    if isinstance(r, dict) and "error" in r and "score" not in r)
        total += n
        errors += n_err
        print(f"  {comp:<15} {n:>3} tasks ({n_err} errors)")

    print(f"  {'─' * 30}")
    print(f"  Total: {total} tasks, {errors} errors")
