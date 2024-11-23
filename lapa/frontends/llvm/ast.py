"""
AST handling for LLVM/Clang integration.

This module provides utilities for converting LLVM/Clang AST nodes into
LAPA's intermediate representation (IR).
"""

from typing import Any, Dict, List, Optional, Union, cast
from pathlib import Path

from ...ir import IR, IRNode, IRNodeType, Position


class ASTConverter:
    """Converts LLVM/Clang AST nodes to LAPA IR nodes."""
    
    def __init__(self):
        """Initialize the AST converter."""
        self.ir = IR()
        self.current_namespace: List[str] = []
    
    def convert(self, ast: Any, filename: str = "<unknown>") -> IR:
        """
        Convert an LLVM/Clang AST to LAPA IR.
        
        Args:
            ast: The LLVM/Clang AST (TranslationUnit)
            filename: The source file name
        
        Returns:
            The converted IR
        """
        self.ir.clear()
        self.ir.root.position = Position(line=1, column=0, file=filename)
        self.current_namespace.clear()
        
        # Process all top-level declarations
        for node in ast.cursor.get_children():
            self._process_node(node, self.ir.root)
        
        return self.ir
    
    def _process_node(self, node: Any, parent_ir: IRNode) -> None:
        """Process an AST node and convert it to IR."""
        kind = node.kind.name
        
        if kind == "NAMESPACE":
            self._process_namespace(node, parent_ir)
        elif kind == "CLASS_DECL":
            self._process_class(node, parent_ir)
        elif kind == "FUNCTION_DECL":
            self._process_function(node, parent_ir)
        elif kind == "CXX_METHOD":
            self._process_method(node, parent_ir)
        elif kind == "CONSTRUCTOR":
            self._process_constructor(node, parent_ir)
        elif kind == "DESTRUCTOR":
            self._process_destructor(node, parent_ir)
        elif kind == "FIELD_DECL":
            self._process_field(node, parent_ir)
        elif kind == "VAR_DECL":
            self._process_variable(node, parent_ir)
        elif kind == "FUNCTION_TEMPLATE":
            self._process_template(node, parent_ir)
        elif kind == "CLASS_TEMPLATE":
            self._process_template(node, parent_ir)
        elif kind == "USING_DECLARATION":
            self._process_using(node, parent_ir)
        elif kind == "FRIEND_DECL":
            self._process_friend(node, parent_ir)
    
    def _process_namespace(self, node: Any, parent_ir: IRNode) -> None:
        """Process a namespace declaration."""
        name = node.spelling
        self.current_namespace.append(name)
        
        namespace_ir = IRNode(
            node_type=IRNodeType.NAMESPACE,
            position=self._create_position(node),
            attributes={"name": name}
        )
        parent_ir.add_child(namespace_ir)
        
        # Process namespace contents
        for child in node.get_children():
            self._process_node(child, namespace_ir)
        
        self.current_namespace.pop()
    
    def _process_class(self, node: Any, parent_ir: IRNode) -> None:
        """Process a class declaration."""
        name = node.spelling
        bases = []
        
        # Get base classes
        for child in node.get_children():
            if child.kind.name == "CXX_BASE_SPECIFIER":
                base_type = child.type.spelling
                bases.append(base_type)
        
        class_ir = IRNode(
            node_type=IRNodeType.CLASS,
            position=self._create_position(node),
            attributes={
                "name": name,
                "bases": bases,
                "is_struct": node.kind.name == "STRUCT_DECL",
                "namespace": "::".join(self.current_namespace)
            }
        )
        parent_ir.add_child(class_ir)
        
        # Process class members
        for child in node.get_children():
            if child.kind.name != "CXX_BASE_SPECIFIER":
                self._process_node(child, class_ir)
    
    def _process_function(self, node: Any, parent_ir: IRNode) -> None:
        """Process a function declaration."""
        name = node.spelling
        return_type = node.result_type.spelling
        is_inline = node.is_inline()
        is_const = node.is_const_method()
        
        # Get parameters
        params = []
        for param in node.get_arguments():
            params.append({
                "name": param.spelling,
                "type": param.type.spelling,
                "default_value": None  # TODO: Extract default value
            })
        
        func_ir = IRNode(
            node_type=IRNodeType.FUNCTION,
            position=self._create_position(node),
            attributes={
                "name": name,
                "return_type": return_type,
                "parameters": params,
                "is_inline": is_inline,
                "is_const": is_const,
                "namespace": "::".join(self.current_namespace)
            }
        )
        parent_ir.add_child(func_ir)
    
    def _process_method(self, node: Any, parent_ir: IRNode) -> None:
        """Process a class method."""
        # Methods are similar to functions but with additional attributes
        self._process_function(node, parent_ir)
        method_ir = parent_ir.children[-1]
        method_ir.attributes.update({
            "access": node.access_specifier.name.lower(),
            "is_virtual": node.is_virtual_method(),
            "is_pure_virtual": node.is_pure_virtual_method() if hasattr(node, 'is_pure_virtual_method') else False,
            "is_static": node.is_static_method()
        })
    
    def _process_constructor(self, node: Any, parent_ir: IRNode) -> None:
        """Process a constructor."""
        name = node.spelling
        
        # Get parameters
        params = []
        for param in node.get_arguments():
            params.append({
                "name": param.spelling,
                "type": param.type.spelling,
                "default_value": None
            })
        
        ctor_ir = IRNode(
            node_type=IRNodeType.CONSTRUCTOR,
            position=self._create_position(node),
            attributes={
                "name": name,
                "parameters": params,
                "access": node.access_specifier.name.lower(),
                "is_default": node.is_defaulted(),
                "is_deleted": node.is_deleted()
            }
        )
        parent_ir.add_child(ctor_ir)
    
    def _process_destructor(self, node: Any, parent_ir: IRNode) -> None:
        """Process a destructor."""
        name = node.spelling
        
        dtor_ir = IRNode(
            node_type=IRNodeType.DESTRUCTOR,
            position=self._create_position(node),
            attributes={
                "name": name,
                "access": node.access_specifier.name.lower(),
                "is_virtual": node.is_virtual_method(),
                "is_default": node.is_defaulted(),
                "is_deleted": node.is_deleted()
            }
        )
        parent_ir.add_child(dtor_ir)
    
    def _process_field(self, node: Any, parent_ir: IRNode) -> None:
        """Process a class field declaration."""
        name = node.spelling
        type_name = node.type.spelling
        
        field_ir = IRNode(
            node_type=IRNodeType.FIELD,
            position=self._create_position(node),
            attributes={
                "name": name,
                "type": type_name,
                "access": node.access_specifier.name.lower(),
                "is_mutable": node.is_mutable_field() if hasattr(node, 'is_mutable_field') else False
            }
        )
        parent_ir.add_child(field_ir)
    
    def _process_variable(self, node: Any, parent_ir: IRNode) -> None:
        """Process a variable declaration."""
        name = node.spelling
        type_name = node.type.spelling
        
        var_ir = IRNode(
            node_type=IRNodeType.VARIABLE,
            position=self._create_position(node),
            attributes={
                "name": name,
                "type": type_name,
                "is_static": node.is_static_local_variable() if hasattr(node, 'is_static_local_variable') else False,
                "namespace": "::".join(self.current_namespace)
            }
        )
        parent_ir.add_child(var_ir)
    
    def _process_template(self, node: Any, parent_ir: IRNode) -> None:
        """Process a template declaration."""
        name = node.spelling
        kind = node.kind.name
        
        # Get template parameters
        params = []
        for child in node.get_children():
            if child.kind.name == "TEMPLATE_TYPE_PARAMETER":
                params.append({
                    "name": child.spelling,
                    "kind": "type",
                    "default": None  # TODO: Extract default type
                })
            elif child.kind.name == "TEMPLATE_NON_TYPE_PARAMETER":
                params.append({
                    "name": child.spelling,
                    "kind": "non-type",
                    "type": child.type.spelling,
                    "default": None  # TODO: Extract default value
                })
        
        template_ir = IRNode(
            node_type=IRNodeType.TEMPLATE,
            position=self._create_position(node),
            attributes={
                "name": name,
                "kind": "class" if kind == "CLASS_TEMPLATE" else "function",
                "parameters": params,
                "namespace": "::".join(self.current_namespace)
            }
        )
        parent_ir.add_child(template_ir)
        
        # Process the templated entity
        for child in node.get_children():
            if child.kind.name not in ["TEMPLATE_TYPE_PARAMETER", "TEMPLATE_NON_TYPE_PARAMETER"]:
                self._process_node(child, template_ir)
    
    def _process_using(self, node: Any, parent_ir: IRNode) -> None:
        """Process a using declaration."""
        name = node.spelling
        
        using_ir = IRNode(
            node_type=IRNodeType.USING,
            position=self._create_position(node),
            attributes={
                "name": name,
                "target": node.referenced.spelling if node.referenced else None,
                "namespace": "::".join(self.current_namespace)
            }
        )
        parent_ir.add_child(using_ir)
    
    def _process_friend(self, node: Any, parent_ir: IRNode) -> None:
        """Process a friend declaration."""
        friend_ir = IRNode(
            node_type=IRNodeType.FRIEND,
            position=self._create_position(node),
            attributes={
                "target": node.referenced.spelling if node.referenced else None
            }
        )
        parent_ir.add_child(friend_ir)
    
    def _create_position(self, node: Any) -> Position:
        """Create a Position object from an AST node."""
        return Position(
            line=node.location.line,
            column=node.location.column,
            file=str(node.location.file) if node.location.file else "<unknown>"
        )
