"""
Tests for the LLVM/Clang AST converter.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from lapa.frontends.llvm.ast import ASTConverter
from lapa.ir import IRNodeType


class MockLocation:
    """Mock location for AST nodes."""
    def __init__(self, line: int = 1, column: int = 0, file: str = "<test>"):
        self.line = line
        self.column = column
        self.file = file


class MockAccessSpecifier:
    """Mock access specifier."""
    def __init__(self, name: str):
        self.name = name.upper()
    
    def lower(self) -> str:
        return self.name.lower()


class MockCursor:
    """Mock cursor for AST nodes."""
    def __init__(self, kind_name: str, spelling: str = "", children=None, **kwargs):
        self.kind = MagicMock()
        self.kind.name = kind_name
        self._spelling = spelling
        self.children = children or []
        self.location = MockLocation()
        self.referenced = None
        self.access_specifier = MockAccessSpecifier("public")
        
        # Set additional attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @property
    def spelling(self) -> str:
        return self._spelling
    
    def get_children(self):
        return self.children
    
    def get_arguments(self):
        return []
    
    def is_inline(self) -> bool:
        return False
    
    def is_const_method(self) -> bool:
        return False
    
    def is_virtual_method(self) -> bool:
        return False
    
    def is_static_method(self) -> bool:
        return False
    
    def is_defaulted(self) -> bool:
        return False
    
    def is_deleted(self) -> bool:
        return False


class MockType:
    """Mock type for AST nodes."""
    def __init__(self, spelling: str = ""):
        self._spelling = spelling
    
    @property
    def spelling(self) -> str:
        return self._spelling


class MockAST:
    """Mock AST for testing."""
    def __init__(self, cursor: MockCursor):
        self.cursor = cursor


def test_ast_converter_initialization():
    """Test AST converter initialization."""
    converter = ASTConverter()
    assert converter.ir is not None
    assert converter.current_namespace == []


def test_convert_empty_ast():
    """Test converting an empty AST."""
    ast = MockAST(MockCursor("TRANSLATION_UNIT"))
    converter = ASTConverter()
    ir = converter.convert(ast)
    assert len(ir.root.children) == 0


def test_convert_namespace():
    """Test converting a namespace."""
    ast = MockAST(
        MockCursor("TRANSLATION_UNIT", children=[
            MockCursor("NAMESPACE", "test_ns")
        ])
    )
    
    converter = ASTConverter()
    ir = converter.convert(ast)
    
    assert len(ir.root.children) == 1
    namespace = ir.root.children[0]
    assert namespace.node_type == IRNodeType.NAMESPACE
    assert namespace.attributes["name"] == "test_ns"


def test_convert_class():
    """Test converting a class."""
    ast = MockAST(
        MockCursor("TRANSLATION_UNIT", children=[
            MockCursor("CLASS_DECL", "TestClass")
        ])
    )
    
    converter = ASTConverter()
    ir = converter.convert(ast)
    
    assert len(ir.root.children) == 1
    class_node = ir.root.children[0]
    assert class_node.node_type == IRNodeType.CLASS
    assert class_node.attributes["name"] == "TestClass"
    assert class_node.attributes["bases"] == []


def test_convert_class_with_bases():
    """Test converting a class with base classes."""
    base_type = MockType("BaseClass")
    ast = MockAST(
        MockCursor("TRANSLATION_UNIT", children=[
            MockCursor("CLASS_DECL", "DerivedClass", children=[
                MockCursor("CXX_BASE_SPECIFIER", type=base_type)
            ])
        ])
    )
    
    converter = ASTConverter()
    ir = converter.convert(ast)
    
    assert len(ir.root.children) == 1
    class_node = ir.root.children[0]
    assert class_node.attributes["name"] == "DerivedClass"
    assert class_node.attributes["bases"] == ["BaseClass"]


def test_convert_function():
    """Test converting a function."""
    return_type = MockType("int")
    ast = MockAST(
        MockCursor("TRANSLATION_UNIT", children=[
            MockCursor(
                "FUNCTION_DECL",
                "test_func",
                result_type=return_type
            )
        ])
    )
    
    converter = ASTConverter()
    ir = converter.convert(ast)
    
    assert len(ir.root.children) == 1
    func = ir.root.children[0]
    assert func.node_type == IRNodeType.FUNCTION
    assert func.attributes["name"] == "test_func"
    assert func.attributes["return_type"] == "int"


def test_convert_method():
    """Test converting a class method."""
    return_type = MockType("void")
    ast = MockAST(
        MockCursor("TRANSLATION_UNIT", children=[
            MockCursor("CLASS_DECL", "TestClass", children=[
                MockCursor(
                    "CXX_METHOD",
                    "test_method",
                    result_type=return_type,
                    access_specifier=MockAccessSpecifier("public")
                )
            ])
        ])
    )
    
    converter = ASTConverter()
    ir = converter.convert(ast)
    
    assert len(ir.root.children) == 1
    class_node = ir.root.children[0]
    assert len(class_node.children) == 1
    method = class_node.children[0]
    assert method.node_type == IRNodeType.FUNCTION
    assert method.attributes["name"] == "test_method"
    assert method.attributes["return_type"] == "void"
    assert method.attributes["access"] == "public"


def test_convert_constructor():
    """Test converting a constructor."""
    ast = MockAST(
        MockCursor("TRANSLATION_UNIT", children=[
            MockCursor("CLASS_DECL", "TestClass", children=[
                MockCursor(
                    "CONSTRUCTOR",
                    "TestClass",
                    access_specifier=MockAccessSpecifier("public")
                )
            ])
        ])
    )
    
    converter = ASTConverter()
    ir = converter.convert(ast)
    
    assert len(ir.root.children) == 1
    class_node = ir.root.children[0]
    assert len(class_node.children) == 1
    ctor = class_node.children[0]
    assert ctor.node_type == IRNodeType.CONSTRUCTOR
    assert ctor.attributes["name"] == "TestClass"
    assert ctor.attributes["access"] == "public"


def test_convert_template():
    """Test converting a template."""
    ast = MockAST(
        MockCursor("TRANSLATION_UNIT", children=[
            MockCursor("CLASS_TEMPLATE", "Vector", children=[
                MockCursor("TEMPLATE_TYPE_PARAMETER", "T")
            ])
        ])
    )
    
    converter = ASTConverter()
    ir = converter.convert(ast)
    
    assert len(ir.root.children) == 1
    template = ir.root.children[0]
    assert template.node_type == IRNodeType.TEMPLATE
    assert template.attributes["name"] == "Vector"
    assert template.attributes["kind"] == "class"
    assert len(template.attributes["parameters"]) == 1
    assert template.attributes["parameters"][0]["name"] == "T"


def test_convert_friend():
    """Test converting a friend declaration."""
    ast = MockAST(
        MockCursor("TRANSLATION_UNIT", children=[
            MockCursor("CLASS_DECL", "TestClass", children=[
                MockCursor(
                    "FRIEND_DECL",
                    referenced=MockCursor("CLASS_DECL", "FriendClass")
                )
            ])
        ])
    )
    
    converter = ASTConverter()
    ir = converter.convert(ast)
    
    assert len(ir.root.children) == 1
    class_node = ir.root.children[0]
    assert len(class_node.children) == 1
    friend = class_node.children[0]
    assert friend.node_type == IRNodeType.FRIEND
    assert friend.attributes["target"] == "FriendClass"


def test_convert_using():
    """Test converting a using declaration."""
    ast = MockAST(
        MockCursor("TRANSLATION_UNIT", children=[
            MockCursor(
                "USING_DECLARATION",
                "vector",
                referenced=MockCursor("CLASS_TEMPLATE", "std::vector")
            )
        ])
    )
    
    converter = ASTConverter()
    ir = converter.convert(ast)
    
    assert len(ir.root.children) == 1
    using = ir.root.children[0]
    assert using.node_type == IRNodeType.USING
    assert using.attributes["name"] == "vector"
    assert using.attributes["target"] == "std::vector"


def test_convert_nested_namespace():
    """Test converting nested namespaces."""
    ast = MockAST(
        MockCursor("TRANSLATION_UNIT", children=[
            MockCursor("NAMESPACE", "outer", children=[
                MockCursor("NAMESPACE", "inner", children=[
                    MockCursor("CLASS_DECL", "TestClass")
                ])
            ])
        ])
    )
    
    converter = ASTConverter()
    ir = converter.convert(ast)
    
    assert len(ir.root.children) == 1
    outer = ir.root.children[0]
    assert outer.node_type == IRNodeType.NAMESPACE
    assert outer.attributes["name"] == "outer"
    
    assert len(outer.children) == 1
    inner = outer.children[0]
    assert inner.node_type == IRNodeType.NAMESPACE
    assert inner.attributes["name"] == "inner"
    
    assert len(inner.children) == 1
    class_node = inner.children[0]
    assert class_node.node_type == IRNodeType.CLASS
    assert class_node.attributes["name"] == "TestClass"
    assert class_node.attributes["namespace"] == "outer::inner"
