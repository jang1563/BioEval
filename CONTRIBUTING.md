# Contributing to BioEval

Thank you for your interest in contributing to BioEval! This document provides guidelines and instructions for contributing.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- An Anthropic API key (for running evaluations)

### Development Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/BioEval.git
   cd BioEval
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

5. Set up your API key:
   ```bash
   export ANTHROPIC_API_KEY="your-key-here"
   ```

## Development Workflow

### Creating a Branch

Create a new branch for your work:
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### Making Changes

1. Write your code following the project's style guidelines
2. Add tests for any new functionality
3. Update documentation as needed
4. Run tests to ensure nothing is broken

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=bioeval

# Run specific test file
pytest tests/test_adversarial.py
```

### Code Style

This project uses:
- **Black** for code formatting
- **Ruff** for linting
- **MyPy** for type checking
- **pre-commit** for local quality gates

Run formatting and linting:
```bash
# Format code
black bioeval/ scripts/ tests/

# Check linting
ruff check bioeval/ scripts/ tests/

# Type checking
mypy bioeval/

# Optional but recommended
pre-commit install
pre-commit run --all-files
```

### Committing Changes

Write clear, descriptive commit messages:
```bash
git commit -m "Add new adversarial test type for temporal reasoning"
```

## Types of Contributions

### Adding Evaluation Tasks

Task data is embedded directly in Python data files rather than external JSON/YAML files.

1. **Protocol Tasks** (ProtoReason)
   - Add new tasks to `bioeval/protoreason/extended_data.py` or `advanced_data.py`
   - Follow the existing dictionary schema with `id`, `task_type`, `prompt`, and `answer` fields
   - Include step annotations and expected answers

2. **Causal Biology Tasks** (CausalBio)
   - Add tasks to `bioeval/causalbio/extended_data.py`
   - Include ground truth from experimental data with `source_type` and `source_id` provenance fields
   - Document the data source inline

3. **Adversarial Tasks**
   - Add new adversarial types to `bioeval/adversarial/tasks.py`
   - Include expected behavior and pass criteria
   - Add corresponding prompt enhancements if needed

4. **Experimental Design Flaws** (DesignCheck)
   - Add tasks to `bioeval/designcheck/extended_data.py`
   - Annotate all flaws with categories following the existing schema

### Adding Prompt Enhancements

1. Add your enhancement function to `bioeval/prompts/prompt_templates.py`
2. Follow the existing pattern:
   ```python
   def add_your_enhancement(prompt: str, config: Optional[PromptEnhancementConfig] = None) -> str:
       """
       Docstring explaining the enhancement.
       """
       return f"{YOUR_INSTRUCTIONS}\n\n{prompt}"
   ```
3. Add configuration option to `PromptEnhancementConfig`
4. Export in `bioeval/prompts/__init__.py`
5. Add tests

### Adding Model Support

1. Add a new model class in `bioeval/models/base.py`
2. Follow the existing interface:
   ```python
   class YourModel:
       def __init__(self, model_name: str):
           # Initialize client
           pass

       def generate(self, prompt: str, max_tokens: int = 2048, system: Optional[str] = None) -> str:
           # Generate response
           pass
   ```
3. Update `_init_model()` in `BaseEvaluator`

### Adding New Evaluation Components

To add a new top-level component (e.g., `bioeval/newcomponent/`):

1. **Create the module directory** with the following files:
   ```
   bioeval/newcomponent/
   ├── __init__.py       # Module docstring + public exports
   ├── evaluator.py      # NewComponentEvaluator class
   └── extended_data.py  # Task data as Python dicts
   ```

2. **Implement the evaluator** by subclassing `BaseEvaluator`:
   ```python
   from bioeval.models.base import BaseEvaluator, EvalTask, EvalResult

   class NewComponentEvaluator(BaseEvaluator):
       def load_tasks(self, tier: str = "base") -> list[EvalTask]:
           # Return list of EvalTask objects
           ...

       def evaluate_task(self, task: EvalTask, response: str) -> EvalResult:
           # Score the response and return EvalResult
           ...

       def run(self, model: str, **kwargs) -> dict:
           # Orchestrate task loading, generation, scoring, and reporting
           ...
   ```

3. **Register the component** in four places:
   - `bioeval/__init__.py`: import and add to `__all__`
   - `bioeval/cli.py`: add subcommand and wire to evaluator
   - `bioeval/simulation.py`: add `_simulate_newcomponent()` function
   - `docs/STATUS.md`: add to the canonical inventory

4. **Add tests** in `tests/test_newcomponent.py` following the pattern of existing test files.

5. **Run the consistency check** before submitting:
   ```bash
   python scripts/check_release_consistency.py
   ```

### Bug Fixes

1. Create an issue describing the bug
2. Reference the issue in your PR
3. Include a test that would have caught the bug

## Pull Request Process

1. Update the README.md if needed
2. Update CHANGELOG.md with your changes
3. Ensure all tests pass
4. Submit a pull request to the `main` branch

### PR Title Format

Use a descriptive title:
- `feat: Add new adversarial test type`
- `fix: Correct scoring logic in CausalBio`
- `docs: Update installation instructions`
- `test: Add tests for prompt enhancements`

### PR Description

Include:
- What the PR does
- Why it's needed
- How to test it
- Any breaking changes

## Priority Contribution Areas

We especially welcome contributions in these areas:

1. **Additional Protocol Tasks**
   - Protocols from diverse biological domains
   - Different complexity levels

2. **New Perturbation Datasets**
   - Gene knockout data
   - Drug response data
   - CRISPR screening results

3. **Error Annotation**
   - Categorizing model failures
   - Expanding the error taxonomy

4. **Model Integrations**
   - Support for additional LLM providers
   - Local model support

5. **Documentation**
   - Usage examples
   - Tutorial notebooks
   - API documentation

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Focus on constructive feedback
- Accept different viewpoints gracefully
- Prioritize the project's best interests

### Reporting Issues

If you encounter any issues with contributors or maintainers, please contact the project maintainers directly.

## Questions?

Feel free to:
- Open an issue for questions
- Start a discussion on GitHub
- Contact the maintainers

Thank you for contributing to BioEval!
