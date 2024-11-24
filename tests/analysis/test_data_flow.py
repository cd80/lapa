"""
Unit tests for the DataFlowAnalyzer.
"""

import unittest
from lapa.ir import IR, IRNode, IRNodeType
from lapa.analysis.control_flow import ControlFlowAnalyzer
from lapa.analysis.data_flow import DataFlowAnalyzer

class TestDataFlowAnalyzer(unittest.TestCase):
    def setUp(self):
        self.control_flow_analyzer = ControlFlowAnalyzer()
        self.data_flow_analyzer = DataFlowAnalyzer()
        self.ir = IR()

    def test_analyze_empty_ir(self):
        """Test analyzing an empty IR."""
        try:
            # Generate CFGs for the empty IR
            self.control_flow_analyzer.analyze(self.ir)
            cfgs = self.control_flow_analyzer.cfgs

            # Perform data flow analysis
            self.data_flow_analyzer.analyze(self.ir, cfgs)
        except Exception as e:
            self.fail(f"Analyzer raised an exception on empty IR: {e}")

        # Ensure no reaching definitions are generated
        self.assertEqual(len(self.data_flow_analyzer.reaching_definitions), 0)

    def test_analyze_simple_assignment(self):
        """Test data flow analysis on a simple function with assignments."""
        # Create a simple function node with assignments
        function_node = IRNode(node_type=IRNodeType.FUNCTION, name="simple_function")
        assign_a = IRNode(node_type=IRNodeType.ASSIGNMENT, attributes={"target": "a"})
        assign_b = IRNode(node_type=IRNodeType.ASSIGNMENT, attributes={"target": "b"})
        assign_c = IRNode(node_type=IRNodeType.ASSIGNMENT, attributes={"target": "c"})

        function_node.add_child(assign_a)
        function_node.add_child(assign_b)
        function_node.add_child(assign_c)
        self.ir.root.add_child(function_node)

        # Generate CFGs
        self.control_flow_analyzer.analyze(self.ir)
        cfgs = self.control_flow_analyzer.cfgs

        # Perform data flow analysis
        self.data_flow_analyzer.analyze(self.ir, cfgs)

        # Retrieve the reaching definitions
        rd = self.data_flow_analyzer.reaching_definitions.get("simple_function", {})
        in_sets = rd.get('in_sets', {})
        out_sets = rd.get('out_sets', {})

        # Assertions
        cfg = cfgs["simple_function"]
        entry_block = cfg.entry_block

        # Expected definitions
        def_a = ("a", assign_a)
        def_b = ("b", assign_b)
        def_c = ("c", assign_c)

        expected_gen = {def_a, def_b, def_c}
        expected_in = set()
        expected_out = expected_gen

        # Check that the in and out sets match expected values
        self.assertEqual(in_sets[entry_block], expected_in)
        self.assertEqual(out_sets[entry_block], expected_out)

    def test_analyze_branching_assignments(self):
        """Test data flow analysis on a function with branching assignments."""
        # Create a function node with a control flow node representing if-else
        function_node = IRNode(node_type=IRNodeType.FUNCTION, name="branching_function")
        control_flow_node = IRNode(node_type=IRNodeType.CONTROL_FLOW, attributes={"type": "if_else"})

        # Create if_branch and else_branch nodes
        if_branch = IRNode(node_type=IRNodeType.BLOCK, name="if_branch")
        assign_x = IRNode(node_type=IRNodeType.ASSIGNMENT, attributes={"target": "x"})
        if_branch.add_child(assign_x)

        else_branch = IRNode(node_type=IRNodeType.BLOCK, name="else_branch")
        assign_y = IRNode(node_type=IRNodeType.ASSIGNMENT, attributes={"target": "y"})
        else_branch.add_child(assign_y)

        # Add branches to control flow node
        control_flow_node.add_child(if_branch)
        control_flow_node.add_child(else_branch)

        # Add control flow node to function node
        function_node.add_child(control_flow_node)
        self.ir.root.add_child(function_node)

        # Generate CFGs
        self.control_flow_analyzer.analyze(self.ir)
        cfgs = self.control_flow_analyzer.cfgs

        # Perform data flow analysis
        self.data_flow_analyzer.analyze(self.ir, cfgs)

        # Retrieve the reaching definitions
        rd = self.data_flow_analyzer.reaching_definitions.get("branching_function", {})
        in_sets = rd.get('in_sets', {})
        out_sets = rd.get('out_sets', {})

        # Assertions
        cfg = cfgs["branching_function"]
        entry_block = cfg.entry_block
        if_block = cfg.blocks["if_block_1"]
        else_block = cfg.blocks["else_block_2"]
        end_block = cfg.blocks["end_block_3"]

        # Expected definitions
        def_x = ("x", assign_x)
        def_y = ("y", assign_y)

        # Expected in and out sets
        expected_in_entry = set()
        expected_out_entry = set()
        expected_in_if = set()
        expected_out_if = {def_x}
        expected_in_else = set()
        expected_out_else = {def_y}
        expected_in_end = {def_x, def_y}
        expected_out_end = {def_x, def_y}

        # Check the in and out sets for each block
        self.assertEqual(in_sets[entry_block], expected_in_entry)
        self.assertEqual(out_sets[entry_block], expected_out_entry)

        self.assertEqual(in_sets[if_block], expected_in_if)
        self.assertEqual(out_sets[if_block], expected_out_if)

        self.assertEqual(in_sets[else_block], expected_in_else)
        self.assertEqual(out_sets[else_block], expected_out_else)

        self.assertEqual(in_sets[end_block], expected_in_end)
        self.assertEqual(out_sets[end_block], expected_out_end)

if __name__ == '__main__':
    unittest.main()
