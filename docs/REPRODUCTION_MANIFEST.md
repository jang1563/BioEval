# BioEval Reproduction Manifest

This document records all parameters required to exactly reproduce a BioEval
evaluation run.  Every published result table **must** reference a manifest
instance (either inline in the JSON output or as a separate file).

---

## Required Fields

| Field | Description | Example |
|---|---|---|
| `bioeval_version` | Semantic version of BioEval | `0.3.0` |
| `git_sha` | Full Git SHA of the BioEval commit | `a1b2c3d...` |
| `task_set_sha256` | SHA-256 hash of the serialized task set | `e3b0c44...` |
| `python_version` | Python interpreter version | `3.11.14` |
| `model` | Model identifier used for generation | `claude-sonnet-4-20250514` |
| `temperature` | Generation temperature | `0.0` |
| `seed` | Random seed for reproducibility | `42` |
| `data_tier` | Task subset used (`base`, `extended`, `all`) | `all` |
| `timestamp` | ISO 8601 evaluation start time | `2026-02-28T10:00:00` |

## Optional Fields

| Field | Description | Example |
|---|---|---|
| `judge_model` | Model used for LLM-as-Judge scoring | `claude-sonnet-4-20250514` |
| `judge_temperature` | Judge model temperature | `0.0` |
| `depmap_release` | DepMap data release for CausalBio tasks | `24Q4` |
| `n_runs` | Number of repeated runs for multi-run aggregation | `3` |
| `max_concurrent` | Async runner concurrency limit | `5` |
| `adapter_path` | LoRA adapter path (HuggingFace models) | `./adapters/bio-lora` |
| `dependency_versions` | Key dependency versions | `{"scipy": "1.14.0", ...}` |

---

## How to Generate

The CLI automatically records manifest fields in the output JSON under
`metadata`.  To verify reproducibility:

```bash
# Run evaluation with explicit seed and temperature
bioeval run --model claude-sonnet-4-20250514 \
    --seed 42 \
    --temperature 0.0 \
    --judge-temperature 0.0 \
    --data-tier all \
    --output results/run1.json

# Verify task set integrity
python -c "
from bioeval.registry import get_all_tasks
import hashlib, json
tasks = get_all_tasks('all')
h = hashlib.sha256(json.dumps([t.id for t in tasks], sort_keys=True).encode())
print(f'task_set_sha256: {h.hexdigest()}')
"
```

---

## Verification Checklist

Before submitting results for publication:

- [ ] `git_sha` matches a tagged release or is committed to `main`
- [ ] `task_set_sha256` matches the expected value for the data tier
- [ ] `temperature = 0.0` for deterministic generation (unless studying stochasticity)
- [ ] `seed` is documented and consistent across compared runs
- [ ] All model API versions are recorded (check provider changelogs)
- [ ] Multi-run results include per-run scores, not just aggregates
- [ ] Public/private split fractions match expected ~80/20 ratio
