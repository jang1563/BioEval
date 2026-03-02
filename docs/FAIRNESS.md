# Token Budget Fairness

## Background

BioEval evaluates multiple LLMs using a standardized `max_tokens=2048` output
budget. However, **Gemini 2.5 thinking models** present a unique challenge:
thinking tokens are consumed from the output token budget, leaving significantly
fewer tokens for the actual response.

## The Problem

When `max_tokens=2048`:

| Model | Thinking tokens | Response tokens | Effective output |
|-------|:-:|:-:|:-:|
| Claude Sonnet 4 | N/A (separate) | 2048 | 2048 |
| GPT-4o | N/A | 2048 | 2048 |
| DeepSeek V3 | N/A | 2048 | 2048 |
| Llama 3.3 70B | N/A | 2048 | 2048 |
| Gemini 2.5 Flash | ~1500 | ~500 | **~500** |

This caused Gemini responses to be truncated (avg 566 chars for DesignCheck vs
5141 for Claude), leading to artificially low scores.

## The Solution

BioEval applies a **4x token multiplier** for Gemini thinking models:

```python
GEMINI_THINKING_TOKEN_MULTIPLIER = 4
# max_tokens=2048 -> max_completion_tokens=8192
```

This gives Gemini sufficient budget for both thinking (~6000 tokens) and
response content (~2000 tokens), achieving functional parity with other models.

## Token Budget Summary

| Model | max_tokens | Effective param | Budget |
|-------|:-:|---|:-:|
| Claude Sonnet 4 | 2048 | `max_tokens=2048` | 2048 |
| GPT-4o | 2048 | `max_tokens=2048` | 2048 |
| DeepSeek V3 | 2048 | `max_tokens=2048` | 2048 |
| Llama 3.3 70B | 2048 | `max_tokens=2048` | 2048 |
| Gemini 2.5 Flash | 2048 | `max_completion_tokens=8192` | 8192 |

## Strict Fairness Mode

For strict token-budget comparisons, use `--equalize-tokens`:

```bash
bioeval run --all -m gemini-2.5-flash --equalize-tokens
```

This disables the multiplier, giving Gemini the same `max_tokens=2048` as other
models. Note that this will likely produce truncated Gemini responses.

## Recording

All result files include metadata recording the fairness setting:

```json
{
  "metadata": {
    "equalize_tokens": false,
    "gemini_token_multiplier": 4
  }
}
```

## Disclosure for Publication

When reporting BioEval results, disclose:

1. Whether `--equalize-tokens` was used
2. The Gemini token multiplier value (default: 4x)
3. That Gemini's total output budget differs from other models

This transparency allows readers to assess whether the token asymmetry
affects the validity of cross-model comparisons.
