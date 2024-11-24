"""
Unit tests for the IR module.
"""

import unittest
from lapa.ir import IR, IRNode, IRNodeType, Position


class TestIR(unittest.TestCase):
    def setUp(self):
        self.ir = IR()

    def test_empty_ir_validation(self):
        """Test validation on an empty IR."""
        result = self.ir.validate()
        self.assertTrue(result)

    def test_ir_with_duplicate_symbols(self):
        """Test validation detects duplicate symbols."""
        func1 = IRNode(node_type=IRNodeType.FUNCTION, name="foo")
        func2 = IRNode(node_type=IRNodeType.FUNCTION, name="foo")
        self.ir.root.add_child(func1)
        self.ir.root.add_child(func2)
        result = self.ir.validate()
        self.assertFalse(result)

    def test_build_from_ast(self):
        """Test building IR from an AST node."""
        # Mock AST node
        class MockASTNode:
            def __init__(self):
                self.name = "foo"
                self.lineno = 1
                self.col_offset = 0
                self.filename = "test.py"
                self.body = []

            @property
            def __class__(self):
                return type("FunctionDef", (), {})

        ast_node = MockASTNode()
        self.ir.build_from_ast(ast_node)
        self.assertEqual(len(self.ir.root.children), 1)
        func_node = self.ir.root.children[0]
        self.assertEqual(func_node.name, "foo")
        self.assertEqual(func_node.node_type, IRNodeType.FUNCTION_DEF)

    def test_irnode_find_nodes_by_type(self):
        """Test finding nodes by type."""
        func_node = IRNode(node_type=IRNodeType.FUNCTION_DEF, name="foo")
        class_node = IRNode(node_type=IRNodeType.CLASS, name="Bar")
        func_node.add_child(class_node)
        self.ir.root.add_child(func_node)
        nodes = self.ir.root.find_nodes_by_type(IRNodeType.CLASS)
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].name, "Bar")

    def test_get_node_by_position(self):
        """Test getting node by source code position."""
        position = Position(line=10, column=5, file="test.py")
        var_node = IRNode(
            node_type=IRNodeType.VARIABLE,
            name="x",
            position=position
        )
        self.ir.root.add_child(var_node)
        found_node = self.ir.get_node_by_position(position)
        self.assertIsNotNone(found_node)
        self.assertEqual(found_node.name, "x")

    def test_to_dot(self):
        """Test conversion of IR to DOT format."""
        func_node = IRNode(node_type=IRNodeType.FUNCTION_DEF, name="foo")
        self.ir.root.add_child(func_node)
        dot_output = self.ir.to_dot()
        expected_line = '"{}:{}" -> "{}:{}";'.format(
            self.ir.root.node_type.name, self.ir.root.name,
            func_node.node_type.name, func_node.name
        )
        self.assertIn(expected_line, dot_output)

    # Additional test cases can be added here


if __name__ == '__main__':
    unittest.main()
