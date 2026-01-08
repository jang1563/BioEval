"""
Base evaluator interface and model wrappers for BioEval.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import os
import json
from datetime import datetime


@dataclass
class EvalTask:
    """Single evaluation task."""
    id: str
    component: str
    task_type: str
    prompt: str
    ground_truth: dict
    metadata: Optional[dict] = None
    system_prompt: Optional[str] = None  # Optional system prompt for enhanced reasoning


@dataclass  
class EvalResult:
    """Result from a single evaluation."""
    task_id: str
    model: str
    response: str
    scores: dict
    error_annotations: Optional[list] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class BaseEvaluator(ABC):
    """Abstract base class for component evaluators."""
    
    def __init__(self, model_name: str = "claude-sonnet-4-20250514"):
        self.model_name = model_name
        self.model = self._init_model(model_name)
    
    def _init_model(self, model_name: str):
        """Initialize the appropriate model client."""
        if "claude" in model_name.lower():
            return ClaudeModel(model_name)
        elif "gpt" in model_name.lower():
            return OpenAIModel(model_name)
        else:
            raise ValueError(f"Unknown model: {model_name}")
    
    @abstractmethod
    def load_tasks(self) -> list[EvalTask]:
        """Load evaluation tasks for this component."""
        pass
    
    @abstractmethod
    def score_response(self, task: EvalTask, response: str) -> dict:
        """Score a model response against ground truth."""
        pass
    
    def evaluate_task(self, task: EvalTask) -> EvalResult:
        """Run evaluation on a single task."""
        response = self.model.generate(task.prompt, system=task.system_prompt)
        scores = self.score_response(task, response)

        return EvalResult(
            task_id=task.id,
            model=self.model_name,
            response=response,
            scores=scores
        )
    
    def run_evaluation(self, tasks: Optional[list[EvalTask]] = None) -> list[EvalResult]:
        """Run full evaluation on all tasks."""
        if tasks is None:
            tasks = self.load_tasks()
        
        results = []
        for task in tasks:
            result = self.evaluate_task(task)
            results.append(result)
        
        return results


class ClaudeModel:
    """Wrapper for Anthropic Claude models."""

    def __init__(self, model_name: str = "claude-sonnet-4-20250514"):
        from anthropic import Anthropic
        self.client = Anthropic()
        self.model = model_name

    def generate(self, prompt: str, max_tokens: int = 2048, system: Optional[str] = None) -> str:
        """Generate response from Claude."""
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}]
        }
        if system:
            kwargs["system"] = system

        response = self.client.messages.create(**kwargs)
        return response.content[0].text


class OpenAIModel:
    """Wrapper for OpenAI models."""

    def __init__(self, model_name: str = "gpt-4"):
        from openai import OpenAI
        self.client = OpenAI()
        self.model = model_name

    def generate(self, prompt: str, max_tokens: int = 2048, system: Optional[str] = None) -> str:
        """Generate response from OpenAI model."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=messages
        )
        return response.choices[0].message.content
