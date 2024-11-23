"""
JavaScript/TypeScript frontend implementation.
"""

from typing import Any, Dict, List, Optional, Set, Union
from pathlib import Path

from ..frontend import Frontend, LanguageFeature, ParsingError, FrontendRegistry
from ..ir import IR
from .grammars import get_language, create_parser


class JavaScriptFrontend(Frontend):
    """Frontend for JavaScript/TypeScript code analysis."""
    
    def __init__(self):
        """Initialize JavaScript frontend."""
        super().__init__()
        
        # Register supported features
        self.features = {
            LanguageFeature.FUNCTIONS,
            LanguageFeature.CLASSES,
            LanguageFeature.INHERITANCE,
            LanguageFeature.INTERFACES,
            LanguageFeature.GENERICS,
            LanguageFeature.MODULES,
            LanguageFeature.PACKAGES,
            LanguageFeature.ASYNC_AWAIT,
            LanguageFeature.GENERATORS,
            LanguageFeature.EXCEPTIONS,
            LanguageFeature.GARBAGE_COLLECTION,
            LanguageFeature.TYPE_INFERENCE,
            LanguageFeature.LAMBDA_FUNCTIONS,
            LanguageFeature.DECORATORS,
            LanguageFeature.REFLECTION
        }
        
        # Register supported file extensions
        self.file_extensions = {
            ".js", ".jsx",  # JavaScript
            ".ts", ".tsx",  # TypeScript
            ".mjs", ".cjs"  # ES modules
        }
        
        # Initialize parser
        self.parser = None
        self.language = None
    
    def supports_language(self, language: str) -> bool:
        """Check if frontend supports a language."""
        return language.lower() == "javascript"
    
    def build_ast(self, path: Union[str, Path]) -> None:
        """Build AST from source file (for testing)."""
        raise NotImplementedError("AST building not implemented")
    
    def _ensure_parser(self) -> None:
        """Ensure parser is initialized."""
        if self.parser is None:
            try:
                self.parser = create_parser("javascript")
            except Exception as e:
                raise RuntimeError(f"Failed to initialize parser: {str(e)}")
    
    def parse_file(self, path: Union[str, Path], ir: IR) -> None:
        """
        Parse a JavaScript/TypeScript source file and update the IR.
        
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
        Parse JavaScript/TypeScript source code string and update the IR.
        
        Args:
            source: Source code string
            ir: IR to update
        
        Raises:
            NotImplementedError: If parsing is not implemented
            ParsingError: If parsing fails
        """
        try:
            self._ensure_parser()
            tree = self.parser.parse(bytes(source, "utf8"))
            if tree.root_node.has_error:
                raise ParsingError("Syntax error in source code")
            self._process_ast(tree.root_node, ir)
        except Exception as e:
            if isinstance(e, NotImplementedError):
                raise
            raise ParsingError(f"Failed to parse source: {str(e)}")
    
    def _process_ast(self, node: Any, ir: IR) -> None:
        """
        Process JavaScript/TypeScript AST and update IR.
        
        Args:
            node: AST node
            ir: IR to update
        """
        # Process imports
        if node.type == "import_statement":
            self._process_import(node, ir)
        elif node.type == "export_statement":
            self._process_export(node, ir)
        
        # Process declarations
        elif node.type == "function_declaration":
            self._process_function(node, ir)
        elif node.type == "class_declaration":
            self._process_class(node, ir)
        elif node.type == "variable_declaration":
            self._process_variable(node, ir)
        
        # Process children
        for child in node.children:
            self._process_ast(child, ir)
    
    def _process_import(self, node: Any, ir: IR) -> None:
        """Process import statement."""
        raise NotImplementedError("Import processing not implemented")
    
    def _process_export(self, node: Any, ir: IR) -> None:
        """Process export statement."""
        raise NotImplementedError("Export processing not implemented")
    
    def _process_function(self, node: Any, ir: IR) -> None:
        """Process function declaration."""
        raise NotImplementedError("Function processing not implemented")
    
    def _process_class(self, node: Any, ir: IR) -> None:
        """Process class declaration."""
        raise NotImplementedError("Class processing not implemented")
    
    def _process_variable(self, node: Any, ir: IR) -> None:
        """Process variable declaration."""
        raise NotImplementedError("Variable processing not implemented")


# Register frontend
FrontendRegistry.register("javascript", JavaScriptFrontend)
