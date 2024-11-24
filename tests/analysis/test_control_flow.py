"""
Unit tests for the ControlFlowAnalyzer.
"""

import unittest
from lapa.ir import IR
from lapa.ir import IRNode, IRNodeType
from lapa.analysis.control_flow import ControlFlowAnalyzer

class TestControlFlowAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = ControlFlowAnalyzer()
        self.ir = IR()

    def test_analyze_empty_ir(self):
        """Test analyzing an empty IR."""
        try:
            self.analyzer.analyze(self.ir)
        except Exception as e:
            self.fail(f"Analyzer raised an exception on empty IR: {e}")

        # Check that no CFGs were created
        self.assertEqual(len(self.analyzer.cfgs), 0)

    def test_analyze_simple_control_flow(self):
        """Test analyzing a simple control flow structure."""
        # Create a simple function node with an if-else statement
        function_node = IRNode(node_type=IRNodeType.FUNCTION, name="test_function")
        if_node = IRNode(node_type=IRNodeType.CONTROL_FLOW, attributes={"type": "if"})
        else_node = IRNode(node_type=IRNodeType.CONTROL_FLOW, attributes={"type": "else"})

        function_node.add_child(if_node)
        function_node.add_child(else_node)
        self.ir.root.add_child(function_node)

        # Perform analysis
        self.analyzer.analyze(self.ir)

        # Verify that a CFG was created for the function
        self.assertIn("test_function", self.analyzer.cfgs)
        cfg = self.analyzer.cfgs["test_function"]

        # Check that the CFG has expected blocks
        self.assertIn("entry", cfg.blocks)
        self.assertIn("if_block_1", cfg.blocks)
        self.assertIn("else_block_2", cfg.blocks)
        self.assertIn("end_block_3", cfg.blocks)

        # Check block successors
        entry_block = cfg.blocks["entry"]
        self.assertEqual(len(entry_block.successors), 2)
        self.assertTrue(cfg.blocks["if_block_1"] in entry_block.successors)
        self.assertTrue(cfg.blocks["else_block_2"] in entry_block.successors)

        # Verify the structure of the CFG
        if_block = cfg.blocks["if_block_1"]
        else_block = cfg.blocks["else_block_2"]
        end_block = cfg.blocks["end_block_3"]

        self.assertEqual(if_block.successors, {end_block})
        self.assertEqual(else_block.successors, {end_block})

    def test_analyze_loop_structure(self):
        """Test analyzing a loop structure."""
        # Create a function node with a loop
        function_node = IRNode(node_type=IRNodeType.FUNCTION, name="loop_function")
        loop_node = IRNode(node_type=IRNodeType.LOOP, attributes={"type": "for"})

        function_node.add_child(loop_node)
        self.ir.root.add_child(function_node)

        # Perform analysis
        self.analyzer.analyze(self.ir)

        # Verify that a CFG was created for the function
        self.assertIn("loop_function", self.analyzer.cfgs)
        cfg = self.analyzer.cfgs["loop_function"]

        # Check that the CFG has expected blocks
        self.assertIn("entry", cfg.blocks)
        self.assertIn("loop_block_1", cfg.blocks)
        self.assertIn("after_loop_block_2", cfg.blocks)

        # Check block successors
        entry_block = cfg.blocks["entry"]
        loop_block = cfg.blocks["loop_block_1"]
        after_loop_block = cfg.blocks["after_loop_block_2"]

        self.assertEqual(entry_block.successors, {loop_block})
        self.assertEqual(loop_block.successors, {loop_block, after_loop_block})

        # Verify that the loop block loops back to itself
        self.assertTrue(loop_block in loop_block.successors)

if __name__ == '__main__':
    unittest.main()
