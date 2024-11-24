"""
Type Inference Analysis module.

This module provides functionality to perform type inference on the IR.
"""

from typing import Dict, Any, Optional, List
from lapa.ir import IR, IRNode, IRNodeType


class TypeInferenceAnalyzer:
    """Performs type inference analysis on the IR."""

    def __init__(self):
        """Initialize the type inference analyzer."""
        # Stores the inferred types of IR nodes
        self.type_information: Dict[IRNode, Any] = {}

    def analyze(self, ir: IR) -> None:
        """
        Perform type inference analysis on the given IR.

        Args:
            ir: The intermediate representation to analyze.
        """
        # Start the type inference by traversing from the root node
        self.traverse(ir.root)

    def traverse(self, node: IRNode) -> None:
        """
        Recursively traverse the IR tree and infer types.

        Args:
            node: The current IR node.
        """
        self.infer_type(node)
        for child in node.children:
            self.traverse(child)

    def infer_type(self, node: Optional[IRNode]) -> Optional[Any]:
        """
        Infer the type of a given IR node.

        Args:
            node: The IR node to infer the type for.

        Returns:
            The inferred type of the node, or None if not applicable.
        """
        # Handle None nodes
        if node is None:
            return None

        # Skip PROGRAM nodes as they do not represent a value with a type
        if node.node_type == IRNodeType.PROGRAM:
            return None

        # If the type is already inferred, return it
        if node in self.type_information:
            return self.type_information[node]

        inferred_type = None

        if node.node_type == IRNodeType.LITERAL:
            # For literals, the type can be directly inferred
            inferred_type = self.infer_literal_type(node)
        elif node.node_type == IRNodeType.VARIABLE:
            # For variables, infer type based on assignments or definitions
            inferred_type = self.infer_variable_type(node)
        elif node.node_type == IRNodeType.BINARY_OPERATION:
            # For binary operations, infer type based on operands
            inferred_type = self.infer_binary_operation_type(node)
        elif node.node_type == IRNodeType.FUNCTION_CALL:
            # For function calls, infer type based on function definition
            inferred_type = self.infer_function_call_type(node)
        elif node.node_type == IRNodeType.ASSIGNMENT:
            # For assignments, infer type from the right-hand side
            inferred_type = self.infer_assignment_type(node)
        elif node.node_type == IRNodeType.CONDITIONAL:
            # For conditionals, infer type based on branches
            inferred_type = self.infer_conditional_type(node)
        elif node.node_type == IRNodeType.LOOP:
            # For loops, infer type of condition and body
            inferred_type = self.infer_loop_type(node)
        elif node.node_type == IRNodeType.FUNCTION_DEF:
            # Infer return type and parameter types
            inferred_type = self.infer_function_def_type(node)
        elif node.node_type == IRNodeType.CLASS_DEF:
            # Infer types within class definitions
            inferred_type = self.infer_class_def_type(node)
        elif node.node_type == IRNodeType.COLLECTION:
            # Infer type for collections like lists, dicts, sets, tuples
            inferred_type = self.infer_collection_type(node)
        else:
            # For other node types, default to 'unknown'
            inferred_type = 'unknown'

        # Store the inferred type if applicable
        if inferred_type is not None:
            self.type_information[node] = inferred_type

        return inferred_type

    def infer_literal_type(self, node: IRNode) -> Any:
        """Infer type for a literal node."""
        # Assume node.attributes['value'] contains the literal value
        value = node.attributes.get('value')
        if isinstance(value, bool):
            return 'bool'
        elif isinstance(value, int):
            return 'int'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, str):
            return 'str'
        elif isinstance(value, list):
            return f'List[{self.infer_collection_element_type(value)}]'
        elif isinstance(value, dict):
            return f'Dict[{self.infer_dict_key_value_types(value)}]'
        elif isinstance(value, tuple):
            return f'Tuple[{", ".join(self.infer_tuple_element_types(value))}]'
        elif isinstance(value, set):
            return f'Set[{self.infer_collection_element_type(value)}]'
        else:
            return 'unknown'

    def infer_variable_type(self, node: IRNode) -> Any:
        """Infer type for a variable node."""
        # Check if the variable has been assigned a type
        if node in self.type_information:
            return self.type_information[node]
        elif 'definition' in node.attributes:
            inferred_type = self.infer_type(node.attributes['definition'])
            self.type_information[node] = inferred_type
            return inferred_type
        else:
            return 'unknown'

    def infer_binary_operation_type(self, node: IRNode) -> Any:
        """Infer type for a binary operation node."""
        left_operand = node.attributes.get('left_operand')
        right_operand = node.attributes.get('right_operand')
        operator = node.attributes.get('operator')

        left_type = self.infer_type(left_operand) if left_operand else 'unknown'
        right_type = self.infer_type(right_operand) if right_operand else 'unknown'

        return self.resolve_binary_operation_type(operator, left_type, right_type)

    def infer_function_call_type(self, node: IRNode) -> Any:
        """Infer type for a function call node."""
        function_def = node.attributes.get('function')
        if function_def:
            # Return the function's return type directly if available
            return_type = function_def.attributes.get('return_type', 'unknown')
            return return_type
        return 'unknown'

    def infer_assignment_type(self, node: IRNode) -> Any:
        """Infer type for an assignment node."""
        right = node.attributes.get('right')
        left = node.attributes.get('left')
        inferred_type = self.infer_type(right)
        # Update the variable's type information
        if isinstance(left, IRNode):
            self.type_information[left] = inferred_type
        return inferred_type

    def infer_conditional_type(self, node: IRNode) -> Any:
        """Infer type for a conditional node."""
        condition = node.attributes.get('condition')
        true_branch = node.attributes.get('true_branch')
        false_branch = node.attributes.get('false_branch')

        self.infer_type(condition)
        true_type = self.infer_type(true_branch)
        false_type = self.infer_type(false_branch)

        if true_type == false_type:
            return true_type
        else:
            return 'unknown'  # Could be improved with union types

    def infer_loop_type(self, node: IRNode) -> Any:
        """Infer type for a loop node."""
        condition = node.attributes.get('condition')
        body = node.attributes.get('body')
        self.infer_type(condition)
        self.infer_type(body)
        return 'void'

    def infer_function_def_type(self, node: IRNode) -> Any:
        """Infer return type for a function definition."""
        # Infer types of parameters
        parameters = node.attributes.get('parameters', [])
        for param in parameters:
            self.infer_type(param)
        # Infer type of the function body if it exists
        body = node.attributes.get('body')
        if body is not None:
            self.infer_type(body)
        # Get the return type if specified
        return_type = node.attributes.get('return_type', 'void')
        self.type_information[node] = return_type
        return return_type

    def infer_class_def_type(self, node: IRNode) -> Any:
        """Infer types within a class definition."""
        class_name = node.attributes.get('name', 'UnknownClass')
        # Infer types of attributes and methods
        members = node.attributes.get('members', [])
        for member in members:
            self.infer_type(member)
        self.type_information[node] = class_name
        return class_name

    def infer_collection_type(self, node: IRNode) -> Any:
        """Infer type for collection nodes."""
        collection_type = node.attributes.get('collection_type')
        elements = node.attributes.get('elements', [])
        element_types = [self.infer_type(element) for element in elements]
        element_type = self.unify_types(element_types)

        if collection_type == 'list':
            return f'List[{element_type}]'
        elif collection_type == 'dict':
            key_types = []
            value_types = []
            for key, value in elements:
                key_types.append(self.infer_type(key))
                value_types.append(self.infer_type(value))
            key_type = self.unify_types(key_types)
            value_type = self.unify_types(value_types)
            return f'Dict[{key_type}, {value_type}]'
        elif collection_type == 'set':
            return f'Set[{element_type}]'
        elif collection_type == 'tuple':
            return f'Tuple[{", ".join(element_types)}]'
        else:
            return 'unknown'

    def unify_types(self, types: List[Any]) -> Any:
        """Unify a list of types into a single type."""
        types_set = set(types)
        if len(types_set) == 1:
            return types[0]
        elif 'unknown' in types_set:
            types_set.discard('unknown')
            if len(types_set) == 1:
                return types_set.pop()
            else:
                return 'unknown'
        else:
            return 'Any'  # Could be improved with union types or type variables

    def infer_collection_element_type(self, collection: Any) -> Any:
        """Infer the type of elements within a collection."""
        element_types = [self.infer_literal_type(IRNode(attributes={'value': element}, node_type=IRNodeType.LITERAL)) for element in collection]
        return self.unify_types(element_types)

    def infer_dict_key_value_types(self, dictionary: dict) -> str:
        """Infer the types of keys and values in a dictionary."""
        key_types = []
        value_types = []
        for key, value in dictionary.items():
            key_type = self.infer_literal_type(IRNode(attributes={'value': key}, node_type=IRNodeType.LITERAL))
            value_type = self.infer_literal_type(IRNode(attributes={'value': value}, node_type=IRNodeType.LITERAL))
            key_types.append(key_type)
            value_types.append(value_type)
        unified_key_type = self.unify_types(key_types)
        unified_value_type = self.unify_types(value_types)
        return f'{unified_key_type}, {unified_value_type}'

    def infer_tuple_element_types(self, tuple_obj: tuple) -> List[str]:
        """Infer the types of elements in a tuple."""
        return [self.infer_literal_type(IRNode(attributes={'value': element}, node_type=IRNodeType.LITERAL)) for element in tuple_obj]

    def resolve_binary_operation_type(self, operator: str, left_type: Any, right_type: Any) -> Any:
        """Resolve the type of a binary operation based on operand types."""
        # Simplified type resolution logic
        if left_type == right_type:
            if operator in ['+', '-', '*', '/']:
                return left_type
            elif operator in ['==', '!=', '<', '<=', '>', '>=']:
                return 'bool'
            else:
                return 'unknown'
        else:
            # Handle type promotion, e.g., int + float => float
            if 'unknown' in (left_type, right_type):
                return 'unknown'
            if 'float' in (left_type, right_type):
                if operator in ['+', '-', '*', '/']:
                    return 'float'
                elif operator in ['==', '!=', '<', '<=', '>', '>=']:
                    return 'bool'
            if 'int' in (left_type, right_type):
                if operator in ['+', '-', '*', '/']:
                    return 'float' if 'float' in (left_type, right_type) else 'int'
                elif operator in ['==', '!=', '<', '<=', '>', '>=']:
                    return 'bool'
            return 'unknown'

    # Additional methods can be added here to handle more complex cases
