"""
Base evaluator interface and model wrappers for BioEval.

Supports:
- Anthropic Claude models (API)
- OpenAI models (API)
- OpenAI-compatible providers (DeepSeek, Groq, Gemini, Together)
- HuggingFace models (local, including LoRA fine-tuned)
"""

from __future__ import annotations

import time as _time
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
    source: Optional[str] = None  # Provenance: origin of the task (e.g. "DepMap_24Q4", "CLSI_M100")
    validator: Optional[str] = None  # Provenance: who validated the task (e.g. "domain_expert_1")


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


def init_model(
    model_name: str,
    temperature: float = 0.0,
    adapter_path: Optional[str] = None,
    use_4bit: bool = True,
):
    """Initialize model client based on name routing.

    This is the single source of truth for model name → backend mapping.
    Used by BaseEvaluator and standalone evaluators alike.
    """
    name_lower = model_name.lower()
    if "claude" in name_lower:
        return ClaudeModel(model_name, temperature=temperature)
    elif "gpt" in name_lower or "o1" in name_lower or "o3" in name_lower:
        return OpenAIModel(model_name, temperature=temperature)
    elif "deepseek" in name_lower:
        return OpenAICompatibleModel(
            model_name,
            base_url="https://api.deepseek.com",
            api_key_env="DEEPSEEK_API_KEY",
            temperature=temperature,
        )
    elif "groq" in name_lower or "mixtral" in name_lower:
        return OpenAICompatibleModel(
            model_name,
            base_url="https://api.groq.com/openai/v1",
            api_key_env="GROQ_API_KEY",
            temperature=temperature,
        )
    elif "gemini" in name_lower:
        return OpenAICompatibleModel(
            model_name,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key_env="GEMINI_API_KEY",
            temperature=temperature,
        )
    elif "llama" in name_lower or "together" in name_lower:
        return OpenAICompatibleModel(
            model_name,
            base_url="https://api.together.xyz/v1",
            api_key_env="TOGETHER_API_KEY",
            temperature=temperature,
        )
    elif "/" in model_name or adapter_path:
        # HuggingFace model (local)
        return HuggingFaceModel(model_name, adapter_path=adapter_path, use_4bit=use_4bit)
    else:
        raise ValueError(f"Unknown model: {model_name}")


class BaseEvaluator(ABC):
    """Abstract base class for component evaluators."""

    def __init__(
        self,
        model_name: str = "claude-sonnet-4-20250514",
        adapter_path: Optional[str] = None,
        use_4bit: bool = True,
        temperature: float = 0.0,
    ):
        self.model_name = model_name
        self.adapter_path = adapter_path
        self.temperature = temperature
        self.model = self._init_model(model_name, adapter_path, use_4bit)

    def _init_model(
        self,
        model_name: str,
        adapter_path: Optional[str] = None,
        use_4bit: bool = True,
    ):
        """Initialize the appropriate model client."""
        temperature = getattr(self, "temperature", 0.0)
        return init_model(
            model_name,
            temperature=temperature,
            adapter_path=adapter_path,
            use_4bit=use_4bit,
        )

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

        return EvalResult(task_id=task.id, model=self.model_name, response=response, scores=scores)

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

    def __init__(self, model_name: str = "claude-sonnet-4-20250514", temperature: float = 0.0):
        from anthropic import Anthropic

        self.client = Anthropic()
        self.model = model_name
        self.temperature = temperature

    def _reset_client(self):
        """Recreate HTTP client after connection errors."""
        from anthropic import Anthropic

        self.client = Anthropic()

    def _retry_call(self, fn, **kwargs):
        """Retry API call with exponential backoff (3 attempts)."""
        last_err = None
        for attempt in range(3):
            try:
                return fn(**kwargs)
            except (BrokenPipeError, ConnectionError, OSError) as exc:
                last_err = exc
                if attempt < 2:
                    _time.sleep(2**attempt)
                    self._reset_client()
        raise last_err  # type: ignore[misc]

    def generate(self, prompt: str, max_tokens: int = 2048, system: Optional[str] = None) -> str:
        """Generate response from Claude."""
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": self.temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system

        response = self._retry_call(self.client.messages.create, **kwargs)
        return response.content[0].text

    def generate_chat(self, messages: list, max_tokens: int = 2048, system: Optional[str] = None) -> str:
        """Generate response from Claude with multi-turn message history."""
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": self.temperature,
            "messages": messages,
        }
        if system:
            kwargs["system"] = system

        response = self._retry_call(self.client.messages.create, **kwargs)
        return response.content[0].text


