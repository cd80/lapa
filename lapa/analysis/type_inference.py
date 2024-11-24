"""
Type Inference Analysis module.

This module provides functionality to perform type inference on the IR.
"""

from typing import Dict, Any, Optional
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
            left_operand = node.attributes.get('left_operand')
            right_operand = node.attributes.get('right_operand')
            operator = node.attributes.get('operator')

            left_type = self.infer_type(left_operand) if left_operand else 'unknown'
            right_type = self.infer_type(right_operand) if right_operand else 'unknown'

            inferred_type = self.resolve_binary_operation_type(operator, left_type, right_type)
        elif node.node_type == IRNodeType.FUNCTION_CALL:
            # For function calls, infer type based on function definition
            inferred_type = self.infer_function_call_type(node)
        elif node.node_type == IRNodeType.ASSIGNMENT:
            # For assignments, infer type from the right-hand side
            right = node.attributes.get('right')
            left = node.attributes.get('left')
            inferred_type = self.infer_type(right)
            # Update the variable's type information
            if isinstance(left, IRNode):
                self.type_information[left] = inferred_type
        elif node.node_type == IRNodeType.CONDITIONAL:
            # For conditionals, infer type based on branches
            condition = node.attributes.get('condition')
            true_branch = node.attributes.get('true_branch')
            false_branch = node.attributes.get('false_branch')
            self.infer_type(condition)
            self.infer_type(true_branch)
            self.infer_type(false_branch)
            inferred_type = 'void'
        elif node.node_type == IRNodeType.LOOP:
            # For loops, infer type of condition and body
            condition = node.attributes.get('condition')
            body = node.attributes.get('body')
            self.infer_type(condition)
            self.infer_type(body)
            inferred_type = 'void'
        elif node.node_type == IRNodeType.FUNCTION_DEF:
            # Infer return type and parameter types
            inferred_type = self.infer_function_def_type(node)
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
        if isinstance(value, bool):  # Check for bool first since bool is a subclass of int
            return 'bool'
        elif isinstance(value, int):
            return 'int'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, str):
            return 'str'
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
                    return 'int'
                elif operator in ['==', '!=', '<', '<=', '>', '>=']:
                    return 'bool'
            return 'unknown'

    def infer_function_call_type(self, node: IRNode) -> Any:
        """Infer type for a function call node."""
        # Get the function definition from node.attributes['function']
        function_def = node.attributes.get('function')
        if function_def:
            # Return the function's return type directly if available
            return function_def.attributes.get('return_type', 'unknown')
        return 'unknown'

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

    # Additional methods can be added here to handle more complex cases
