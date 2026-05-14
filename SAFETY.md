# Responsible Use and Safety Scope

BioEval is a **multi-dimensional evaluation framework** for assessing whether
large language models can reason about biology rather than just recall facts.
It is intended for evaluation research and benchmarking; it is not a deployed
safety system.

## In Scope

- Evaluation of LLMs across multiple biological reasoning components
  (protocol execution, prediction, debate, methodological audit, long-horizon)
- Comparison of evaluation harnesses, scoring rubrics, and judge models
- Extension of the benchmark with new domain tasks under the same scoring
  contract
- Reproducible reporting of base-296 / extended-400 task results with
  version-pinned task counts

## Out of Scope

- Use as a sole determinant of model deployment readiness for biological
  applications; BioEval measures reasoning quality on a curated task set,
  not safety on adversarial inputs
- Reframing aggregate accuracy as a global capability claim about a model
- Adversarial reuse: repurposing tasks to bypass safety systems on
  deployed models
- Use of tasks that touch dual-use territory (e.g. in BioAmbiguity, certain
  long-horizon items) outside of evaluation context

## Withheld Content

- BioEval focuses on legitimate biological reasoning. Tasks that intersect
  the dual-use frontier are documented with safety framing and do not
  contain operational synthesis, dosing, or weaponization detail.
- Per-task ground-truth labels are released; per-model raw outputs are
  released only at the level needed to reproduce the metric.

## Reporting Concerns

- Open a GitHub issue with the `safety` label for a task definition that
  could be misused, a label that is wrong, or an evaluation result that
  is misleading.
- For sensitive disclosures, email jak4013@med.cornell.edu with subject
  "BIOEVAL SAFETY".

## Limitations Recap

- Solo author for task curation; expert review pending
- 296 base / 400 extended tasks is a sampled set; not exhaustive of
  biological reasoning
- LLM-as-judge scoring introduces evaluator-model dependence; multi-judge
  consistency is reported but not yet formally adjudicated
- English-only

See also [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md) and [`docs/STATUS.md`](docs/STATUS.md).
