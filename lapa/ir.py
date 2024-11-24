"""
Intermediate Representation (IR) for LAPA framework.

This module defines the core IR classes and utilities used throughout
the framework for representing and manipulating program structures.
"""

from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass
from collections import Counter


class IRNodeType(Enum):
    """Types of IR nodes."""
    PROGRAM = auto()
    FUNCTION_DEF = auto()
    FUNCTION = auto()
    CLASS_DEF = auto()
    CLASS = auto()
    METHOD = auto()
    VARIABLE = auto()
    LITERAL = auto()
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
    FUNCTION_CALL = auto()
    OPERATOR = auto()
    NO_OP = auto()
    BLOCK = auto()
    BINARY_OP = auto()
    UNARY_OP = auto()
    CONDITIONAL = auto()
    TRY = auto()
    EXCEPT_HANDLER = auto()
    COLLECTION = auto()
    STRUCT = auto()
    ENUM = auto()
    TRAIT = auto()
    MACRO = auto()
    IMPLEMENTATION = auto()
    TYPE = auto()
    ALIAS = auto()
    WHILE = auto()
    FOR = auto()
    IF = auto()
    IMPORT_FROM = auto()
    ARRAY_ACCESS = auto()  # Added for array/collection access analysis
    PHI = auto()  # Added for SSA form phi nodes


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

    def get_symbols(self) -> List[str]:
        """
        Get all symbol names defined in this node and its children.

        Returns:
            A list of symbol names.
        """
        symbols = []
        if self.node_type in {
            IRNodeType.FUNCTION_DEF,
            IRNodeType.FUNCTION,
            IRNodeType.CLASS_DEF,
            IRNodeType.CLASS,
            IRNodeType.VARIABLE,
            IRNodeType.STRUCT,
            IRNodeType.ENUM,
            IRNodeType.TRAIT,
            IRNodeType.MACRO,
        } and self.name:
            symbols.append(self.name)
        for child in self.children:
            symbols.extend(child.get_symbols())
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

    def find_nodes_by_type(self, node_type: IRNodeType) -> List['IRNode']:
        """Find all nodes of a specific type in the subtree starting from this node."""
        nodes = []
        if self.node_type == node_type:
            nodes.append(self)
        for child in self.children:
            nodes.extend(child.find_nodes_by_type(node_type))
        return nodes

    @staticmethod
    def from_ast_node(ast_node: Any) -> 'IRNode':
        """
        Create an IRNode from an AST node.

        Args:
            ast_node: The AST node to convert.

        Returns:
            The corresponding IRNode.
        """
        # Placeholder implementation; actual implementation depends on AST structure
        node_type_mapping = {
            'FunctionDef': IRNodeType.FUNCTION_DEF,
            'ClassDef': IRNodeType.CLASS_DEF,
            'Assign': IRNodeType.ASSIGNMENT,
            'Call': IRNodeType.FUNCTION_CALL,
            'If': IRNodeType.IF,
            'For': IRNodeType.FOR,
            'While': IRNodeType.WHILE,
            'Try': IRNodeType.TRY,
            'Return': IRNodeType.RETURN,
            'Import': IRNodeType.IMPORT,
            # Add more mappings as needed
        }

        node_type = node_type_mapping.get(ast_node.__class__.__name__, IRNodeType.NO_OP)

        name = getattr(ast_node, 'name', None)
        position = Position(
            line=getattr(ast_node, 'lineno', -1),
            column=getattr(ast_node, 'col_offset', -1),
            file=getattr(ast_node, 'filename', '')
        )
        attributes = {}  # Extract relevant attributes from the AST node

        ir_node = IRNode(
            node_type=node_type,
            name=name,
            position=position,
            attributes=attributes
        )

        # Recursively convert child nodes
        for child_ast in getattr(ast_node, 'body', []):
            child_ir = IRNode.from_ast_node(child_ast)
            ir_node.add_child(child_ir)

        return ir_node


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
            node_type=IRNodeType.FUNCTION_DEF,
            name=name,
            position=position,
            attributes={"return_type": return_type, "parameters": parameters},
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
        definition: Optional[IRNode] = None,
    ):
        super().__init__(
            node_type=IRNodeType.VARIABLE,
            name=name,
            position=position,
            attributes={"type": var_type, "ownership": ownership, "definition": definition},
        )
        self.var_type = var_type
        self.ownership = ownership
        self.definition = definition


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
        errors = []

        # Collect all symbol names, including duplicates
        symbol_names = self.root.get_symbols()

        # Count occurrences to find duplicates
        symbol_counts = Counter(symbol_names)
        duplicates = [name for name, count in symbol_counts.items() if count > 1]

        if duplicates:
            errors.append(f"Duplicate symbols found: {', '.join(duplicates)}")

        # Check for nodes with invalid types or missing names
        def validate_node(node: IRNode):
            if not isinstance(node.node_type, IRNodeType):
                errors.append(f"Invalid node type at {node}")
            if node.node_type in {
                IRNodeType.CLASS_DEF,
                IRNodeType.CLASS,
                IRNodeType.FUNCTION,
                IRNodeType.FUNCTION_DEF,
                IRNodeType.VARIABLE,
                IRNodeType.STRUCT,
                IRNodeType.ENUM,
                IRNodeType.TRAIT,
                IRNodeType.MACRO,
            } and not node.name:
                errors.append(f"Missing name for node type {node.node_type}")
            for child in node.children:
                if child.parent != node:
                    errors.append(f"Parent-child relationship broken between {node} and {child}")
                validate_node(child)

        validate_node(self.root)

        # Report errors if any
        if errors:
            for error in errors:
                print("Validation Error:", error)
            return False
        return True

    def build_from_ast(self, ast: Any) -> None:
        """Build IR from an AST."""
        self.clear()
        ir_node = IRNode.from_ast_node(ast)
        self.root.add_child(ir_node)
        # Update symbol table and other structures
        self.symbol_table.update(self.get_symbols())
        self.type_information.update(self.get_types())
        self.dependencies.update(self.get_dependencies())

    def optimize(self) -> None:
        """Optimize the IR."""
        self.constant_folding()
        self.dead_code_elimination()
        self.remove_unused_variables()

    def constant_folding(self) -> None:
        """Perform constant folding optimization."""
        def fold_constants(node: IRNode):
            for child in node.children:
                fold_constants(child)
            if node.node_type == IRNodeType.BINARY_OP:  # Updated to use BINARY_OP
                left = node.children[0]
                right = node.children[1]
                if left.node_type == IRNodeType.LITERAL and right.node_type == IRNodeType.LITERAL:
                    op = node.attributes.get('operator')
                    if op and isinstance(left.attributes.get('value'), (int, float)) and isinstance(right.attributes.get('value'), (int, float)):
                        result = None
                        if op == '+':
                            result = left.attributes['value'] + right.attributes['value']
                        elif op == '-':
                            result = left.attributes['value'] - right.attributes['value']
                        elif op == '*':
                            result = left.attributes['value'] * right.attributes['value']
                        elif op == '/':
                            if right.attributes['value'] != 0:
                                result = left.attributes['value'] / right.attributes['value']
                        if result is not None:
                            node.node_type = IRNodeType.LITERAL
                            node.attributes = {'value': result}
                            node.children = []

        fold_constants(self.root)

    def dead_code_elimination(self) -> None:
        """Perform dead code elimination."""
        def eliminate_dead_code(node: IRNode):
            new_children = []
            for child in node.children:
                eliminate_dead_code(child)
                if not (child.node_type == IRNodeType.NO_OP):
                    new_children.append(child)
            node.children = new_children

        eliminate_dead_code(self.root)

    def remove_unused_variables(self) -> None:
        """Remove variables that are declared but never used."""
        variable_usage = set()

        def collect_variable_usage(node: IRNode):
            if node.node_type == IRNodeType.VARIABLE and node.name:
                variable_usage.add(node.name)
            for child in node.children:
                collect_variable_usage(child)

        def remove_unused(node: IRNode):
            new_children = []
            for child in node.children:
                if child.node_type == IRNodeType.VARIABLE and child.name not in variable_usage:
                    continue  # Skip unused variable
                remove_unused(child)
                new_children.append(child)
            node.children = new_children

        collect_variable_usage(self.root)
        remove_unused(self.root)

    def to_dot(self) -> str:
        """Convert to DOT format for visualization."""
        lines = ['digraph IR {']

        def add_edges(node: IRNode):
            for child in node.children:
                lines.append(f'  "{node.node_type.name}:{node.name}" -> "{child.node_type.name}:{child.name}";')
                add_edges(child)

        add_edges(self.root)
        lines.append('}')
        return '\n'.join(lines)

    def get_node_by_position(self, position: Position) -> Optional[IRNode]:
        """Find a node at the given source position."""
        return self.root.get_node_by_position(position)

    def get_symbols(self) -> Dict[str, Any]:
        """Get all symbol names defined in the IR."""
        symbols = {}

        def collect_symbols(node: IRNode):
            if node.node_type in {
                IRNodeType.CLASS_DEF,
                IRNodeType.CLASS,
                IRNodeType.FUNCTION,
                IRNodeType.FUNCTION_DEF,
                IRNodeType.VARIABLE,
                IRNodeType.STRUCT,
                IRNodeType.ENUM,
                IRNodeType.TRAIT,
                IRNodeType.MACRO,
            } and node.name:
                symbols[node.name] = node
            for child in node.children:
                collect_symbols(child)

        collect_symbols(self.root)
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
