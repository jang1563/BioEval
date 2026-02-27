"""
Tests for the multi-agent debate evaluation module.
"""

import pytest

# =============================================================================
# DATA LOADING
# =============================================================================


class TestTaskLoading:
    """Test that debate tasks load correctly."""

    def test_25_tasks_loaded(self):
        from bioeval.debate.tasks import DEBATE_TASKS

        assert len(DEBATE_TASKS) == 25

    def test_task_required_fields(self):
        from bioeval.debate.tasks import DEBATE_TASKS

        for task in DEBATE_TASKS:
            assert task.id, f"Task missing id"
            assert task.task_type is not None
            assert task.scenario, f"Task {task.id} missing scenario"
            assert task.context, f"Task {task.id} missing context"
            assert task.answer_options, f"Task {task.id} missing answer_options"
            assert task.ground_truth, f"Task {task.id} missing ground_truth"
            assert task.difficulty in ("easy", "medium", "hard"), f"Task {task.id} invalid difficulty"
            assert task.domain, f"Task {task.id} missing domain"

    def test_five_types_covered(self):
        from bioeval.debate.tasks import DEBATE_TASKS, DebateTaskType

        types_found = {t.task_type for t in DEBATE_TASKS}
        assert types_found == set(DebateTaskType)

    def test_five_per_type(self):
        from bioeval.debate.tasks import DEBATE_TASKS, DebateTaskType
        from collections import Counter

        counts = Counter(t.task_type for t in DEBATE_TASKS)
        for tt in DebateTaskType:
            assert counts[tt] == 5, f"{tt.value} has {counts[tt]} tasks, expected 5"

    def test_ground_truth_has_classification(self):
        from bioeval.debate.tasks import DEBATE_TASKS

        for task in DEBATE_TASKS:
            assert "classification" in task.ground_truth, f"Task {task.id} missing classification"
            assert "key_criteria" in task.ground_truth, f"Task {task.id} missing key_criteria"

    def test_answer_options_include_ground_truth(self):
        from bioeval.debate.tasks import DEBATE_TASKS

        for task in DEBATE_TASKS:
            gt = task.ground_truth["classification"].lower()
            options_lower = [o.lower() for o in task.answer_options]
            assert gt in options_lower, f"Task {task.id}: ground truth '{gt}' not in answer_options {task.answer_options}"


# =============================================================================
# AGENT CONFIG
# =============================================================================


class TestAgentConfig:
    """Test agent configuration and panel creation."""

    def test_homogeneous_panel(self):
        from bioeval.debate.agents import create_homogeneous_panel, AgentRole

        panel = create_homogeneous_panel("claude-sonnet-4-20250514", n_agents=3)
        assert len(panel.agents) == 3
        assert panel.judge is None
        assert not panel.is_heterogeneous
        assert all(a.model_name == "claude-sonnet-4-20250514" for a in panel.agents)

    def test_homogeneous_with_judge(self):
        from bioeval.debate.agents import create_homogeneous_panel, AgentRole

        panel = create_homogeneous_panel("claude-sonnet-4-20250514", n_agents=3, with_judge=True)
        assert len(panel.agents) == 3
        assert panel.judge is not None
        assert panel.judge.role == AgentRole.JUDGE

    def test_heterogeneous_panel(self):
        from bioeval.debate.agents import create_heterogeneous_panel

        panel = create_heterogeneous_panel(["claude-sonnet-4-20250514", "gpt-4o", "gpt-4-turbo"])
        assert len(panel.agents) == 3
        assert panel.is_heterogeneous
        assert len(panel.model_names) == 3

    def test_adversarial_panel(self):
        from bioeval.debate.agents import create_adversarial_panel, AgentRole

        panel = create_adversarial_panel("claude-sonnet-4-20250514", ["pathogenic", "benign"])
        assert len(panel.agents) == 2
        assert panel.judge is not None
        assert all(a.role == AgentRole.ADVOCATE for a in panel.agents)

    def test_role_assignment(self):
        from bioeval.debate.agents import create_homogeneous_panel, AgentRole

        panel = create_homogeneous_panel("claude-sonnet-4-20250514", n_agents=3)
        roles = [a.role for a in panel.agents]
        assert roles.count(AgentRole.SOLVER) == 2
        assert roles.count(AgentRole.CRITIC) == 1

    def test_single_agent_is_solver(self):
        from bioeval.debate.agents import create_homogeneous_panel, AgentRole

        panel = create_homogeneous_panel("claude-sonnet-4-20250514", n_agents=1)
        assert panel.agents[0].role == AgentRole.SOLVER

    def test_get_agents_by_role(self):
        from bioeval.debate.agents import create_homogeneous_panel, AgentRole

        panel = create_homogeneous_panel("claude-sonnet-4-20250514", n_agents=3)
        solvers = panel.get_agents_by_role(AgentRole.SOLVER)
        critics = panel.get_agents_by_role(AgentRole.CRITIC)
        assert len(solvers) == 2
        assert len(critics) == 1


