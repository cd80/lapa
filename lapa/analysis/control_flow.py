"""
Control Flow Analysis module.

This module provides functionality to build a control flow graph (CFG) from the IR.
"""

from typing import Dict, Set, List
from lapa.ir import IR, IRNode, IRNodeType


class BasicBlock:
    """Represents a basic block in the control flow graph."""

    def __init__(self, name: str):
        self.name = name
        self.statements: List[IRNode] = []
        self.predecessors: Set['BasicBlock'] = set()
        self.successors: Set['BasicBlock'] = set()

    def add_statement(self, node: IRNode):
        self.statements.append(node)

    def add_successor(self, block: 'BasicBlock'):
        self.successors.add(block)
        block.predecessors.add(self)


class ControlFlowGraph:
    """Represents the control flow graph of a function."""

    def __init__(self, name: str):
        self.name = name
        self.entry_block = BasicBlock("entry")
        self.exit_block = BasicBlock("exit")
        self.blocks: Dict[str, BasicBlock] = {
            "entry": self.entry_block,
            "exit": self.exit_block,
        }
        self.block_counter = 1  # Initialize a counter for block IDs


class ControlFlowAnalyzer:
    """Performs control flow analysis on the IR."""

    def __init__(self):
        """Initialize the control flow analyzer."""
        self.cfgs: Dict[str, ControlFlowGraph] = {}

    def analyze(self, ir: IR) -> None:
        """
        Perform control flow analysis on the given IR.

        Args:
            ir: The intermediate representation to analyze.
        """
        for function_node in self._get_function_nodes(ir.root):
            cfg = self._build_cfg(function_node)
            function_name = function_node.name or "anonymous"
            self.cfgs[function_name] = cfg

    def _get_function_nodes(self, node: IRNode) -> List[IRNode]:
        """Recursively gather all function nodes in the IR."""
        function_nodes = []
        if node.node_type in {IRNodeType.FUNCTION_DEF, IRNodeType.FUNCTION}:
            function_nodes.append(node)
        for child in node.children:
            function_nodes.extend(self._get_function_nodes(child))
        return function_nodes

    def _build_cfg(self, function_node: IRNode) -> ControlFlowGraph:
        """Build a control flow graph for a given function node."""
        function_name = function_node.name or "anonymous"
        cfg = ControlFlowGraph(function_name)
        current_block = cfg.entry_block

        # Process the function body directly from the function node's children
        current_block = self._process_node_list(function_node.children, current_block, cfg)
        current_block.add_successor(cfg.exit_block)

        return cfg

    def _process_node(self, node: IRNode, current_block: BasicBlock, cfg: ControlFlowGraph) -> BasicBlock:
        """Process an IR node and update the CFG accordingly."""
        if node.node_type == IRNodeType.CONTROL_FLOW:
            control_type = node.attributes.get("type")
            if control_type in {"if", "if_else"}:
                # Handle if-else control flow
                condition = node.attributes.get("condition")

                # Create blocks with appropriate block IDs
                if_block_id = cfg.block_counter
                if_block = BasicBlock(f"if_block_{if_block_id}")
                cfg.block_counter += 1

                else_block_id = cfg.block_counter
                else_block = BasicBlock(f"else_block_{else_block_id}")
                cfg.block_counter += 1

                end_block_id = cfg.block_counter
                end_block = BasicBlock(f"end_block_{end_block_id}")
                cfg.block_counter += 1

                # Add blocks to CFG
                cfg.blocks[if_block.name] = if_block
                cfg.blocks[else_block.name] = else_block
                cfg.blocks[end_block.name] = end_block

                # Connect current block to condition evaluation
                if condition:
                    current_block.add_statement(condition)
                current_block.add_successor(if_block)
                current_block.add_successor(else_block)

                # Process the 'if' branch
                if_children = node.children[0].children if node.children else []
                new_if_block = self._process_node_list(if_children, if_block, cfg)
                new_if_block.add_successor(end_block)

                # Process the 'else' branch
                else_children = node.children[1].children if len(node.children) > 1 else []
                if else_children:
                    new_else_block = self._process_node_list(else_children, else_block, cfg)
                    new_else_block.add_successor(end_block)
                else:
                    else_block.add_successor(end_block)

                # Continue from the end block
                current_block = end_block

            else:
                # Unknown control flow type; treat as normal statements
                current_block.add_statement(node)
                current_block = self._process_node_list(node.children, current_block, cfg)

        elif node.node_type == IRNodeType.LOOP:
            # Handle loops
            loop_block_id = cfg.block_counter
            loop_block = BasicBlock(f"loop_block_{loop_block_id}")
            cfg.block_counter += 1

            after_loop_block_id = cfg.block_counter
            after_loop_block = BasicBlock(f"after_loop_block_{after_loop_block_id}")
            cfg.block_counter += 1

            # Add blocks to CFG
            cfg.blocks[loop_block.name] = loop_block
            cfg.blocks[after_loop_block.name] = after_loop_block

            # Connect current block to loop block
            current_block.add_successor(loop_block)

            # Process loop condition if present
            condition = node.attributes.get("condition")
            if condition:
                loop_block.add_statement(condition)

            # Process loop body
            loop_body = node.children
            new_loop_block = self._process_node_list(loop_body, loop_block, cfg)

            # Loop back to the loop block
            new_loop_block.add_successor(loop_block)

            # Exit loop to after_loop_block
            loop_block.add_successor(after_loop_block)

            # Continue from after_loop_block
            current_block = after_loop_block

        else:
            # Process normal statements
            current_block.add_statement(node)
            current_block = self._process_node_list(node.children, current_block, cfg)

        return current_block

    def _process_node_list(self, nodes: List[IRNode], current_block: BasicBlock, cfg: ControlFlowGraph) -> BasicBlock:
        """Process a list of IR nodes and update the current block."""
        for node in nodes:
            current_block = self._process_node(node, current_block, cfg)
        return current_block
