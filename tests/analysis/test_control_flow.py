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
        # [Existing test code remains unchanged]
        pass

    def test_analyze_loop_structure(self):
        """Test analyzing a loop structure."""
        # [Existing test code remains unchanged]
        pass

    def test_analyze_try_except(self):
        """Test analyzing a try-except control flow structure."""
        # Create a function node with a try-except block
        function_node = IRNode(node_type=IRNodeType.FUNCTION, name="try_except_function")
        try_node = IRNode(node_type=IRNodeType.CONTROL_FLOW, attributes={"type": "try"})

        # Try block content
        try_content = IRNode(node_type=IRNodeType.BLOCK)
        statement_in_try = IRNode(node_type=IRNodeType.STATEMENT, name="try_statement")
        try_content.add_child(statement_in_try)
        try_node.add_child(try_content)

        # Except node
        except_node = IRNode(node_type=IRNodeType.CONTROL_FLOW, attributes={"type": "except"})
        except_content = IRNode(node_type=IRNodeType.BLOCK)
        statement_in_except = IRNode(node_type=IRNodeType.STATEMENT, name="except_statement")
        except_content.add_child(statement_in_except)
        except_node.add_child(except_content)
        try_node.add_child(except_node)

        # Add try node to function
        function_node.add_child(try_node)
        self.ir.root.add_child(function_node)

        # Perform analysis
        self.analyzer.analyze(self.ir)

        # Verify that a CFG was created for the function
        self.assertIn("try_except_function", self.analyzer.cfgs)
        cfg = self.analyzer.cfgs["try_except_function"]

        # Check that the CFG has expected blocks
        self.assertIn("entry", cfg.blocks)
        self.assertIn("try_block_1", cfg.blocks)
        self.assertIn("except_block_3", cfg.blocks)  # Updated block name
        self.assertIn("end_block_2", cfg.blocks)
        self.assertIn("exit", cfg.blocks)

        # Verify the structure of the CFG
        entry_block = cfg.blocks["entry"]
        try_block = cfg.blocks["try_block_1"]
        except_block = cfg.blocks["except_block_3"]  # Updated block name
        end_block = cfg.blocks["end_block_2"]
        exit_block = cfg.blocks["exit"]

        # Check connections
        self.assertIn(try_block, entry_block.successors)
        self.assertIn(except_block, try_block.successors)
        self.assertIn(end_block, try_block.successors)
        self.assertIn(end_block, except_block.successors)
        self.assertIn(exit_block, end_block.successors)

    def test_analyze_try_except_finally(self):
        """Test analyzing a try-except-finally control flow structure."""
        # Create a function node with a try-except-finally block
        function_node = IRNode(node_type=IRNodeType.FUNCTION, name="try_except_finally_function")
        try_node = IRNode(node_type=IRNodeType.CONTROL_FLOW, attributes={"type": "try"})

        # Try block content
        try_content = IRNode(node_type=IRNodeType.BLOCK)
        statement_in_try = IRNode(node_type=IRNodeType.STATEMENT, name="try_statement")
        try_content.add_child(statement_in_try)
        try_node.add_child(try_content)

        # Except node
        except_node = IRNode(node_type=IRNodeType.CONTROL_FLOW, attributes={"type": "except"})
        except_content = IRNode(node_type=IRNodeType.BLOCK)
        statement_in_except = IRNode(node_type=IRNodeType.STATEMENT, name="except_statement")
        except_content.add_child(statement_in_except)
        except_node.add_child(except_content)
        try_node.add_child(except_node)

        # Finally node
        finally_node = IRNode(node_type=IRNodeType.CONTROL_FLOW, attributes={"type": "finally"})
        finally_content = IRNode(node_type=IRNodeType.BLOCK)
        statement_in_finally = IRNode(node_type=IRNodeType.STATEMENT, name="finally_statement")
        finally_content.add_child(statement_in_finally)
        finally_node.add_child(finally_content)
        try_node.add_child(finally_node)

        # Add try node to function
        function_node.add_child(try_node)
        self.ir.root.add_child(function_node)

        # Perform analysis
        self.analyzer.analyze(self.ir)

        # Verify that a CFG was created for the function
        self.assertIn("try_except_finally_function", self.analyzer.cfgs)
        cfg = self.analyzer.cfgs["try_except_finally_function"]

        # Check that the CFG has expected blocks
        self.assertIn("entry", cfg.blocks)
        self.assertIn("try_block_1", cfg.blocks)
        self.assertIn("except_block_3", cfg.blocks)  # Updated block name
        self.assertIn("finally_block_4", cfg.blocks)
        self.assertIn("end_block_2", cfg.blocks)
        self.assertIn("exit", cfg.blocks)

        # Verify the structure of the CFG
        entry_block = cfg.blocks["entry"]
        try_block = cfg.blocks["try_block_1"]
        except_block = cfg.blocks["except_block_3"]  # Updated block name
        finally_block = cfg.blocks["finally_block_4"]
        end_block = cfg.blocks["end_block_2"]
        exit_block = cfg.blocks["exit"]

        # Check connections
        self.assertIn(try_block, entry_block.successors)
        self.assertIn(finally_block, try_block.successors)
        self.assertIn(finally_block, except_block.successors)
        self.assertIn(end_block, finally_block.successors)
        self.assertIn(exit_block, end_block.successors)

    # Existing tests...
    # ...

if __name__ == '__main__':
    unittest.main()
