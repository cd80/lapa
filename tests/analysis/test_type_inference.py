"""
Unit tests for the TypeInferenceAnalyzer.
"""

import unittest
from lapa.ir import IR, IRNode, IRNodeType
from lapa.analysis.type_inference import TypeInferenceAnalyzer


class TestTypeInferenceAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = TypeInferenceAnalyzer()
        self.ir = IR()

    def test_empty_ir(self):
        """Test type inference on an empty IR."""
        self.analyzer.analyze(self.ir)
        self.assertEqual(len(self.analyzer.type_information), 0)

    def test_literal_type_inference(self):
        """Test type inference for literals."""
        literal_node = IRNode(
            node_type=IRNodeType.LITERAL, attributes={'value': 42}
        )
        self.ir.root.add_child(literal_node)
        self.analyzer.analyze(self.ir)
        inferred_type = self.analyzer.type_information.get(literal_node)
        self.assertEqual(inferred_type, 'int')

    def test_variable_type_inference(self):
        """Test type inference for variables."""
        var_node = IRNode(
            node_type=IRNodeType.VARIABLE, attributes={'name': 'x'}
        )
        assign_node = IRNode(
            node_type=IRNodeType.ASSIGNMENT,
            attributes={'left': var_node, 'right': IRNode(
                node_type=IRNodeType.LITERAL, attributes={'value': 3.14}
            )},
        )
        self.ir.root.add_child(assign_node)
        self.analyzer.analyze(self.ir)
        inferred_type = self.analyzer.type_information.get(var_node)
        self.assertEqual(inferred_type, 'float')

    def test_binary_operation_type_inference(self):
        """Test type inference for binary operations."""
        left_node = IRNode(
            node_type=IRNodeType.LITERAL, attributes={'value': 5}
        )
        right_node = IRNode(
            node_type=IRNodeType.LITERAL, attributes={'value': 10}
        )
        bin_op_node = IRNode(
            node_type=IRNodeType.BINARY_OPERATION,
            attributes={
                'operator': '+',
                'left_operand': left_node,
                'right_operand': right_node,
            },
        )
        self.ir.root.add_child(bin_op_node)
        self.analyzer.analyze(self.ir)
        inferred_type = self.analyzer.type_information.get(bin_op_node)
        self.assertEqual(inferred_type, 'int')

    def test_function_call_type_inference(self):
        """Test type inference for function calls."""
        func_def_node = IRNode(
            node_type=IRNodeType.FUNCTION_DEF,
            attributes={'name': 'add', 'return_type': 'int'},
        )
        func_call_node = IRNode(
            node_type=IRNodeType.FUNCTION_CALL,
            attributes={'function': func_def_node},
        )
        self.ir.root.add_child(func_call_node)
        self.analyzer.analyze(self.ir)
        inferred_type = self.analyzer.type_information.get(func_call_node)
        self.assertEqual(inferred_type, 'int')

    def test_assignment_type_inference(self):
        """Test type inference in assignments."""
        var_node = IRNode(
            node_type=IRNodeType.VARIABLE, attributes={'name': 'message'}
        )
        literal_node = IRNode(
            node_type=IRNodeType.LITERAL, attributes={'value': 'Hello'}
        )
        assign_node = IRNode(
            node_type=IRNodeType.ASSIGNMENT,
            attributes={'left': var_node, 'right': literal_node},
        )
        self.ir.root.add_child(assign_node)
        self.analyzer.analyze(self.ir)
        inferred_type = self.analyzer.type_information.get(var_node)
        self.assertEqual(inferred_type, 'str')

    def test_conditional_type_inference(self):
        """Test type inference for conditionals."""
        condition = IRNode(
            node_type=IRNodeType.LITERAL, attributes={'value': True}
        )
        true_branch = IRNode(
            node_type=IRNodeType.LITERAL, attributes={'value': 1}
        )
        false_branch = IRNode(
            node_type=IRNodeType.LITERAL, attributes={'value': 0}
        )
        cond_node = IRNode(
            node_type=IRNodeType.CONDITIONAL,
            attributes={
                'condition': condition,
                'true_branch': true_branch,
                'false_branch': false_branch,
            },
        )
        self.ir.root.add_child(cond_node)
        self.analyzer.analyze(self.ir)
        inferred_type = self.analyzer.type_information.get(cond_node)
        self.assertEqual(inferred_type, 'int')

    def test_loop_type_inference(self):
        """Test type inference for loops."""
        condition = IRNode(
            node_type=IRNodeType.LITERAL, attributes={'value': True}
        )
        body = IRNode(
            node_type=IRNodeType.FUNCTION_CALL,
            attributes={'function': IRNode(
                node_type=IRNodeType.FUNCTION_DEF,
                attributes={'name': 'do_something', 'return_type': 'void'}
            )},
        )
        loop_node = IRNode(
            node_type=IRNodeType.LOOP,
            attributes={
                'condition': condition,
                'body': body,
            },
        )
        self.ir.root.add_child(loop_node)
        self.analyzer.analyze(self.ir)
        inferred_type = self.analyzer.type_information.get(loop_node)
        self.assertEqual(inferred_type, 'void')

    def test_function_def_type_inference(self):
        """Test type inference for function definitions."""
        func_def_node = IRNode(
            node_type=IRNodeType.FUNCTION_DEF,
            attributes={
                'name': 'compute',
                'return_type': 'float',
                'parameters': [],
                'body': IRNode(
                    node_type=IRNodeType.RETURN,
                    attributes={'value': IRNode(
                        node_type=IRNodeType.LITERAL,
                        attributes={'value': 3.14}
                    )},
                ),
            },
        )
        self.ir.root.add_child(func_def_node)
        self.analyzer.analyze(self.ir)
        inferred_type = self.analyzer.type_information.get(func_def_node)
        self.assertEqual(inferred_type, 'float')

    def test_complex_expression_type_inference(self):
        """Test type inference for complex expressions."""
        left_node = IRNode(
            node_type=IRNodeType.LITERAL, attributes={'value': 2}
        )
        right_node = IRNode(
            node_type=IRNodeType.LITERAL, attributes={'value': 3.5}
        )
        bin_op_node = IRNode(
            node_type=IRNodeType.BINARY_OPERATION,
            attributes={
                'operator': '*',
                'left_operand': left_node,
                'right_operand': right_node,
            },
        )
        assign_node = IRNode(
            node_type=IRNodeType.ASSIGNMENT,
            attributes={
                'left': IRNode(
                    node_type=IRNodeType.VARIABLE, attributes={'name': 'result'}
                ),
                'right': bin_op_node,
            },
        )
        self.ir.root.add_child(assign_node)
        self.analyzer.analyze(self.ir)
        var_node = assign_node.attributes['left']
        inferred_type = self.analyzer.type_information.get(var_node)
        self.assertEqual(inferred_type, 'float')

    def test_program_node_type_inference(self):
        """Test that the program node does not get a type."""
        self.analyzer.analyze(self.ir)
        inferred_type = self.analyzer.type_information.get(self.ir.root)
        self.assertIsNone(inferred_type)


if __name__ == '__main__':
    unittest.main()
