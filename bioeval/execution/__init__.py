"""Async execution and response caching for BioEval.

Provides high-throughput parallel evaluation via async API calls,
configurable concurrency limits, exponential backoff retry logic,
and a response cache to avoid redundant API calls.
"""
