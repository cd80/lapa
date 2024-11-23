"""
JavaScript/TypeScript language frontend for LAPA framework.

This module provides the implementation of a JavaScript/TypeScript language
frontend that parses JavaScript and TypeScript code into the framework's IR.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast

from ..frontend import LanguageFeatures, LanguageFrontend, ParsingError
from ..ir import IR, IRNode, IRNodeType, Position
from .grammars import create_parser


class JavaScriptFrontend(LanguageFrontend):
    """Frontend implementation for JavaScript and TypeScript."""

    def __init__(self):
        """Initialize the JavaScript frontend."""
        super().__init__()
        try:
            self.parser = create_parser('javascript')
        except RuntimeError as e:
            # We'll initialize without a parser and raise errors when parsing is attempted
            self.parser = None

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
        if self.parser is None:
            raise NotImplementedError(
                "JavaScript/TypeScript parsing not yet implemented"
            )
        
        try:
            tree = self.parser.parse(bytes(content, "utf8"))
            if tree is None:
                raise ParsingError("Parser returned None")
            
            self.ir.clear()  # Reset IR before parsing
            self._process_tree(tree, filename)
            return self.ir
        except Exception as e:
            if isinstance(e, NotImplementedError):
                raise
            raise ParsingError(f"Failed to parse JavaScript/TypeScript code: {str(e)}")

    def get_file_extensions(self) -> List[str]:
        """Get supported JavaScript and TypeScript file extensions."""
        return [".js", ".jsx", ".ts", ".tsx"]

    def _process_tree(self, tree: Any, filename: str) -> None:
        """Process tree-sitter AST and convert it to IR."""
        self.ir.root.position = Position(line=1, column=0, file=filename)
        self._process_node(tree.root_node, self.ir.root)

    def _process_node(self, node: Any, parent_ir: IRNode) -> None:
        """Process a tree-sitter node and its children."""
        if node.type == "program":
            self._process_children(node, parent_ir)
        elif node.type == "function_declaration":
            self._process_function(node, parent_ir)
        elif node.type == "class_declaration":
            self._process_class(node, parent_ir)
        elif node.type == "variable_declaration":
            self._process_variable(node, parent_ir)
        elif node.type == "import_declaration":
            self._process_import(node, parent_ir)
        elif node.type == "export_statement":
            self._process_export(node, parent_ir)
        else:
            # Process children for unknown node types
            self._process_children(node, parent_ir)

    def _process_children(self, node: Any, parent_ir: IRNode) -> None:
        """Process all children of a node."""
        for child in node.children:
            self._process_node(child, parent_ir)

    def _process_function(self, node: Any, parent_ir: IRNode) -> None:
        """Process a function declaration."""
        name = ""
        for child in node.children:
            if child.type == "identifier":
                name = child.text.decode("utf8")
                break
        
        attributes = {
            "name": name or "<anonymous>",
            "is_async": any(child.type == "async" for child in node.children),
            "is_generator": any(child.type == "*" for child in node.children),
        }
        
        func_ir = IRNode(
            node_type=IRNodeType.FUNCTION,
            position=self._create_position(node),
            attributes=attributes
        )
        parent_ir.add_child(func_ir)
        
        # Process function body
        for child in node.children:
            if child.type == "statement_block":
                self._process_children(child, func_ir)

    def _process_class(self, node: Any, parent_ir: IRNode) -> None:
        """Process a class declaration."""
        name = ""
        extends = None
        for child in node.children:
            if child.type == "identifier":
                name = child.text.decode("utf8")
            elif child.type == "extends_clause":
                extends = child.text.decode("utf8")
        
        attributes = {
            "name": name or "<anonymous>",
            "extends": extends,
            "decorators": [],  # TODO: Process decorators
        }
        
        class_ir = IRNode(
            node_type=IRNodeType.CLASS,
            position=self._create_position(node),
            attributes=attributes
        )
        parent_ir.add_child(class_ir)
        
        # Process class body
        for child in node.children:
            if child.type == "class_body":
                self._process_children(child, class_ir)

    def _process_variable(self, node: Any, parent_ir: IRNode) -> None:
        """Process a variable declaration."""
        kind = None
        for child in node.children:
            if child.type in ["const", "let", "var"]:
                kind = child.text.decode("utf8")
                break
        
        for child in node.children:
            if child.type == "variable_declarator":
                name = None
                value = None
                for subchild in child.children:
                    if subchild.type == "identifier":
                        name = subchild.text.decode("utf8")
                    elif subchild.type in ["string", "number", "true", "false", "null"]:
                        value = subchild.text.decode("utf8")
                
                if name:
                    attributes = {
                        "name": name,
                        "kind": kind,
                        "value": value
                    }
                    
                    var_ir = IRNode(
                        node_type=IRNodeType.VARIABLE,
                        position=self._create_position(child),
                        attributes=attributes
                    )
                    parent_ir.add_child(var_ir)

    def _process_import(self, node: Any, parent_ir: IRNode) -> None:
        """Process an import declaration."""
        source = None
        specifiers = []
        
        for child in node.children:
            if child.type == "string":
                source = child.text.decode("utf8").strip('"\'')
            elif child.type == "import_specifier":
                imported = None
                local = None
                for subchild in child.children:
                    if subchild.type == "identifier":
                        if not imported:
                            imported = subchild.text.decode("utf8")
                        else:
                            local = subchild.text.decode("utf8")
                specifiers.append({
                    "imported": imported,
                    "local": local or imported
                })
        
        if source:
            attributes = {
                "source": source,
                "specifiers": specifiers
            }
            
            import_ir = IRNode(
                node_type=IRNodeType.IMPORT,
                position=self._create_position(node),
                attributes=attributes
            )
            parent_ir.add_child(import_ir)

    def _process_export(self, node: Any, parent_ir: IRNode) -> None:
        """Process an export statement."""
        # TODO: Implement export processing
        pass

    def _create_position(self, node: Any) -> Position:
        """Create Position object from tree-sitter node."""
        return Position(
            line=node.start_point[0] + 1,  # tree-sitter uses 0-based lines
            column=node.start_point[1],
            file=self.ir.root.position.file if self.ir.root.position else "<unknown>"
        )
