# Example Results

This directory contains sample evaluation results from BioEval.

## Files

### `sample_comparison_results.json`

A comparison between enhanced and baseline prompt configurations on adversarial robustness tests.

**Key Findings:**

| Metric | Value |
|--------|-------|
| Enhanced Pass Rate | 83.3% |
| Baseline Pass Rate | 62.5% |
| Overall Improvement | +20.8% |

**Improvements by Test Type:**

| Test Type | Baseline | Enhanced | Change |
|-----------|----------|----------|--------|
| False Premise | 60% | 100% | +40% |
| Plausible Nonsense | 67% | 100% | +33% |
| Edge Case | 75% | 100% | +25% |
| Hallucination Trap | 80% | 100% | +20% |
| Overly Specific | 100% | 100% | 0% |
| Contradictory | 50% | 50% | 0% |
| Misleading Context | 0% | 0% | 0% |

## Generating Your Own Results

To run the comparison test yourself:

```bash
# Set your API key
export ANTHROPIC_API_KEY="your-key-here"

# Run comparison
python scripts/run_comparison.py
```

Results will be saved to the `results/` directory with timestamps.

## Understanding the Results

### Pass Rate
The percentage of adversarial tests where the model correctly identified the trap or provided an appropriate response.

### Test Types

- **False Premise**: Questions that contain incorrect assumptions the model should challenge
- **Hallucination Trap**: Questions about made-up entities the model should not recognize
- **Plausible Nonsense**: Realistic-sounding but incorrect biological claims
- **Edge Case**: Boundary conditions where standard rules may not apply
- **Misleading Context**: Irrelevant information that should be ignored
- **Contradictory**: Self-contradicting statements
- **Overly Specific**: Questions requiring unreasonably precise answers
