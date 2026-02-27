"""
Async Execution and Caching Module

Provides:
1. Async API calls for 10x faster evaluation
2. Response caching to avoid re-running expensive calls
3. Rate limiting to stay within API limits
4. Progress tracking and resumable evaluation
"""

import asyncio
import hashlib
import json
import os
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable, Any
import sqlite3

# =============================================================================
# CONFIGURATION
# =============================================================================


@dataclass
class ExecutionConfig:
    """Configuration for async execution."""

    max_concurrent: int = 5  # Max parallel API calls
    rate_limit_rpm: int = 50  # Requests per minute
    rate_limit_tpm: int = 40000  # Tokens per minute
    retry_attempts: int = 3
    retry_delay: float = 1.0  # Seconds between retries
    cache_enabled: bool = True
    cache_dir: str = ".bioeval_cache"
    timeout: float = 120.0  # Seconds per request


# =============================================================================
# CACHING
# =============================================================================


class ResponseCache:
    """SQLite-based response cache for API calls."""

    def __init__(self, cache_dir: str = ".bioeval_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.db_path = self.cache_dir / "cache.db"
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS responses (
                    cache_key TEXT PRIMARY KEY,
                    model TEXT,
                    prompt_hash TEXT,
                    response TEXT,
                    usage_json TEXT,
                    created_at TEXT,
                    task_id TEXT
                )
            """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_task_id ON responses(task_id)
            """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_model ON responses(model)
            """
            )

    def _compute_key(self, model: str, prompt: str, system: Optional[str] = None) -> str:
        """Compute cache key from model and prompt."""
        content = f"{model}::{system or ''}::{prompt}"
        return hashlib.sha256(content.encode()).hexdigest()[:32]

    def get(self, model: str, prompt: str, system: Optional[str] = None) -> Optional[dict]:
        """Retrieve cached response if exists."""
        cache_key = self._compute_key(model, prompt, system)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT response, usage_json FROM responses WHERE cache_key = ?", (cache_key,))
            row = cursor.fetchone()

            if row:
                return {"response": row[0], "usage": json.loads(row[1]) if row[1] else None, "cached": True}
        return None

    def set(
        self,
        model: str,
        prompt: str,
        response: str,
        usage: Optional[dict] = None,
        system: Optional[str] = None,
        task_id: Optional[str] = None,
    ):
        """Store response in cache."""
        cache_key = self._compute_key(model, prompt, system)
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO responses 
                (cache_key, model, prompt_hash, response, usage_json, created_at, task_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    cache_key,
                    model,
                    prompt_hash,
                    response,
                    json.dumps(usage) if usage else None,
                    datetime.now().isoformat(),
                    task_id,
                ),
            )

    def get_stats(self) -> dict:
        """Get cache statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM responses")
            total = cursor.fetchone()[0]

            cursor = conn.execute("SELECT model, COUNT(*) FROM responses GROUP BY model")
            by_model = dict(cursor.fetchall())

        return {"total_cached": total, "by_model": by_model, "cache_path": str(self.db_path)}

    def clear(self, model: Optional[str] = None):
        """Clear cache, optionally for specific model only."""
        with sqlite3.connect(self.db_path) as conn:
            if model:
                conn.execute("DELETE FROM responses WHERE model = ?", (model,))
            else:
                conn.execute("DELETE FROM responses")


# =============================================================================
# RATE LIMITER
# =============================================================================


class RateLimiter:
    """Token bucket rate limiter for API calls."""

    def __init__(self, rpm: int = 50, tpm: int = 40000):
        self.rpm = rpm
        self.tpm = tpm
        self.request_times: list[float] = []
        self.token_usage: list[tuple[float, int]] = []
        self._lock = asyncio.Lock()

    async def acquire(self, estimated_tokens: int = 1000):
        """Wait until rate limit allows another request."""
        async with self._lock:
            now = time.time()

            # Clean old entries (older than 60 seconds)
            self.request_times = [t for t in self.request_times if now - t < 60]
            self.token_usage = [(t, tokens) for t, tokens in self.token_usage if now - t < 60]

            # Check request rate
            while len(self.request_times) >= self.rpm:
                wait_time = 60 - (now - self.request_times[0])
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                now = time.time()
                self.request_times = [t for t in self.request_times if now - t < 60]

            # Check token rate
            current_tokens = sum(tokens for _, tokens in self.token_usage)
            while current_tokens + estimated_tokens > self.tpm:
                wait_time = 60 - (now - self.token_usage[0][0])
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                now = time.time()
                self.token_usage = [(t, tokens) for t, tokens in self.token_usage if now - t < 60]
                current_tokens = sum(tokens for _, tokens in self.token_usage)

            # Record this request
            self.request_times.append(now)

    def record_usage(self, tokens: int):
        """Record actual token usage after request completes."""
        self.token_usage.append((time.time(), tokens))


# =============================================================================
# ASYNC CLIENT
# =============================================================================


class AsyncBioEvalClient:
    """Async client for running BioEval evaluations."""

    def __init__(self, model: str = "claude-sonnet-4-20250514", config: Optional[ExecutionConfig] = None):
        self.model = model
        self.config = config or ExecutionConfig()
        self.cache = ResponseCache(self.config.cache_dir) if self.config.cache_enabled else None
        self.rate_limiter = RateLimiter(rpm=self.config.rate_limit_rpm, tpm=self.config.rate_limit_tpm)
        self._client = None
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent)

        # Stats tracking
        self.stats = {"total_requests": 0, "cache_hits": 0, "api_calls": 0, "errors": 0, "total_tokens": 0}

    @property
    def client(self):
        """Lazy load async Anthropic client."""
        if self._client is None:
            from anthropic import AsyncAnthropic

            self._client = AsyncAnthropic()
        return self._client

    async def generate(
        self, prompt: str, system: Optional[str] = None, max_tokens: int = 2000, task_id: Optional[str] = None
    ) -> dict:
        """Generate a single response with caching and rate limiting."""
        self.stats["total_requests"] += 1

        # Check cache first
        if self.cache:
            cached = self.cache.get(self.model, prompt, system)
            if cached:
                self.stats["cache_hits"] += 1
                return cached

        # Rate limit and make API call
        async with self._semaphore:
            await self.rate_limiter.acquire(estimated_tokens=max_tokens)

            for attempt in range(self.config.retry_attempts):
                try:
                    messages = [{"role": "user", "content": prompt}]

                    kwargs = {"model": self.model, "max_tokens": max_tokens, "messages": messages}
                    if system:
                        kwargs["system"] = system

                    response = await asyncio.wait_for(self.client.messages.create(**kwargs), timeout=self.config.timeout)

                    self.stats["api_calls"] += 1

                    # Record token usage
                    usage = {"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens}
                    total_tokens = usage["input_tokens"] + usage["output_tokens"]
                    self.rate_limiter.record_usage(total_tokens)
                    self.stats["total_tokens"] += total_tokens

                    result = {"response": response.content[0].text, "usage": usage, "cached": False}

                    # Cache the response
                    if self.cache:
                        self.cache.set(
                            model=self.model,
                            prompt=prompt,
                            response=result["response"],
                            usage=usage,
                            system=system,
                            task_id=task_id,
                        )

                    return result

                except asyncio.TimeoutError:
                    self.stats["errors"] += 1
                    if attempt < self.config.retry_attempts - 1:
                        await asyncio.sleep(self.config.retry_delay * (attempt + 1))
                    else:
                        return {"response": "", "error": "Timeout", "cached": False}

                except Exception as e:
                    self.stats["errors"] += 1
                    if attempt < self.config.retry_attempts - 1:
                        await asyncio.sleep(self.config.retry_delay * (attempt + 1))
                    else:
                        return {"response": "", "error": str(e), "cached": False}

        return {"response": "", "error": "Max retries exceeded", "cached": False}

    async def batch_generate(
        self, tasks: list[dict], progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> list[dict]:
        """Generate responses for multiple tasks concurrently."""

        async def process_task(idx: int, task: dict) -> dict:
            result = await self.generate(
                prompt=task["prompt"],
                system=task.get("system"),
                max_tokens=task.get("max_tokens", 2000),
                task_id=task.get("task_id"),
            )
            result["task_id"] = task.get("task_id")
            result["task_idx"] = idx

            if progress_callback:
                progress_callback(idx + 1, len(tasks))

            return result

        # Run all tasks concurrently (semaphore limits parallelism)
        results = await asyncio.gather(*[process_task(i, task) for i, task in enumerate(tasks)])

        return sorted(results, key=lambda x: x["task_idx"])

    def get_stats(self) -> dict:
        """Get execution statistics."""
        stats = self.stats.copy()
        if self.cache:
            stats["cache"] = self.cache.get_stats()
        stats["cache_hit_rate"] = stats["cache_hits"] / stats["total_requests"] if stats["total_requests"] > 0 else 0
        return stats


# =============================================================================
# PROGRESS TRACKING
# =============================================================================


@dataclass
class EvaluationProgress:
    """Tracks evaluation progress for resumability."""

    total_tasks: int
    completed_tasks: int = 0
    failed_tasks: int = 0
    results: list = field(default_factory=list)
    start_time: Optional[str] = None
    end_time: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "EvaluationProgress":
        return cls(**data)


class ProgressTracker:
    """Saves and loads evaluation progress for resumability."""

    def __init__(self, progress_dir: str = ".bioeval_progress"):
        self.progress_dir = Path(progress_dir)
        self.progress_dir.mkdir(exist_ok=True)

    def _get_path(self, evaluation_id: str) -> Path:
        return self.progress_dir / f"{evaluation_id}.json"

    def save(self, evaluation_id: str, progress: EvaluationProgress):
        """Save progress to disk."""
        with open(self._get_path(evaluation_id), "w") as f:
            json.dump(progress.to_dict(), f, indent=2, default=str)

    def load(self, evaluation_id: str) -> Optional[EvaluationProgress]:
        """Load progress from disk."""
        path = self._get_path(evaluation_id)
        if path.exists():
            with open(path) as f:
                return EvaluationProgress.from_dict(json.load(f))
        return None

    def delete(self, evaluation_id: str):
        """Delete progress file."""
        path = self._get_path(evaluation_id)
        if path.exists():
            path.unlink()


# =============================================================================
# HIGH-LEVEL RUNNER
# =============================================================================


async def run_async_evaluation(
    tasks: list[dict],
    model: str = "claude-sonnet-4-20250514",
    config: Optional[ExecutionConfig] = None,
    evaluation_id: Optional[str] = None,
    resume: bool = True,
) -> tuple[list[dict], dict]:
    """
    Run evaluation asynchronously with caching and progress tracking.

    Args:
        tasks: List of task dicts with 'prompt', 'task_id', optional 'system'
        model: Model to use
        config: Execution configuration
        evaluation_id: ID for progress tracking (for resumability)
        resume: Whether to resume from previous progress

    Returns:
        Tuple of (results list, stats dict)
    """
    config = config or ExecutionConfig()
    client = AsyncBioEvalClient(model=model, config=config)

    # Progress tracking
    tracker = ProgressTracker()
    progress = None
    completed_task_ids = set()

    if evaluation_id and resume:
        progress = tracker.load(evaluation_id)
        if progress:
            completed_task_ids = {r.get("task_id") for r in progress.results}
            print(f"Resuming: {progress.completed_tasks}/{progress.total_tasks} already complete")

    if not progress:
        progress = EvaluationProgress(total_tasks=len(tasks), start_time=datetime.now().isoformat())

    # Filter to incomplete tasks
    remaining_tasks = [t for t in tasks if t.get("task_id") not in completed_task_ids]

    if not remaining_tasks:
        print("All tasks already completed!")
        return progress.results, client.get_stats()

    print(f"Running {len(remaining_tasks)} tasks with max {config.max_concurrent} concurrent...")

    # Progress callback
    def on_progress(completed: int, total: int):
        pct = (progress.completed_tasks + completed) / progress.total_tasks * 100
        print(f"\rProgress: {progress.completed_tasks + completed}/{progress.total_tasks} ({pct:.1f}%)", end="")

    # Run evaluation
    new_results = await client.batch_generate(remaining_tasks, progress_callback=on_progress)
    print()  # Newline after progress

    # Update progress
    progress.results.extend(new_results)
    progress.completed_tasks = len([r for r in progress.results if not r.get("error")])
    progress.failed_tasks = len([r for r in progress.results if r.get("error")])
    progress.end_time = datetime.now().isoformat()

    # Save progress
    if evaluation_id:
        tracker.save(evaluation_id, progress)

    stats = client.get_stats()
    print(
        f"\nStats: {stats['api_calls']} API calls, {stats['cache_hits']} cache hits, " f"{stats['total_tokens']} tokens used"
    )

    return progress.results, stats


def run_sync_wrapper(
    tasks: list[dict],
    model: str = "claude-sonnet-4-20250514",
    config: Optional[ExecutionConfig] = None,
    evaluation_id: Optional[str] = None,
) -> tuple[list[dict], dict]:
    """Synchronous wrapper for async evaluation."""
    return asyncio.run(run_async_evaluation(tasks=tasks, model=model, config=config, evaluation_id=evaluation_id))


# =============================================================================
# CLI UTILITIES
# =============================================================================


def clear_cache(model: Optional[str] = None):
    """Clear response cache."""
    cache = ResponseCache()
    cache.clear(model)
    print(f"Cache cleared" + (f" for model {model}" if model else ""))


def show_cache_stats():
    """Show cache statistics."""
    cache = ResponseCache()
    stats = cache.get_stats()
    print("Cache Statistics:")
    print(f"  Total cached responses: {stats['total_cached']}")
    print(f"  By model: {stats['by_model']}")
    print(f"  Cache path: {stats['cache_path']}")


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "clear-cache":
            model = sys.argv[2] if len(sys.argv) > 2 else None
            clear_cache(model)
        elif sys.argv[1] == "cache-stats":
            show_cache_stats()
    else:
        print("Usage:")
        print("  python async_runner.py clear-cache [model]")
        print("  python async_runner.py cache-stats")
