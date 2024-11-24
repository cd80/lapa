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
            function_name = function_node.attributes.get("name", "anonymous")
            self.cfgs[function_name] = cfg

    def _get_function_nodes(self, node: IRNode) -> List[IRNode]:
        """Recursively gather all function nodes in the IR."""
        function_nodes = []
        if node.node_type == IRNodeType.FUNCTION_DEF:
            function_nodes.append(node)
        for child in node.children:
            function_nodes.extend(self._get_function_nodes(child))
        return function_nodes

    def _build_cfg(self, function_node: IRNode) -> ControlFlowGraph:
        """Build a control flow graph for a given function node."""
        function_name = function_node.attributes.get("name", "anonymous")
        cfg = ControlFlowGraph(function_name)
        current_block = cfg.entry_block

        body = function_node.attributes.get("body")
        if body:
            current_block = self._process_node_list(body.children, current_block, cfg)
        current_block.add_successor(cfg.exit_block)

        return cfg

    def _process_node(self, node: IRNode, current_block: BasicBlock, cfg: ControlFlowGraph) -> BasicBlock:
        """Process an IR node and update the CFG accordingly."""
        if node.node_type == IRNodeType.CONDITIONAL:
            # Handle conditionals (if-else)
            condition = node.attributes.get("condition")

            # Create blocks
            block_id = cfg.block_counter
            if_block = BasicBlock(f"if_block_{block_id}")
            cfg.block_counter += 1
            else_block = BasicBlock(f"else_block_{cfg.block_counter}")
            cfg.block_counter += 1
            end_block = BasicBlock(f"end_if_block_{cfg.block_counter}")
            cfg.block_counter += 1

            # Add blocks to CFG
            cfg.blocks[if_block.name] = if_block
            cfg.blocks[else_block.name] = else_block
            cfg.blocks[end_block.name] = end_block

            # Connect current block to condition evaluation
            current_block.add_statement(condition)
            current_block.add_successor(if_block)
            current_block.add_successor(else_block)

            # Process the 'true' branch
            true_branch = node.attributes.get("true_branch")
            if true_branch:
                new_block_if = self._process_node_list(true_branch.children, if_block, cfg)
                new_block_if.add_successor(end_block)
            else:
                if_block.add_successor(end_block)

            # Process the 'false' branch
            false_branch = node.attributes.get("false_branch")
            if false_branch:
                new_block_else = self._process_node_list(false_branch.children, else_block, cfg)
                new_block_else.add_successor(end_block)
            else:
                else_block.add_successor(end_block)

            # Continue from the end block
            current_block = end_block

        elif node.node_type == IRNodeType.LOOP:
            # Handle loops
            block_id = cfg.block_counter
            loop_condition_block = BasicBlock(f"loop_condition_block_{block_id}")
            cfg.block_counter += 1
            loop_body_block = BasicBlock(f"loop_body_block_{cfg.block_counter}")
            cfg.block_counter += 1
            loop_end_block = BasicBlock(f"loop_end_block_{cfg.block_counter}")
            cfg.block_counter += 1

            # Add blocks to CFG
            cfg.blocks[loop_condition_block.name] = loop_condition_block
            cfg.blocks[loop_body_block.name] = loop_body_block
            cfg.blocks[loop_end_block.name] = loop_end_block

            # Connect current block to loop condition
            current_block.add_successor(loop_condition_block)

            # Process loop condition
            condition = node.attributes.get("condition")
            loop_condition_block.add_statement(condition)
            loop_condition_block.add_successor(loop_body_block)
            loop_condition_block.add_successor(loop_end_block)

            # Process loop body
            body = node.attributes.get("body")
            if body:
                new_loop_body_block = self._process_node_list(body.children, loop_body_block, cfg)
                new_loop_body_block.add_successor(loop_condition_block)
            else:
                loop_body_block.add_successor(loop_condition_block)

            # Continue from loop end block
            current_block = loop_end_block

        elif node.node_type == IRNodeType.TRY_EXCEPT:
            # Handle try-except-finally blocks
            block_id = cfg.block_counter
            try_block = BasicBlock(f"try_block_{block_id}")
            cfg.block_counter += 1
            end_try_block = BasicBlock(f"end_try_block_{cfg.block_counter}")
            cfg.block_counter += 1

            # Add blocks to CFG
            cfg.blocks[try_block.name] = try_block
            cfg.blocks[end_try_block.name] = end_try_block

            # Connect current block to try block
            current_block.add_successor(try_block)

            # Process try block
            try_body = node.attributes.get("try_body")
            if try_body:
                new_try_block = self._process_node_list(try_body.children, try_block, cfg)
            else:
                new_try_block = try_block
            new_try_block.add_successor(end_try_block)

            # Process except blocks
            except_blocks = node.attributes.get("except_blocks", [])
            except_end_blocks = []
            for except_node in except_blocks:
                except_block_id = cfg.block_counter
                except_block = BasicBlock(f"except_block_{except_block_id}")
                cfg.block_counter += 1
                cfg.blocks[except_block.name] = except_block

                # Connect from try block to except block
                try_block.add_successor(except_block)

                # Process except block
                except_body = except_node.attributes.get("body")
                if except_body:
                    new_except_block = self._process_node_list(except_body.children, except_block, cfg)
                else:
                    new_except_block = except_block

                # Connect except block to end_try_block
                new_except_block.add_successor(end_try_block)
                except_end_blocks.append(new_except_block)

            # Process finally block if present
            finally_body = node.attributes.get("finally_body")
            if finally_body:
                finally_block = BasicBlock(f"finally_block_{cfg.block_counter}")
                cfg.block_counter += 1
                cfg.blocks[finally_block.name] = finally_block

                # Connect end_try_block to finally_block
                end_try_block.add_successor(finally_block)

                # Process finally block
                new_finally_block = self._process_node_list(finally_body.children, finally_block, cfg)
                current_block = new_finally_block
            else:
                current_block = end_try_block

        else:
            # Process normal statements
            current_block.add_statement(node)
            for child in node.children:
                current_block = self._process_node(child, current_block, cfg)

        return current_block

    def _process_node_list(self, nodes: List[IRNode], current_block: BasicBlock, cfg: ControlFlowGraph) -> BasicBlock:
        """Process a list of IR nodes and update the current block."""
        for node in nodes:
            current_block = self._process_node(node, current_block, cfg)
        return current_block
