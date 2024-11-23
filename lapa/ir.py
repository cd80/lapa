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
    OPERATOR = auto()
    # Added new node types
    STRUCT = auto()
    ENUM = auto()
    TRAIT = auto()
    MACRO = auto()
    IMPLEMENTATION = auto()


@dataclass
class Position:
    """Source code position information."""
    line: int
    column: int
    file: str


@dataclass
class OwnershipInfo:
    """Ownership information for variables and parameters."""
    is_mutable: bool = False
    is_reference: bool = False
    lifetime: Optional[str] = None


class IRNode:
    """Node in the intermediate representation."""

    def __init__(
        self,
        node_type: IRNodeType,
        name: Optional[str] = None,
        position: Optional[Position] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize an IR node.

        Args:
            node_type: Type of the node
            name: Name of the node
            position: Source code position
            attributes: Additional node attributes
        """
        self.node_type = node_type
        self.name = name
        self.position = position
        self.attributes = attributes or {}
        self.children: List['IRNode'] = []
        self.parent: Optional['IRNode'] = None

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
        if self.name:
            symbols[self.name] = self
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
            if (
                self.position.line == position.line
                and self.position.column <= position.column
            ):
                return self

        for child in self.children:
            result = child.get_node_by_position(position)
            if result:
                return result

        return None


class Function(IRNode):
    """Represents a function in the IR."""

    def __init__(
        self,
        name: str,
        return_type: Optional[str] = None,
        parameters: Optional[List[Dict[str, Any]]] = None,
        position: Optional[Position] = None,
    ):
        super().__init__(
            node_type=IRNodeType.FUNCTION,
            name=name,
            position=position,
            attributes={"return_type": return_type},
        )
        self.parameters = parameters or []
        self.return_type = return_type


class Struct(IRNode):
    """Represents a struct in the IR."""

    def __init__(
        self,
        name: str,
        fields: Optional[List[Dict[str, Any]]] = None,
        position: Optional[Position] = None,
    ):
        super().__init__(node_type=IRNodeType.STRUCT, name=name, position=position)
        self.fields = fields or []


class Enum(IRNode):
    """Represents an enum in the IR."""

    def __init__(
        self,
        name: str,
        variants: Optional[List[Dict[str, Any]]] = None,
        position: Optional[Position] = None,
    ):
        super().__init__(node_type=IRNodeType.ENUM, name=name, position=position)
        self.variants = variants or []


class Trait(IRNode):
    """Represents a trait in the IR."""

    def __init__(
        self,
        name: str,
        items: Optional[List[Any]] = None,
        position: Optional[Position] = None,
    ):
        super().__init__(node_type=IRNodeType.TRAIT, name=name, position=position)
        self.items = items or []


class Macro(IRNode):
    """Represents a macro in the IR."""

    def __init__(
        self,
        name: str,
        body: Optional[str] = None,
        position: Optional[Position] = None,
    ):
        super().__init__(node_type=IRNodeType.MACRO, name=name, position=position)
        self.body = body


class Implementation(IRNode):
    """Represents an implementation block in the IR."""

    def __init__(
        self,
        type_name: str,
        methods: Optional[List[Any]] = None,
        position: Optional[Position] = None,
    ):
        super().__init__(
            node_type=IRNodeType.IMPLEMENTATION,
            name=type_name,
            position=position,
        )
        self.methods = methods or []


class Variable(IRNode):
    """Represents a variable in the IR."""

    def __init__(
        self,
        name: str,
        var_type: Optional[str] = None,
        ownership: Optional[OwnershipInfo] = None,
        position: Optional[Position] = None,
    ):
        super().__init__(node_type=IRNodeType.VARIABLE, name=name, position=position)
        self.var_type = var_type
        self.ownership = ownership


class IR:
    """Complete intermediate representation of a program."""

    def __init__(self):
        """Initialize an empty IR."""
        self.root = IRNode(IRNodeType.PROGRAM)
        self.symbol_table: Dict[str, Any] = {}
        self.type_information: Dict[str, Any] = {}
        self.dependencies: Set[str] = set()
        self.imports: Set[str] = set()
        self.functions: List[Function] = []
        self.structs: List[Struct] = []
        self.enums: List[Enum] = []
        self.traits: List[Trait] = []
        self.macros: List[Macro] = []
        self.implementations: List[Implementation] = []
        self.variables: List[Variable] = []
        self.metadata: Dict[str, Any] = {}

    def add_function(self, function: Function) -> None:
        """Add a function to the IR."""
        self.functions.append(function)
        self.root.add_child(function)
        self.symbol_table[function.name] = function

    def add_struct(self, struct: Struct) -> None:
        """Add a struct to the IR."""
        self.structs.append(struct)
        self.root.add_child(struct)
        self.symbol_table[struct.name] = struct

    def add_enum(self, enum: Enum) -> None:
        """Add an enum to the IR."""
        self.enums.append(enum)
        self.root.add_child(enum)
        self.symbol_table[enum.name] = enum

    def add_trait(self, trait: Trait) -> None:
        """Add a trait to the IR."""
        self.traits.append(trait)
        self.root.add_child(trait)
        self.symbol_table[trait.name] = trait

    def add_macro(self, macro: Macro) -> None:
        """Add a macro to the IR."""
        self.macros.append(macro)
        self.root.add_child(macro)
        self.symbol_table[macro.name] = macro

    def add_implementation(self, implementation: Implementation) -> None:
        """Add an implementation to the IR."""
        self.implementations.append(implementation)
        self.root.add_child(implementation)
        self.symbol_table[implementation.name] = implementation

    def add_variable(self, variable: Variable) -> None:
        """Add a variable to the IR."""
        self.variables.append(variable)
        self.root.add_child(variable)
        self.symbol_table[variable.name] = variable

    def clear(self) -> None:
        """Clear the IR."""
        self.__init__()

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
