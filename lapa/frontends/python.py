"""
Python frontend implementation using tree-sitter.
"""

from typing import Any, Union
from pathlib import Path

from ..frontend import (
    Frontend,
    LanguageFeature,
    ParsingError,
    FrontendRegistry
)
from ..ir import IR
from .grammars import create_parser


class PythonFrontend(Frontend):
    """Frontend for Python code analysis using tree-sitter."""

    def __init__(self):
        """Initialize Python frontend."""
        super().__init__()

        # Register supported features
        self.features = {
            LanguageFeature.FUNCTIONS,
            LanguageFeature.CLASSES,
            LanguageFeature.INHERITANCE,
            LanguageFeature.DECORATORS,
            LanguageFeature.ANNOTATIONS,
            LanguageFeature.GENERATORS,
            LanguageFeature.ASYNC_AWAIT,
            LanguageFeature.EXCEPTIONS,
            LanguageFeature.GARBAGE_COLLECTION,
            LanguageFeature.MODULES,
            LanguageFeature.PACKAGES,
            LanguageFeature.TYPE_INFERENCE,
            LanguageFeature.LAMBDA_FUNCTIONS,
            LanguageFeature.REFLECTION,
            LanguageFeature.COMPILE_TIME_EVALUATION
        }

        # Register supported file extensions
        self.file_extensions = {".py", ".pyi", ".pyx", ".pxd"}

        # Initialize parser
        self.parser = None
        self.language = None

    def supports_language(self, language: str) -> bool:
        """Check if frontend supports a language."""
        return language.lower() == "python"

    def _ensure_parser(self) -> None:
        """Ensure parser is initialized."""
        if self.parser is None:
            try:
                self.parser = create_parser("python")
            except Exception as e:
                raise RuntimeError(f"Failed to initialize parser: {str(e)}")

    def parse_file(self, path: Union[str, Path], ir: IR) -> None:
        """
        Parse a Python source file and update the IR.

        Args:
            path: Path to source file
            ir: IR to update

        Raises:
            FileNotFoundError: If file doesn't exist
            ParsingError: If parsing fails
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                source = f.read()
            self.parse_string(source, ir)
        except Exception as e:
            raise ParsingError(f"Failed to parse {path}: {str(e)}")

    def parse_string(self, source: str, ir: IR) -> None:
        """
        Parse Python source code string and update the IR.

        Args:
            source: Source code string
            ir: IR to update

        Raises:
            ParsingError: If parsing fails
        """
        try:
            self._ensure_parser()
            tree = self.parser.parse(bytes(source, "utf8"))
            if tree.root_node.has_error:
                raise ParsingError("Syntax error in source code")
            self._process_ast(tree.root_node, ir)
        except Exception as e:
            raise ParsingError(f"Failed to parse source: {str(e)}")

    def _process_ast(self, node: Any, ir: IR) -> None:
        """
        Process Python AST and update IR.

        Args:
            node: AST node
            ir: IR to update
        """
        # Process imports
        if node.type == "import_statement":
            self._process_import(node, ir)
        elif node.type == "import_from_statement":
            self._process_import_from(node, ir)

        # Process declarations
        elif node.type == "function_definition":
            self._process_function(node, ir)
        elif node.type == "class_definition":
            self._process_class(node, ir)

        # Process children nodes
        for child in node.children:
            self._process_ast(child, ir)

    def _process_import(self, node: Any, ir: IR) -> None:
        """Process import statement."""
        # TODO: Implement import processing
        pass

    def _process_import_from(self, node: Any, ir: IR) -> None:
        """Process 'from ... import ...' statement."""
        # TODO: Implement 'import from' processing
        pass

    def _process_function(self, node: Any, ir: IR) -> None:
        """Process function definition."""
        # TODO: Implement function processing
        pass

    def _process_class(self, node: Any, ir: IR) -> None:
        """Process class definition."""
        # TODO: Implement class processing
        pass


# Register frontend
FrontendRegistry.register("python", PythonFrontend)
