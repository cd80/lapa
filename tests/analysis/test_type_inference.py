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

if __name__ == '__main__':
    unittest.main()
