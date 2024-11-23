"""
Intermediate Representation (IR) for LAPA framework.

This module defines the core IR classes and utilities used throughout
the framework for representing and manipulating program structures.
"""

from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Union
from dataclasses import dataclass


class IRNodeType(Enum):
    """Types of IR nodes."""
    PROGRAM = auto()
    FUNCTION = auto()
    CLASS = auto()
    METHOD = auto()
    VARIABLE = auto()
    FIELD = auto()
    NAMESPACE = auto()
    CONSTRUCTOR = auto()
    DESTRUCTOR = auto()
    TEMPLATE = auto()
    USING = auto()
    FRIEND = auto()
    IMPORT = auto()
    EXPORT = auto()
    MODULE = auto()
    PACKAGE = auto()
    RETURN = auto()
    ASSIGNMENT = auto()
    CONTROL_FLOW = auto()
    LOOP = auto()
    CALL = auto()
    OPERATOR = auto()  # Added for operator overloading


@dataclass
class Position:
    """Source code position information."""
    line: int
    column: int
    file: str


class IRNode:
    """Node in the intermediate representation."""
    
    def __init__(
        self,
        node_type: IRNodeType,
        position: Optional[Position] = None,
        attributes: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize an IR node.
        
        Args:
            node_type: Type of the node
            position: Source code position
            attributes: Additional node attributes
        """
        self.node_type = node_type
        self.position = position
        self.attributes = attributes or {}
        self.children: List[IRNode] = []
        self.parent: Optional[IRNode] = None
    
    def add_child(self, child: 'IRNode') -> None:
        """Add a child node."""
        self.children.append(child)
        child.parent = self
    
    def remove_child(self, child: 'IRNode') -> None:
        """Remove a child node."""
        self.children.remove(child)
        child.parent = None
    
    def get_symbols(self) -> Dict[str, Any]:
        """Get all symbol names defined in this node and its children."""
        symbols = {}
        if "name" in self.attributes:
            symbols[self.attributes["name"]] = self.attributes
        for child in self.children:
            symbols.update(child.get_symbols())
        return symbols
    
    def get_types(self) -> Dict[str, Any]:
        """Get all type names used in this node and its children."""
        types = {}
        if "type" in self.attributes:
            types[self.attributes["type"]] = self.attributes
        if "return_type" in self.attributes:
            types[self.attributes["return_type"]] = self.attributes
        for child in self.children:
            types.update(child.get_types())
        return types
    
    def get_dependencies(self) -> Set[str]:
        """Get all external dependencies used in this node and its children."""
        deps = set()
        if "source" in self.attributes:
            deps.add(self.attributes["source"])
        for child in self.children:
            deps.update(child.get_dependencies())
        return deps
    
    def get_node_by_position(self, position: Position) -> Optional['IRNode']:
        """Find a node at the given source position."""
        if self.position and self.position.file == position.file:
            if (self.position.line == position.line and
                self.position.column <= position.column):
                return self
        
        for child in self.children:
            result = child.get_node_by_position(position)
            if result:
                return result
        
        return None


class IR:
    """Complete intermediate representation of a program."""
    
    def __init__(self):
        """Initialize an empty IR."""
        self.root = IRNode(IRNodeType.PROGRAM)
        self.symbol_table: Dict[str, Any] = {}
        self.type_information: Dict[str, Any] = {}
        self.dependencies: Set[str] = set()
    
    def clear(self) -> None:
        """Clear the IR."""
        self.root = IRNode(IRNodeType.PROGRAM)
        self.symbol_table.clear()
        self.type_information.clear()
        self.dependencies.clear()
    
    def validate(self) -> bool:
        """Validate the IR structure."""
        # TODO: Implement validation
        return True
    
    def build_from_ast(self, ast: Any) -> None:
        """Build IR from an AST."""
        raise NotImplementedError("build_from_ast not implemented")
    
    def optimize(self) -> None:
        """Optimize the IR."""
        raise NotImplementedError("optimize not implemented")
    
    def to_dot(self) -> str:
        """Convert to DOT format for visualization."""
        raise NotImplementedError("to_dot not implemented")
    
    def get_node_by_position(self, position: Position) -> Optional[IRNode]:
        """Find a node at the given source position."""
        return self.root.get_node_by_position(position)
    
    def get_symbols(self) -> Dict[str, Any]:
        """Get all symbol names defined in the IR."""
        symbols = dict(self.symbol_table)
        symbols.update(self.root.get_symbols())
        return symbols
    
    def get_types(self) -> Dict[str, Any]:
        """Get all type names used in the IR."""
        types = dict(self.type_information)
        types.update(self.root.get_types())
        return types
    
    def get_dependencies(self) -> Set[str]:
        """Get all external dependencies used in the IR."""
        deps = set(self.dependencies)
        deps.update(self.root.get_dependencies())
        return deps
