"""
Tests for the C/C++ language frontend.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from lapa.frontend import ParsingError
from lapa.frontends.cpp import CPPFrontend
from lapa.ir import IRNodeType


def test_cpp_frontend_features():
    """Test C/C++ frontend language features."""
    frontend = CPPFrontend()
    features = frontend._get_language_features()
    
    # C++ features
    assert features.has_classes is True
    assert features.has_interfaces is False
    assert features.has_generics is True  # Templates
    assert features.has_exceptions is True
    assert features.has_async is False
    assert features.has_decorators is False
    assert features.has_operator_overloading is True
    assert features.has_multiple_inheritance is True
    assert features.typing_system == "static"
    assert features.memory_management == "manual"


def test_cpp_frontend_file_extensions():
    """Test C/C++ frontend file extensions."""
    frontend = CPPFrontend()
    extensions = frontend.get_file_extensions()
    
    # C extensions
    assert ".c" in extensions
    assert ".h" in extensions
    
    # C++ extensions
    assert ".cpp" in extensions
    assert ".hpp" in extensions
    assert ".cc" in extensions
    assert ".hh" in extensions
    assert ".cxx" in extensions
    assert ".hxx" in extensions


def test_parse_nonexistent_file():
    """Test error when parsing nonexistent file."""
    frontend = CPPFrontend()
    with pytest.raises(FileNotFoundError):
        frontend.parse_file("nonexistent.cpp")


def test_not_implemented_error():
    """Test NotImplementedError when parser is not available."""
    frontend = CPPFrontend()
    with pytest.raises(NotImplementedError):
        frontend.parse_string("int main() { return 0; }")


@pytest.mark.skip(reason="C/C++ parsing not yet implemented")
def test_parse_simple_function():
    """Test parsing a simple C++ function."""
    code = """
    int add(int a, int b) {
        return a + b;
    }
    """
    frontend = CPPFrontend()
    ir = frontend.parse_string(code)
    
    assert len(ir.root.children) == 1
    func = ir.root.children[0]
    assert func.node_type == IRNodeType.FUNCTION
    assert func.attributes["name"] == "add"
    assert func.attributes["return_type"] == "int"


@pytest.mark.skip(reason="C/C++ parsing not yet implemented")
def test_parse_class():
    """Test parsing a C++ class."""
    code = """
    class Person {
    public:
        Person(std::string name) : name_(name) {}
        
        std::string getName() const {
            return name_;
        }
        
    private:
        std::string name_;
    };
    """
    frontend = CPPFrontend()
    ir = frontend.parse_string(code)
    
    assert len(ir.root.children) == 1
    class_ir = ir.root.children[0]
    assert class_ir.node_type == IRNodeType.CLASS
    assert class_ir.attributes["name"] == "Person"


@pytest.mark.skip(reason="C/C++ parsing not yet implemented")
def test_parse_template():
    """Test parsing a C++ template."""
    code = """
    template<typename T>
    T max(T a, T b) {
        return (a > b) ? a : b;
    }
    """
    frontend = CPPFrontend()
    ir = frontend.parse_string(code)
    
    assert len(ir.root.children) == 1
    func = ir.root.children[0]
    assert func.node_type == IRNodeType.FUNCTION
    assert func.attributes["name"] == "max"
    assert func.attributes["is_template"] is True


@pytest.mark.skip(reason="C/C++ parsing not yet implemented")
def test_parse_includes():
    """Test parsing C++ includes."""
    code = """
    #include <iostream>
    #include "myheader.h"
    """
    frontend = CPPFrontend()
    ir = frontend.parse_string(code)
    
    assert len(ir.root.children) == 2
    for node in ir.root.children:
        assert node.node_type == IRNodeType.IMPORT


@pytest.mark.skip(reason="C/C++ parsing not yet implemented")
def test_parse_namespace():
    """Test parsing C++ namespace."""
    code = """
    namespace math {
        double PI = 3.14159;
        
        double circumference(double radius) {
            return 2 * PI * radius;
        }
    }
    """
    frontend = CPPFrontend()
    ir = frontend.parse_string(code)
    
    assert len(ir.root.children) == 1
    namespace = ir.root.children[0]
    assert namespace.node_type == IRNodeType.NAMESPACE
    assert namespace.attributes["name"] == "math"


@pytest.mark.skip(reason="C/C++ parsing not yet implemented")
def test_parse_operator_overload():
    """Test parsing C++ operator overloading."""
    code = """
    class Complex {
    public:
        Complex operator+(const Complex& other) const {
            return Complex(real + other.real, imag + other.imag);
        }
    private:
        double real;
        double imag;
    };
    """
    frontend = CPPFrontend()
    ir = frontend.parse_string(code)
    
    assert len(ir.root.children) == 1
    class_ir = ir.root.children[0]
    assert class_ir.node_type == IRNodeType.CLASS
    assert any(
        child.attributes.get("is_operator") is True
        for child in class_ir.children
    )


@pytest.mark.skip(reason="C/C++ parsing not yet implemented")
def test_parse_multiple_inheritance():
    """Test parsing C++ multiple inheritance."""
    code = """
    class Derived : public Base1, public Base2 {
    public:
        void method() override {
            Base1::method();
            Base2::method();
        }
    };
    """
    frontend = CPPFrontend()
    ir = frontend.parse_string(code)
    
    assert len(ir.root.children) == 1
    class_ir = ir.root.children[0]
    assert class_ir.node_type == IRNodeType.CLASS
    assert len(class_ir.attributes["bases"]) == 2


@pytest.mark.skip(reason="C/C++ parsing not yet implemented")
def test_parse_friend():
    """Test parsing C++ friend declarations."""
    code = """
    class A {
        friend class B;
        friend void func(A&);
    private:
        int data;
    };
    """
    frontend = CPPFrontend()
    ir = frontend.parse_string(code)
    
    assert len(ir.root.children) == 1
    class_ir = ir.root.children[0]
    assert class_ir.node_type == IRNodeType.CLASS
    assert any(
        child.attributes.get("is_friend") is True
        for child in class_ir.children
    )
