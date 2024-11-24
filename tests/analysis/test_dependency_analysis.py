"""
Unit tests for the DependencyAnalyzer.
"""

import unittest
from lapa.ir import IR, IRNode, IRNodeType
from lapa.analysis.dependency_analysis import DependencyAnalyzer


class TestDependencyAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = DependencyAnalyzer()
        self.ir = IR()

    def test_empty_ir(self):
        """Test dependency analysis on an empty IR."""
        try:
            self.analyzer.analyze(self.ir)
        except Exception as e:
            self.fail(f"DependencyAnalyzer raised an exception on empty IR: {e}")
        # Ensure that dependencies are empty
        self.assertEqual(len(self.analyzer.dependencies), 0)

    def test_function_definition(self):
        """Test dependency analysis with a simple function definition."""
        func_node = IRNode(
            node_type=IRNodeType.FUNCTION_DEF,
            name='foo',
            attributes={
                'parameters': [],
                'body': None
            }
        )
        self.ir.root.add_child(func_node)
        self.analyzer.analyze(self.ir)
        self.assertIn(func_node, self.analyzer.dependencies)
        self.assertEqual(len(self.analyzer.dependencies[func_node]), 0)

    def test_function_call(self):
        """Test dependency analysis with a function call."""
        func_def = IRNode(
            node_type=IRNodeType.FUNCTION_DEF,
            name='foo',
            attributes={
                'parameters': [],
                'body': None
            }
        )
        func_call = IRNode(
            node_type=IRNodeType.FUNCTION_CALL,
            attributes={
                'function': func_def,
                'arguments': []
            }
        )
        self.ir.root.add_child(func_def)
        self.ir.root.add_child(func_call)
        self.analyzer.analyze(self.ir)
        self.assertIn(func_call, self.analyzer.dependencies)
        self.assertIn(func_def, self.analyzer.dependencies[func_call])

    def test_variable_assignment(self):
        """Test dependency analysis with variable assignment."""
        var_node = IRNode(
            node_type=IRNodeType.VARIABLE,
            name='x'
        )
        literal_node = IRNode(
            node_type=IRNodeType.LITERAL,
            attributes={'value': 42}
        )
        assign_node = IRNode(
            node_type=IRNodeType.ASSIGNMENT,
            attributes={
                'left': var_node,
                'right': literal_node
            }
        )
        self.ir.root.add_child(assign_node)
        self.analyzer.analyze(self.ir)
        self.assertIn(var_node, self.analyzer.dependencies)
        self.assertIn(literal_node, self.analyzer.dependencies[var_node])

    def test_import(self):
        """Test dependency analysis with an import statement."""
        import_node = IRNode(
            node_type=IRNodeType.IMPORT,
            attributes={
                'module_name': 'os'
            }
        )
        self.ir.root.add_child(import_node)
        self.analyzer.analyze(self.ir)
        self.assertIn(import_node, self.analyzer.dependencies)
        self.assertEqual(len(self.analyzer.dependencies[import_node]), 1)

if __name__ == '__main__':
    unittest.main()
