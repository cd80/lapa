"""
Control Flow Analysis module.

This module provides functionality to build a control flow graph (CFG) from the IR, including handling of exception constructs.
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
        self.is_join_point = False  # Flag to mark join points

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
        cfg = ControlFlowGraph(function_node.name or "anonymous")
        current_block = cfg.entry_block

        # Process the function body
        current_block = self._process_node_list(function_node.children, current_block, cfg)
        current_block.add_successor(cfg.exit_block)

        return cfg

    def _process_node_list(
        self, nodes: List[IRNode], current_block: BasicBlock, cfg: ControlFlowGraph
    ) -> BasicBlock:
        """Process a list of IR nodes and update the current block."""
        i = 0
        while i < len(nodes):
            node = nodes[i]

            if node.node_type == IRNodeType.CONTROL_FLOW:
                control_type = node.attributes.get("type")
                if control_type == "if":
                    # Check for a following 'else' node
                    if (
                        i + 1 < len(nodes)
                        and nodes[i + 1].node_type == IRNodeType.CONTROL_FLOW
                        and nodes[i + 1].attributes.get("type") == "else"
                    ):
                        else_node = nodes[i + 1]
                        current_block = self._process_if_else_node(
                            node, else_node, current_block, cfg
                        )
                        i += 2  # Skip both 'if' and 'else' nodes
                    else:
                        current_block = self._process_if_node(node, current_block, cfg)
                        i += 1
                elif control_type == "try":
                    current_block = self._process_try_except_node(node, current_block, cfg)
                    i += 1
                else:
                    # Unknown CONTROL_FLOW type; process as normal
                    current_block.add_statement(node)
                    i += 1
            elif node.node_type == IRNodeType.LOOP:
                current_block = self._process_loop_node(node, current_block, cfg)
                i += 1
            else:
                current_block.add_statement(node)
                i += 1
        return current_block

    def _process_if_node(
        self, if_node: IRNode, current_block: BasicBlock, cfg: ControlFlowGraph
    ) -> BasicBlock:
        """Process an 'if' node without an 'else'."""
        # Process condition
        condition = if_node.attributes.get("condition")
        if condition:
            current_block.add_statement(condition)

        # Create if block
        if_block_name = f"if_block_{cfg.block_counter}"
        cfg.block_counter += 1
        if_block = BasicBlock(if_block_name)
        cfg.blocks[if_block_name] = if_block

        # Create end block
        end_block_name = f"end_block_{cfg.block_counter}"
        cfg.block_counter += 1
        end_block = BasicBlock(end_block_name)
        end_block.is_join_point = True
        cfg.blocks[end_block_name] = end_block

        # Connect blocks
        current_block.add_successor(if_block)      # True branch
        current_block.add_successor(end_block)     # False branch
        # Process 'if' block
        new_if_block = self._process_node_list(if_node.children, if_block, cfg)
        new_if_block.add_successor(end_block)

        # Continue from end block
        return end_block

    def _process_if_else_node(
        self, if_node: IRNode, else_node: IRNode, current_block: BasicBlock, cfg: ControlFlowGraph
    ) -> BasicBlock:
        """Process an 'if' node followed by an 'else' node."""
        # Process condition
        condition = if_node.attributes.get("condition")
        if condition:
            current_block.add_statement(condition)

        # Create if block
        if_block_name = f"if_block_{cfg.block_counter}"
        cfg.block_counter += 1
        if_block = BasicBlock(if_block_name)
        cfg.blocks[if_block_name] = if_block

        # Create else block
        else_block_name = f"else_block_{cfg.block_counter}"
        cfg.block_counter += 1
        else_block = BasicBlock(else_block_name)
        cfg.blocks[else_block_name] = else_block

        # Create end block
        end_block_name = f"end_block_{cfg.block_counter}"
        cfg.block_counter += 1
        end_block = BasicBlock(end_block_name)
        end_block.is_join_point = True
        cfg.blocks[end_block_name] = end_block

        # Connect current block to if and else blocks
        current_block.add_successor(if_block)
        current_block.add_successor(else_block)

        # Process 'if' block
        new_if_block = self._process_node_list(if_node.children, if_block, cfg)
        new_if_block.add_successor(end_block)

        # Process 'else' block
        new_else_block = self._process_node_list(else_node.children, else_block, cfg)
        new_else_block.add_successor(end_block)

        # Continue from end block
        return end_block

    def _process_loop_node(
        self, loop_node: IRNode, current_block: BasicBlock, cfg: ControlFlowGraph
    ) -> BasicBlock:
        """Process a loop node."""
        # Process condition if present
        condition = loop_node.attributes.get("condition")
        if condition:
            current_block.add_statement(condition)

        # Create loop header block
        loop_header_name = f"loop_block_{cfg.block_counter}"
        cfg.block_counter += 1
        loop_header = BasicBlock(loop_header_name)
        cfg.blocks[loop_header_name] = loop_header

        # Create after loop block
        after_loop_block_name = f"after_loop_block_{cfg.block_counter}"
        cfg.block_counter += 1
        after_loop_block = BasicBlock(after_loop_block_name)
        after_loop_block.is_join_point = True
        cfg.blocks[after_loop_block_name] = after_loop_block

        # Connect current block to loop header
        current_block.add_successor(loop_header)

        # Loop header decision
        loop_header.add_successor(after_loop_block)  # False branch exits loop

        # Process loop body
        new_loop_block = self._process_node_list(loop_node.children, loop_header, cfg)

        # Loop back to loop header
        new_loop_block.add_successor(loop_header)

        # Continue from after loop block
        return after_loop_block

    def _process_try_except_node(
        self, try_node: IRNode, current_block: BasicBlock, cfg: ControlFlowGraph
    ) -> BasicBlock:
        """Process a 'try-except-finally' node."""
        # Create try block
        try_block_name = f"try_block_{cfg.block_counter}"
        cfg.block_counter += 1
        try_block = BasicBlock(try_block_name)
        cfg.blocks[try_block_name] = try_block

        # Create end block
        end_block_name = f"end_block_{cfg.block_counter}"
        cfg.block_counter += 1
        end_block = BasicBlock(end_block_name)
        end_block.is_join_point = True
        cfg.blocks[end_block_name] = end_block

        # Connect current block to try block
        current_block.add_successor(try_block)

        # Process try block
        new_try_block = self._process_node_list(try_node.children, try_block, cfg)

        # Collect 'except' and 'finally' nodes
        except_nodes = [child for child in try_node.children if child.attributes.get("type") == "except"]
        finally_node = next((child for child in try_node.children if child.attributes.get("type") == "finally"), None)

        # Process 'except' blocks
        prev_except_blocks = []
        for except_node in except_nodes:
            except_block_name = f"except_block_{cfg.block_counter}"
            cfg.block_counter += 1
            except_block = BasicBlock(except_block_name)
            cfg.blocks[except_block_name] = except_block

            # Connect try block to except block
            try_block.add_successor(except_block)

            # Process except block
            new_except_block = self._process_node_list(except_node.children, except_block, cfg)
            prev_except_blocks.append(new_except_block)

        # If there are no except blocks, assume exceptions propagate
        if not except_nodes:
            # Exceptions propagate; connect try block to end block
            try_block.add_successor(end_block)

        # Process 'finally' block if present
        if finally_node:
            finally_block_name = f"finally_block_{cfg.block_counter}"
            cfg.block_counter += 1
            finally_block = BasicBlock(finally_block_name)
            cfg.blocks[finally_block_name] = finally_block

            # Process finally block
            new_finally_block = self._process_node_list(finally_node.children, finally_block, cfg)

            # Connect try block and except blocks to finally block
            new_try_block.add_successor(finally_block)
            for except_block in prev_except_blocks:
                except_block.add_successor(finally_block)

            # Connect finally block to end block
            new_finally_block.add_successor(end_block)
        else:
            # No finally block; connect try and except blocks directly to end block
            new_try_block.add_successor(end_block)
            for except_block in prev_except_blocks:
                except_block.add_successor(end_block)

        # Continue from end block
        return end_block
