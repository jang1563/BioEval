"""
Component registry for BioEval.

Provides a centralized registry for evaluation components, making it easy to:
- Add new components without modifying cli.py
- List available components and their capabilities
- Discover task counts and data tiers
- Validate component configurations

Usage:
    from bioeval.registry import REGISTRY

    # List all components
    for name, info in REGISTRY.items():
        print(f"{name}: {info.description}")

    # Get evaluator for a component
    evaluator = REGISTRY["adversarial"].create_evaluator("claude-sonnet-4-20250514")

    # Add a custom component
    register_component("my_component", ComponentInfo(...))
"""

from __future__ import annotations

import inspect
from contextlib import contextmanager
from dataclasses import dataclass, field


class _RegistryDummyModel:
    """Dummy model used to bypass API client initialization during task loading."""

    def generate(self, prompt: str, **kwargs) -> str:
        return ""

    def generate_chat(self, messages: list, **kwargs) -> str:
        return ""


@contextmanager
def _bypass_base_model_init():
    """Temporarily bypass BaseEvaluator model client setup."""
    try:
        from bioeval.models.base import BaseEvaluator
    except Exception:
        # If base module is unavailable, proceed without patching.
        yield
        return

    original = BaseEvaluator._init_model
    BaseEvaluator._init_model = lambda self, *args, **kwargs: _RegistryDummyModel()
    try:
        yield
    finally:
        BaseEvaluator._init_model = original


@dataclass
class ComponentInfo:
    """Metadata and factory for a BioEval component."""

    name: str
    description: str
    evaluator_module: str  # e.g., "bioeval.adversarial.tasks"
    evaluator_class: str  # e.g., "AdversarialEvaluator"
    task_data_module: str  # Module containing task data (for stats/validation)
    task_types: list[str] = field(default_factory=list)
    supports_data_tiers: list[str] = field(default_factory=lambda: ["base"])
    normalizer_name: str = ""  # Name of the normalizer function (if any)
    judge_rubric_types: list[str] = field(default_factory=list)

    def create_evaluator(self, model: str):
        """Dynamically import and instantiate the evaluator."""
        import importlib

        mod = importlib.import_module(self.evaluator_module)
        cls = getattr(mod, self.evaluator_class)
        return cls(model)

    def load_tasks(self, data_tier: str = "base"):
        """Load tasks using the evaluator's load_tasks method."""
        # Create a dummy evaluator just to load tasks (model not used for loading)
        with _bypass_base_model_init():
            evaluator = self.create_evaluator("dummy")
        load_tasks = getattr(evaluator, "load_tasks")
        sig = inspect.signature(load_tasks)
        has_var_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
        if "data_tier" in sig.parameters or has_var_kwargs:
            return load_tasks(data_tier=data_tier)
        return load_tasks()

    def get_task_count(self, data_tier: str = "base") -> int:
        """Get the number of tasks for this component."""
        try:
            tasks = self.load_tasks(data_tier=data_tier)
            return len(tasks)
        except Exception:
            return 0


# =============================================================================
# BUILT-IN COMPONENTS
# =============================================================================

