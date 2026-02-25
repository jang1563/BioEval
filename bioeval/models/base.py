"""
Base evaluator interface and model wrappers for BioEval.

Supports:
- Anthropic Claude models (API)
- OpenAI models (API)
- HuggingFace models (local, including LoRA fine-tuned)
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

    def __init__(
        self,
        model_name: str = "claude-sonnet-4-20250514",
        adapter_path: Optional[str] = None,
        use_4bit: bool = True,
    ):
        self.model_name = model_name
        self.adapter_path = adapter_path
        self.model = self._init_model(model_name, adapter_path, use_4bit)

    def _init_model(
        self,
        model_name: str,
        adapter_path: Optional[str] = None,
        use_4bit: bool = True,
    ):
        """Initialize the appropriate model client."""
        if "claude" in model_name.lower():
            return ClaudeModel(model_name)
        elif "gpt" in model_name.lower():
            return OpenAIModel(model_name)
        elif "/" in model_name or adapter_path:
            # HuggingFace model (local)
            return HuggingFaceModel(model_name, adapter_path=adapter_path, use_4bit=use_4bit)
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
            raise ImportError(
                "Please install transformers and torch: "
                "pip install transformers torch accelerate"
            )

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