class OpenAIModel:
    """Wrapper for OpenAI models."""

    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.0):
        from openai import OpenAI

        self.client = OpenAI()
        self.model = model_name
        self.temperature = temperature

    def _reset_client(self):
        """Recreate HTTP client after connection errors."""
        from openai import OpenAI

        self.client = OpenAI()

    def _retry_call(self, fn, **kwargs):
        """Retry API call with exponential backoff (3 attempts)."""
        last_err = None
        for attempt in range(3):
            try:
                return fn(**kwargs)
            except (BrokenPipeError, ConnectionError, OSError) as exc:
                last_err = exc
                if attempt < 2:
                    _time.sleep(2**attempt)
                    self._reset_client()
        raise last_err  # type: ignore[misc]

    def generate(self, prompt: str, max_tokens: int = 2048, system: Optional[str] = None) -> str:
        """Generate response from OpenAI model."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self._retry_call(
            self.client.chat.completions.create,
            model=self.model,
            max_tokens=max_tokens,
            temperature=self.temperature,
            messages=messages,
        )
        return response.choices[0].message.content

    def generate_chat(self, messages: list, max_tokens: int = 2048, system: Optional[str] = None) -> str:
        """Generate response from OpenAI model with multi-turn message history."""
        msgs = []
        if system:
            msgs.append({"role": "system", "content": system})
        msgs.extend(messages)

        response = self._retry_call(
            self.client.chat.completions.create,
            model=self.model,
            max_tokens=max_tokens,
            temperature=self.temperature,
            messages=msgs,
        )
        return response.choices[0].message.content


class OpenAICompatibleModel:
    """Wrapper for OpenAI-compatible API providers (DeepSeek, Groq, Gemini, Together, etc.)."""

    def __init__(
        self,
        model_name: str,
        base_url: str,
        api_key_env: str,
        temperature: float = 0.0,
    ):
        from openai import OpenAI

        api_key = os.environ.get(api_key_env)
        if not api_key:
            raise ValueError(f"{api_key_env} environment variable not set")
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model_name
        self.temperature = temperature
        self._base_url = base_url
        self._api_key_env = api_key_env

    def _reset_client(self):
        """Recreate HTTP client after connection errors."""
        from openai import OpenAI

        api_key = os.environ.get(self._api_key_env)
        self.client = OpenAI(base_url=self._base_url, api_key=api_key)

    def _retry_call(self, fn, **kwargs):
        """Retry API call with exponential backoff (3 attempts)."""
        last_err = None
        for attempt in range(3):
            try:
                return fn(**kwargs)
            except (BrokenPipeError, ConnectionError, OSError) as exc:
                last_err = exc
                if attempt < 2:
                    _time.sleep(2**attempt)
                    self._reset_client()
        raise last_err  # type: ignore[misc]

    def generate(self, prompt: str, max_tokens: int = 2048, system: Optional[str] = None) -> str:
        """Generate response from OpenAI-compatible API."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self._retry_call(
            self.client.chat.completions.create,
            model=self.model,
            max_tokens=max_tokens,
            temperature=self.temperature,
            messages=messages,
        )
        return response.choices[0].message.content

    def generate_chat(self, messages: list, max_tokens: int = 2048, system: Optional[str] = None) -> str:
        """Generate response from OpenAI-compatible API with multi-turn message history."""
        msgs = []
        if system:
            msgs.append({"role": "system", "content": system})
        msgs.extend(messages)

        response = self._retry_call(
            self.client.chat.completions.create,
            model=self.model,
            max_tokens=max_tokens,
            temperature=self.temperature,
            messages=msgs,
        )
        return response.choices[0].message.content


class HuggingFaceModel:
    """Wrapper for HuggingFace local models with LoRA support."""

    def __init__(
        self,
        model_name: str = "mistralai/Mistral-7B-v0.3",
        adapter_path: Optional[str] = None,
        use_4bit: bool = True,
        device: str = "auto",
    ):
        self.model_name = model_name
        self.adapter_path = adapter_path
        self._load_model(model_name, adapter_path, use_4bit, device)

    def _load_model(
        self,
        model_name: str,
        adapter_path: Optional[str],
        use_4bit: bool,
        device: str,
    ):
        """Load the model and tokenizer."""
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError:
            raise ImportError("Please install transformers and torch: " "pip install transformers torch accelerate")

        print(f"Loading HuggingFace model: {model_name}")

        # Check for GPU
        if torch.cuda.is_available():
            print(f"Using GPU: {torch.cuda.get_device_name(0)}")
            device_map = "auto" if device == "auto" else device
        else:
            print("No GPU detected, using CPU (will be slow)")
            device_map = "cpu"
            use_4bit = False

        # Load tokenizer (from adapter if available)
        tokenizer_path = adapter_path if adapter_path else model_name
        self.tokenizer = AutoTokenizer.from_pretrained(
            tokenizer_path,
            trust_remote_code=True,
        )
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Load model with optional 4-bit quantization
        if use_4bit:
            try:
                from transformers import BitsAndBytesConfig

                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                )
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    quantization_config=bnb_config,
                    device_map=device_map,
                    trust_remote_code=True,
                )
            except ImportError:
                print("bitsandbytes not available, loading without quantization")
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    device_map=device_map,
                    torch_dtype=torch.float16,
                    trust_remote_code=True,
                )
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map=device_map,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                trust_remote_code=True,
            )

        # Load LoRA adapters if specified
        if adapter_path:
            try:
                from peft import PeftModel

                print(f"Loading LoRA adapters from: {adapter_path}")
                self.model = PeftModel.from_pretrained(self.model, adapter_path)
            except ImportError:
                raise ImportError("Please install peft: pip install peft")

        self.model.eval()
        print("Model loaded successfully!")

    def generate(
        self,
        prompt: str,
        max_tokens: int = 2048,
        system: Optional[str] = None,
        temperature: float = 0.3,
    ) -> str:
        """Generate response from HuggingFace model."""
        import torch

        # Format prompt
        if system:
            formatted_prompt = f"### System:\n{system}\n\n### Instruction:\n{prompt}\n\n### Response:\n"
        else:
            formatted_prompt = f"### Instruction:\n{prompt}\n\n### Response:\n"

        # Tokenize
        inputs = self.tokenizer(formatted_prompt, return_tensors="pt")
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature if temperature > 0 else 0.1,
                top_p=0.9,
                do_sample=temperature > 0,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        # Decode response
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract just the response part
        if "### Response:" in response:
            response = response.split("### Response:")[-1].strip()

        return response
