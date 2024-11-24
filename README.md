# LAPA: Language-Agnostic Program Analyzer

LAPA is a language-agnostic program analysis tool designed to parse and analyze source code written in multiple programming languages. It provides a unified intermediate representation (IR) and a suite of analysis modules to facilitate advanced code analysis and transformations.

## Features

- **Multi-language Support**:

  - ✅ Python
  - ✅ JavaScript/TypeScript
  - ✅ C/C++
  - ✅ Rust
  - ✅ Java

- **Unified Intermediate Representation**: Standardizes code representation across different languages for consistent analysis.

- **Program Analysis Modules**:

  - Control Flow Analysis
  - Data Flow Analysis
  - Type Inference
  - Dependency Analysis

- **Extensible Plugin System**: Easily add new analysis modules or extend existing ones.

## Latest Updates

- **Program Analysis Enhancements**:

  - Enhanced control flow analyzer to handle complex control structures, including loops and exception handling.
  - Improved data flow analyzer with live variable analysis and branching assignments.
  - Extended type inference analyzer to support collection types and user-defined classes.
  - All unit tests are now passing with a 100% success rate.
  - Test coverage is currently at **75%**, aiming for over 80% in the next milestone.

- **Documentation Updates**:
  - Updated `PROJECT_STATUS.md` and `ROADMAP.md` with the latest project progress.
  - Improved code documentation and comments for better clarity.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/lapa.git

# Navigate to the project directory
cd lapa

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Analyze a source code file
python -m lapa.analyzer your_source_file.py

# Run the test suite
pytest
```

## Contributing

Contributions are welcome! Please read the [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to the project.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Roadmap

For planned features and future enhancements, see the [ROADMAP.md](ROADMAP.md).

## Contact

For questions or feedback, please open an issue or contact the maintainers at [developer@example.com](mailto:developer@example.com).
