"""
DebateEvaluator: CLI-compatible evaluator for multi-agent debate.

Standalone evaluator (does not extend BaseEvaluator) because debate
requires multiple model instances via AgentModelPool.
"""

from typing import Optional

from bioeval.debate.agents import (
    AgentModelPool,
    create_heterogeneous_panel,
    create_homogeneous_panel,
)
from bioeval.debate.protocols import (
    DebateConfig,
    ProtocolType,
    TerminationCondition,
    create_protocol,
)
from bioeval.debate.scoring import score_debate
from bioeval.debate.tasks import DEBATE_TASKS, DebateTask, score_debate_task_outcome


class _DebateTaskAdapter:
    """Wraps DebateTask so CLI can access .id and .task_type (str)."""

    def __init__(self, task: DebateTask):
        self.id = task.id
        self.task_type = task.task_type.value  # str
        self.debate_task = task
        self.prompt = task.scenario
        self.ground_truth = task.ground_truth


class DebateEvaluator:
    """Multi-agent debate evaluator.

    Not a BaseEvaluator subclass — manages its own AgentModelPool.
    """

    def __init__(
        self,
        model_name: str = "claude-sonnet-4-20250514",
        protocol: str = "simultaneous",
        num_agents: int = 3,
        max_rounds: int = 3,
        agent_models: Optional[list[str]] = None,
        include_baseline: bool = True,
    ):
        self.model_name = model_name
        self.protocol_type = ProtocolType(protocol)
        self.num_agents = num_agents
        self.max_rounds = max_rounds
        self.include_baseline = include_baseline

        # Build panel
        if agent_models:
            self.panel = create_heterogeneous_panel(
                agent_models,
                with_judge=(self.protocol_type == ProtocolType.JUDGE_MEDIATED),
                judge_model=model_name,
            )
        else:
            self.panel = create_homogeneous_panel(
                model_name,
                n_agents=num_agents,
                with_judge=(self.protocol_type == ProtocolType.JUDGE_MEDIATED),
            )

        # Config
        self.config = DebateConfig(
            protocol_type=self.protocol_type,
            max_rounds=max_rounds,
            termination=TerminationCondition.ADAPTIVE,
            include_self_consistency=include_baseline,
            self_consistency_samples=3,
        )

        # Model pool (lazy — models created on first generate())
        self.model_pool = AgentModelPool()

    def load_tasks(self) -> list[_DebateTaskAdapter]:
        return [_DebateTaskAdapter(t) for t in DEBATE_TASKS]

    def evaluate_task(self, task) -> dict:
        """Run debate on a single task and return result dict.

        Args:
            task: _DebateTaskAdapter (from load_tasks) or DebateTask.

        Returns:
            dict with keys: task_id, response, scores, debate_trace.
        """
        dt = task.debate_task if hasattr(task, "debate_task") else task

        task_metadata = {
            "task_id": dt.id,
            "answer_options": dt.answer_options,
            "ground_truth": dt.ground_truth,
        }

        # Run debate protocol
        protocol = create_protocol(
            self.protocol_type, self.panel, self.config, self.model_pool,
        )
        trace = protocol.run_debate(dt.scenario, task_metadata)

        # Self-consistency baseline (independent single-model answers)
        if self.include_baseline:
            sc_answers = self._run_self_consistency(dt)
            trace.self_consistency_answers = sc_answers
            if sc_answers:
                from bioeval.debate.scoring import _positions_match
                gt = dt.ground_truth.get("classification", "")
                correct = sum(1 for a in sc_answers if _positions_match(a, gt))
                trace.self_consistency_agreement = correct / len(sc_answers)

        # Single-model baseline
        single_baseline = None
        if self.include_baseline:
            single_baseline = self._run_single_baseline(dt)

        # Score
        debate_score = score_debate(trace, dt.ground_truth, single_baseline)

        # Build result dict (CLI-compatible)
        return {
            "task_id": dt.id,
            "task_type": dt.task_type.value if hasattr(dt.task_type, "value") else str(dt.task_type),
            "response": trace.final_answer,
            "scores": {
                "composite_score": round(debate_score.composite_score, 4),
                "outcome_accuracy": debate_score.outcome.accuracy,
                "outcome_correct": debate_score.outcome.correct,
                "reasoning_quality": debate_score.outcome.reasoning_quality,
                "correction_rate": debate_score.process.correction_rate,
                "reversal_rate": debate_score.process.reversal_rate,
                "sycophancy_score": debate_score.process.sycophancy_score,
                "convergence_round": debate_score.process.convergence_speed,
                "dissent_preservation": debate_score.process.dissent_preservation,
                "unique_arguments": debate_score.process.unique_arguments,
                "evidence_introduction_rate": debate_score.process.evidence_introduction_rate,
                "total_tokens": debate_score.efficiency.total_tokens,
                "accuracy_per_1k_tokens": debate_score.efficiency.accuracy_per_1k_tokens,
                "rounds_used": debate_score.efficiency.rounds_used,
                "rounds_needed": debate_score.efficiency.rounds_needed,
                "debate_lift_vs_single": debate_score.comparison.debate_lift_vs_single,
                "debate_lift_vs_sc": debate_score.comparison.debate_lift_vs_sc,
                "protocol": self.protocol_type.value,
                "num_agents": len(self.panel.agents),
                "num_rounds": len(trace.rounds),
            },
            "debate_trace": {
                "protocol": trace.protocol_type.value,
                "rounds": len(trace.rounds),
                "terminated_early": trace.terminated_early,
                "termination_reason": trace.termination_reason,
                "final_confidence": trace.final_confidence,
                "total_tokens": trace.total_tokens,
                "models_used": self.panel.model_names,
                "is_heterogeneous": self.panel.is_heterogeneous,
            },
        }

    def _run_self_consistency(self, task: DebateTask) -> list[str]:
        """Run N independent single-model answers for self-consistency baseline."""
        answers = []
        first_agent = self.panel.agents[0] if self.panel.agents else None
        if not first_agent:
            return answers

        prompt = (
            f"{task.scenario}\n\n"
            f"Provide your answer. Choose from: {', '.join(task.answer_options)}. "
            f"State your confidence (0-100%)."
        )

        for _ in range(self.config.self_consistency_samples):
            try:
                response_text, _ = self.model_pool.generate(first_agent, prompt)
                # Extract position
                from bioeval.debate.protocols import BaseDebateProtocol
                protocol = create_protocol(
                    self.protocol_type, self.panel, self.config, self.model_pool,
                )
                pos = protocol._extract_position(
                    response_text,
                    {"answer_options": task.answer_options},
                )
                answers.append(pos or "unknown")
            except Exception:
                answers.append("unknown")
        return answers

    def _run_single_baseline(self, task: DebateTask) -> Optional[str]:
        """Run a single-model baseline answer."""
        first_agent = self.panel.agents[0] if self.panel.agents else None
        if not first_agent:
            return None

        prompt = (
            f"{task.scenario}\n\n"
            f"Provide your answer. Choose from: {', '.join(task.answer_options)}. "
            f"State your confidence (0-100%)."
        )

        try:
            response_text, _ = self.model_pool.generate(first_agent, prompt)
            protocol = create_protocol(
                self.protocol_type, self.panel, self.config, self.model_pool,
            )
            return protocol._extract_position(
                response_text,
                {"answer_options": task.answer_options},
            )
        except Exception:
            return None
