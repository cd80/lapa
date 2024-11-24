"""
Unit tests for the DependencyAnalyzer.
"""

import unittest
from lapa.ir import IR, IRNode
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

if __name__ == '__main__':
    unittest.main()
