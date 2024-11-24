"""
Swift Frontend for LAPA.

This module provides the frontend implementation for the Swift programming language.
"""

from typing import Any, Union
from pathlib import Path
import os  # Needed for file operations

from ..frontend import (
    Frontend,
    LanguageFeature,
    ParsingError,
    FrontendRegistry
)
from ..ir import IR
from .grammars import create_parser


class SwiftFrontend(Frontend):
    """Frontend for Swift code analysis using tree-sitter."""

    def __init__(self):
        """Initialize Swift frontend."""
        super().__init__()

        self.language_name = "Swift"  # Added language_name attribute

        # Register supported features
        self.features = {
            LanguageFeature.FUNCTIONS,
            LanguageFeature.CLASSES,
            LanguageFeature.INHERITANCE,
            LanguageFeature.GENERICS,
            LanguageFeature.ASYNC_AWAIT,
            LanguageFeature.PROTOCOLS,
            LanguageFeature.EXTENSIONS,
            LanguageFeature.ENUMS,
            LanguageFeature.STRUCTS,
        }

        # Register supported file extensions
        self.file_extensions = {".swift"}

        # Initialize parser
        self.parser = None
        self.language = None

    def supports_language(self, language: str) -> bool:
        """Check if frontend supports a language."""
        return language.lower() == "swift"

    def _ensure_parser(self) -> None:
        """Ensure parser is initialized."""
        if self.parser is None:
            try:
                self.parser = create_parser("swift")
            except Exception as e:
                raise RuntimeError(f"Failed to initialize parser: {str(e)}")

    def parse(self, code: Union[str, Path], ir: IR) -> None:
        """
        Parse Swift code from a string or file and update the IR.

        Args:
            code: The Swift source code as a string or path to a file.
            ir: The intermediate representation to update.

        Raises:
            ParsingError: If parsing fails.
        """
        if isinstance(code, (str, bytes)):
            self.parse_string(code, ir)
        else:
            self.parse_file(code, ir)

    def parse_file(self, path: Union[str, Path], ir: IR) -> None:
        """
        Parse a Swift source file and update the IR.

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
        Parse Swift source code string and update the IR.

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
            self.ast_to_ir(tree, ir)
        except Exception as e:
            raise ParsingError(f"Failed to parse source: {str(e)}")

    def ast_to_ir(self, ast: Any, ir: IR) -> None:
        """
        Convert a Swift AST to the intermediate representation (IR).

        Args:
            ast: The abstract syntax tree to convert.
            ir: IR to update

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        # TODO: Implement AST to IR conversion for Swift
        raise NotImplementedError("Swift AST to IR conversion is not yet implemented.")

    def _process_ast(self, node: Any, ir: IR) -> None:
        """
        Process Swift AST and update IR.

        Args:
            node: AST node
            ir: IR to update
        """
        # TODO: Implement AST processing for Swift
        pass


# Register frontend
FrontendRegistry.register("swift", SwiftFrontend)
