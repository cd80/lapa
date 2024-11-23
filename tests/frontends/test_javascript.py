"""
Tests for the JavaScript/TypeScript language frontend.
"""

import pytest
from pathlib import Path
from typing import Optional, List
from unittest.mock import patch, MagicMock

from tree_sitter import Node, Tree

from lapa.frontend import ParsingError
from lapa.frontends.javascript import JavaScriptFrontend
from lapa.ir import IRNodeType


class MockNode:
    """Mock tree-sitter Node for testing."""
    def __init__(self, type_name: str, text: bytes = b"", children: Optional[List['MockNode']] = None, **fields):
        self.type = type_name
        self._text = text
        self.children = children or []
        self.fields = fields
        self.start_point = (0, 0)
    
    @property
    def text(self) -> bytes:
        """Get the node's text."""
        return self._text
    
    def child_by_field_name(self, name: str) -> Optional['MockNode']:
        """Get a child node by field name."""
        return self.fields.get(name)
    
    def children_by_field_name(self, name: str) -> List['MockNode']:
        """Get child nodes by field name."""
        return self.fields.get(name, [])


class MockTree:
    """Mock tree-sitter Tree for testing."""
    def __init__(self, root_node: MockNode):
        self.root_node = root_node


def test_javascript_frontend_features():
    """Test JavaScript frontend language features."""
    frontend = JavaScriptFrontend()
    features = frontend._get_language_features()
    
    assert features.has_classes is True
    assert features.has_interfaces is True  # Via TypeScript
    assert features.has_generics is True    # Via TypeScript
    assert features.has_exceptions is True
    assert features.has_async is True
    assert features.has_decorators is True  # Via TypeScript
    assert features.has_operator_overloading is False
    assert features.has_multiple_inheritance is False
    assert features.typing_system == "gradual"  # Due to TypeScript
    assert features.memory_management == "gc"


def test_javascript_frontend_file_extensions():
    """Test JavaScript frontend file extensions."""
    frontend = JavaScriptFrontend()
    extensions = frontend.get_file_extensions()
    
    assert ".js" in extensions
    assert ".jsx" in extensions
    assert ".ts" in extensions
    assert ".tsx" in extensions


def test_parse_nonexistent_file():
    """Test error when parsing nonexistent file."""
    frontend = JavaScriptFrontend()
    with pytest.raises(FileNotFoundError):
        frontend.parse_file("nonexistent.js")


@patch('lapa.frontends.javascript.create_parser')
def test_parse_simple_function(mock_create_parser):
    """Test parsing a simple JavaScript function."""
    code = """
    function greet(name) {
        return "Hello, " + name;
    }
    """
    
    # Create mock AST
    func_node = MockNode(
        "function_declaration",
        children=[
            MockNode("identifier", b"greet"),
            MockNode("formal_parameters"),
            MockNode("statement_block")
        ]
    )
    tree = MockTree(MockNode("program", children=[func_node]))
    
    # Mock parser
    mock_parser = MagicMock()
    mock_parser.parse.return_value = tree
    mock_create_parser.return_value = mock_parser
    
    frontend = JavaScriptFrontend()
    ir = frontend.parse_string(code)
    
    # Verify IR
    assert len(ir.root.children) == 1
    func = ir.root.children[0]
    assert func.node_type == IRNodeType.FUNCTION
    assert func.attributes["name"] == "greet"


@patch('lapa.frontends.javascript.create_parser')
def test_parse_class(mock_create_parser):
    """Test parsing a JavaScript class."""
    code = """
    class Person {
        constructor(name) {
            this.name = name;
        }
        
        greet() {
            return "Hello, " + this.name;
        }
    }
    """
    
    # Create mock AST
    class_node = MockNode(
        "class_declaration",
        children=[
            MockNode("identifier", b"Person"),
            MockNode("class_body")
        ]
    )
    tree = MockTree(MockNode("program", children=[class_node]))
    
    # Mock parser
    mock_parser = MagicMock()
    mock_parser.parse.return_value = tree
    mock_create_parser.return_value = mock_parser
    
    frontend = JavaScriptFrontend()
    ir = frontend.parse_string(code)
    
    # Verify IR
    assert len(ir.root.children) == 1
    class_ir = ir.root.children[0]
    assert class_ir.node_type == IRNodeType.CLASS
    assert class_ir.attributes["name"] == "Person"