# =============================================================================
# CONFIDENCE PARSING
# =============================================================================


class TestConfidenceParsing:
    """Test confidence extraction from response text."""

    def _parse(self, text):
        from bioeval.debate.protocols import (
            DebateConfig,
            ProtocolType,
            SimultaneousProtocol,
        )
        from bioeval.debate.agents import (
            AgentModelPool,
            create_homogeneous_panel,
        )

        panel = create_homogeneous_panel("dummy")
        config = DebateConfig(protocol_type=ProtocolType.SIMULTANEOUS)
        protocol = SimultaneousProtocol(panel, config, AgentModelPool())
        return protocol._parse_confidence(text)

    def test_percent_format(self):
        assert self._parse("Confidence: 85%") == 0.85

    def test_decimal_format(self):
        assert self._parse("Confidence: 0.85") == 0.85

    def test_confident_suffix(self):
        assert self._parse("I am 90% confident in this answer") == 0.9

    def test_none_when_missing(self):
        assert self._parse("No confidence stated here.") is None

    def test_zero_percent(self):
        assert self._parse("Confidence: 0%") == 0.0

    def test_100_percent(self):
        assert self._parse("Confidence: 100%") == 1.0


# =============================================================================
# POSITION EXTRACTION
# =============================================================================


class TestPositionExtraction:
    """Test position extraction from response text."""

    def _extract(self, text, options):
        from bioeval.debate.protocols import (
            DebateConfig,
            ProtocolType,
            SimultaneousProtocol,
        )
        from bioeval.debate.agents import (
            AgentModelPool,
            create_homogeneous_panel,
        )

        panel = create_homogeneous_panel("dummy")
        config = DebateConfig(protocol_type=ProtocolType.SIMULTANEOUS)
        protocol = SimultaneousProtocol(panel, config, AgentModelPool())
        return protocol._extract_position(text, {"answer_options": options})

    def test_exact_match(self):
        options = ["pathogenic", "VUS", "benign"]
        assert self._extract("This variant is VUS.", options) == "VUS"

    def test_case_insensitive(self):
        options = ["CML", "CMML", "AML"]
        assert self._extract("Most likely diagnosis is cml due to...", options) == "CML"

    def test_fallback_regex(self):
        # Options are single letters, so "A" appears in "answer"
        # Use options that won't match, then test fallback
        options = ["xyza", "xyzb"]
        result = self._extract("My final answer: something specific here.", options)
        assert result == "something specific here"

    def test_none_when_not_found(self):
        options = ["alpha", "beta"]
        result = self._extract("This is completely unrelated text.", options)
        assert result is None


# =============================================================================
# PROTOCOL MECHANICS (with mock model)
# =============================================================================


