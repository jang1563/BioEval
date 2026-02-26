"""
Debate protocol implementations.

Three protocols:
- RoundRobinProtocol: agents respond sequentially, each seeing prior responses
- SimultaneousProtocol: all agents respond in parallel each round, then iterate
- JudgeMediatedProtocol: debater agents + separate judge agent
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from bioeval.debate.agents import (
    AgentConfig,
    AgentModelPool,
    AgentResponse,
    AgentRole,
    DebatePanel,
)


# =============================================================================
# ENUMS & CONFIG
# =============================================================================

class ProtocolType(Enum):
    ROUND_ROBIN = "round_robin"
    SIMULTANEOUS = "simultaneous"
    JUDGE_MEDIATED = "judge_mediated"


class TerminationCondition(Enum):
    FIXED_ROUNDS = "fixed_rounds"
    CONSENSUS = "consensus"
    CONFIDENCE_THRESHOLD = "confidence"
    ADAPTIVE = "adaptive"


@dataclass
class DebateConfig:
    protocol_type: ProtocolType
    max_rounds: int = 3
    termination: TerminationCondition = TerminationCondition.ADAPTIVE
    consensus_threshold: float = 0.8
    confidence_threshold: float = 0.9
    include_self_consistency: bool = True
    self_consistency_samples: int = 3


@dataclass
class DebateRound:
    round_number: int
    responses: list[AgentResponse] = field(default_factory=list)
    positions: dict = field(default_factory=dict)


@dataclass
class DebateTrace:
    task_id: str
    protocol_type: ProtocolType
    panel: DebatePanel
    config: DebateConfig
    rounds: list[DebateRound] = field(default_factory=list)
    final_answer: str = ""
    final_confidence: float = 0.5
    total_tokens: int = 0
    terminated_early: bool = False
    termination_reason: Optional[str] = None
    self_consistency_answers: list[str] = field(default_factory=list)
    self_consistency_agreement: float = 0.0


# =============================================================================
# BASE PROTOCOL
# =============================================================================

class BaseDebateProtocol(ABC):
    """Abstract base for debate protocols."""

    def __init__(
        self,
        panel: DebatePanel,
        config: DebateConfig,
        model_pool: AgentModelPool,
    ):
        self.panel = panel
        self.config = config
        self.model_pool = model_pool

    @abstractmethod
    def run_debate(self, task_prompt: str, task_metadata: dict) -> DebateTrace:
        pass

    def _should_terminate(self, rounds: list[DebateRound]) -> tuple[bool, str]:
        if not rounds:
            return False, ""

        if len(rounds) >= self.config.max_rounds:
            return True, "max_rounds"

        if self.config.termination == TerminationCondition.FIXED_ROUNDS:
            return False, ""

        last = rounds[-1]

        if self.config.termination == TerminationCondition.CONSENSUS:
            positions = set(v for v in last.positions.values() if v)
            if len(positions) <= 1:
                return True, "consensus_reached"

        if self.config.termination == TerminationCondition.CONFIDENCE_THRESHOLD:
            confidences = [
                r.confidence for r in last.responses if r.confidence is not None
            ]
            if confidences and all(
                c >= self.config.confidence_threshold for c in confidences
            ):
                return True, "confidence_threshold"

        if self.config.termination == TerminationCondition.ADAPTIVE:
            if len(rounds) >= 2:
                prev_positions = rounds[-2].positions
                curr_positions = last.positions
                if prev_positions and prev_positions == curr_positions:
                    return True, "no_position_change"

        return False, ""

    def _parse_confidence(self, response_text: str) -> Optional[float]:
        patterns = [
            r"[Cc]onfidence[:\s]*(\d{1,3})\s*%",
            r"[Cc]onfidence[:\s]*0\.(\d{1,2})",
            r"(\d{1,3})\s*%\s*confident",
        ]
        for pat in patterns:
            m = re.search(pat, response_text)
            if m:
                val = float(m.group(1))
                if val > 1:
                    val /= 100.0
                return min(1.0, max(0.0, val))
        return None

    def _extract_position(
        self, response_text: str, task_metadata: dict
    ) -> Optional[str]:
        options = task_metadata.get("answer_options", [])
        response_lower = response_text.lower()
        # Sort longest-first to prevent substring matching issues
        # e.g., "not_practice_changing" must be checked before "practice_changing"
        for opt in sorted(options, key=len, reverse=True):
            if opt.lower() in response_lower:
                return opt
        # Fallback: look for "my answer is X", "I conclude X"
        m = re.search(
            r"(?:my (?:final )?answer|I conclude|verdict|classification)[:\s]+([^\n.]{3,80})",
            response_text,
            re.IGNORECASE,
        )
        if m:
            return m.group(1).strip()
        return None

    def _confidence_weighted_vote(
        self, responses: list[AgentResponse]
    ) -> tuple[str, float]:
        """Select final answer via confidence-weighted voting."""
        position_weights: dict[str, float] = {}
        position_responses: dict[str, AgentResponse] = {}

        for resp in responses:
            pos = resp.position or "unknown"
            conf = resp.confidence or 0.5
            position_weights[pos] = position_weights.get(pos, 0.0) + conf
            if pos not in position_responses or (resp.confidence or 0) > (
                position_responses[pos].confidence or 0
            ):
                position_responses[pos] = resp

        if not position_weights:
            return responses[-1].content if responses else "", 0.5

        best_pos = max(position_weights, key=position_weights.get)
        best_resp = position_responses.get(best_pos)
        avg_conf = position_weights[best_pos] / max(
            1, sum(1 for r in responses if (r.position or "unknown") == best_pos)
        )

        return (best_resp.content if best_resp else best_pos), min(1.0, avg_conf)


# =============================================================================
# ROUND-ROBIN PROTOCOL
# =============================================================================

class RoundRobinProtocol(BaseDebateProtocol):
    """Agents respond sequentially, each seeing all prior responses."""

    def run_debate(self, task_prompt: str, task_metadata: dict) -> DebateTrace:
        rounds = []
        all_responses: list[AgentResponse] = []
        total_tokens = 0
        termination_reason = None

        for round_num in range(1, self.config.max_rounds + 1):
            round_responses = []

            for agent in self.panel.agents:
                prompt = self._build_agent_prompt(
                    agent, task_prompt, all_responses, round_num
                )
                response_text, tokens = self.model_pool.generate(agent, prompt)
                total_tokens += tokens

                agent_resp = AgentResponse(
                    agent_id=agent.agent_id,
                    role=agent.role,
                    model_name=agent.model_name,
                    round_number=round_num,
                    content=response_text,
                    confidence=self._parse_confidence(response_text),
                    token_count=tokens,
                    position=self._extract_position(response_text, task_metadata),
                )
                round_responses.append(agent_resp)
                all_responses.append(agent_resp)

            positions = {r.agent_id: r.position for r in round_responses}
            rounds.append(
                DebateRound(
                    round_number=round_num,
                    responses=round_responses,
                    positions=positions,
                )
            )

            terminate, reason = self._should_terminate(rounds)
            if terminate:
                termination_reason = reason
                break

        final_answer, final_confidence = self._confidence_weighted_vote(
            rounds[-1].responses
        )

        return DebateTrace(
            task_id=task_metadata.get("task_id", ""),
            protocol_type=ProtocolType.ROUND_ROBIN,
            panel=self.panel,
            config=self.config,
            rounds=rounds,
            final_answer=final_answer,
            final_confidence=final_confidence,
            total_tokens=total_tokens,
            terminated_early=len(rounds) < self.config.max_rounds,
            termination_reason=termination_reason
            if len(rounds) < self.config.max_rounds
            else None,
        )

    def _build_agent_prompt(
        self,
        agent: AgentConfig,
        task_prompt: str,
        prior_responses: list[AgentResponse],
        round_num: int,
    ) -> str:
        if round_num == 1 and not prior_responses:
            return (
                f"{task_prompt}\n\n"
                f"Provide your analysis and answer. State your confidence level (0-100%)."
            )

        history = "\n\n".join(
            [
                f"--- {r.agent_id} (Round {r.round_number}, {r.role.value}) ---\n{r.content}"
                for r in prior_responses
            ]
        )
        return (
            f"{task_prompt}\n\n"
            f"## Previous Discussion\n{history}\n\n"
            f"## Your Turn (Round {round_num})\n"
            f"Review the above responses. You may update your position based on "
            f"new arguments, or defend your previous position with stronger evidence. "
            f"State your confidence level (0-100%)."
        )


# =============================================================================
# SIMULTANEOUS PROTOCOL
# =============================================================================

class SimultaneousProtocol(BaseDebateProtocol):
    """All agents respond in parallel each round, then see each other."""

    def run_debate(self, task_prompt: str, task_metadata: dict) -> DebateTrace:
        rounds = []
        total_tokens = 0
        termination_reason = None

        for round_num in range(1, self.config.max_rounds + 1):
            prev_responses = rounds[-1].responses if rounds else []
            round_responses = []

            for agent in self.panel.agents:
                prompt = self._build_simultaneous_prompt(
                    agent, task_prompt, prev_responses, round_num
                )
                response_text, tokens = self.model_pool.generate(agent, prompt)
                total_tokens += tokens

                round_responses.append(
                    AgentResponse(
                        agent_id=agent.agent_id,
                        role=agent.role,
                        model_name=agent.model_name,
                        round_number=round_num,
                        content=response_text,
                        confidence=self._parse_confidence(response_text),
                        token_count=tokens,
                        position=self._extract_position(
                            response_text, task_metadata
                        ),
                    )
                )

            positions = {r.agent_id: r.position for r in round_responses}
            rounds.append(
                DebateRound(
                    round_number=round_num,
                    responses=round_responses,
                    positions=positions,
                )
            )

            terminate, reason = self._should_terminate(rounds)
            if terminate:
                termination_reason = reason
                break

        final_answer, final_confidence = self._confidence_weighted_vote(
            rounds[-1].responses
        )

        return DebateTrace(
            task_id=task_metadata.get("task_id", ""),
            protocol_type=ProtocolType.SIMULTANEOUS,
            panel=self.panel,
            config=self.config,
            rounds=rounds,
            final_answer=final_answer,
            final_confidence=final_confidence,
            total_tokens=total_tokens,
            terminated_early=len(rounds) < self.config.max_rounds,
            termination_reason=termination_reason
            if len(rounds) < self.config.max_rounds
            else None,
        )

    def _build_simultaneous_prompt(
        self,
        agent: AgentConfig,
        task_prompt: str,
        prev_responses: list[AgentResponse],
        round_num: int,
    ) -> str:
        if round_num == 1:
            return (
                f"{task_prompt}\n\n"
                f"Provide your independent analysis and answer. "
                f"State your confidence level (0-100%)."
            )

        others = "\n\n".join(
            [
                f"--- {r.agent_id} ({r.role.value}) ---\n{r.content}"
                for r in prev_responses
                if r.agent_id != agent.agent_id
            ]
        )
        own = next(
            (r for r in prev_responses if r.agent_id == agent.agent_id), None
        )
        own_text = f"\n\n## Your Previous Response\n{own.content}" if own else ""

        return (
            f"{task_prompt}\n\n"
            f"## Other Agents' Responses (Round {round_num - 1})\n{others}"
            f"{own_text}\n\n"
            f"## Round {round_num}\n"
            f"Consider the other perspectives. Update or defend your position. "
            f"State your confidence level (0-100%)."
        )


# =============================================================================
# JUDGE-MEDIATED PROTOCOL
# =============================================================================

class JudgeMediatedProtocol(BaseDebateProtocol):
    """Debater agents argue, then a judge evaluates and decides."""

    def run_debate(self, task_prompt: str, task_metadata: dict) -> DebateTrace:
        if not self.panel.judge:
            raise ValueError(
                "JudgeMediatedProtocol requires a judge agent in the panel"
            )

        rounds = []
        total_tokens = 0
        termination_reason = None

        for round_num in range(1, self.config.max_rounds + 1):
            prev_responses = rounds[-1].responses if rounds else []

            # Step 1: Debaters respond
            debater_responses = []
            for agent in self.panel.agents:
                prompt = self._build_debater_prompt(
                    agent, task_prompt, prev_responses, round_num
                )
                response_text, tokens = self.model_pool.generate(agent, prompt)
                total_tokens += tokens

                debater_responses.append(
                    AgentResponse(
                        agent_id=agent.agent_id,
                        role=agent.role,
                        model_name=agent.model_name,
                        round_number=round_num,
                        content=response_text,
                        confidence=self._parse_confidence(response_text),
                        token_count=tokens,
                        position=self._extract_position(
                            response_text, task_metadata
                        ),
                    )
                )

            # Step 2: Judge evaluates
            judge_prompt = self._build_judge_prompt(
                task_prompt, debater_responses, round_num
            )
            judge_text, judge_tokens = self.model_pool.generate(
                self.panel.judge, judge_prompt
            )
            total_tokens += judge_tokens

            judge_response = AgentResponse(
                agent_id=self.panel.judge.agent_id,
                role=AgentRole.JUDGE,
                model_name=self.panel.judge.model_name,
                round_number=round_num,
                content=judge_text,
                confidence=self._parse_confidence(judge_text),
                token_count=judge_tokens,
                position=self._extract_position(judge_text, task_metadata),
            )

            all_responses = debater_responses + [judge_response]
            positions = {r.agent_id: r.position for r in all_responses}
            rounds.append(
                DebateRound(
                    round_number=round_num,
                    responses=all_responses,
                    positions=positions,
                )
            )

            terminate, reason = self._should_terminate(rounds)
            if terminate:
                termination_reason = reason
                break

        # Final answer is judge's last response
        last_judge = next(
            (
                r
                for r in reversed(rounds[-1].responses)
                if r.role == AgentRole.JUDGE
            ),
            rounds[-1].responses[-1],
        )

        return DebateTrace(
            task_id=task_metadata.get("task_id", ""),
            protocol_type=ProtocolType.JUDGE_MEDIATED,
            panel=self.panel,
            config=self.config,
            rounds=rounds,
            final_answer=last_judge.content,
            final_confidence=last_judge.confidence or 0.5,
            total_tokens=total_tokens,
            terminated_early=len(rounds) < self.config.max_rounds,
            termination_reason=termination_reason
            if len(rounds) < self.config.max_rounds
            else None,
        )

    def _build_debater_prompt(
        self,
        agent: AgentConfig,
        task_prompt: str,
        prev_responses: list[AgentResponse],
        round_num: int,
    ) -> str:
        if round_num == 1:
            return (
                f"{task_prompt}\n\n"
                f"You are the {agent.role.value}. "
                f"Provide your analysis and answer. State your confidence (0-100%)."
            )

        history = "\n\n".join(
            [
                f"--- {r.agent_id} ({r.role.value}) ---\n{r.content}"
                for r in prev_responses
            ]
        )
        return (
            f"{task_prompt}\n\n"
            f"## Previous Round\n{history}\n\n"
            f"## Round {round_num}\n"
            f"As {agent.role.value}, respond to the judge's feedback and "
            f"other agents. Update or strengthen your position. "
            f"State your confidence (0-100%)."
        )

    def _build_judge_prompt(
        self,
        task_prompt: str,
        debater_responses: list[AgentResponse],
        round_num: int,
    ) -> str:
        args = "\n\n".join(
            [
                f"--- {r.agent_id} ({r.role.value}, confidence: {r.confidence}) ---\n{r.content}"
                for r in debater_responses
            ]
        )
        return (
            f"## Task\n{task_prompt}\n\n"
            f"## Agent Responses (Round {round_num})\n{args}\n\n"
            f"## Judge Instructions\n"
            f"Evaluate each agent's response for scientific accuracy, reasoning "
            f"quality, and evidence strength. Identify the strongest position. "
            f"If agents disagree, explain which is correct and why. "
            f"Provide your synthesized answer with confidence (0-100%)."
        )


# =============================================================================
# PROTOCOL FACTORY
# =============================================================================

PROTOCOL_CLASSES = {
    ProtocolType.ROUND_ROBIN: RoundRobinProtocol,
    ProtocolType.SIMULTANEOUS: SimultaneousProtocol,
    ProtocolType.JUDGE_MEDIATED: JudgeMediatedProtocol,
}


def create_protocol(
    protocol_type: ProtocolType,
    panel: DebatePanel,
    config: DebateConfig,
    model_pool: AgentModelPool,
) -> BaseDebateProtocol:
    """Factory function to create a protocol instance."""
    cls = PROTOCOL_CLASSES.get(protocol_type)
    if cls is None:
        raise ValueError(f"Unknown protocol type: {protocol_type}")
    return cls(panel, config, model_pool)
