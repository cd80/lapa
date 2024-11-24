"""
Data Flow Analysis module.

This module provides functionality to perform data flow analysis on the IR.
"""

from typing import Dict, Set, Tuple, Any
from lapa.ir import IR, IRNode, IRNodeType
from lapa.analysis.control_flow import ControlFlowAnalyzer, ControlFlowGraph, BasicBlock

Definition = Tuple[str, IRNode]  # (variable name, assignment node)

class DataFlowAnalyzer:
    """Performs data flow analysis on the IR."""

    def __init__(self):
        """Initialize the data flow analyzer."""
        self.reaching_definitions: Dict[str, Dict[str, Dict[BasicBlock, Set[Definition]]]] = {}

    def analyze(self, ir: IR, cfgs: Dict[str, ControlFlowGraph]) -> None:
        """
        Perform data flow analysis on the given IR.

        Args:
            ir: The intermediate representation to analyze.
            cfgs: The control flow graphs generated from the IR.
        """
        for function_name, cfg in cfgs.items():
            self._analyze_function(function_name, cfg)

    def _analyze_function(self, function_name: str, cfg: ControlFlowGraph) -> None:
        """Perform data flow analysis on a single function's CFG."""
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
                predecessors = self._get_predecessors(cfg, block)
                for pred in predecessors:
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

    def _get_predecessors(self, cfg: ControlFlowGraph, block: BasicBlock) -> Set[BasicBlock]:
        """Get predecessors of a block in the CFG."""
        predecessors = set()
        for potential_pred in cfg.blocks.values():
            if block in potential_pred.successors:
                predecessors.add(potential_pred)
        return predecessors