class TestProtocolMechanics:
    """Test protocol flow using a mock model pool."""

    class MockModelPool:
        """Returns deterministic responses for testing."""

        def __init__(self, responses=None):
            self._idx = 0
            self._responses = responses or []

        def generate(self, agent, prompt):
            if self._idx < len(self._responses):
                text = self._responses[self._idx]
            else:
                text = f"Agent {agent.agent_id}: VUS. Confidence: 70%"
            self._idx += 1
            return text, len(text) // 4

        def get_model(self, model_name):
            return None

    def test_round_robin_runs(self):
        from bioeval.debate.protocols import (
            DebateConfig,
            ProtocolType,
            TerminationCondition,
            RoundRobinProtocol,
        )
        from bioeval.debate.agents import create_homogeneous_panel

        panel = create_homogeneous_panel("dummy", n_agents=2)
        config = DebateConfig(
            protocol_type=ProtocolType.ROUND_ROBIN,
            max_rounds=2,
            termination=TerminationCondition.FIXED_ROUNDS,
        )
        protocol = RoundRobinProtocol(panel, config, self.MockModelPool())
        trace = protocol.run_debate("Test scenario", {"task_id": "t1", "answer_options": ["VUS", "pathogenic"]})
        assert len(trace.rounds) == 2
        assert trace.total_tokens > 0

    def test_simultaneous_runs(self):
        from bioeval.debate.protocols import (
            DebateConfig,
            ProtocolType,
            TerminationCondition,
            SimultaneousProtocol,
        )
        from bioeval.debate.agents import create_homogeneous_panel

        panel = create_homogeneous_panel("dummy", n_agents=3)
        config = DebateConfig(
            protocol_type=ProtocolType.SIMULTANEOUS,
            max_rounds=2,
            termination=TerminationCondition.FIXED_ROUNDS,
        )
        protocol = SimultaneousProtocol(panel, config, self.MockModelPool())
        trace = protocol.run_debate("Test scenario", {"task_id": "t1", "answer_options": ["VUS"]})
        assert len(trace.rounds) == 2
        # Each round should have 3 responses
        for rnd in trace.rounds:
            assert len(rnd.responses) == 3

    def test_judge_mediated_requires_judge(self):
        from bioeval.debate.protocols import (
            DebateConfig,
            ProtocolType,
            JudgeMediatedProtocol,
        )
        from bioeval.debate.agents import create_homogeneous_panel

        panel = create_homogeneous_panel("dummy", n_agents=2, with_judge=False)
        config = DebateConfig(protocol_type=ProtocolType.JUDGE_MEDIATED, max_rounds=1)
        protocol = JudgeMediatedProtocol(panel, config, self.MockModelPool())
        with pytest.raises(ValueError, match="judge"):
            protocol.run_debate("Test", {"task_id": "t1", "answer_options": []})

    def test_judge_mediated_runs(self):
        from bioeval.debate.protocols import (
            DebateConfig,
            ProtocolType,
            TerminationCondition,
            JudgeMediatedProtocol,
        )
        from bioeval.debate.agents import create_homogeneous_panel, AgentRole

        panel = create_homogeneous_panel("dummy", n_agents=2, with_judge=True)
        config = DebateConfig(
            protocol_type=ProtocolType.JUDGE_MEDIATED,
            max_rounds=1,
            termination=TerminationCondition.FIXED_ROUNDS,
        )
        protocol = JudgeMediatedProtocol(panel, config, self.MockModelPool())
        trace = protocol.run_debate("Test", {"task_id": "t1", "answer_options": ["VUS"]})
        assert len(trace.rounds) == 1
        # Should have debaters + judge
        judge_responses = [r for r in trace.rounds[0].responses if r.role == AgentRole.JUDGE]
        assert len(judge_responses) == 1

    def test_adaptive_termination(self):
        """When positions don't change, adaptive termination stops early."""
        from bioeval.debate.protocols import (
            DebateConfig,
            ProtocolType,
            TerminationCondition,
            SimultaneousProtocol,
        )
        from bioeval.debate.agents import create_homogeneous_panel

        panel = create_homogeneous_panel("dummy", n_agents=2)
        config = DebateConfig(
            protocol_type=ProtocolType.SIMULTANEOUS,
            max_rounds=5,
            termination=TerminationCondition.ADAPTIVE,
        )
        # All agents say VUS every round → positions won't change after round 2
        responses = ["VUS. Confidence: 80%"] * 20
        protocol = SimultaneousProtocol(panel, config, self.MockModelPool(responses))
        trace = protocol.run_debate("Test", {"task_id": "t1", "answer_options": ["VUS", "pathogenic"]})
        # Should terminate before max_rounds=5
        assert len(trace.rounds) <= 3
        assert trace.terminated_early


