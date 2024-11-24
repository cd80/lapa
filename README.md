# LAPA: Language-Agnostic Program Analysis Framework

LAPA is a language-agnostic program analysis framework designed to provide comprehensive analysis tools for various programming languages. It utilizes an intermediate representation (IR) to perform static analysis, control flow analysis, data flow analysis, type inference, and dependency analysis.

## Features

- **Multi-language Support**: Parse and analyze code written in multiple programming languages.
- **Enhanced Intermediate Representation (IR)**: Convert source code into a language-neutral IR for unified analysis. The IR system now includes:
  - **Validation**: Ensure the integrity of the IR with the `validate` method, which checks for structural correctness and duplicate symbols.
  - **Building from AST**: Construct the IR directly from abstract syntax trees (AST) using the `build_from_ast` method.
  - **Optimization**: Optimize the IR for more efficient analysis with the `optimize` method.
  - **Improved IRNode Class**: Enhanced `IRNode` class with additional helper methods for better manipulation and traversal of the IR.
- **Control Flow Analysis**: Analyze the control flow of programs to identify structures like loops and conditionals.
- **Data Flow Analysis**: Track data through variables and expressions to identify dependencies and side effects.
- **Type Inference Analyzer**: Infer types of variables and expressions in code without explicit type annotations.
- **Dependency Analyzer**: Analyze dependencies between functions, variables, and modules to understand code relationships.
- **Plugin Architecture**: Extend the framework with custom analysis plugins.

## Installation

Instructions for installing LAPA.

## Usage

Instructions for using LAPA.

### Intermediate Representation (IR)

The IR system serves as the core of LAPA, providing a unified representation of programs across different languages. Recent enhancements include the implementation of key methods and improvements to the `IRNode` class.

#### Validation

Use the `validate` method to check the integrity of the IR structure.

```python
from lapa.ir import IR

ir = IR()
# After building or modifying the IR
is_valid = ir.validate()
if is_valid:
    print("IR is valid.")
else:
    print("IR validation failed.")
```

#### Building from AST

Construct the IR directly from an AST node using the `build_from_ast` method.

```python
from lapa.ir import IR

ir = IR()
# Assuming 'ast_node' is an AST node obtained from a parser
ir.build_from_ast(ast_node)
```

#### Optimization

Optimize the IR for more efficient analysis.

```python
from lapa.ir import IR

ir = IR()
# After building the IR
ir.optimize()
```

#### Improved IRNode Class

The `IRNode` class now includes additional helper methods for better manipulation and traversal.

- **get_symbols**: Retrieve all symbol names defined in the node and its children.
- **find_nodes_by_type**: Find all nodes of a specific type.
- **get_node_by_position**: Locate a node based on its source code position.

### Type Inference Analyzer

The `TypeInferenceAnalyzer` performs type inference on the IR, allowing you to:

- Infer the types of variables and expressions.
- Handle literals, variables, binary operations, function calls, and more.
- Assist in type checking and identifying potential type errors.

Usage example:

```python
from lapa.analysis.type_inference import TypeInferenceAnalyzer

analyzer = TypeInferenceAnalyzer()
analyzer.analyze(ir)
type_info = analyzer.type_information
```

### Dependency Analyzer

The `DependencyAnalyzer` analyzes dependencies within the IR, helping you:

- Build a dependency graph of functions, variables, and modules.
- Understand relationships and dependencies in the codebase.
- Assist in impact analysis and refactoring efforts.

Usage example:

```python
from lapa.analysis.dependency_analysis import DependencyAnalyzer

analyzer = DependencyAnalyzer()
analyzer.analyze(ir)
dependencies = analyzer.get_dependencies()
```

## Contributing

Instructions for contributing.

## License

License information.
