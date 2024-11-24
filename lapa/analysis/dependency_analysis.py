"""
Dependency Analysis module.

This module provides functionality to perform dependency analysis on the IR.
"""

from typing import Dict, Set, Optional
from lapa.ir import IR, IRNode, IRNodeType


class DependencyAnalyzer:
    """Performs dependency analysis on the IR."""

    def __init__(self):
        """Initialize the dependency analyzer."""
        # Maps an IR node to a set of IR nodes it depends on
        self.dependencies: Dict[IRNode, Set[IRNode]] = {}

    def analyze(self, ir: IR) -> None:
        """
        Perform dependency analysis on the given IR.

        Args:
            ir: The intermediate representation to analyze.
        """
        # Start traversal from the root node
        self.traverse(ir.root)

    def traverse(self, node: IRNode) -> None:
        """
        Recursively traverse the IR tree and build dependencies.

        Args:
            node: The current IR node.
        """
        # Skip processing for PROGRAM nodes
        if node.node_type == IRNodeType.PROGRAM:
            for child in node.children:
                self.traverse(child)
            return

        self.process_node(node)
        for child in node.children:
            self.traverse(child)

    def process_node(self, node: IRNode) -> None:
        """
        Process an IR node and update dependencies.

        Args:
            node: The IR node to process.
        """
        # Initialize the dependencies set for the node if not already done
        if node not in self.dependencies:
            self.dependencies[node] = set()

        # Handle different types of nodes
        if node.node_type == IRNodeType.FUNCTION_DEF:
            self.process_function_def(node)
        elif node.node_type == IRNodeType.FUNCTION_CALL:
            self.process_function_call(node)
        elif node.node_type == IRNodeType.VARIABLE:
            self.process_variable(node)
        elif node.node_type == IRNodeType.ASSIGNMENT:
            self.process_assignment(node)
        elif node.node_type == IRNodeType.IMPORT:
            self.process_import(node)
        # Add processing for other node types as needed

    def process_function_def(self, node: IRNode) -> None:
        """Process a function definition node."""
        # Dependencies may include parameters and the body
        parameters = node.attributes.get('parameters', [])
        body = node.attributes.get('body')

        for param in parameters:
            self.dependencies[node].add(param)
            # Also process parameters
            self.process_node(param)

        if body:
            self.dependencies[node].add(body)
            self.process_node(body)

    def process_function_call(self, node: IRNode) -> None:
        """Process a function call node."""
        # Depends on the function being called and arguments
        function = node.attributes.get('function')
        arguments = node.attributes.get('arguments', [])

        if function:
            self.dependencies[node].add(function)
            self.process_node(function)

        for arg in arguments:
            self.dependencies[node].add(arg)
            self.process_node(arg)

    def process_variable(self, node: IRNode) -> None:
        """Process a variable node."""
        # Variables may depend on their type and initializer
        var_type = node.attributes.get('type')
        initializer = node.attributes.get('initializer')

        if var_type:
            self.dependencies[node].add(var_type)
            self.process_node(var_type)

        if initializer:
            self.dependencies[node].add(initializer)
            self.process_node(initializer)

    def process_assignment(self, node: IRNode) -> None:
        """Process an assignment node."""
        # The left-hand side depends on the right-hand side
        left = node.attributes.get('left')
        right = node.attributes.get('right')

        if left and right:
            self.dependencies.setdefault(left, set())
            self.dependencies[left].add(right)
            self.process_node(left)
            self.process_node(right)

    def process_import(self, node: IRNode) -> None:
        """Process an import node."""
        # The module depends on the imported module
        module_name = node.attributes.get('module_name')
        if module_name:
            # Create a dummy node for the imported module
            imported_module = IRNode(
                node_type=IRNodeType.MODULE,
                name=module_name,
                attributes={"module_name": module_name}
            )
            self.dependencies[node].add(imported_module)

    def get_dependencies(self) -> Dict[IRNode, Set[IRNode]]:
        """
        Get the computed dependencies.

        Returns:
            A dictionary mapping IR nodes to sets of dependent IR nodes.
        """
        return self.dependencies

    # Additional methods for processing other node types as needed
