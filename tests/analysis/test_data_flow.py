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
        # Create a function node
        function_node = IRNode(node_type=IRNodeType.FUNCTION, name="simple_assignment")

        # Create an assignment node
        assign_x = IRNode(
            node_type=IRNodeType.ASSIGNMENT,
            attributes={
                "target": "x",
                "value": IRNode(node_type=IRNodeType.LITERAL, attributes={"value": 42})
            }
        )

        # Add assignment to function
        function_node.add_child(assign_x)

        # Add function to IR
        self.ir.root.add_child(function_node)

        # Generate CFGs
        self.control_flow_analyzer.analyze(self.ir)
        cfgs = self.control_flow_analyzer.cfgs

        # Perform data flow analysis
        self.data_flow_analyzer.analyze(self.ir, cfgs)

        # Retrieve the reaching definitions
        rd = self.data_flow_analyzer.reaching_definitions.get("simple_assignment", {})
        in_sets = rd.get('in_sets', {})
        out_sets = rd.get('out_sets', {})

        # Assertions
        entry_block_name = cfgs["simple_assignment"].entry_block.name
        assign_block_name = "block_1"

        assign_def = ("x", assign_x)

        expected_in_entry = set()
        expected_out_entry = set()
        expected_in_assign = set()
        expected_out_assign = {assign_def}

        # Check the in and out sets for each block
        self.assertEqual(in_sets[entry_block_name], expected_in_entry)
        self.assertEqual(out_sets[entry_block_name], expected_out_entry)
        self.assertEqual(in_sets[assign_block_name], expected_in_assign)
        self.assertEqual(out_sets[assign_block_name], expected_out_assign)

    def test_analyze_branching_assignments(self):
        """Test data flow analysis on a function with branching assignments."""
        # [This test remains as previously updated]
        # ... (existing code from previous updates)

    def test_analyze_array_access(self):
        """Test data flow analysis with array accesses."""
        # Create a function node
        function_node = IRNode(node_type=IRNodeType.FUNCTION, name="array_access_function")

        # Create an array assignment
        assign_array = IRNode(
            node_type=IRNodeType.ASSIGNMENT,
            attributes={
                "target": "arr",
                "value": IRNode(node_type=IRNodeType.COLLECTION, attributes={"elements": []})
            }
        )

        # Create an array access
        array_access = IRNode(
            node_type=IRNodeType.ARRAY_ACCESS,
            attributes={
                "array": "arr",
                "index": IRNode(node_type=IRNodeType.LITERAL, attributes={"value": 0})
            }
        )
        read_value = IRNode(node_type=IRNodeType.VARIABLE, name="x")
        array_access.add_child(read_value)

        # Add nodes to function
        function_node.add_child(assign_array)
        function_node.add_child(array_access)
        self.ir.root.add_child(function_node)

        # Generate CFGs
        self.control_flow_analyzer.analyze(self.ir)
        cfgs = self.control_flow_analyzer.cfgs

        # Perform data flow analysis
        self.data_flow_analyzer.analyze(self.ir, cfgs)

        # Assertions can be added here to verify the analysis results

    def test_analyze_interprocedural_flow(self):
        """Test interprocedural data flow analysis."""
        # Create function A
        function_a = IRNode(node_type=IRNodeType.FUNCTION, name="function_a")
        assign_x = IRNode(
            node_type=IRNodeType.ASSIGNMENT,
            attributes={
                "target": "x",
                "value": IRNode(node_type=IRNodeType.LITERAL, attributes={"value": 10})
            }
        )
        function_a.add_child(assign_x)

        # Create function B
        function_b = IRNode(node_type=IRNodeType.FUNCTION, name="function_b")
        call_a = IRNode(
            node_type=IRNodeType.FUNCTION_CALL,
            attributes={"function": "function_a"}
        )
        function_b.add_child(call_a)
        use_x = IRNode(
            node_type=IRNodeType.VARIABLE,
            name="x"
        )
        function_b.add_child(use_x)

        # Add functions to IR
        self.ir.root.add_child(function_a)
        self.ir.root.add_child(function_b)

        # Generate CFGs
        self.control_flow_analyzer.analyze(self.ir)
        cfgs = self.control_flow_analyzer.cfgs

        # Perform data flow analysis
        self.data_flow_analyzer.analyze(self.ir, cfgs)

        # Assertions can be added here to verify interprocedural flow

    def test_analyze_phi_nodes(self):
        """Test phi node insertion at join points."""
        # [This test remains as previously updated]
        # ... (existing code from previous updates)

    def test_analyze_loop_carried_dependencies(self):
        """Test analysis of loop-carried dependencies."""
        # [This test remains as previously updated]
        # ... (existing code from previous updates)


if __name__ == '__main__':
    unittest.main()
