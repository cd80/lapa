"""
Data Flow Analysis module.

This module provides functionality to perform data flow analysis on the IR.
"""

from typing import Dict, Set, Tuple, List, Optional, Any
from lapa.ir import IR, IRNode, IRNodeType
from lapa.analysis.control_flow import ControlFlowAnalyzer, ControlFlowGraph, BasicBlock

Definition = Tuple[str, IRNode]  # (variable name, assignment node)


class DataFlowAnalyzer:
    """Performs data flow analysis on the IR, including reaching definitions and live variable analysis."""

    def __init__(self):
        """Initialize the data flow analyzer."""
        self.reaching_definitions: Dict[str, Dict[str, Any]] = {}
        self.live_variables: Dict[str, Dict[str, Any]] = {}
        self.phi_nodes: Dict[str, Dict[str, List[IRNode]]] = {}
        self.array_defs: Dict[str, Dict[str, Set[Definition]]] = {}
        self.interprocedural_defs: Dict[str, Dict[str, Set[Definition]]] = {}

    def analyze(self, ir: IR, cfgs: Dict[str, ControlFlowGraph]) -> None:
        """
        Perform data flow analysis on the given IR.

        Args:
            ir: The intermediate representation to analyze.
            cfgs: The control flow graphs generated from the IR.
        """
        # First pass: Analyze function definitions
        function_defs = self._collect_function_definitions(ir)
        
        # Second pass: Analyze each function independently
        for function_name, cfg in cfgs.items():
            self._analyze_reaching_definitions(function_name, cfg)
            self._analyze_live_variables(function_name, cfg)
            self._analyze_array_accesses(function_name, cfg)
            self._insert_phi_nodes(function_name, cfg)

        # Third pass: Interprocedural analysis
        self._analyze_interprocedural_flow(ir, cfgs, function_defs)

    def _collect_function_definitions(self, ir: IR) -> Dict[str, IRNode]:
        """Collect all function definitions from the IR."""
        function_defs = {}

        def collect_functions(node: IRNode):
            if node.node_type in {IRNodeType.FUNCTION_DEF, IRNodeType.FUNCTION}:
                if node.name:
                    function_defs[node.name] = node
            for child in node.children:
                collect_functions(child)

        collect_functions(ir.root)
        return function_defs

    def _analyze_reaching_definitions(self, function_name: str, cfg: ControlFlowGraph) -> None:
        """Perform reaching definitions analysis on a single function's CFG."""
        in_sets: Dict[str, Set[Definition]] = {}
        out_sets: Dict[str, Set[Definition]] = {}
        gen_sets: Dict[str, Set[Definition]] = {}
        kill_sets: Dict[str, Set[Definition]] = {}

        # Initialize gen and kill sets for each block
        all_defs = self._get_all_definitions(cfg)
        for block_name, block in cfg.blocks.items():
            gen_sets[block_name] = self._compute_gen_set(block)
            kill_sets[block_name] = self._compute_kill_set(block, gen_sets[block_name], all_defs)

        # Initialize in and out sets to empty sets
        for block_name in cfg.blocks.keys():
            in_sets[block_name] = set()
            out_sets[block_name] = set()

        changed = True
        while changed:
            changed = False
            for block_name, block in cfg.blocks.items():
                # Compute in[B] as the union of out sets of predecessors
                in_b = set()
                for pred in block.predecessors:
                    in_b.update(out_sets[pred.name])

                # Compute out[B] = gen[B] ∪ (in[B] - kill[B])
                old_out = out_sets[block_name]
                out_b = gen_sets[block_name].union(in_b - kill_sets[block_name])

                if out_b != old_out:
                    out_sets[block_name] = out_b
                    changed = True
                in_sets[block_name] = in_b

        # Store the results for the function
        self.reaching_definitions[function_name] = {
            'in_sets': in_sets,
            'out_sets': out_sets,
        }

    def _analyze_live_variables(self, function_name: str, cfg: ControlFlowGraph) -> None:
        """Perform live variable analysis on a single function's CFG."""
        in_sets: Dict[str, Set[str]] = {}
        out_sets: Dict[str, Set[str]] = {}
        use_sets: Dict[str, Set[str]] = {}
        def_sets: Dict[str, Set[str]] = {}

        # Initialize use and def sets for each block
        for block_name, block in cfg.blocks.items():
            use_sets[block_name], def_sets[block_name] = self._compute_use_def_sets(block)

        # Initialize in and out sets to empty sets
        for block_name in cfg.blocks.keys():
            in_sets[block_name] = set()
            out_sets[block_name] = set()

        changed = True
        while changed:
            changed = False
            # Process blocks in reverse order
            for block_name, block in reversed(list(cfg.blocks.items())):
                old_in = in_sets[block_name].copy()
                old_out = out_sets[block_name].copy()

                # Compute out[B] as the union of in sets of successors
                out_b = set()
                for succ in block.successors:
                    out_b.update(in_sets[succ.name])

                # Compute in[B] = use[B] ∪ (out[B] - def[B])
                in_b = use_sets[block_name].union(out_b - def_sets[block_name])

                in_sets[block_name] = in_b
                out_sets[block_name] = out_b

                if in_b != old_in or out_b != old_out:
                    changed = True

        # Store the results for the function
        self.live_variables[function_name] = {
            'in_sets': in_sets,
            'out_sets': out_sets,
        }

    def _analyze_array_accesses(self, function_name: str, cfg: ControlFlowGraph) -> None:
        """Analyze array and collection access patterns."""
        array_defs: Dict[str, Set[Definition]] = {}

        for block in cfg.blocks.values():
            for node in block.statements:
                if node.node_type == IRNodeType.ASSIGNMENT:
                    target = node.attributes.get('target')
                    if target and self._is_array_access(node):
                        array_name = self._get_array_name(node)
                        if array_name:
                            array_defs.setdefault(array_name, set()).add((target, node))

        self.array_defs[function_name] = array_defs

    def _analyze_interprocedural_flow(self, ir: IR, cfgs: Dict[str, ControlFlowGraph], function_defs: Dict[str, IRNode]) -> None:
        """Perform interprocedural data flow analysis."""
        # First, collect all function parameters
        function_params: Dict[str, List[str]] = {}
        for func_name, func_node in function_defs.items():
            params = []
            if 'parameters' in func_node.attributes:
                for param in func_node.attributes['parameters']:
                    if isinstance(param, IRNode) and param.node_type == IRNodeType.VARIABLE:
                        params.append(param.name)
                    elif isinstance(param, str):
                        params.append(param)
            function_params[func_name] = params

        # Then analyze function calls and map arguments to parameters
        for function_name, cfg in cfgs.items():
            for block in cfg.blocks.values():
                for node in block.statements:
                    if node.node_type == IRNodeType.FUNCTION_CALL:
                        called_func = node.attributes.get('function')
                        if isinstance(called_func, IRNode):
                            called_name = called_func.name
                            if called_name in function_params:
                                args = node.attributes.get('arguments', [])
                                params = function_params[called_name]
                                interprocedural_defs = self.interprocedural_defs.setdefault(called_name, {})
                                for param, arg in zip(params, args):
                                    if isinstance(arg, IRNode):
                                        interprocedural_defs.setdefault(param, set()).add(
                                            (arg.name, node)
                                        )
                                    else:
                                        interprocedural_defs.setdefault(param, set()).add(
                                            (str(arg), node)
                                        )

    def _insert_phi_nodes(self, function_name: str, cfg: ControlFlowGraph) -> None:
        """Insert phi nodes for SSA form."""
        phi_nodes: Dict[str, List[IRNode]] = {}

        # Find join points that need phi nodes
        for block_name, block in cfg.blocks.items():
            # A block is a join point if:
            # 1. It's marked as a join point by the control flow analyzer, or
            # 2. It has multiple predecessors
            is_join_point = getattr(block, 'is_join_point', False) or len(block.predecessors) > 1

            if is_join_point:
                # Get variables that have different definitions in predecessor blocks
                vars_needing_phi = self._find_vars_needing_phi(block, cfg, function_name)

                # Create phi nodes
                block_phi_nodes = []
                for var in vars_needing_phi:
                    # Get reaching definitions from each predecessor
                    pred_defs = {}
                    for pred in block.predecessors:
                        defs = self._get_reaching_defs_for_var(var, pred.name, function_name)
                        if defs:
                            pred_defs[pred.name] = defs
                    # Only create phi node if we have reaching definitions from predecessors
                    if pred_defs:
                        phi_node = IRNode(
                            node_type=IRNodeType.PHI,
                            attributes={
                                'target': var,
                                'sources': pred_defs
                            }
                        )
                        block_phi_nodes.append(phi_node)

                if block_phi_nodes:
                    # Add phi nodes to the block's statements at the beginning
                    block.statements = block_phi_nodes + block.statements
                    # Store phi nodes for this block using block name as key
                    phi_nodes[block_name] = block_phi_nodes

        # Store the phi nodes for the function
        self.phi_nodes[function_name] = phi_nodes

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
            elif node.node_type == IRNodeType.PHI:
                var_name = node.attributes.get('target')
                sources = node.attributes.get('sources', {})
                for src_defs in sources.values():
                    for var, _ in src_defs:
                        if var not in def_set:
                            use_set.add(var)
                if var_name:
                    def_set.add(var_name)
            elif node.node_type == IRNodeType.LOOP:
                # Handle loop variables
                condition = node.attributes.get('condition')
                if condition:
                    loop_vars = self._extract_variables(condition)
                    use_set.update(loop_vars)
            else:
                vars_used = self._extract_variables(node)
                for var in vars_used:
                    if var not in def_set:
                        use_set.add(var)
        return use_set, def_set

    def _extract_variables(self, node: Optional[IRNode]) -> Set[str]:
        """Recursively extract variable names used in a node."""
        vars_found = set()
        if node is None:
            return vars_found
        if node.node_type == IRNodeType.VARIABLE:
            var_name = node.attributes.get('name')
            if var_name:
                vars_found.add(var_name)
        elif node.node_type in {IRNodeType.BINARY_OP, IRNodeType.UNARY_OP}:
            operands = node.attributes.get('operands', [])
            for operand in operands:
                if isinstance(operand, IRNode):
                    vars_found.update(self._extract_variables(operand))
            # Handle specific left and right operands if present
            left = node.attributes.get('left_operand')
            right = node.attributes.get('right_operand')
            if isinstance(left, IRNode):
                vars_found.update(self._extract_variables(left))
            if isinstance(right, IRNode):
                vars_found.update(self._extract_variables(right))
        elif node.node_type == IRNodeType.FUNCTION_CALL:
            args = node.attributes.get('arguments', [])
            for arg in args:
                if isinstance(arg, IRNode):
                    vars_found.update(self._extract_variables(arg))
        elif node.node_type == IRNodeType.ARRAY_ACCESS:
            array = node.attributes.get('array')
            index = node.attributes.get('index')
            if isinstance(array, IRNode):
                vars_found.update(self._extract_variables(array))
            if isinstance(index, IRNode):
                vars_found.update(self._extract_variables(index))
        # Process child nodes
        for child in node.children:
            vars_found.update(self._extract_variables(child))
        return vars_found

    def _compute_gen_set(self, block: BasicBlock) -> Set[Definition]:
        """Compute the gen set for a basic block."""
        gen_set = set()
        for node in block.statements:
            if node.node_type in {IRNodeType.ASSIGNMENT, IRNodeType.PHI}:
                var_name = node.attributes.get('target')
                if var_name:
                    gen_set.add((var_name, node))
            elif node.node_type == IRNodeType.LOOP:
                # Handle loop variables
                body = node.attributes.get('body')
                if isinstance(body, IRNode):
                    for child in body.children:
                        if child.node_type == IRNodeType.ASSIGNMENT:
                            var_name = child.attributes.get('target')
                            if var_name:
                                gen_set.add((var_name, child))
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
            # Remove all other definitions of the variable
            kill_set.update(all_defs.get(var, set()) - {d for d in gen_set if d[0] == var})
        return kill_set

    def _get_all_definitions(self, cfg: ControlFlowGraph) -> Dict[str, Set[Definition]]:
        """Get all definitions in the CFG."""
        all_defs: Dict[str, Set[Definition]] = {}
        for block in cfg.blocks.values():
            for node in block.statements:
                if node.node_type in {IRNodeType.ASSIGNMENT, IRNodeType.PHI}:
                    var_name = node.attributes.get('target')
                    if var_name:
                        definition = (var_name, node)
                        all_defs.setdefault(var_name, set()).add(definition)
                elif node.node_type == IRNodeType.LOOP:
                    # Handle loop variables
                    body = node.attributes.get('body')
                    if isinstance(body, IRNode):
                        for child in body.children:
                            if child.node_type == IRNodeType.ASSIGNMENT:
                                var_name = child.attributes.get('target')
                                if var_name:
                                    definition = (var_name, child)
                                    all_defs.setdefault(var_name, set()).add(definition)
        return all_defs

    def _is_array_access(self, node: IRNode) -> bool:
        """Check if a node represents an array access."""
        if node.node_type == IRNodeType.ARRAY_ACCESS:
            return True
        if node.node_type == IRNodeType.ASSIGNMENT:
            value = node.attributes.get('value')
            if isinstance(value, IRNode):
                return self._is_array_access(value)
        return False

    def _get_array_name(self, node: IRNode) -> Optional[str]:
        """Extract the array name from an array access node."""
        if node.node_type == IRNodeType.ARRAY_ACCESS:
            array = node.attributes.get('array')
            if isinstance(array, IRNode) and array.node_type == IRNodeType.VARIABLE:
                return array.attributes.get('name')
            else:
                return self._get_array_name(array)
        elif node.node_type == IRNodeType.ASSIGNMENT:
            value = node.attributes.get('value')
            if isinstance(value, IRNode):
                return self._get_array_name(value)
        return None

    def _find_vars_needing_phi(self, block: BasicBlock, cfg: ControlFlowGraph, function_name: str) -> Set[str]:
        """Find variables that need phi nodes at a join point."""
        vars_needing_phi = set()

        # Get reaching definitions at the start of the block
        rd = self.reaching_definitions.get(function_name, {})
        in_sets = rd.get('in_sets', {})
        block_in_defs = in_sets.get(block.name, set())

        # For each variable, check if it has multiple definitions from predecessors
        var_pred_defs: Dict[str, Set[IRNode]] = {}
        for pred in block.predecessors:
            pred_out_defs = self.reaching_definitions[function_name]['out_sets'].get(pred.name, set())
            for var, node in pred_out_defs:
                var_pred_defs.setdefault(var, set()).add(node)

        # Variables that have multiple different definitions from predecessors need phi nodes
        for var, defs in var_pred_defs.items():
            if len(defs) > 1:
                vars_needing_phi.add(var)

        return vars_needing_phi

    def _get_reaching_defs_for_var(self, var: str, block_name: str, function_name: str) -> Set[Definition]:
        """Get reaching definitions for a variable at the end of a block."""
        rd = self.reaching_definitions.get(function_name, {})
        out_sets = rd.get('out_sets', {})
        return {d for d in out_sets.get(block_name, set()) if d[0] == var}