@patch('lapa.frontends.javascript.create_parser')
def test_parse_imports(mock_create_parser):
    """Test parsing JavaScript imports."""
    code = """
    import { Component } from 'react';
    import DefaultExport from 'module';
    import * as utils from './utils';
    """
    
    # Create mock AST
    import_nodes = [
        MockNode(
            "import_declaration",
            children=[
                MockNode("string", b"'react'"),
                MockNode(
                    "import_specifier",
                    children=[MockNode("identifier", b"Component")]
                )
            ]
        ),
        MockNode(
            "import_declaration",
            children=[
                MockNode("string", b"'module'"),
                MockNode(
                    "import_specifier",
                    children=[MockNode("identifier", b"DefaultExport")]
                )
            ]
        )
    ]
    tree = MockTree(MockNode("program", children=import_nodes))
    
    # Mock parser
    mock_parser = MagicMock()
    mock_parser.parse.return_value = tree
    mock_create_parser.return_value = mock_parser
    
    frontend = JavaScriptFrontend()
    ir = frontend.parse_string(code)
    
    # Verify IR
    assert len(ir.root.children) == 2
    for node in ir.root.children:
        assert node.node_type == IRNodeType.IMPORT


@patch('lapa.frontends.javascript.create_parser')
def test_parse_async_function(mock_create_parser):
    """Test parsing an async JavaScript function."""
    code = """
    async function fetchData() {
        const response = await fetch('/api/data');
        return response.json();
    }
    """
    
    # Create mock AST
    func_node = MockNode(
        "function_declaration",
        children=[
            MockNode("async"),
            MockNode("identifier", b"fetchData"),
            MockNode("formal_parameters"),
            MockNode("statement_block")
        ]
    )
    tree = MockTree(MockNode("program", children=[func_node]))
    
    # Mock parser
    mock_parser = MagicMock()
    mock_parser.parse.return_value = tree
    mock_create_parser.return_value = mock_parser
    
    frontend = JavaScriptFrontend()
    ir = frontend.parse_string(code)
    
    # Verify IR
    assert len(ir.root.children) == 1
    func = ir.root.children[0]
    assert func.node_type == IRNodeType.FUNCTION
    assert func.attributes["name"] == "fetchData"
    assert func.attributes["is_async"] is True


def test_not_implemented_error():
    """Test NotImplementedError when parser is not available."""
    frontend = JavaScriptFrontend()
    frontend.parser = None
    
    with pytest.raises(NotImplementedError):
        frontend.parse_string("const x = 1;")


@patch('lapa.frontends.javascript.create_parser')
def test_parse_error(mock_create_parser):
    """Test handling of parsing errors."""
    mock_parser = MagicMock()
    mock_parser.parse.side_effect = Exception("Parse error")
    mock_create_parser.return_value = mock_parser
    
    frontend = JavaScriptFrontend()
    with pytest.raises(ParsingError):
        frontend.parse_string("invalid code")


@patch('lapa.frontends.javascript.create_parser')
def test_parse_variable_declarations(mock_create_parser):
    """Test parsing JavaScript variable declarations."""
    code = """
    const x = 1;
    let y = "hello";
    var z = true;
    """
    
    # Create mock AST
    var_nodes = [
        MockNode(
            "variable_declaration",
            children=[
                MockNode("const", b"const"),
                MockNode(
                    "variable_declarator",
                    children=[
                        MockNode("identifier", b"x"),
                        MockNode("number", b"1")
                    ]
                )
            ]
        ),
        MockNode(
            "variable_declaration",
            children=[
                MockNode("let", b"let"),
                MockNode(
                    "variable_declarator",
                    children=[
                        MockNode("identifier", b"y"),
                        MockNode("string", b"'hello'")
                    ]
                )
            ]
        )
    ]
    tree = MockTree(MockNode("program", children=var_nodes))
    
    # Mock parser
    mock_parser = MagicMock()
    mock_parser.parse.return_value = tree
    mock_create_parser.return_value = mock_parser
    
    frontend = JavaScriptFrontend()
    ir = frontend.parse_string(code)
    
    # Verify IR
    assert len(ir.root.children) == 2
    for node in ir.root.children:
        assert node.node_type == IRNodeType.VARIABLE
