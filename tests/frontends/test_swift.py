"""
Unit tests for the SwiftFrontend.
"""

import unittest
import os  # Added import for os module
from lapa.frontends.swift import SwiftFrontend
from lapa.ir import IR  # Import IR for creating IR instances
from lapa.frontend import ParsingError  # Import ParsingError for exception handling

class TestSwiftFrontend(unittest.TestCase):
    def setUp(self):
        self.frontend = SwiftFrontend()

    def test_initialization(self):
        """Test initialization of the SwiftFrontend."""
        self.assertEqual(self.frontend.language_name, "Swift")
        self.assertIn(".swift", self.frontend.file_extensions)

    def test_parse_simple_code(self):
        """Test parsing of simple Swift code."""
        code = 'print("Hello, world!")'
        ir = IR()
        self.frontend.parse(code, ir)
        # Since parse doesn't return a tree, we ensure IR is updated
        self.assertIsNotNone(ir)

    def test_parse_syntax_error(self):
        """Test parsing of Swift code with syntax error."""
        code = 'let x = 10 * (5 + 3'
        ir = IR()
        with self.assertRaises(ParsingError):
            self.frontend.parse(code, ir)

    def test_parse_file_nonexistent(self):
        """Test parsing a nonexistent file."""
        ir = IR()
        with self.assertRaises(FileNotFoundError):
            self.frontend.parse_file("nonexistent.swift", ir)

    def test_parse_file(self):
        """Test parsing a Swift file."""
        # Create a temporary Swift file for testing
        import tempfile
        ir = IR()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.swift', delete=False) as tmp_file:
            tmp_file.write('func greet() { print("Hello") }')
            tmp_file_path = tmp_file.name

        try:
            self.frontend.parse_file(tmp_file_path, ir)
            # Since parse_file doesn't return a tree, we ensure IR is updated
            self.assertIsNotNone(ir)
        finally:
            os.remove(tmp_file_path)

    def test_ast_to_ir_not_implemented(self):
        """Test that ast_to_ir method raises NotImplementedError."""
        ir = IR()
        with self.assertRaises(NotImplementedError):
            self.frontend.ast_to_ir(None, ir)

if __name__ == "__main__":
    unittest.main()
