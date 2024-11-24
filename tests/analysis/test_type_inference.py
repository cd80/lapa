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
        try:
            self.analyzer.analyze(self.ir)
        except Exception as e:
            self.fail(f"TypeInferenceAnalyzer raised an exception on empty IR: {e}")

        # Ensure that type_information is empty
        self.assertEqual(len(self.analyzer.type_information), 0)

    def test_literal_type_inference(self):
        """Test type inference for literal nodes."""
        # Integer literal
        int_node = IRNode(IRNodeType.LITERAL)
        int_node.attributes['value'] = 42
        self.assertEqual(self.analyzer.infer_literal_type(int_node), 'int')

        # Float literal
        float_node = IRNode(IRNodeType.LITERAL)
        float_node.attributes['value'] = 3.14
        self.assertEqual(self.analyzer.infer_literal_type(float_node), 'float')

        # String literal
        str_node = IRNode(IRNodeType.LITERAL)
        str_node.attributes['value'] = "hello"
        self.assertEqual(self.analyzer.infer_literal_type(str_node), 'str')

        # Boolean literal
        bool_node = IRNode(IRNodeType.LITERAL)
        bool_node.attributes['value'] = True
        self.assertEqual(self.analyzer.infer_literal_type(bool_node), 'bool')

        # Unknown literal
        unknown_node = IRNode(IRNodeType.LITERAL)
        unknown_node.attributes['value'] = None
        self.assertEqual(self.analyzer.infer_literal_type(unknown_node), 'unknown')

    def test_variable_type_inference(self):
        """Test type inference for variable nodes."""
        # Variable with definition
        var_node = IRNode(IRNodeType.VARIABLE)
        def_node = IRNode(IRNodeType.LITERAL)
        def_node.attributes['value'] = 42
        var_node.attributes['definition'] = def_node
        
        self.assertEqual(self.analyzer.infer_variable_type(var_node), 'int')

        # Variable without definition
        undefined_var = IRNode(IRNodeType.VARIABLE)
        self.assertEqual(self.analyzer.infer_variable_type(undefined_var), 'unknown')

    def test_binary_operation_type_inference(self):
        """Test type inference for binary operations."""
        # Test same type operands
        self.assertEqual(
            self.analyzer.resolve_binary_operation_type('+', 'int', 'int'),
            'int'
        )
        self.assertEqual(
            self.analyzer.resolve_binary_operation_type('>', 'int', 'int'),
            'bool'
        )

        # Test type promotion
        self.assertEqual(
            self.analyzer.resolve_binary_operation_type('+', 'int', 'float'),
            'float'
        )

        # Test comparison operators
        self.assertEqual(
            self.analyzer.resolve_binary_operation_type('==', 'int', 'float'),
            'bool'
        )

        # Test unknown type handling
        self.assertEqual(
            self.analyzer.resolve_binary_operation_type('+', 'unknown', 'int'),
            'unknown'
        )

    def test_function_call_type_inference(self):
        """Test type inference for function calls."""
        # Create a function definition node
        func_def = IRNode(IRNodeType.FUNCTION_DEF)
        func_def.attributes['return_type'] = 'int'

        # Create a function call node
        func_call = IRNode(IRNodeType.FUNCTION_CALL)
        func_call.attributes['function'] = func_def

        self.assertEqual(self.analyzer.infer_function_call_type(func_call), 'int')

        # Test function call without definition
        undefined_call = IRNode(IRNodeType.FUNCTION_CALL)
        self.assertEqual(self.analyzer.infer_function_call_type(undefined_call), 'unknown')

    def test_assignment_type_inference(self):
        """Test type inference for assignments."""
        # Create nodes for assignment
        assign_node = IRNode(IRNodeType.ASSIGNMENT)
        left_node = IRNode(IRNodeType.VARIABLE)
        right_node = IRNode(IRNodeType.LITERAL)
        right_node.attributes['value'] = 42
        assign_node.attributes['left'] = left_node
        assign_node.attributes['right'] = right_node

        # Infer type
        inferred_type = self.analyzer.infer_type(assign_node)
        self.assertEqual(inferred_type, 'int')
        # Check that the variable's type was updated
        self.assertEqual(self.analyzer.type_information[left_node], 'int')

    def test_conditional_type_inference(self):
        """Test type inference for conditional statements."""
        # Create nodes for conditional
        cond_node = IRNode(IRNodeType.CONDITIONAL)
        condition = IRNode(IRNodeType.LITERAL)
        condition.attributes['value'] = True
        true_branch = IRNode(IRNodeType.LITERAL)
        true_branch.attributes['value'] = 1
        false_branch = IRNode(IRNodeType.LITERAL)
        false_branch.attributes['value'] = 0
        
        cond_node.attributes['condition'] = condition
        cond_node.attributes['true_branch'] = true_branch
        cond_node.attributes['false_branch'] = false_branch

        # Infer type
        inferred_type = self.analyzer.infer_type(cond_node)
        self.assertEqual(inferred_type, 'void')

    def test_loop_type_inference(self):
        """Test type inference for loops."""
        # Create nodes for loop
        loop_node = IRNode(IRNodeType.LOOP)
        condition = IRNode(IRNodeType.LITERAL)
        condition.attributes['value'] = True
        body = IRNode(IRNodeType.LITERAL)
        body.attributes['value'] = 42
        
        loop_node.attributes['condition'] = condition
        loop_node.attributes['body'] = body

        # Infer type
        inferred_type = self.analyzer.infer_type(loop_node)
        self.assertEqual(inferred_type, 'void')

    def test_function_def_type_inference(self):
        """Test type inference for function definitions."""
        # Create function definition node
        func_def = IRNode(IRNodeType.FUNCTION_DEF)
        param = IRNode(IRNodeType.VARIABLE)
        body = IRNode(IRNodeType.LITERAL)
        body.attributes['value'] = 42
        
        func_def.attributes['parameters'] = [param]
        func_def.attributes['body'] = body
        func_def.attributes['return_type'] = 'int'

        # Infer type
        inferred_type = self.analyzer.infer_type(func_def)
        self.assertEqual(inferred_type, 'int')

    def test_program_node_type_inference(self):
        """Test type inference for program nodes."""
        program_node = IRNode(IRNodeType.PROGRAM)
        self.assertIsNone(self.analyzer.infer_type(program_node))

    def test_complex_expression_type_inference(self):
        """Test type inference for complex expressions."""
        # Create a complex expression: (1 + 2.0) * 3
        mul_node = IRNode(IRNodeType.BINARY_OPERATION)
        add_node = IRNode(IRNodeType.BINARY_OPERATION)
        int_lit1 = IRNode(IRNodeType.LITERAL)
        float_lit = IRNode(IRNodeType.LITERAL)
        int_lit2 = IRNode(IRNodeType.LITERAL)

        int_lit1.attributes['value'] = 1
        float_lit.attributes['value'] = 2.0
        int_lit2.attributes['value'] = 3

        add_node.attributes['operator'] = '+'
        add_node.attributes['left_operand'] = int_lit1
        add_node.attributes['right_operand'] = float_lit

        mul_node.attributes['operator'] = '*'
        mul_node.attributes['left_operand'] = add_node
        mul_node.attributes['right_operand'] = int_lit2

        # First infer type of the addition
        add_type = self.analyzer.infer_type(add_node)
        self.assertEqual(add_type, 'float')  # int + float = float

        # Then infer type of the multiplication
        mul_type = self.analyzer.infer_type(mul_node)
        self.assertEqual(mul_type, 'float')  # float * int = float

if __name__ == '__main__':
    unittest.main()
