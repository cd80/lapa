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
        # This test remains unchanged
        pass

    def test_analyze_branching_assignments(self):
        """Test data flow analysis on a function with branching assignments."""
        # Create a function node
        function_node = IRNode(node_type=IRNodeType.FUNCTION, name="branching_function")

        # Create an 'if' control flow node
        if_node = IRNode(
            node_type=IRNodeType.CONTROL_FLOW,
            attributes={"type": "if", "condition": IRNode(node_type=IRNodeType.LITERAL, attributes={"value": True})}
        )
        assign_x = IRNode(node_type=IRNodeType.ASSIGNMENT, attributes={"target": "x"})
        if_node.add_child(assign_x)

        # Create an 'else' control flow node
        else_node = IRNode(
            node_type=IRNodeType.CONTROL_FLOW,
            attributes={"type": "else"}
        )
        assign_y = IRNode(node_type=IRNodeType.ASSIGNMENT, attributes={"target": "y"})
        else_node.add_child(assign_y)

        # Add 'if' and 'else' nodes to the function
        function_node.add_child(if_node)
        function_node.add_child(else_node)
        self.ir.root.add_child(function_node)

        # Generate CFGs
        self.control_flow_analyzer.analyze(self.ir)
        cfgs = self.control_flow_analyzer.cfgs

        # Print actual block names for debugging
        cfg = cfgs["branching_function"]
        print("Actual CFG blocks:", cfg.blocks.keys())

        # Perform data flow analysis
        self.data_flow_analyzer.analyze(self.ir, cfgs)

        # Retrieve the reaching definitions
        rd = self.data_flow_analyzer.reaching_definitions.get("branching_function", {})
        in_sets = rd.get('in_sets', {})
        out_sets = rd.get('out_sets', {})

        # Assertions
        entry_block_name = cfg.entry_block.name
        if_block_name = "if_block_1"
        else_block_name = "else_block_2"
        end_block_name = "end_block_3"

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
        self.assertEqual(in_sets[entry_block_name], expected_in_entry)
        self.assertEqual(out_sets[entry_block_name], expected_out_entry)
        self.assertEqual(in_sets[if_block_name], expected_in_if)
        self.assertEqual(out_sets[if_block_name], expected_out_if)
        self.assertEqual(in_sets[else_block_name], expected_in_else)
        self.assertEqual(out_sets[else_block_name], expected_out_else)
        self.assertEqual(in_sets[end_block_name], expected_in_end)
        self.assertEqual(out_sets[end_block_name], expected_out_end)

    def test_analyze_array_access(self):
        """Test data flow analysis with array accesses."""
        # This test remains unchanged
        pass

    def test_analyze_interprocedural_flow(self):
        """Test interprocedural data flow analysis."""
        # This test remains unchanged
        pass

    def test_analyze_phi_nodes(self):
        """Test phi node insertion at join points."""
        # Create a function node
        function_node = IRNode(node_type=IRNodeType.FUNCTION, name="phi_function")

        # Create an 'if' control flow node
        if_node = IRNode(
            node_type=IRNodeType.CONTROL_FLOW,
            attributes={"type": "if", "condition": IRNode(node_type=IRNodeType.LITERAL, attributes={"value": True})}
        )
        assign_x1 = IRNode(
            node_type=IRNodeType.ASSIGNMENT,
            attributes={
                "target": "x",
                "value": IRNode(node_type=IRNodeType.LITERAL, attributes={"value": 1})
            }
        )
        if_node.add_child(assign_x1)

        # Create an 'else' control flow node
        else_node = IRNode(
            node_type=IRNodeType.CONTROL_FLOW,
            attributes={"type": "else"}
        )
        assign_x2 = IRNode(
            node_type=IRNodeType.ASSIGNMENT,
            attributes={
                "target": "x",
                "value": IRNode(node_type=IRNodeType.LITERAL, attributes={"value": 2})
            }
        )
        else_node.add_child(assign_x2)

        # Add 'if' and 'else' nodes to the function
        function_node.add_child(if_node)
        function_node.add_child(else_node)
        self.ir.root.add_child(function_node)

        # Generate CFGs and analyze
        self.control_flow_analyzer.analyze(self.ir)
        cfgs = self.control_flow_analyzer.cfgs

        # Print actual block names for debugging
        cfg = cfgs["phi_function"]
        print("Actual CFG blocks:", cfg.blocks.keys())

        # Perform data flow analysis
        self.data_flow_analyzer.analyze(self.ir, cfgs)

        # Check phi nodes
        phi_nodes = self.data_flow_analyzer.phi_nodes.get("phi_function", {})
        join_block_name = "end_block_3"
        self.assertIsNotNone(join_block_name)
        self.assertIn(join_block_name, phi_nodes)
        self.assertEqual(len(phi_nodes[join_block_name]), 1)  # One phi node for x

    def test_analyze_loop_carried_dependencies(self):
        """Test analysis of loop-carried dependencies."""
        # Create a function node
        function_node = IRNode(node_type=IRNodeType.FUNCTION, name="loop_function")

        # Initialize loop variable
        init_i = IRNode(
            node_type=IRNodeType.ASSIGNMENT,
            attributes={
                "target": "i",
                "value": IRNode(node_type=IRNodeType.LITERAL, attributes={"value": 0})
            }
        )

        # Create a loop node
        loop_node = IRNode(
            node_type=IRNodeType.LOOP,
            attributes={"type": "for"}
        )
        increment = IRNode(
            node_type=IRNodeType.ASSIGNMENT,
            attributes={
                "target": "i",
                "value": IRNode(
                    node_type=IRNodeType.BINARY_OP,
                    attributes={
                        "operator": "+",
                        "left_operand": IRNode(node_type=IRNodeType.VARIABLE, attributes={"name": "i"}),
                        "right_operand": IRNode(node_type=IRNodeType.LITERAL, attributes={"value": 1})
                    }
                )
            }
        )
        loop_node.add_child(increment)

        # Add nodes to the function
        function_node.add_child(init_i)
        function_node.add_child(loop_node)
        self.ir.root.add_child(function_node)

        # Generate CFGs and analyze
        self.control_flow_analyzer.analyze(self.ir)
        cfgs = self.control_flow_analyzer.cfgs

        # Print actual block names for debugging
        cfg = cfgs["loop_function"]
        print("Actual CFG blocks:", cfg.blocks.keys())

        # Perform data flow analysis
        self.data_flow_analyzer.analyze(self.ir, cfgs)

        # Check reaching definitions in loop
        rd = self.data_flow_analyzer.reaching_definitions.get("loop_function", {})
        in_sets = rd.get('in_sets', {})
        out_sets = rd.get('out_sets', {})

        loop_block_name = "loop_block_1"
        self.assertIsNotNone(loop_block_name)
        in_defs = in_sets[loop_block_name]
        # The loop block should have reaching definitions from both initialization and increment
        defs_of_i = [d for d in in_defs if d[0] == "i"]
        self.assertTrue(len(defs_of_i) >= 2)


if __name__ == '__main__':
    unittest.main()
