"""
Data Flow Analysis module.

This module provides functionality to perform data flow analysis on the IR.
"""

from typing import Dict, Set, Tuple, Any
from lapa.ir import IR, IRNode, IRNodeType
from lapa.analysis.control_flow import ControlFlowAnalyzer, ControlFlowGraph, BasicBlock

Definition = Tuple[str, IRNode]  # (variable name, assignment node)


class DataFlowAnalyzer:
    """Performs data flow analysis on the IR, including reaching definitions and live variable analysis."""

    def __init__(self):
        """Initialize the data flow analyzer."""
        self.reaching_definitions: Dict[str, Dict[str, Any]] = {}
        self.live_variables: Dict[str, Dict[str, Any]] = {}

    def analyze(self, ir: IR, cfgs: Dict[str, ControlFlowGraph]) -> None:
        """
        Perform data flow analysis on the given IR.

        Args:
            ir: The intermediate representation to analyze.
            cfgs: The control flow graphs generated from the IR.
        """
        for function_name, cfg in cfgs.items():
            self._analyze_reaching_definitions(function_name, cfg)
            self._analyze_live_variables(function_name, cfg)

    def _analyze_reaching_definitions(self, function_name: str, cfg: ControlFlowGraph) -> None:
        """Perform reaching definitions analysis on a single function's CFG."""
        in_sets: Dict[BasicBlock, Set[Definition]] = {}
        out_sets: Dict[BasicBlock, Set[Definition]] = {}
        gen_sets: Dict[BasicBlock, Set[Definition]] = {}
        kill_sets: Dict[BasicBlock, Set[Definition]] = {}

        # Initialize gen and kill sets for each block
        all_defs = self._get_all_definitions(cfg)
        for block in cfg.blocks.values():
            gen_sets[block] = self._compute_gen_set(block)
            kill_sets[block] = self._compute_kill_set(block, gen_sets[block], all_defs)

        # Initialize in and out sets to empty sets
        for block in cfg.blocks.values():
            in_sets[block] = set()
            out_sets[block] = set()

        changed = True
        while changed:
            changed = False
            for block in cfg.blocks.values():
                # Compute in[B] as the union of out sets of predecessors
                in_b = set()
                for pred in block.predecessors:
                    in_b.update(out_sets[pred])

                # Compute out[B] = gen[B] ∪ (in[B] - kill[B])
                old_out = out_sets[block]
                out_b = gen_sets[block].union(in_b - kill_sets[block])

                if out_b != old_out:
                    out_sets[block] = out_b
                    changed = True
                in_sets[block] = in_b

        # Store the results for the function
        self.reaching_definitions[function_name] = {
            'in_sets': in_sets,
            'out_sets': out_sets,
        }

    def _analyze_live_variables(self, function_name: str, cfg: ControlFlowGraph) -> None:
        """Perform live variable analysis on a single function's CFG."""
        in_sets: Dict[BasicBlock, Set[str]] = {}
        out_sets: Dict[BasicBlock, Set[str]] = {}
        use_sets: Dict[BasicBlock, Set[str]] = {}
        def_sets: Dict[BasicBlock, Set[str]] = {}

        # Initialize use and def sets for each block
        for block in cfg.blocks.values():
            use_sets[block], def_sets[block] = self._compute_use_def_sets(block)

        # Initialize in and out sets to empty sets
        for block in cfg.blocks.values():
            in_sets[block] = set()
            out_sets[block] = set()

        changed = True
        while changed:
            changed = False
            # Process blocks in reverse order
            for block in reversed(list(cfg.blocks.values())):
                old_in = in_sets[block].copy()
                old_out = out_sets[block].copy()

                # Compute out[B] as the union of in sets of successors
                out_b = set()
                for succ in block.successors:
                    out_b.update(in_sets[succ])

                # Compute in[B] = use[B] ∪ (out[B] - def[B])
                in_b = use_sets[block].union(out_b - def_sets[block])

                in_sets[block] = in_b
                out_sets[block] = out_b

                if in_b != old_in or out_b != old_out:
                    changed = True

        # Store the results for the function
        self.live_variables[function_name] = {
            'in_sets': in_sets,
            'out_sets': out_sets,
        }

    def _compute_use_def_sets(self, block: BasicBlock) -> Tuple[Set[str], Set[str]]:
        """Compute the use and def sets for a basic block."""
        use_set = set()
        def_set = set()
        for node in block.statements:
            if node.node_type == IRNodeType.ASSIGNMENT:
                var_name = node.attributes.get('target')
                rhs_vars = self._extract_variables(node.attributes.get('value'))
                # Variables used in RHS that are not yet defined are added to use set
                for var in rhs_vars:
                    if var not in def_set:
                        use_set.add(var)
                # Variable assigned to is added to def set
                if var_name:
                    def_set.add(var_name)
            else:
                vars_used = self._extract_variables(node)
                for var in vars_used:
                    if var not in def_set:
                        use_set.add(var)
        return use_set, def_set

    def _extract_variables(self, node: IRNode) -> Set[str]:
        """Recursively extract variable names used in a node."""
        vars_found = set()
        if node is None:
            return vars_found
        if node.node_type == IRNodeType.VARIABLE:
            var_name = node.attributes.get('name')
            if var_name:
                vars_found.add(var_name)
        elif node.node_type == IRNodeType.BINARY_OPERATION:
            left = node.attributes.get('left_operand')
            right = node.attributes.get('right_operand')
            vars_found.update(self._extract_variables(left))
            vars_found.update(self._extract_variables(right))
        elif node.node_type == IRNodeType.FUNCTION_CALL:
            args = node.attributes.get('arguments', [])
            for arg in args:
                vars_found.update(self._extract_variables(arg))
        # Process child nodes
        for child in node.children:
            vars_found.update(self._extract_variables(child))
        return vars_found

    def _compute_gen_set(self, block: BasicBlock) -> Set[Definition]:
        """Compute the gen set for a basic block."""
        gen_set = set()
        for node in block.statements:
            if node.node_type == IRNodeType.ASSIGNMENT:
                var_name = node.attributes.get('target')
                if var_name:
                    gen_set.add((var_name, node))
        return gen_set

    def _compute_kill_set(
        self,
        block: BasicBlock,
        gen_set: Set[Definition],
        all_defs: Dict[str, Set[Definition]],
    ) -> Set[Definition]:
        """Compute the kill set for a basic block."""
        kill_set = set()
        gen_vars = {var for var, _ in gen_set}
        for var in gen_vars:
            # Correctly compute the kill set by removing all definitions of the variable
            # that are not the current definition in the gen set.
            kill_set.update(all_defs[var] - {d for d in gen_set if d[0] == var})
        return kill_set

    def _get_all_definitions(self, cfg: ControlFlowGraph) -> Dict[str, Set[Definition]]:
        """Get all definitions in the CFG."""
        all_defs: Dict[str, Set[Definition]] = {}
        for block in cfg.blocks.values():
            for node in block.statements:
                if node.node_type == IRNodeType.ASSIGNMENT:
                    var_name = node.attributes.get('target')
                    if var_name:
                        definition = (var_name, node)
                        all_defs.setdefault(var_name, set()).add(definition)
        return all_defs
