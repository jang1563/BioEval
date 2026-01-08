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
- **Flake8** for linting
- **MyPy** for type checking

Run formatting and linting:
```bash
# Format code
black bioeval/ scripts/ tests/

# Check linting
flake8 bioeval/ scripts/ tests/

# Type checking
mypy bioeval/
```

### Committing Changes

Write clear, descriptive commit messages:
```bash
git commit -m "Add new adversarial test type for temporal reasoning"
```

## Types of Contributions

### Adding Evaluation Tasks

1. **Protocol Tasks** (ProtoReason)
   - Add new protocols to `bioeval/protoreason/data/`
   - Follow the existing JSON schema
   - Include step annotations and expected answers

2. **Causal Biology Tasks** (CausalBio)
   - Add tasks to `bioeval/causalbio/data/`
   - Include ground truth from experimental data
   - Document the data source

3. **Adversarial Tasks**
   - Add new adversarial types to `bioeval/adversarial/tasks.py`
   - Include expected behavior and pass criteria
   - Add corresponding prompt enhancements if needed

4. **Experimental Design Flaws** (DesignCheck)
   - Add designs to `bioeval/designcheck/data/`
   - Annotate all flaws with categories

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
