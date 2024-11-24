"""
Unit tests for the Java Frontend.

This module contains tests for the Java frontend in the LAPA framework.
"""

import unittest
from lapa.frontends.java import JavaFrontend
from lapa.ir import IR

class TestJavaFrontend(unittest.TestCase):
    def setUp(self):
        self.frontend = JavaFrontend()

    def test_java_frontend_initialization(self):
        self.assertIsNotNone(self.frontend)
        self.assertEqual(self.frontend.language_name, "Java")

    def test_java_frontend_language_support(self):
        self.assertTrue(self.frontend.supports_language("Java"))
        self.assertFalse(self.frontend.supports_language("Python"))

    def test_java_frontend_file_extensions(self):
        self.assertTrue(self.frontend.supports_file_extension(".java"))
        self.assertFalse(self.frontend.supports_file_extension(".py"))

    def test_parse_simple_class(self):
        code = '''
        public class HelloWorld {
            public static void main(String[] args) {
                System.out.println("Hello, World!");
            }
        }
        '''
        ir = IR()
        self.frontend.parse(code, ir)
        self.assertIsNotNone(ir)
        self.assertGreater(len(ir.root.children), 0)

    def test_parse_syntax_error(self):
        code = 'public class {'
        ir = IR()
        with self.assertRaises(Exception):
            self.frontend.parse(code, ir)

if __name__ == '__main__':
    unittest.main()