_BUILTIN_COMPONENTS = {
    "protoreason": ComponentInfo(
        name="protoreason",
        description="Protocol reasoning: step ordering, missing steps, calculations, troubleshooting",
        evaluator_module="bioeval.protoreason.evaluator",
        evaluator_class="ProtoReasonEvaluator",
        task_data_module="bioeval.protoreason.evaluator",
        task_types=["step_ordering", "missing_step", "calculation", "troubleshooting", "safety"],
        supports_data_tiers=["base", "extended", "advanced"],
        normalizer_name="normalize_protoreason",
        judge_rubric_types=["protocol_troubleshooting", "calculation"],
    ),
    "causalbio": ComponentInfo(
        name="causalbio",
        description="Causal biology: knockouts, pathways, drug response, epistasis",
        evaluator_module="bioeval.causalbio.evaluator",
        evaluator_class="CausalBioEvaluator",
        task_data_module="bioeval.causalbio.evaluator",
        task_types=["knockout_prediction", "pathway_reasoning", "drug_response", "epistasis"],
        supports_data_tiers=["base", "extended", "advanced"],
        normalizer_name="normalize_causalbio",
        judge_rubric_types=["knockout_prediction", "pathway_reasoning", "epistasis"],
    ),
    "designcheck": ComponentInfo(
        name="designcheck",
        description="Experimental design critique: flaw detection and severity classification",
        evaluator_module="bioeval.designcheck.evaluator",
        evaluator_class="DesignCheckEvaluator",
        task_data_module="bioeval.designcheck.evaluator",
        task_types=["flaw_detection"],
        supports_data_tiers=["base", "extended", "advanced"],
        normalizer_name="normalize_designcheck",
        judge_rubric_types=["flaw_detection"],
    ),
    "adversarial": ComponentInfo(
        name="adversarial",
        description="Adversarial robustness: false premises, hallucination traps, edge cases",
        evaluator_module="bioeval.adversarial.tasks",
        evaluator_class="AdversarialEvaluator",
        task_data_module="bioeval.adversarial.tasks",
        task_types=[
            "false_premise",
            "hallucination_trap",
            "misleading_context",
            "edge_case",
            "contradictory",
            "plausible_nonsense",
            "outdated_knowledge",
            "overly_specific",
        ],
        supports_data_tiers=["base"],
        normalizer_name="normalize_adversarial",
    ),
    "multiturn": ComponentInfo(
        name="multiturn",
        description="Multi-turn dialogue: hypothesis refinement, experimental design, troubleshooting",
        evaluator_module="bioeval.multiturn.dialogues",
        evaluator_class="MultiTurnEvaluator",
        task_data_module="bioeval.multiturn.dialogues",
        task_types=["hypothesis_refinement", "experimental_design", "troubleshooting", "data_interpretation", "peer_review"],
        supports_data_tiers=["base", "extended"],
        normalizer_name="normalize_multiturn",
    ),
    "calibration": ComponentInfo(
        name="calibration",
        description="Confidence calibration: uncertainty quantification and overconfidence detection",
        evaluator_module="bioeval.scoring.calibration",
        evaluator_class="CalibrationEvaluator",
        task_data_module="bioeval.scoring.calibration",
        task_types=[
            "acknowledge_unknown",
            "high_confidence_correct",
            "partial_knowledge",
            "context_dependent",
            "moderate_confidence",
            "overconfidence_trap",
        ],
        supports_data_tiers=["base"],
        normalizer_name="normalize_calibration",
    ),
    "biosafety": ComponentInfo(
        name="biosafety",
        description="Biological safety: BSL classification, dual-use recognition, risk assessment, ethics",
        evaluator_module="bioeval.biosafety.tasks",
        evaluator_class="BiosafetyEvaluator",
        task_data_module="bioeval.biosafety.tasks",
        task_types=[
            "bsl_classification",
            "dual_use_recognition",
            "responsible_refusal",
            "risk_assessment",
            "ethics_reasoning",
        ],
        supports_data_tiers=["base"],
        normalizer_name="normalize_biosafety",
    ),
    "datainterp": ComponentInfo(
        name="datainterp",
        description="Data interpretation: qPCR analysis, dose-response, statistical tests, survival analysis, multi-assay integration",
        evaluator_module="bioeval.datainterp.tasks",
        evaluator_class="DataInterpEvaluator",
        task_data_module="bioeval.datainterp.tasks",
        task_types=["qpcr_analysis", "dose_response", "statistical_test", "survival_analysis", "multi_assay"],
        supports_data_tiers=["base"],
        normalizer_name="normalize_datainterp",
    ),
    "debate": ComponentInfo(
        name="debate",
        description="Multi-agent debate: variant interpretation, diagnosis, evidence synthesis via structured debate",
        evaluator_module="bioeval.debate.evaluator",
        evaluator_class="DebateEvaluator",
        task_data_module="bioeval.debate.tasks",
        task_types=[
            "variant_interpretation",
            "differential_diagnosis",
            "experimental_critique",
            "evidence_synthesis",
            "mechanism_dispute",
        ],
        supports_data_tiers=["base"],
        normalizer_name="normalize_debate",
        judge_rubric_types=["debate_outcome", "debate_process"],
    ),
    "longhorizon": ComponentInfo(
        name="longhorizon",
        description="Long-horizon scientific reasoning: constraint tracking, "
                    "state accumulation, error propagation, resource management, "
                    "adaptive replanning across multi-stage experiments",
        evaluator_module="bioeval.longhorizon.evaluator",
        evaluator_class="LongHorizonEvaluator",
        task_data_module="bioeval.longhorizon.tasks",
        task_types=[
            "constraint_tracking",
            "state_accumulation",
            "error_propagation",
            "resource_management",
            "adaptive_replanning",
        ],
        supports_data_tiers=["base"],
        normalizer_name="normalize_longhorizon",
        judge_rubric_types=["adaptive_replanning", "error_propagation_reasoning"],
    ),
    "agentic": ComponentInfo(
        name="agentic",
        description="Pseudo-agentic multi-step scientific reasoning: "
                    "experimental design, bioinformatics pipelines, "
                    "literature research, troubleshooting workflows",
        evaluator_module="bioeval.agentic.evaluator",
        evaluator_class="AgenticEvaluator",
        task_data_module="bioeval.agentic.tasks",
        task_types=[
            "experimental_design",
            "bioinformatics_pipeline",
            "literature_research",
            "troubleshooting",
        ],
        supports_data_tiers=["base"],
        normalizer_name="normalize_agentic",
    ),
    "bioambiguity": ComponentInfo(
        name="bioambiguity",
        description="Context-dependent biological reasoning: same gene/pathway/compound "
                    "behaves differently across tissue, disease, species, dose, or developmental context",
        evaluator_module="bioeval.bioambiguity.evaluator",
        evaluator_class="BioAmbiguityEvaluator",
        task_data_module="bioeval.bioambiguity.tasks",
        task_types=[
            "gene_context",
            "pathway_crosstalk",
            "dose_response",
            "temporal_shift",
            "species_translation",
        ],
        supports_data_tiers=["base"],
        normalizer_name="normalize_bioambiguity",
        judge_rubric_types=["bioambiguity_reasoning"],
    ),
}

