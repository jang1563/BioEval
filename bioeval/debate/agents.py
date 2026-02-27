"""
Agent configuration, model pooling, and panel presets for multi-agent debate.

Defines agent roles, configurations, and model management for debate protocols.
Reuses existing model wrappers from bioeval.models.base.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

# =============================================================================
# ENUMS & DATACLASSES
# =============================================================================


class AgentRole(Enum):
    """Roles an agent can play in a debate."""

    SOLVER = "solver"
    ADVOCATE = "advocate"
    CRITIC = "critic"
    JUDGE = "judge"
    SYNTHESIZER = "synthesizer"


@dataclass
class AgentConfig:
    """Configuration for a single debate agent."""

    agent_id: str
    role: AgentRole
    model_name: str
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1500
    persona: Optional[str] = None
    require_confidence: bool = True


@dataclass
class AgentResponse:
    """Single response from an agent in one round."""

    agent_id: str
    role: AgentRole
    model_name: str
    round_number: int
    content: str
    confidence: Optional[float] = None
    token_count: int = 0
    position: Optional[str] = None


@dataclass
class DebatePanel:
    """Configuration for the full set of agents in a debate."""

    agents: list[AgentConfig] = field(default_factory=list)
    judge: Optional[AgentConfig] = None

    def get_agents_by_role(self, role: AgentRole) -> list[AgentConfig]:
        return [a for a in self.agents if a.role == role]

    @property
    def model_names(self) -> list[str]:
        models = {a.model_name for a in self.agents}
        if self.judge:
            models.add(self.judge.model_name)
        return sorted(models)

    @property
    def is_heterogeneous(self) -> bool:
        return len(set(a.model_name for a in self.agents)) > 1


# =============================================================================
# ROLE SYSTEM PROMPTS
# =============================================================================

ROLE_SYSTEM_PROMPTS = {
    AgentRole.SOLVER: (
        "You are a biomedical research scientist. Analyze the problem carefully, "
        "provide your answer with supporting reasoning, and state your confidence "
        "level (0-100%). Consider multiple hypotheses before settling on one."
    ),
    AgentRole.ADVOCATE: (
        "You are a biomedical scientist assigned to argue for the position: {position}. "
        "Present the strongest possible case with biological evidence. "
        "Acknowledge counterarguments but explain why your position is stronger. "
        "State your confidence (0-100%)."
    ),
    AgentRole.CRITIC: (
        "You are a rigorous scientific reviewer. Your job is to identify weaknesses, "
        "logical errors, missing evidence, and alternative explanations in the provided "
        "responses. Be specific and constructive. State your confidence (0-100%)."
    ),
    AgentRole.JUDGE: (
        "You are an expert scientific judge. Evaluate the arguments presented by multiple "
        "agents. Identify which response is most scientifically accurate and well-reasoned. "
        "Synthesize the best elements. Provide your final verdict with confidence (0-100%)."
    ),
    AgentRole.SYNTHESIZER: (
        "You are a scientific synthesizer. Review all previous responses and create a "
        "comprehensive answer that integrates the strongest arguments. Resolve contradictions "
        "using evidence-based reasoning. State your confidence (0-100%)."
    ),
}


# =============================================================================
# MODEL POOL
# =============================================================================


class AgentModelPool:
    """Pool of model instances, reused across agents using the same model."""

    def __init__(self):
        self._models: dict[str, object] = {}

    def get_model(self, model_name: str):
        if model_name not in self._models:
            if "claude" in model_name.lower():
                from bioeval.models.base import ClaudeModel

                self._models[model_name] = ClaudeModel(model_name)
            elif "gpt" in model_name.lower():
                from bioeval.models.base import OpenAIModel

                self._models[model_name] = OpenAIModel(model_name)
            elif "/" in model_name:
                from bioeval.models.base import HuggingFaceModel

                self._models[model_name] = HuggingFaceModel(model_name)
            else:
                raise ValueError(f"Unknown model: {model_name}")
        return self._models[model_name]

    def generate(self, agent: AgentConfig, prompt: str) -> tuple[str, int]:
        model = self.get_model(agent.model_name)
        response = model.generate(
            prompt,
            max_tokens=agent.max_tokens,
            system=agent.system_prompt,
        )
        approx_tokens = len(response) // 4
        return response, approx_tokens


# =============================================================================
# PANEL FACTORY FUNCTIONS
# =============================================================================


def create_homogeneous_panel(
    model_name: str,
    n_agents: int = 3,
    with_judge: bool = False,
) -> DebatePanel:
    """Create a panel where all agents use the same model."""
    roles = _assign_default_roles(n_agents)
    agents = [
        AgentConfig(
            agent_id=f"agent_{i+1}",
            role=roles[i],
            model_name=model_name,
            system_prompt=ROLE_SYSTEM_PROMPTS.get(roles[i]),
        )
        for i in range(n_agents)
    ]
    judge = None
    if with_judge:
        judge = AgentConfig(
            agent_id="judge",
            role=AgentRole.JUDGE,
            model_name=model_name,
            system_prompt=ROLE_SYSTEM_PROMPTS[AgentRole.JUDGE],
            temperature=0.3,
        )
    return DebatePanel(agents=agents, judge=judge)


def create_heterogeneous_panel(
    models: list[str],
    with_judge: bool = False,
    judge_model: Optional[str] = None,
) -> DebatePanel:
    """Create a panel where different agents use different models."""
    n = len(models)
    roles = _assign_default_roles(n)
    agents = [
        AgentConfig(
            agent_id=f"agent_{i+1}",
            role=roles[i],
            model_name=models[i],
            system_prompt=ROLE_SYSTEM_PROMPTS.get(roles[i]),
        )
        for i in range(n)
    ]
    judge = None
    if with_judge:
        jm = judge_model or models[0]
        judge = AgentConfig(
            agent_id="judge",
            role=AgentRole.JUDGE,
            model_name=jm,
            system_prompt=ROLE_SYSTEM_PROMPTS[AgentRole.JUDGE],
            temperature=0.3,
        )
    return DebatePanel(agents=agents, judge=judge)


def create_adversarial_panel(
    model_name: str,
    positions: list[str],
) -> DebatePanel:
    """Create a panel where each agent advocates for a different position."""
    agents = []
    for i, pos in enumerate(positions):
        sys_prompt = ROLE_SYSTEM_PROMPTS[AgentRole.ADVOCATE].format(position=pos)
        agents.append(
            AgentConfig(
                agent_id=f"advocate_{pos}",
                role=AgentRole.ADVOCATE,
                model_name=model_name,
                system_prompt=sys_prompt,
                persona=f"Advocate for {pos}",
            )
        )
    judge = AgentConfig(
        agent_id="judge",
        role=AgentRole.JUDGE,
        model_name=model_name,
        system_prompt=ROLE_SYSTEM_PROMPTS[AgentRole.JUDGE],
        temperature=0.3,
    )
    return DebatePanel(agents=agents, judge=judge)


def _assign_default_roles(n_agents: int) -> list[AgentRole]:
    """Assign default roles: solvers + one critic."""
    if n_agents <= 1:
        return [AgentRole.SOLVER]
    if n_agents == 2:
        return [AgentRole.SOLVER, AgentRole.SOLVER]
    return [AgentRole.SOLVER] * (n_agents - 1) + [AgentRole.CRITIC]