# =============================================================================
# SCORING
# =============================================================================


class TestScoring:
    """Test scoring system with synthetic traces."""

    def _make_trace(self, r1_positions, r3_positions, gt="VUS"):
        """Create a minimal synthetic DebateTrace for testing."""
        from bioeval.debate.protocols import DebateTrace, DebateRound, DebateConfig, ProtocolType
        from bioeval.debate.agents import AgentResponse, AgentRole, DebatePanel, AgentConfig

        agents = [AgentConfig(agent_id=f"a{i}", role=AgentRole.SOLVER, model_name="dummy") for i in range(len(r1_positions))]
        panel = DebatePanel(agents=agents)

        def _make_round(rnum, positions):
            return DebateRound(
                round_number=rnum,
                responses=[
                    AgentResponse(
                        agent_id=f"a{i}",
                        role=AgentRole.SOLVER,
                        model_name="dummy",
                        round_number=rnum,
                        content=f"My answer is {pos}. Confidence: 75%",
                        confidence=0.75,
                        position=pos,
                        token_count=50,
                    )
                    for i, pos in enumerate(positions)
                ],
                positions={f"a{i}": pos for i, pos in enumerate(positions)},
            )

        rounds = [_make_round(1, r1_positions)]
        if r3_positions != r1_positions:
            rounds.append(_make_round(2, r3_positions))
        rounds.append(_make_round(len(rounds) + 1, r3_positions))

        return DebateTrace(
            task_id="test",
            protocol_type=ProtocolType.SIMULTANEOUS,
            panel=panel,
            config=DebateConfig(protocol_type=ProtocolType.SIMULTANEOUS),
            rounds=rounds,
            final_answer=f"My answer is {r3_positions[0]}. Confidence: 75%",
            final_confidence=0.75,
            total_tokens=sum(50 * len(r1_positions) for _ in rounds),
        )

    def test_correct_outcome(self):
        from bioeval.debate.scoring import score_debate

        gt = {"classification": "VUS", "key_criteria": ["PM2", "PP3", "VUS"]}
        trace = self._make_trace(["VUS", "VUS", "VUS"], ["VUS", "VUS", "VUS"], "VUS")
        score = score_debate(trace, gt)
        assert score.outcome.correct is True
        assert score.outcome.accuracy == 1.0

    def test_wrong_outcome(self):
        from bioeval.debate.scoring import score_debate

        gt = {"classification": "VUS", "key_criteria": ["PM2", "PP3"]}
        trace = self._make_trace(["pathogenic", "pathogenic"], ["pathogenic", "pathogenic"], "VUS")
        score = score_debate(trace, gt)
        assert score.outcome.correct is False

    def test_correction_rate(self):
        from bioeval.debate.scoring import score_debate

        gt = {"classification": "VUS", "key_criteria": []}
        # Round 1: agent0=pathogenic(wrong), agent1=VUS(right)
        # Round 3: both VUS (agent0 corrected)
        trace = self._make_trace(["pathogenic", "VUS"], ["VUS", "VUS"])
        score = score_debate(trace, gt)
        assert score.process.correction_rate == 1.0

    def test_reversal_rate(self):
        from bioeval.debate.scoring import score_debate

        gt = {"classification": "VUS", "key_criteria": []}
        # Round 1: agent0=VUS(right), agent1=VUS(right)
        # Round 3: agent0=pathogenic(reversed), agent1=VUS
        trace = self._make_trace(["VUS", "VUS"], ["pathogenic", "VUS"])
        score = score_debate(trace, gt)
        assert score.process.reversal_rate == 0.5  # 1 of 2 reversed

    def test_composite_score_range(self):
        from bioeval.debate.scoring import score_debate

        gt = {"classification": "VUS", "key_criteria": []}
        trace = self._make_trace(["VUS", "VUS"], ["VUS", "VUS"])
        score = score_debate(trace, gt)
        assert 0.0 <= score.composite_score <= 1.0

    def test_partial_credit(self):
        from bioeval.debate.scoring import _partial_credit

        # Adjacent in ACMG classification
        assert _partial_credit("likely_pathogenic", "pathogenic", {}) == 0.5
        assert _partial_credit("VUS", "pathogenic", {}) == 0.25
        assert _partial_credit("benign", "pathogenic", {}) == 0.0