# Public registry (mutable copy)
REGISTRY: dict[str, ComponentInfo] = dict(_BUILTIN_COMPONENTS)


def register_component(name: str, info: ComponentInfo):
    """Register a new component in the global registry."""
    if name in REGISTRY:
        raise ValueError(f"Component '{name}' already registered")
    REGISTRY[name] = info


def unregister_component(name: str):
    """Remove a component from the registry."""
    if name in _BUILTIN_COMPONENTS:
        raise ValueError(f"Cannot unregister built-in component '{name}'")
    REGISTRY.pop(name, None)


def list_components() -> list[str]:
    """Return sorted list of registered component names."""
    return sorted(REGISTRY.keys())


def get_component(name: str) -> ComponentInfo:
    """Get component info by name, raising KeyError if not found."""
    if name not in REGISTRY:
        available = ", ".join(list_components())
        raise KeyError(f"Unknown component '{name}'. Available: {available}")
    return REGISTRY[name]


# =============================================================================
# TEXT OUTPUT
# =============================================================================


def print_registry():
    """Print the component registry."""
    print(f"\n{'=' * 60}")
    print("BioEval Component Registry")
    print(f"{'=' * 60}")
    print(f"\n{len(REGISTRY)} registered components:\n")

    for name in sorted(REGISTRY):
        info = REGISTRY[name]
        tiers = ", ".join(info.supports_data_tiers)
        types = ", ".join(info.task_types[:4])
        if len(info.task_types) > 4:
            types += f" (+{len(info.task_types) - 4} more)"
        print(f"  {name}")
        print(f"    {info.description}")
        print(f"    Types: {types}")
        print(f"    Tiers: {tiers}")
        print()
