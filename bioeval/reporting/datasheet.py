"""
Datasheet for Datasets (Gebru et al., 2021) — BioEval

Generates a structured datasheet following the Datasheets for Datasets
framework, as recommended by NeurIPS Datasets & Benchmarks track.
"""


def generate_datasheet() -> dict:
    """Generate the BioEval datasheet as structured data."""
    return {
        "title": "BioEval: A Multi-Component Benchmark for Evaluating LLM Biology Reasoning",
        "version": "0.3.0",

        # ── Motivation ────────────────────────────────────────────────
        "motivation": {
            "purpose": (
                "BioEval evaluates frontier large language models on six dimensions of "
                "biological reasoning: protocol understanding, causal inference, experimental "
                "design critique, adversarial robustness, multi-turn scientific dialogue, "
                "and confidence calibration."
            ),
            "creators": "Developed as part of AI biology benchmarking research.",
            "funding": "Self-funded research project.",
            "who_created": (
                "Tasks were authored by researchers with graduate-level training in "
                "molecular biology, cancer biology, and bioinformatics."
            ),
        },

        # ── Composition ───────────────────────────────────────────────
        "composition": {
            "instance_types": (
                "Each instance is a structured evaluation task containing: "
                "a natural-language prompt, ground-truth annotations (expected behaviors, "
                "correct answers, flaws to detect, etc.), scoring rubric metadata, "
                "and difficulty tier information."
            ),
            "total_instances": "~190 tasks (base+extended), ~300 including advanced tier.",
            "components": {
                "ProtoReason": "Protocol comprehension: step ordering, gap identification, calculations, troubleshooting.",
                "CausalBio": "Causal biological reasoning: gene knockout prediction, pathway analysis, drug response, epistasis.",
                "DesignCheck": "Experimental design critique: identifying flaws in proposed study designs.",
                "Adversarial": "Adversarial robustness: false premises, hallucination traps, misleading context.",
                "MultiTurn": "Multi-turn dialogue: maintaining scientific coherence across conversation turns.",
                "Calibration": "Confidence calibration: appropriate uncertainty expression, overconfidence detection.",
            },
            "labels": (
                "Ground truth includes: categorical labels (essential/non-essential, up/down), "
                "expected key terms, flaw lists with severity, direction predictions, "
                "confidence behavior expectations, and nuance indicators."
            ),
            "missing_data": "No missing data; all tasks are complete with ground truth.",
            "confidentiality": "No confidential data. All tasks are constructed from public biology knowledge.",
            "offensive_content": "No offensive content. Tasks are scientific in nature.",
        },

        # ── Collection ────────────────────────────────────────────────
        "collection": {
            "process": (
                "Tasks were manually authored by domain experts based on established "
                "biology knowledge from textbooks, review articles, and primary literature. "
                "No data was scraped from existing benchmarks or copyrighted sources."
            ),
            "collection_mechanisms": "Manual expert authoring with structured templates.",
            "who_collected": "Researchers with molecular/cancer biology expertise.",
            "timeframe": "2024-2025.",
            "ethical_review": "Not applicable — no human subjects data.",
            "third_party_data": "No third-party data was used.",
        },

        # ── Preprocessing ────────────────────────────────────────────
        "preprocessing": {
            "steps": (
                "Tasks undergo validation for scientific accuracy, prompt clarity, "
                "and scoring rubric completeness. Human validation protocol available "
                "via bioeval.validation.human_protocol module."
            ),
            "raw_data_preserved": "All task data is stored in Python source files with full metadata.",
        },

        # ── Uses ──────────────────────────────────────────────────────
        "uses": {
            "intended_uses": (
                "Evaluating and comparing LLMs on biology-specific reasoning tasks. "
                "Identifying specific weaknesses (e.g., poor causal reasoning, "
                "overconfidence, vulnerability to adversarial prompts)."
            ),
            "not_intended_for": (
                "Not intended for clinical decision-making, medical diagnosis, "
                "or as a substitute for wet-lab validation. Not designed to rank "
                "models for general intelligence or non-biology domains."
            ),
            "potential_misuse": (
                "Could be used to overfit models to biology benchmark tasks without "
                "genuine reasoning improvement. Private test split mitigates this risk."
            ),
        },

        # ── Distribution ──────────────────────────────────────────────
        "distribution": {
            "how_distributed": "Open-source Python package (pip installable).",
            "license": "MIT License (or similar permissive license).",
            "access_restrictions": "None — fully open access.",
            "export_controls": "Not applicable.",
        },

        # ── Maintenance ───────────────────────────────────────────────
        "maintenance": {
            "who_maintains": "Original benchmark authors.",
            "contact": "Via GitHub issues on the BioEval repository.",
            "update_plan": (
                "Planned annual updates to add new tasks, retire contaminated items, "
                "and track evolving LLM capabilities. Private split enables "
                "contamination detection between versions."
            ),
            "versioning": "Semantic versioning (MAJOR.MINOR.PATCH). Current: 0.3.0.",
        },
    }


def print_datasheet():
    """Print the datasheet in a human-readable format."""
    ds = generate_datasheet()

    print(f"\n{'=' * 70}")
    print(f"DATASHEET FOR DATASETS: {ds['title']}")
    print(f"Version: {ds['version']}")
    print(f"{'=' * 70}")

    for section_key, section in ds.items():
        if section_key in ("title", "version"):
            continue
        print(f"\n{'─' * 50}")
        print(f"  {section_key.upper()}")
        print(f"{'─' * 50}")
        if isinstance(section, dict):
            for k, v in section.items():
                if isinstance(v, dict):
                    print(f"\n  {k}:")
                    for sk, sv in v.items():
                        print(f"    {sk}: {sv}")
                else:
                    # Wrap long text
                    label = k.replace("_", " ").title()
                    print(f"\n  {label}:")
                    print(f"    {v}")
        else:
            print(f"  {section}")