# =============================================================================
# TASK OUTCOME SCORING
# =============================================================================


class TestTaskOutcomeScoring:
    """Test the task-level outcome scoring function."""

    def test_correct_position(self):
        from bioeval.debate.tasks import DEBATE_TASKS, score_debate_task_outcome

        task = DEBATE_TASKS[0]
        gt_class = task.ground_truth["classification"]
        result = score_debate_task_outcome(task, gt_class, f"Because of {' '.join(task.ground_truth['key_criteria'][:3])}")
        assert result["position_correct"] is True
        assert result["accuracy"] == 1.0

    def test_wrong_position(self):
        from bioeval.debate.tasks import DEBATE_TASKS, score_debate_task_outcome

        task = DEBATE_TASKS[0]
        result = score_debate_task_outcome(task, "benign", "No reasoning.")
        assert result["position_correct"] is False

    def test_reasoning_quality(self):
        from bioeval.debate.tasks import DEBATE_TASKS, score_debate_task_outcome

        task = DEBATE_TASKS[0]
        criteria = task.ground_truth["key_criteria"]
        answer = f"Analysis: {' '.join(criteria)}"
        result = score_debate_task_outcome(task, task.ground_truth["classification"], answer)
        assert result["reasoning_quality"] > 0.5


# =============================================================================
# TASK WRAPPER
# =============================================================================


class TestTaskWrapper:
    """Test wrapping existing component tasks for debate."""

    def test_wrap_eval_task(self):
        from bioeval.debate.wrapper import wrap_eval_task
        from bioeval.models.base import EvalTask

        task = EvalTask(
            id="test_001",
            component="causalbio",
            task_type="knockout_prediction",
            prompt="Is gene X essential?",
            ground_truth={"effect": "essential"},
        )
        wrapped = wrap_eval_task(task, answer_options=["essential", "non-essential"])
        assert wrapped.id.startswith("debate_wrap_")
        assert wrapped.source_task_id == "test_001"
        assert wrapped.answer_options == ["essential", "non-essential"]
        assert wrapped.scenario == "Is gene X essential?"


# =============================================================================
# CONFIG & REGISTRY INTEGRATION
# =============================================================================


class TestIntegration:
    """Test integration with config, registry, and normalizer."""

    def test_debate_in_components(self):
        from bioeval.config import COMPONENTS

        assert "debate" in COMPONENTS

    def test_debate_in_task_types(self):
        from bioeval.config import TASK_TYPES

        assert "debate" in TASK_TYPES
        assert "variant_interpretation" in TASK_TYPES["debate"]

    def test_debate_in_registry(self):
        from bioeval.registry import REGISTRY

        assert "debate" in REGISTRY
        info = REGISTRY["debate"]
        assert info.evaluator_class == "DebateEvaluator"
        assert info.evaluator_module == "bioeval.debate.evaluator"

    def test_normalizer(self):
        from bioeval.scoring.normalizer import normalize_debate, normalize_result

        result = {
            "task_id": "test_001",
            "scores": {
                "composite_score": 0.72,
                "outcome_accuracy": 1.0,
                "correction_rate": 0.8,
                "reversal_rate": 0.0,
                "sycophancy_score": 0.05,
                "dissent_preservation": 0.6,
                "accuracy_per_1k_tokens": 0.2,
                "protocol": "simultaneous",
            },
        }
        ns = normalize_debate(result)
        assert ns.component == "debate"
        assert ns.score == 0.72
        assert ns.passed is True
        assert "outcome_accuracy" in ns.subscores

        # Also via dispatcher
        ns2 = normalize_result(result, "debate")
        assert ns2.score == ns.score

    def test_debate_constants(self):
        from bioeval.config import (
            DEFAULT_DEBATE_PROTOCOL,
            DEFAULT_DEBATE_AGENTS,
            DEFAULT_DEBATE_ROUNDS,
            DEFAULT_DEBATE_TERMINATION,
        )

        assert DEFAULT_DEBATE_PROTOCOL == "simultaneous"
        assert DEFAULT_DEBATE_AGENTS == 3
        assert DEFAULT_DEBATE_ROUNDS == 3
        assert DEFAULT_DEBATE_TERMINATION == "adaptive"


