# LAPA (LLM Assisted Program Analysis)

A feature-rich, powerful, efficient, and fast program analysis framework based on Python, utilizing Large Language Models (LLMs) for enhanced code analysis and understanding.

## Overview

LAPA is a comprehensive program analysis framework designed to support multiple programming languages through an Intermediate Representation (IR) system. It combines traditional static and dynamic analysis techniques with modern LLM capabilities to provide deep insights into codebases.

## Key Features

- Multi-language support through Intermediate Representation (IR)
- Integration with Large Language Models (LLMs)
- Comprehensive static and dynamic analysis capabilities
- Machine learning-based code smell detection
- Advanced visualization and reporting
- Modular plugin system
- DevOps and CI/CD pipeline integration

## Supported Languages

- ✅ Python (Complete)
- 🔄 JavaScript/TypeScript (In Progress)
- 📅 Java (Planned)
- 📅 C/C++ (Planned)
- 📅 Rust (Planned)
- 📅 Swift (Planned)
- 📅 Kotlin (Planned)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- virtualenv (recommended)

### Basic Installation

```bash
# Create and activate virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install from requirements
pip install -r requirements.txt
```

### Development Installation

```bash
# Install development dependencies
pip install -r requirements.txt

# Install in editable mode
pip install -e .
```

### Language-Specific Requirements

#### Python Support

- No additional requirements (built-in ast module used)

#### JavaScript/TypeScript Support

- Requires tree-sitter and language grammars:

```bash
pip install tree-sitter tree-sitter-javascript
```

## Quick Start

```python
from lapa import Analyzer

# Initialize analyzer
analyzer = Analyzer()

# Analyze Python code
results = analyzer.analyze("path/to/code.py")

# Access analysis results
for issue in results.issues:
    print(f"{issue.severity}: {issue.message} at {issue.location}")
```

## Core Analysis Techniques

### Static Analysis

- Control Flow Analysis
- Data Flow Analysis
- Pointer Analysis
- Type Inference
- Abstract Interpretation
- Program Slicing
- Dependency Analysis

### Dynamic Analysis

- Profiling
- Runtime Monitoring
- Memory Analysis
- Race Condition Detection

### AI/ML Features

- LLM-powered code understanding
- Code smell detection
- Automated optimization suggestions
- Context-aware analysis

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=lapa

# Run specific test file
pytest tests/test_specific.py
```

### Code Style

The project uses:

- Black for code formatting
- isort for import sorting
- mypy for type checking
- pylint for linting

```bash
# Format code
black .
isort .

# Type check
mypy .

# Lint
pylint lapa tests
```

## Documentation

Detailed documentation is under development. To build the docs:

```bash
cd docs
make html
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## Project Status

See [PROJECT_STATUS.md](PROJECT_STATUS.md) for current development status and [ROADMAP.md](ROADMAP.md) for planned features and milestones.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Kim, Sungwoo
