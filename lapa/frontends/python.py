"""
Python language frontend for LAPA framework.

This module provides the implementation of a Python language frontend
that parses Python source code into the framework's IR using Python's
built-in ast module.
"""

import ast
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast

from ..frontend import LanguageFeatures, LanguageFrontend, ParsingError
from ..ir import IR, IRNode, IRNodeType, Position


class PythonFrontend(LanguageFrontend):
    """Frontend implementation for the Python programming language."""

    def _get_language_features(self) -> LanguageFeatures:
        """Get Python language features."""
        features = LanguageFeatures()
        features.has_classes = True
        features.has_interfaces = False  # Python uses abstract base classes instead
        features.has_generics = True    # Via type hints
        features.has_exceptions = True
        features.has_async = True
        features.has_decorators = True
        features.has_operator_overloading = True
        features.has_multiple_inheritance = True
        features.typing_system = "dynamic"
        features.memory_management = "gc"
        return features

    def parse_file(self, path: Union[str, Path]) -> IR:
        """Parse a Python source file into IR."""
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
        """Parse Python source code from a string into IR."""
        try:
            tree = ast.parse(content, filename)
            self.ir.clear()  # Reset IR before parsing
            self._process_ast(tree, filename)
            return self.ir
        except SyntaxError as e:
            position = Position(
                line=e.lineno or 0,
                column=e.offset or 0,
                file=filename
            )
            raise ParsingError(str(e), position)
        except Exception as e:
            raise ParsingError(f"Failed to parse Python code: {str(e)}")

    def get_file_extensions(self) -> List[str]:
        """Get supported Python file extensions."""
        return [".py", ".pyw"]

    def _process_ast(self, node: ast.AST, filename: str) -> None:
        """Process Python AST and convert it to IR."""
        visitor = PythonASTVisitor(self.ir, filename)
        visitor.visit(node)


class PythonASTVisitor(ast.NodeVisitor):
    """AST visitor that converts Python AST to LAPA IR."""

    def __init__(self, ir: IR, filename: str):
        self.ir = ir
        self.filename = filename
        self.current_node = ir.root

    def _create_position(self, node: ast.AST) -> Position:
        """Create Position object from AST node."""
        return Position(
            line=getattr(node, 'lineno', 0),
            column=getattr(node, 'col_offset', 0),
            file=self.filename
        )

    def _create_ir_node(
        self,
        node: ast.AST,
        node_type: IRNodeType,
        attributes: Optional[Dict[str, Any]] = None
    ) -> IRNode:
        """Create an IR node from an AST node."""
        ir_node = IRNode(
            node_type=node_type,
            position=self._create_position(node),
            attributes=attributes or {}
        )
        self.current_node.add_child(ir_node)
        return ir_node

    def visit_Module(self, node: ast.Module) -> None:
        """Process module node."""
        # Module node is already represented by IR root
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Process function definition."""
        attributes = {
            'name': node.name,
            'is_async': False,
            'decorators': [ast.unparse(d) for d in node.decorator_list],
            'returns': ast.unparse(node.returns) if node.returns else None
        }
        
        prev_node = self.current_node
        self.current_node = self._create_ir_node(node, IRNodeType.FUNCTION, attributes)
        self.generic_visit(node)
        self.current_node = prev_node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Process async function definition."""
        attributes = {
            'name': node.name,
            'is_async': True,
            'decorators': [ast.unparse(d) for d in node.decorator_list],
            'returns': ast.unparse(node.returns) if node.returns else None
        }
        
        prev_node = self.current_node
        self.current_node = self._create_ir_node(node, IRNodeType.FUNCTION, attributes)
        self.generic_visit(node)
        self.current_node = prev_node

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Process class definition."""
        attributes = {
            'name': node.name,
            'bases': [ast.unparse(b) for b in node.bases],
            'decorators': [ast.unparse(d) for d in node.decorator_list],
            'keywords': {k.arg: ast.unparse(k.value) for k in node.keywords}
        }
        
        prev_node = self.current_node
        self.current_node = self._create_ir_node(node, IRNodeType.CLASS, attributes)
        self.generic_visit(node)
        self.current_node = prev_node

    def visit_Import(self, node: ast.Import) -> None:
        """Process import statement."""
        for name in node.names:
            attributes = {
                'name': name.name,
                'asname': name.asname
            }
            self._create_ir_node(node, IRNodeType.IMPORT, attributes)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Process from-import statement."""
        for name in node.names:
            attributes = {
                'module': node.module,
                'name': name.name,
                'asname': name.asname,
                'level': node.level
            }
            self._create_ir_node(node, IRNodeType.IMPORT, attributes)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Process assignment."""
        attributes = {
            'targets': [ast.unparse(t) for t in node.targets],
            'value': ast.unparse(node.value)
        }
        self._create_ir_node(node, IRNodeType.ASSIGNMENT, attributes)

    def visit_Call(self, node: ast.Call) -> None:
        """Process function/method call."""
        attributes = {
            'func': ast.unparse(node.func),
            'args': [ast.unparse(arg) for arg in node.args],
            'keywords': {k.arg: ast.unparse(k.value) for k in node.keywords}
        }
        self._create_ir_node(node, IRNodeType.CALL, attributes)

    def visit_Return(self, node: ast.Return) -> None:
        """Process return statement."""
        attributes = {
            'value': ast.unparse(node.value) if node.value else None
        }
        self._create_ir_node(node, IRNodeType.RETURN, attributes)

    def visit_If(self, node: ast.If) -> None:
        """Process if statement."""
        attributes = {
            'test': ast.unparse(node.test)
        }
        prev_node = self.current_node
        self.current_node = self._create_ir_node(node, IRNodeType.CONTROL_FLOW, attributes)
        self.generic_visit(node)
        self.current_node = prev_node

    def visit_For(self, node: ast.For) -> None:
        """Process for loop."""
        attributes = {
            'target': ast.unparse(node.target),
            'iter': ast.unparse(node.iter),
            'is_async': False
        }
        prev_node = self.current_node
        self.current_node = self._create_ir_node(node, IRNodeType.LOOP, attributes)
        self.generic_visit(node)
        self.current_node = prev_node

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        """Process async for loop."""
        attributes = {
            'target': ast.unparse(node.target),
            'iter': ast.unparse(node.iter),
            'is_async': True
        }
        prev_node = self.current_node
        self.current_node = self._create_ir_node(node, IRNodeType.LOOP, attributes)
        self.generic_visit(node)
        self.current_node = prev_node

    def visit_While(self, node: ast.While) -> None:
        """Process while loop."""
        attributes = {
            'test': ast.unparse(node.test)
        }
        prev_node = self.current_node
        self.current_node = self._create_ir_node(node, IRNodeType.LOOP, attributes)
        self.generic_visit(node)
        self.current_node = prev_node
