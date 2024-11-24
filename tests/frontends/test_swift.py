"""
Unit tests for the SwiftFrontend.
"""

import unittest
from lapa.frontends.swift import SwiftFrontend

class TestSwiftFrontend(unittest.TestCase):
    def setUp(self):
        self.frontend = SwiftFrontend()

    def test_initialization(self):
        """Test initialization of the SwiftFrontend."""
        self.assertEqual(self.frontend.language, "Swift")
        self.assertIn(".swift", self.frontend.file_extensions)

    def test_parse_not_implemented(self):
        """Test that parse method raises NotImplementedError."""
        with self.assertRaises(NotImplementedError):
            self.frontend.parse("")

    def test_ast_to_ir_not_implemented(self):
        """Test that ast_to_ir method raises NotImplementedError."""
        with self.assertRaises(NotImplementedError):
            self.frontend.ast_to_ir(None)

if __name__ == "__main__":
    unittest.main()
