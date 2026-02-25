"""
Multi-Agent Debate Evaluation Module

Evaluates LLM reasoning through structured multi-agent debate protocols.
Multiple agents debate biomedical questions, and the system measures both
the quality of the final answer (outcome) and the debate process itself
(correction rate, sycophancy, dissent preservation, efficiency).

Supported protocols:
- Round-Robin: agents respond sequentially, each seeing prior responses
- Simultaneous: all agents respond in parallel, then iterate
- Judge-Mediated: debater agents + separate judge

Key design principles (from literature):
- Heterogeneous agents (different models) outperform homogeneous
- Confidence-weighted voting outperforms simple majority
- 3 rounds is optimal (diminishing returns beyond)
- Always compare against self-consistency baseline
"""

from bioeval.debate.agents import (
    AgentRole,
    AgentConfig,
    AgentResponse,
    DebatePanel,
    AgentModelPool,
    create_homogeneous_panel,
    create_heterogeneous_panel,
    create_adversarial_panel,
)
from bioeval.debate.protocols import (
    ProtocolType,
    TerminationCondition,
    DebateConfig,
    DebateRound,
    DebateTrace,
)
from bioeval.debate.tasks import DebateTaskType, DebateTask, DEBATE_TASKS
from bioeval.debate.scoring import DebateScore, score_debate
from bioeval.debate.evaluator import DebateEvaluator

__all__ = [
    "AgentRole",
    "AgentConfig",
    "AgentResponse",
    "DebatePanel",
    "AgentModelPool",
    "create_homogeneous_panel",
    "create_heterogeneous_panel",
    "create_adversarial_panel",
    "ProtocolType",
    "TerminationCondition",
    "DebateConfig",
    "DebateRound",
    "DebateTrace",
    "DebateTaskType",
    "DebateTask",
    "DEBATE_TASKS",
    "DebateScore",
    "score_debate",
    "DebateEvaluator",
]