# =============================================================================
# EVALUATOR
# =============================================================================


class TestEvaluator:
    """Test DebateEvaluator interface."""

    def test_load_tasks(self):
        from bioeval.debate.evaluator import DebateEvaluator

        evaluator = DebateEvaluator(model_name="dummy", include_baseline=False)
        tasks = evaluator.load_tasks()
        assert len(tasks) == 25
        # Check adapter properties
        for t in tasks:
            assert hasattr(t, "id")
            assert hasattr(t, "task_type")
            assert isinstance(t.task_type, str)
            assert hasattr(t, "prompt")
            assert hasattr(t, "ground_truth")

    def test_evaluator_init_protocols(self):
        """Evaluator should accept all protocol types."""
        from bioeval.debate.evaluator import DebateEvaluator

        for proto in ["round_robin", "simultaneous", "judge_mediated"]:
            ev = DebateEvaluator(model_name="dummy", protocol=proto, include_baseline=False)
            assert ev.protocol_type.value == proto


# =============================================================================
# SIMULATION
# =============================================================================


class TestSimulation:
    """Test debate simulation integration."""

    def test_simulate_debate_good(self):
        from bioeval.simulation import _simulate_debate
        import random

        result = _simulate_debate("good", random.Random(42))
        assert result["component"] == "debate"
        assert result["num_tasks"] == 25
        assert len(result["results"]) == 25
        for r in result["results"]:
            assert "scores" in r
            assert r["scores"]["outcome_correct"] is True

    def test_simulate_debate_bad(self):
        from bioeval.simulation import _simulate_debate
        import random

        result = _simulate_debate("bad", random.Random(42))
        for r in result["results"]:
            assert r["scores"]["outcome_correct"] is False

    def test_simulate_debate_mixed(self):
        from bioeval.simulation import _simulate_debate
        import random

        result = _simulate_debate("mixed", random.Random(42))
        correct_count = sum(1 for r in result["results"] if r["scores"]["outcome_correct"])
        # Should have a mix
        assert 0 < correct_count < 25


# =============================================================================
# PROTOCOL FACTORY
# =============================================================================


class TestProtocolFactory:
    """Test protocol factory function."""

    def test_create_all_protocols(self):
        from bioeval.debate.protocols import (
            ProtocolType,
            DebateConfig,
            create_protocol,
            RoundRobinProtocol,
            SimultaneousProtocol,
            JudgeMediatedProtocol,
        )
        from bioeval.debate.agents import AgentModelPool, create_homogeneous_panel

        panel = create_homogeneous_panel("dummy", with_judge=True)
        pool = AgentModelPool()

        expected = {
            ProtocolType.ROUND_ROBIN: RoundRobinProtocol,
            ProtocolType.SIMULTANEOUS: SimultaneousProtocol,
            ProtocolType.JUDGE_MEDIATED: JudgeMediatedProtocol,
        }
        for ptype, expected_cls in expected.items():
            config = DebateConfig(protocol_type=ptype)
            proto = create_protocol(ptype, panel, config, pool)
            assert isinstance(proto, expected_cls)

    def test_unknown_protocol_raises(self):
        from bioeval.debate.protocols import ProtocolType, DebateConfig, create_protocol
        from bioeval.debate.agents import AgentModelPool, create_homogeneous_panel

        panel = create_homogeneous_panel("dummy")
        pool = AgentModelPool()
        # Use a mock unknown type
        with pytest.raises(ValueError):
            create_protocol("invalid", panel, DebateConfig(protocol_type=ProtocolType.SIMULTANEOUS), pool)
