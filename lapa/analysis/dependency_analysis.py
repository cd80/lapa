"""
Dependency Analysis module.

This module provides functionality to perform dependency analysis on the IR.
"""

from typing import Dict, Set, Optional, List
from lapa.ir import IR, IRNode, IRNodeType


class DependencyAnalyzer:
    """Performs dependency analysis on the IR."""

    def __init__(self):
        """Initialize the dependency analyzer."""
        # Maps an IR node to a set of IR nodes it depends on
        self.dependencies: Dict[IRNode, Set[IRNode]] = {}
        # Track circular dependencies
        self.circular_deps: List[Set[IRNode]] = []
        # Track visited nodes during traversal
        self.visited: Set[IRNode] = set()
        # Track current path for cycle detection
        self.path: List[IRNode] = []

    def analyze(self, ir: IR) -> None:
        """
        Perform dependency analysis on the given IR.

        Args:
            ir: The intermediate representation to analyze.
        """
        # Reset state for new analysis
        self.visited.clear()
        self.path.clear()
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
        elif node.node_type == IRNodeType.CLASS_DEF:
            self.process_class_def(node)
        elif node.node_type == IRNodeType.IF:
            self.process_if_statement(node)
        elif node.node_type == IRNodeType.WHILE:
            self.process_while_statement(node)
        elif node.node_type == IRNodeType.FOR:
            self.process_for_statement(node)
        elif node.node_type == IRNodeType.TRY:
            self.process_try_statement(node)
        elif node.node_type == IRNodeType.BINARY_OP:
            self.process_binary_op(node)
        elif node.node_type == IRNodeType.UNARY_OP:
            self.process_unary_op(node)

    def process_function_def(self, node: IRNode) -> None:
        """Process a function definition node."""
        # Dependencies may include parameters, return type, decorators and the body
        parameters = node.attributes.get('parameters', [])
        body = node.attributes.get('body')
        return_type = node.attributes.get('return_type')
        decorators = node.attributes.get('decorators', [])

        for param in parameters:
            self.dependencies[node].add(param)
            self._safe_process_node(param)

        if body:
            self.dependencies[node].add(body)
            self._safe_process_node(body)

        if return_type:
            self.dependencies[node].add(return_type)
            self._safe_process_node(return_type)

        for decorator in decorators:
            self.dependencies[node].add(decorator)
            self._safe_process_node(decorator)

    def process_function_call(self, node: IRNode) -> None:
        """Process a function call node."""
        # Depends on the function being called, arguments and type args
        function = node.attributes.get('function')
        arguments = node.attributes.get('arguments', [])
        type_args = node.attributes.get('type_args', [])

        if function:
            self.dependencies[node].add(function)
            self._safe_process_node(function)

        for arg in arguments:
            self.dependencies[node].add(arg)
            self._safe_process_node(arg)

        for type_arg in type_args:
            self.dependencies[node].add(type_arg)
            self._safe_process_node(type_arg)

    def process_variable(self, node: IRNode) -> None:
        """Process a variable node."""
        # Variables may depend on their type, initializer and annotations
        var_type = node.attributes.get('type')
        initializer = node.attributes.get('initializer')
        annotations = node.attributes.get('annotations', [])

        if var_type:
            self.dependencies[node].add(var_type)
            self._safe_process_node(var_type)

        if initializer:
            self.dependencies[node].add(initializer)
            self._safe_process_node(initializer)

        for annotation in annotations:
            self.dependencies[node].add(annotation)
            self._safe_process_node(annotation)

    def process_assignment(self, node: IRNode) -> None:
        """Process an assignment node."""
        # The left-hand side depends on the right-hand side
        left = node.attributes.get('left')
        right = node.attributes.get('right')
        type_annotation = node.attributes.get('type_annotation')

        if left and right:
            self.dependencies.setdefault(left, set())
            self.dependencies[left].add(right)
            self._safe_process_node(left)
            self._safe_process_node(right)

        if type_annotation:
            self.dependencies[node].add(type_annotation)
            self._safe_process_node(type_annotation)

    def process_import(self, node: IRNode) -> None:
        """Process an import node."""
        # The module depends on the imported module and any aliases
        module_name = node.attributes.get('module_name')
        aliases = node.attributes.get('aliases', {})
        from_list = node.attributes.get('from_list', [])

        if module_name:
            # Create a dummy node for the imported module
            imported_module = IRNode(
                node_type=IRNodeType.MODULE,
                name=module_name,
                attributes={"module_name": module_name}
            )
            self.dependencies[node].add(imported_module)

        # Process any aliases
        for alias_name, original_name in aliases.items():
            alias_node = IRNode(
                node_type=IRNodeType.ALIAS,
                name=alias_name,
                attributes={"original_name": original_name}
            )
            self.dependencies[node].add(alias_node)

        # Process from-import items
        for item in from_list:
            item_node = IRNode(
                node_type=IRNodeType.IMPORT_FROM,
                name=item,
                attributes={"module": module_name}
            )
            self.dependencies[node].add(item_node)

    def process_class_def(self, node: IRNode) -> None:
        """Process a class definition node."""
        # Classes depend on their bases, body, decorators, and type parameters
        bases = node.attributes.get('bases', [])
        body = node.attributes.get('body')
        decorators = node.attributes.get('decorators', [])
        type_params = node.attributes.get('type_params', [])

        # Add node to current path for cycle detection
        if node in self.path:
            # Found a circular dependency
            cycle = set(self.path[self.path.index(node):])
            if cycle not in self.circular_deps:
                self.circular_deps.append(cycle)
            return

        self.path.append(node)

        try:
            for base in bases:
                self.dependencies[node].add(base)
                self._safe_process_node(base)

            if body:
                self.dependencies[node].add(body)
                self._safe_process_node(body)

            for decorator in decorators:
                self.dependencies[node].add(decorator)
                self._safe_process_node(decorator)

            for type_param in type_params:
                self.dependencies[node].add(type_param)
                self._safe_process_node(type_param)
        finally:
            # Remove node from path after processing
            self.path.pop()

    def process_if_statement(self, node: IRNode) -> None:
        """Process an if statement node."""
        # If statements depend on their test, body, and else clause
        test = node.attributes.get('test')
        body = node.attributes.get('body')
        else_body = node.attributes.get('else')

        if test:
            self.dependencies[node].add(test)
            self._safe_process_node(test)

        if body:
            self.dependencies[node].add(body)
            self._safe_process_node(body)

        if else_body:
            self.dependencies[node].add(else_body)
            self._safe_process_node(else_body)

    def process_while_statement(self, node: IRNode) -> None:
        """Process a while statement node."""
        # While loops depend on their test and body
        test = node.attributes.get('test')
        body = node.attributes.get('body')

        if test:
            self.dependencies[node].add(test)
            self._safe_process_node(test)

        if body:
            self.dependencies[node].add(body)
            self._safe_process_node(body)

    def process_for_statement(self, node: IRNode) -> None:
        """Process a for statement node."""
        # For loops depend on their target, iter, and body
        target = node.attributes.get('target')
        iter_expr = node.attributes.get('iter')
        body = node.attributes.get('body')

        if target:
            self.dependencies[node].add(target)
            self._safe_process_node(target)

        if iter_expr:
            self.dependencies[node].add(iter_expr)
            self._safe_process_node(iter_expr)

        if body:
            self.dependencies[node].add(body)
            self._safe_process_node(body)

    def process_try_statement(self, node: IRNode) -> None:
        """Process a try statement node."""
        # Try statements depend on their body, handlers, else, and finally
        body = node.attributes.get('body')
        handlers = node.attributes.get('handlers', [])
        else_body = node.attributes.get('else')
        finally_body = node.attributes.get('finally')

        if body:
            self.dependencies[node].add(body)
            self._safe_process_node(body)

        for handler in handlers:
            self.dependencies[node].add(handler)
            self._safe_process_node(handler)

        if else_body:
            self.dependencies[node].add(else_body)
            self._safe_process_node(else_body)

        if finally_body:
            self.dependencies[node].add(finally_body)
            self._safe_process_node(finally_body)

    def process_binary_op(self, node: IRNode) -> None:
        """Process a binary operation node."""
        # Binary operations depend on their left and right operands
        left = node.attributes.get('left')
        right = node.attributes.get('right')

        if left:
            self.dependencies[node].add(left)
            self._safe_process_node(left)

        if right:
            self.dependencies[node].add(right)
            self._safe_process_node(right)

    def process_unary_op(self, node: IRNode) -> None:
        """Process a unary operation node."""
        # Unary operations depend on their operand
        operand = node.attributes.get('operand')

        if operand:
            self.dependencies[node].add(operand)
            self._safe_process_node(operand)

    def _safe_process_node(self, node: IRNode) -> None:
        """
        Safely process a node, avoiding infinite recursion.

        Args:
            node: The node to process.
        """
        if node not in self.visited:
            self.visited.add(node)
            self.process_node(node)

    def get_dependencies(self) -> Dict[IRNode, Set[IRNode]]:
        """
        Get the computed dependencies.

        Returns:
            A dictionary mapping IR nodes to sets of dependent IR nodes.
        """
        return self.dependencies

    def get_circular_dependencies(self) -> List[Set[IRNode]]:
        """
        Get any detected circular dependencies.

        Returns:
            A list of sets, where each set contains nodes forming a circular dependency.
        """
        return self.circular_deps
