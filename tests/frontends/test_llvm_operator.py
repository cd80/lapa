"""
Tests for the LLVM/Clang operator handling module.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from lapa.frontends.llvm.operator import (
    OperatorHandler,
    OperatorKind
)
from lapa.ir import IRNodeType, Position


class MockType:
    """Mock type for AST nodes."""
    def __init__(self, spelling: str, is_const: bool = False):
        self._spelling = spelling
        self._is_const = is_const
    
    @property
    def spelling(self) -> str:
        return self._spelling
    
    def is_const_qualified(self) -> bool:
        return self._is_const


class MockAccessSpecifier:
    """Mock access specifier."""
    def __init__(self, name: str):
        self.name = name


class MockParameter:
    """Mock parameter for operator functions."""
    def __init__(self, spelling: str, type_spelling: str, is_const: bool = False):
        self._spelling = spelling
        self.type = MockType(type_spelling, is_const)
    
    @property
    def spelling(self) -> str:
        return self._spelling


class MockNode:
    """Mock AST node."""
    def __init__(
        self,
        spelling: str,
        result_type: MockType = None,
        access: str = "public",
        is_const: bool = False,
        is_instance: bool = True,
        arguments=None
    ):
        self._spelling = spelling
        self.result_type = result_type or MockType("void")
        self.access_specifier = MockAccessSpecifier(access)
        self._is_const = is_const
        self._is_instance = is_instance
        self._arguments = [
            MockParameter(arg[0], arg[1], arg[2] if len(arg) > 2 else False)
            for arg in (arguments or [])
        ]
    
    @property
    def spelling(self) -> str:
        return self._spelling
    
    def is_const_method(self) -> bool:
        return self._is_const
    
    def is_instance_method(self) -> bool:
        return self._is_instance
    
    def get_arguments(self):
        return self._arguments


def test_operator_kind_constants():
    """Test operator kind constants."""
    assert OperatorKind.PLUS == "+"
    assert OperatorKind.MINUS == "-"
    assert OperatorKind.MULTIPLY == "*"
    assert OperatorKind.DIVIDE == "/"
    assert OperatorKind.SUBSCRIPT == "[]"
    assert OperatorKind.CALL == "()"
    assert OperatorKind.CONVERSION == "conversion"


def test_process_unary_operator():
    """Test processing unary operator."""
    handler = OperatorHandler()
    
    node = MockNode(
        "operator++",
        result_type=MockType("MyClass&"),
        is_const=False
    )
    
    op_info = handler.process_operator(node)
    
    assert op_info["name"] == "operator++"
    assert op_info["kind"] == OperatorKind.INCREMENT
    assert op_info["is_member"] is True
    assert op_info["is_const"] is False
    assert op_info["return_type"] == "MyClass&"
    assert op_info["access"] == "public"


def test_process_binary_operator():
    """Test processing binary operator."""
    handler = OperatorHandler()
    
    node = MockNode(
        "operator+",
        result_type=MockType("MyClass"),
        is_const=True,
        arguments=[("other", "const MyClass&", True)]
    )
    
    op_info = handler.process_operator(node)
    
    assert op_info["name"] == "operator+"
    assert op_info["kind"] == OperatorKind.PLUS
    assert op_info["is_member"] is True
    assert op_info["is_const"] is True
    assert op_info["return_type"] == "MyClass"
    assert len(op_info["parameters"]) == 1
    assert op_info["parameters"][0]["type"] == "const MyClass&"


def test_process_conversion_operator():
    """Test processing conversion operator."""
    handler = OperatorHandler()
    
    node = MockNode(
        "operator std::string",
        result_type=MockType("std::string"),
        is_const=True
    )
    
    op_info = handler.process_operator(node)
    
    assert op_info["name"] == "operator std::string"
    assert op_info["kind"] == OperatorKind.CONVERSION
    assert op_info["is_member"] is True
    assert op_info["is_const"] is True
    assert op_info["return_type"] == "std::string"
    assert op_info["target_type"] == "std::string"


def test_process_assignment_operator():
    """Test processing assignment operator."""
    handler = OperatorHandler()
    
    node = MockNode(
        "operator=",
        result_type=MockType("MyClass&"),
        is_const=False,
        arguments=[("other", "const MyClass&", True)]
    )
    
    op_info = handler.process_operator(node)
    
    assert op_info["name"] == "operator="
    assert op_info["kind"] == OperatorKind.ASSIGN
    assert op_info["is_member"] is True
    assert op_info["is_const"] is False
    assert op_info["return_type"] == "MyClass&"
    assert len(op_info["parameters"]) == 1
    assert op_info["parameters"][0]["type"] == "const MyClass&"


def test_process_subscript_operator():
    """Test processing subscript operator."""
    handler = OperatorHandler()
    
    node = MockNode(
        "operator[]",
        result_type=MockType("int&"),
        is_const=False,
        arguments=[("index", "size_t")]
    )
    
    op_info = handler.process_operator(node)
    
    assert op_info["name"] == "operator[]"
    assert op_info["kind"] == OperatorKind.SUBSCRIPT
    assert op_info["is_member"] is True
    assert op_info["is_const"] is False
    assert op_info["return_type"] == "int&"
    assert len(op_info["parameters"]) == 1
    assert op_info["parameters"][0]["type"] == "size_t"


def test_process_function_call_operator():
    """Test processing function call operator."""
    handler = OperatorHandler()
    
    node = MockNode(
        "operator()",
        result_type=MockType("int"),
        is_const=True,
        arguments=[
            ("x", "int"),
            ("y", "int")
        ]
    )
    
    op_info = handler.process_operator(node)
    
    assert op_info["name"] == "operator()"
    assert op_info["kind"] == OperatorKind.CALL
    assert op_info["is_member"] is True
    assert op_info["is_const"] is True
    assert op_info["return_type"] == "int"
    assert len(op_info["parameters"]) == 2
    assert op_info["parameters"][0]["type"] == "int"
    assert op_info["parameters"][1]["type"] == "int"


def test_create_operator_ir():
    """Test creating IR node for operator."""
    handler = OperatorHandler()
    
    node = MockNode(
        "operator+",
        result_type=MockType("MyClass"),
        is_const=True
    )
    
    position = Position(line=1, column=0, file="test.cpp")
    attributes = {"namespace": "test"}
    
    ir_node = handler.create_operator_ir(node, position, attributes)
    
    assert ir_node.node_type == IRNodeType.OPERATOR
    assert ir_node.position == position
    assert ir_node.attributes["name"] == "operator+"
    assert ir_node.attributes["kind"] == OperatorKind.PLUS
    assert ir_node.attributes["is_const"] is True
    assert ir_node.attributes["return_type"] == "MyClass"
    assert ir_node.attributes["namespace"] == "test"


def test_get_operator_kind():
    """Test getting operator kind."""
    handler = OperatorHandler()
    
    # Test various operator kinds
    assert handler._get_operator_kind(MockNode("operator+")) == OperatorKind.PLUS
    assert handler._get_operator_kind(MockNode("operator-=")) == OperatorKind.SUBTRACT_ASSIGN
    assert handler._get_operator_kind(MockNode("operator[]")) == OperatorKind.SUBSCRIPT
    assert handler._get_operator_kind(MockNode("operator bool")) == OperatorKind.CONVERSION


def test_get_conversion_type():
    """Test getting conversion type."""
    handler = OperatorHandler()
    
    # Test various conversion types
    assert handler._get_conversion_type(MockNode("operator int")) == "int"
    assert handler._get_conversion_type(MockNode("operator const std::string&")) == "std::string"
    assert handler._get_conversion_type(MockNode("operator volatile bool")) == "bool"
