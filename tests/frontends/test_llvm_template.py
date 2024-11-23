"""
Tests for the LLVM/Clang template handling module.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from lapa.frontends.llvm.template import (
    TemplateHandler,
    TemplateParameter,
    TemplateSpecialization
)
from lapa.ir import IRNodeType, Position


class MockKind:
    """Mock kind for AST nodes."""
    def __init__(self, name: str):
        self.name = name


class MockType:
    """Mock type for AST nodes."""
    def __init__(self, spelling: str):
        self.spelling = spelling


class MockNode:
    """Mock AST node."""
    def __init__(
        self,
        kind_name: str,
        spelling: str = "",
        type_spelling: str = "",
        children=None
    ):
        self.kind = MockKind(kind_name)
        self._spelling = spelling
        self.type = MockType(type_spelling)
        self.children = children or []
    
    @property
    def spelling(self) -> str:
        return self._spelling
    
    def get_children(self):
        return self.children


def test_template_parameter_initialization():
    """Test template parameter initialization."""
    param = TemplateParameter("T", "type", "int")
    assert param.name == "T"
    assert param.kind == "type"
    assert param.default == "int"


def test_template_specialization_initialization():
    """Test template specialization initialization."""
    spec = TemplateSpecialization("vector", ["int"])
    assert spec.template_name == "vector"
    assert spec.args == ["int"]


def test_process_template_type_parameter():
    """Test processing template type parameter."""
    handler = TemplateHandler()
    
    # Create mock node for type parameter with default
    default_type = MockNode("TYPE_REF", type_spelling="int")
    param_node = MockNode(
        "TEMPLATE_TYPE_PARAMETER",
        spelling="T",
        children=[default_type]
    )
    
    params = handler.process_template_parameters(
        MockNode("TEMPLATE_DECL", children=[param_node])
    )
    
    assert len(params) == 1
    assert params[0]["name"] == "T"
    assert params[0]["kind"] == "type"
    assert params[0]["default"] == "int"


def test_process_template_non_type_parameter():
    """Test processing non-type template parameter."""
    handler = TemplateHandler()
    
    # Create mock node for non-type parameter with default
    default_value = MockNode("INTEGER_LITERAL", spelling="42")
    param_node = MockNode(
        "TEMPLATE_NON_TYPE_PARAMETER",
        spelling="N",
        type_spelling="size_t",
        children=[default_value]
    )
    
    params = handler.process_template_parameters(
        MockNode("TEMPLATE_DECL", children=[param_node])
    )
    
    assert len(params) == 1
    assert params[0]["name"] == "N"
    assert params[0]["kind"] == "non-type"
    assert params[0]["type"] == "size_t"
    assert params[0]["default"] == "42"


def test_process_template_template_parameter():
    """Test processing template template parameter."""
    handler = TemplateHandler()
    
    # Create mock node for template parameter with nested parameters
    nested_param = MockNode(
        "TEMPLATE_TYPE_PARAMETER",
        spelling="U"
    )
    default_template = MockNode("TEMPLATE_REF", spelling="std::allocator")
    param_node = MockNode(
        "TEMPLATE_TEMPLATE_PARAMETER",
        spelling="Alloc",
        children=[nested_param, default_template]
    )
    
    params = handler.process_template_parameters(
        MockNode("TEMPLATE_DECL", children=[param_node])
    )
    
    assert len(params) == 1
    assert params[0]["name"] == "Alloc"
    assert params[0]["kind"] == "template"
    assert len(params[0]["params"]) == 1
    assert params[0]["default"] == "std::allocator"


def test_process_specialization():
    """Test processing template specialization."""
    handler = TemplateHandler()
    
    # Create mock nodes for specialization
    type_arg = MockNode(
        "TEMPLATE_TYPE_PARAMETER",
        type_spelling="int"
    )
    value_arg = MockNode(
        "TEMPLATE_NON_TYPE_PARAMETER",
        spelling="3",
        type_spelling="size_t"
    )
    spec_node = MockNode(
        "CLASS_TEMPLATE_PARTIAL_SPECIALIZATION",
        spelling="vector<int, 3>",
        children=[type_arg, value_arg]
    )
    
    spec_info = handler.process_specialization(spec_node)
    
    assert spec_info["template_name"] == "vector<int, 3>"
    assert len(spec_info["args"]) == 2
    assert spec_info["args"][0]["kind"] == "type"
    assert spec_info["args"][0]["type"] == "int"
    assert spec_info["args"][1]["kind"] == "non-type"
    assert spec_info["args"][1]["value"] == "3"
    assert spec_info["args"][1]["type"] == "size_t"


def test_create_template_ir():
    """Test creating IR node for template."""
    handler = TemplateHandler()
    
    # Create mock nodes for template with specialization
    type_param = MockNode(
        "TEMPLATE_TYPE_PARAMETER",
        spelling="T"
    )
    spec_node = MockNode(
        "CLASS_TEMPLATE_PARTIAL_SPECIALIZATION",
        spelling="vector<int>",
        children=[
            MockNode(
                "TEMPLATE_TYPE_PARAMETER",
                type_spelling="int"
            )
        ]
    )
    template_node = MockNode(
        "CLASS_TEMPLATE",
        spelling="vector",
        children=[type_param, spec_node]
    )
    
    position = Position(line=1, column=0, file="test.cpp")
    template_ir = handler.create_template_ir(
        template_node,
        position,
        "class",
        {"namespace": "std"}
    )
    
    assert template_ir.node_type == IRNodeType.TEMPLATE
    assert template_ir.attributes["name"] == "vector"
    assert template_ir.attributes["kind"] == "class"
    assert template_ir.attributes["namespace"] == "std"
    assert len(template_ir.attributes["parameters"]) == 1
    
    # Check specialization
    assert len(template_ir.children) == 1
    spec_ir = template_ir.children[0]
    assert spec_ir.node_type == IRNodeType.TEMPLATE
    assert spec_ir.attributes["kind"] == "specialization"
    assert spec_ir.attributes["template_name"] == "vector<int>"
    assert len(spec_ir.attributes["args"]) == 1


def test_is_partial_specialization():
    """Test checking for partial specialization."""
    handler = TemplateHandler()
    
    # Full specialization
    full_spec = MockNode(
        "CLASS_TEMPLATE_SPECIALIZATION",
        spelling="vector<int>",
        children=[]
    )
    assert not handler._is_partial_specialization(full_spec)
    
    # Partial specialization
    partial_spec = MockNode(
        "CLASS_TEMPLATE_PARTIAL_SPECIALIZATION",
        spelling="vector<T*, N>",
        children=[
            MockNode("TEMPLATE_TYPE_PARAMETER", spelling="T"),
            MockNode("TEMPLATE_NON_TYPE_PARAMETER", spelling="N")
        ]
    )
    assert handler._is_partial_specialization(partial_spec)


def test_default_values():
    """Test handling of default values."""
    handler = TemplateHandler()
    
    # Test default type
    type_node = MockNode(
        "TEMPLATE_TYPE_PARAMETER",
        children=[MockNode("TYPE_REF", type_spelling="int")]
    )
    assert handler._get_default_type(type_node) == "int"
    
    # Test default value
    value_node = MockNode(
        "TEMPLATE_NON_TYPE_PARAMETER",
        children=[MockNode("INTEGER_LITERAL", spelling="42")]
    )
    assert handler._get_default_value(value_node) == "42"
    
    # Test default template
    template_node = MockNode(
        "TEMPLATE_TEMPLATE_PARAMETER",
        children=[MockNode("TEMPLATE_REF", spelling="std::allocator")]
    )
    assert handler._get_default_template(template_node) == "std::allocator"
