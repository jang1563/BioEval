"""Model backends and base evaluator interface for BioEval.

Provides unified model routing across Anthropic, OpenAI, and
OpenAI-compatible backends (DeepSeek, Groq, Gemini, Together).
Includes the BaseEvaluator class, EvalTask/EvalResult data types,
and retry logic with exponential backoff.
"""
