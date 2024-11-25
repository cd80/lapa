"""
Unit tests for the ControlFlowAnalyzer.
"""

import unittest
from lapa.ir import IR, IRNode, IRNodeType
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
        # Create a function node
        function_node = IRNode(node_type=IRNodeType.FUNCTION, name="simple_function")

        # Add some statements to the function
        statement1 = IRNode(node_type=IRNodeType.STATEMENT, name="statement1")
        statement2 = IRNode(node_type=IRNodeType.STATEMENT, name="statement2")
        function_node.add_child(statement1)
        function_node.add_child(statement2)

        # Add function to IR
        self.ir.root.add_child(function_node)

        # Perform analysis
        self.analyzer.analyze(self.ir)

        # Verify CFG creation
        self.assertIn("simple_function", self.analyzer.cfgs)
        cfg = self.analyzer.cfgs["simple_function"]

        # Check blocks
        self.assertIn("entry", cfg.blocks)
        self.assertIn("block_1", cfg.blocks)
        self.assertIn("block_2", cfg.blocks)
        self.assertIn("exit", cfg.blocks)

        # Verify connections
        entry_block = cfg.blocks["entry"]
        block1 = cfg.blocks["block_1"]
        block2 = cfg.blocks["block_2"]
        exit_block = cfg.blocks["exit"]

        self.assertIn(block1, entry_block.successors)
        self.assertIn(block2, block1.successors)
        self.assertIn(exit_block, block2.successors)

    def test_analyze_loop_structure(self):
        """Test analyzing a loop structure."""
        # Create a function node
        function_node = IRNode(node_type=IRNodeType.FUNCTION, name="loop_function")

        # Create a loop node
        loop_node = IRNode(node_type=IRNodeType.LOOP, attributes={"type": "while"})
        condition = IRNode(node_type=IRNodeType.LITERAL, attributes={"value": True})
        loop_node.attributes["condition"] = condition

        # Loop body statement
        loop_body_statement = IRNode(node_type=IRNodeType.STATEMENT, name="loop_body_statement")
        loop_node.add_child(loop_body_statement)

        # Add loop to function
        function_node.add_child(loop_node)
        self.ir.root.add_child(function_node)

        # Perform analysis
        self.analyzer.analyze(self.ir)

        # Verify CFG creation
        self.assertIn("loop_function", self.analyzer.cfgs)
        cfg = self.analyzer.cfgs["loop_function"]

        # Check blocks
        self.assertIn("entry", cfg.blocks)
        self.assertIn("loop_block_1", cfg.blocks)
        self.assertIn("block_3", cfg.blocks)  # Loop body block
        self.assertIn("after_loop_block_2", cfg.blocks)
        self.assertIn("exit", cfg.blocks)

        # Verify connections
        entry_block = cfg.blocks["entry"]
        loop_block = cfg.blocks["loop_block_1"]
        loop_body_block = cfg.blocks["block_3"]
        after_loop_block = cfg.blocks["after_loop_block_2"]
        exit_block = cfg.blocks["exit"]

        self.assertIn(loop_block, entry_block.successors)
        self.assertIn(loop_body_block, loop_block.successors)
        self.assertIn(loop_block, loop_body_block.successors)  # Loop back
        self.assertIn(after_loop_block, loop_block.successors)
        self.assertIn(exit_block, after_loop_block.successors)

    def test_analyze_if_else(self):
        """Test analyzing an if-else control flow structure."""
        # Create a function node
        function_node = IRNode(node_type=IRNodeType.FUNCTION, name="if_else_function")

        # Create an 'if' node
        if_node = IRNode(
            node_type=IRNodeType.CONTROL_FLOW,
            attributes={
                "type": "if",
                "condition": IRNode(node_type=IRNodeType.LITERAL, attributes={"value": True})
            }
        )
        if_statement = IRNode(node_type=IRNodeType.STATEMENT, name="if_statement")
        if_node.add_child(if_statement)

        # Create an 'else' node
        else_node = IRNode(
            node_type=IRNodeType.CONTROL_FLOW,
            attributes={"type": "else"}
        )
        else_statement = IRNode(node_type=IRNodeType.STATEMENT, name="else_statement")
        else_node.add_child(else_statement)

        # Add 'if' and 'else' to function
        function_node.add_child(if_node)
        function_node.add_child(else_node)
        self.ir.root.add_child(function_node)

        # Perform analysis
        self.analyzer.analyze(self.ir)

        # Verify CFG creation
        self.assertIn("if_else_function", self.analyzer.cfgs)
        cfg = self.analyzer.cfgs["if_else_function"]

        # Check blocks
        self.assertIn("entry", cfg.blocks)
        self.assertIn("if_block_1", cfg.blocks)
        self.assertIn("block_4", cfg.blocks)  # If body block
        self.assertIn("else_block_2", cfg.blocks)
        self.assertIn("block_5", cfg.blocks)  # Else body block
        self.assertIn("end_block_3", cfg.blocks)
        self.assertIn("exit", cfg.blocks)

        # Verify connections
        entry_block = cfg.blocks["entry"]
        if_block = cfg.blocks["if_block_1"]
        if_body_block = cfg.blocks["block_4"]
        else_block = cfg.blocks["else_block_2"]
        else_body_block = cfg.blocks["block_5"]
        end_block = cfg.blocks["end_block_3"]
        exit_block = cfg.blocks["exit"]

        self.assertIn(if_block, entry_block.successors)
        self.assertIn(else_block, entry_block.successors)
        self.assertIn(if_body_block, if_block.successors)
        self.assertIn(end_block, if_body_block.successors)
        self.assertIn(else_body_block, else_block.successors)
        self.assertIn(end_block, else_body_block.successors)
        self.assertIn(exit_block, end_block.successors)

    def test_analyze_nested_control_flow(self):
        """Test analyzing nested control flow structures."""
        # Create a function node
        function_node = IRNode(node_type=IRNodeType.FUNCTION, name="nested_control_flow")

        # Outer 'if' node
        outer_if_node = IRNode(
            node_type=IRNodeType.CONTROL_FLOW,
            attributes={
                "type": "if",
                "condition": IRNode(node_type=IRNodeType.LITERAL, attributes={"value": True})
            }
        )

        # Inner 'for' loop inside 'if'
        for_loop_node = IRNode(
            node_type=IRNodeType.LOOP,
            attributes={"type": "for"}
        )
        loop_statement = IRNode(node_type=IRNodeType.STATEMENT, name="loop_statement")
        for_loop_node.add_child(loop_statement)

        outer_if_node.add_child(for_loop_node)
        function_node.add_child(outer_if_node)
        self.ir.root.add_child(function_node)

        # Perform analysis
        self.analyzer.analyze(self.ir)

        # Note: Additional assertions can be added here if needed

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

        # Check blocks
        self.assertIn("entry", cfg.blocks)
        self.assertIn("try_block_1", cfg.blocks)
        self.assertIn("block_2", cfg.blocks)  # Try block content
        self.assertIn("except_block_4", cfg.blocks)
        self.assertIn("block_5", cfg.blocks)  # Except block content
        self.assertIn("end_block_3", cfg.blocks)
        self.assertIn("exit", cfg.blocks)

        # Verify connections
        entry_block = cfg.blocks["entry"]
        try_block = cfg.blocks["try_block_1"]
        try_content_block = cfg.blocks["block_2"]
        except_block = cfg.blocks["except_block_4"]
        except_content_block = cfg.blocks["block_5"]
        end_block = cfg.blocks["end_block_3"]
        exit_block = cfg.blocks["exit"]

        self.assertIn(try_block, entry_block.successors)
        self.assertIn(try_content_block, try_block.successors)
        self.assertIn(end_block, try_content_block.successors)
        self.assertIn(except_block, try_block.successors)
        self.assertIn(except_content_block, except_block.successors)
        self.assertIn(end_block, except_content_block.successors)
        self.assertIn(exit_block, end_block.successors)
        self.assertIn(except_block, try_block.successors)

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

        # Check blocks
        self.assertIn("entry", cfg.blocks)
        self.assertIn("try_block_1", cfg.blocks)
        self.assertIn("block_2", cfg.blocks)  # Try block content
        self.assertIn("except_block_4", cfg.blocks)
        self.assertIn("block_5", cfg.blocks)  # Except block content
        self.assertIn("finally_block_6", cfg.blocks)
        self.assertIn("block_7", cfg.blocks)  # Finally block content
        self.assertIn("end_block_3", cfg.blocks)
        self.assertIn("exit", cfg.blocks)

        # Verify connections
        entry_block = cfg.blocks["entry"]
        try_block = cfg.blocks["try_block_1"]
        try_content_block = cfg.blocks["block_2"]
        except_block = cfg.blocks["except_block_4"]
        except_content_block = cfg.blocks["block_5"]
        finally_block = cfg.blocks["finally_block_6"]
        finally_content_block = cfg.blocks["block_7"]
        end_block = cfg.blocks["end_block_3"]
        exit_block = cfg.blocks["exit"]

        self.assertIn(try_block, entry_block.successors)
        self.assertIn(try_content_block, try_block.successors)
        self.assertIn(end_block, try_content_block.successors)
        self.assertIn(finally_block, end_block.successors)
        self.assertIn(except_block, try_block.successors)
        self.assertIn(except_content_block, except_block.successors)
        self.assertIn(end_block, except_content_block.successors)
        self.assertIn(finally_block, end_block.successors)
        self.assertIn(finally_content_block, finally_block.successors)
        self.assertIn(exit_block, finally_content_block.successors)
        self.assertIn(except_block, try_block.successors)

if __name__ == '__main__':
    unittest.main()
