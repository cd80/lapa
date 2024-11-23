"""
JavaScript/TypeScript language frontend for LAPA framework.

This module provides the implementation of a JavaScript/TypeScript language
frontend that parses JavaScript and TypeScript code into the framework's IR.
Note: This implementation requires the 'tree-sitter' and 'tree-sitter-javascript'
packages for parsing.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast

from ..frontend import LanguageFeatures, LanguageFrontend, ParsingError
from ..ir import IR, IRNode, IRNodeType, Position

try:
    from tree_sitter import Language, Parser, Tree, Node
except ImportError:
    raise ImportError(
        "tree-sitter is required for JavaScript/TypeScript support. "
        "Please install it with: pip install tree-sitter"
    )


class JavaScriptFrontend(LanguageFrontend):
    """Frontend implementation for JavaScript and TypeScript."""

    def __init__(self):
        """Initialize the JavaScript frontend."""
        super().__init__()
        self.parser = self._setup_parser()

    def _setup_parser(self) -> Parser:
        """Set up the tree-sitter parser for JavaScript."""
        try:
            parser = Parser()
            # TODO: Build and load JavaScript grammar
            # This will be implemented when tree-sitter integration is complete
            return parser
        except Exception as e:
            raise RuntimeError(f"Failed to initialize JavaScript parser: {e}")

    def _get_language_features(self) -> LanguageFeatures:
        """Get JavaScript language features."""
        features = LanguageFeatures()
        features.has_classes = True
        features.has_interfaces = True  # Via TypeScript
        features.has_generics = True    # Via TypeScript
        features.has_exceptions = True
        features.has_async = True
        features.has_decorators = True  # Via TypeScript
        features.has_operator_overloading = False
        features.has_multiple_inheritance = False
        features.typing_system = "gradual"  # Due to TypeScript
        features.memory_management = "gc"
        return features

    def parse_file(self, path: Union[str, Path]) -> IR:
        """Parse a JavaScript/TypeScript file into IR."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.parse_string(content, str(path))
        except Exception as e:
            raise ParsingError(f"Failed to parse {path}: {str(e)}")

    def parse_string(self, content: str, filename: str = "<string>") -> IR:
        """Parse JavaScript/TypeScript code from a string into IR."""
        # We let NotImplementedError propagate directly for the test
        raise NotImplementedError(
            "JavaScript/TypeScript parsing not yet implemented"
        )

    def get_file_extensions(self) -> List[str]:
        """Get supported JavaScript and TypeScript file extensions."""
        return [".js", ".jsx", ".ts", ".tsx"]

    def _process_tree(self, tree: Tree, filename: str) -> None:
        """Process tree-sitter AST and convert it to IR."""
        # TODO: Implement tree-sitter AST to IR conversion
        raise NotImplementedError(
            "JavaScript/TypeScript AST processing not yet implemented"
        )

    def _create_position(self, node: Node) -> Position:
        """Create Position object from tree-sitter node."""
        start_point = node.start_point
        return Position(
            line=start_point[0] + 1,  # tree-sitter uses 0-based lines
            column=start_point[1],
            file=self.ir.root.position.file if self.ir.root.position else "<unknown>"
        )

    def _create_ir_node(
        self,
        node: Node,
        node_type: IRNodeType,
        attributes: Optional[Dict[str, Any]] = None
    ) -> IRNode:
        """Create an IR node from a tree-sitter node."""
        ir_node = IRNode(
            node_type=node_type,
            position=self._create_position(node),
            attributes=attributes or {}
        )
        return ir_node
