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
        """Test dependency analysis with a function definition."""
        param_node = IRNode(
            node_type=IRNodeType.VARIABLE,
            name='x',
            attributes={'type': None}
        )
        return_type = IRNode(
            node_type=IRNodeType.TYPE,
            name='int'
        )
        body_node = IRNode(
            node_type=IRNodeType.RETURN,
            attributes={'value': param_node}
        )
        func_node = IRNode(
            node_type=IRNodeType.FUNCTION_DEF,
            name='foo',
            attributes={
                'parameters': [param_node],
                'body': body_node,
                'return_type': return_type
            }
        )
        self.ir.root.add_child(func_node)
        self.analyzer.analyze(self.ir)
        
        # Check function dependencies
        self.assertIn(func_node, self.analyzer.dependencies)
        self.assertIn(param_node, self.analyzer.dependencies[func_node])
        self.assertIn(body_node, self.analyzer.dependencies[func_node])
        self.assertIn(return_type, self.analyzer.dependencies[func_node])

    def test_class_definition(self):
        """Test dependency analysis with class definition and inheritance."""
        base_class = IRNode(
            node_type=IRNodeType.CLASS_DEF,
            name='BaseClass',
            attributes={'bases': [], 'body': None}
        )
        
        method_node = IRNode(
            node_type=IRNodeType.FUNCTION_DEF,
            name='method',
            attributes={'parameters': [], 'body': None}
        )
        
        derived_class = IRNode(
            node_type=IRNodeType.CLASS_DEF,
            name='DerivedClass',
            attributes={
                'bases': [base_class],
                'body': method_node
            }
        )
        
        self.ir.root.add_child(base_class)
        self.ir.root.add_child(derived_class)
        self.analyzer.analyze(self.ir)
        
        # Check class dependencies
        self.assertIn(derived_class, self.analyzer.dependencies)
        self.assertIn(base_class, self.analyzer.dependencies[derived_class])
        self.assertIn(method_node, self.analyzer.dependencies[derived_class])

    def test_control_flow(self):
        """Test dependency analysis with control flow structures."""
        condition = IRNode(
            node_type=IRNodeType.BINARY_OP,
            attributes={'op': '>', 'left': None, 'right': None}
        )
        
        if_body = IRNode(
            node_type=IRNodeType.ASSIGNMENT,
            attributes={'left': None, 'right': None}
        )
        
        else_body = IRNode(
            node_type=IRNodeType.ASSIGNMENT,
            attributes={'left': None, 'right': None}
        )
        
        if_node = IRNode(
            node_type=IRNodeType.IF,
            attributes={
                'test': condition,
                'body': if_body,
                'else': else_body
            }
        )
        
        self.ir.root.add_child(if_node)
        self.analyzer.analyze(self.ir)
        
        # Check control flow dependencies
        self.assertIn(if_node, self.analyzer.dependencies)
        self.assertIn(condition, self.analyzer.dependencies[if_node])
        self.assertIn(if_body, self.analyzer.dependencies[if_node])
        self.assertIn(else_body, self.analyzer.dependencies[if_node])

    def test_try_except(self):
        """Test dependency analysis with exception handling."""
        try_body = IRNode(
            node_type=IRNodeType.FUNCTION_CALL,
            attributes={'function': None, 'arguments': []}
        )
        
        handler = IRNode(
            node_type=IRNodeType.EXCEPT_HANDLER,
            attributes={'type': None, 'body': None}
        )
        
        finally_body = IRNode(
            node_type=IRNodeType.ASSIGNMENT,
            attributes={'left': None, 'right': None}
        )
        
        try_node = IRNode(
            node_type=IRNodeType.TRY,
            attributes={
                'body': try_body,
                'handlers': [handler],
                'finally': finally_body
            }
        )
        
        self.ir.root.add_child(try_node)
        self.analyzer.analyze(self.ir)
        
        # Check exception handling dependencies
        self.assertIn(try_node, self.analyzer.dependencies)
        self.assertIn(try_body, self.analyzer.dependencies[try_node])
        self.assertIn(handler, self.analyzer.dependencies[try_node])
        self.assertIn(finally_body, self.analyzer.dependencies[try_node])

    def test_circular_dependencies(self):
        """Test detection of circular dependencies."""
        class_a = IRNode(
            node_type=IRNodeType.CLASS_DEF,
            name='A',
            attributes={'bases': []}
        )
        
        class_b = IRNode(
            node_type=IRNodeType.CLASS_DEF,
            name='B',
            attributes={'bases': [class_a]}
        )
        
        # Create circular dependency: A -> B -> A
        class_a.attributes['bases'] = [class_b]
        
        self.ir.root.add_child(class_a)
        self.ir.root.add_child(class_b)
        self.analyzer.analyze(self.ir)
        
        # Check circular dependencies
        circular_deps = self.analyzer.get_circular_dependencies()
        self.assertEqual(len(circular_deps), 1)
        cycle = circular_deps[0]
        self.assertIn(class_a, cycle)
        self.assertIn(class_b, cycle)

    def test_complex_import(self):
        """Test dependency analysis with complex import statements."""
        import_node = IRNode(
            node_type=IRNodeType.IMPORT,
            attributes={
                'module_name': 'module',
                'aliases': {'alias1': 'original1', 'alias2': 'original2'},
                'from_list': ['item1', 'item2']
            }
        )
        
        self.ir.root.add_child(import_node)
        self.analyzer.analyze(self.ir)
        
        # Check import dependencies
        self.assertIn(import_node, self.analyzer.dependencies)
        deps = self.analyzer.dependencies[import_node]
        
        # Should have 1 module node + 2 alias nodes + 2 from_list nodes
        self.assertEqual(len(deps), 5)
        
        # Verify types of dependency nodes
        type_counts = {
            IRNodeType.MODULE: 0,
            IRNodeType.ALIAS: 0,
            IRNodeType.IMPORT_FROM: 0
        }
        
        for dep in deps:
            type_counts[dep.node_type] = type_counts.get(dep.node_type, 0) + 1
        
        self.assertEqual(type_counts[IRNodeType.MODULE], 1)
        self.assertEqual(type_counts[IRNodeType.ALIAS], 2)
        self.assertEqual(type_counts[IRNodeType.IMPORT_FROM], 2)

    def test_binary_and_unary_operations(self):
        """Test dependency analysis with binary and unary operations."""
        var_a = IRNode(
            node_type=IRNodeType.VARIABLE,
            name='a'
        )
        
        var_b = IRNode(
            node_type=IRNodeType.VARIABLE,
            name='b'
        )
        
        # Binary operation: a + b
        binary_op = IRNode(
            node_type=IRNodeType.BINARY_OP,
            attributes={
                'op': '+',
                'left': var_a,
                'right': var_b
            }
        )
        
        # Unary operation: -a
        unary_op = IRNode(
            node_type=IRNodeType.UNARY_OP,
            attributes={
                'op': '-',
                'operand': var_a
            }
        )
        
        self.ir.root.add_child(binary_op)
        self.ir.root.add_child(unary_op)
        self.analyzer.analyze(self.ir)
        
        # Check binary operation dependencies
        self.assertIn(binary_op, self.analyzer.dependencies)
        self.assertIn(var_a, self.analyzer.dependencies[binary_op])
        self.assertIn(var_b, self.analyzer.dependencies[binary_op])
        
        # Check unary operation dependencies
        self.assertIn(unary_op, self.analyzer.dependencies)
        self.assertIn(var_a, self.analyzer.dependencies[unary_op])

    def test_loop_dependencies(self):
        """Test dependency analysis with loop structures."""
        # While loop test
        test_var = IRNode(
            node_type=IRNodeType.VARIABLE,
            name='condition'
        )
        
        while_body = IRNode(
            node_type=IRNodeType.ASSIGNMENT,
            attributes={'left': None, 'right': None}
        )
        
        while_node = IRNode(
            node_type=IRNodeType.WHILE,
            attributes={
                'test': test_var,
                'body': while_body
            }
        )
        
        # For loop
        target = IRNode(
            node_type=IRNodeType.VARIABLE,
            name='i'
        )
        
        iter_expr = IRNode(
            node_type=IRNodeType.FUNCTION_CALL,
            name='range',
            attributes={'function': None, 'arguments': []}
        )
        
        for_body = IRNode(
            node_type=IRNodeType.ASSIGNMENT,
            attributes={'left': None, 'right': None}
        )
        
        for_node = IRNode(
            node_type=IRNodeType.FOR,
            attributes={
                'target': target,
                'iter': iter_expr,
                'body': for_body
            }
        )
        
        self.ir.root.add_child(while_node)
        self.ir.root.add_child(for_node)
        self.analyzer.analyze(self.ir)
        
        # Check while loop dependencies
        self.assertIn(while_node, self.analyzer.dependencies)
        self.assertIn(test_var, self.analyzer.dependencies[while_node])
        self.assertIn(while_body, self.analyzer.dependencies[while_node])
        
        # Check for loop dependencies
        self.assertIn(for_node, self.analyzer.dependencies)
        self.assertIn(target, self.analyzer.dependencies[for_node])
        self.assertIn(iter_expr, self.analyzer.dependencies[for_node])
        self.assertIn(for_body, self.analyzer.dependencies[for_node])


if __name__ == '__main__':
    unittest.main()
