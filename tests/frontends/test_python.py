"""
Tests for the Python language frontend.
"""

import ast
import pytest
from pathlib import Path
from textwrap import dedent

from lapa.frontends.python import PythonFrontend
from lapa.frontend import ParsingError
from lapa.ir import IRNodeType


def test_python_frontend_features():
    """Test Python frontend language features."""
    frontend = PythonFrontend()
    features = frontend.features
    
    assert features.has_classes is True
    assert features.has_interfaces is False
    assert features.has_generics is True
    assert features.has_exceptions is True
    assert features.has_async is True
    assert features.has_decorators is True
    assert features.has_operator_overloading is True
    assert features.has_multiple_inheritance is True
    assert features.typing_system == "dynamic"
    assert features.memory_management == "gc"


def test_python_frontend_file_extensions():
    """Test Python frontend supported file extensions."""
    frontend = PythonFrontend()
    extensions = frontend.get_file_extensions()
    
    assert ".py" in extensions
    assert ".pyw" in extensions
    assert len(extensions) == 2


def test_parse_simple_function():
    """Test parsing a simple Python function."""
    frontend = PythonFrontend()
    code = dedent("""
    def hello(name: str) -> str:
        return f"Hello, {name}!"
    """)
    
    ir = frontend.parse_string(code)
    
    # Check function node
    functions = [n for n in ir.root.children if n.node_type == IRNodeType.FUNCTION]
    assert len(functions) == 1
    func = functions[0]
    assert func.attributes["name"] == "hello"
    assert func.attributes["is_async"] is False
    
    # Check return statement
    returns = [n for n in func.children if n.node_type == IRNodeType.RETURN]
    assert len(returns) == 1


def test_parse_class():
    """Test parsing a Python class."""
    frontend = PythonFrontend()
    code = dedent("""
    class Person:
        def __init__(self, name: str):
            self.name = name
        
        def greet(self) -> str:
            return f"Hello, I'm {self.name}!"
    """)
    
    ir = frontend.parse_string(code)
    
    # Check class node
    classes = [n for n in ir.root.children if n.node_type == IRNodeType.CLASS]
    assert len(classes) == 1
    cls = classes[0]
    assert cls.attributes["name"] == "Person"
    
    # Check methods
    methods = [n for n in cls.children if n.node_type == IRNodeType.FUNCTION]
    assert len(methods) == 2
    assert any(m.attributes["name"] == "__init__" for m in methods)
    assert any(m.attributes["name"] == "greet" for m in methods)


def test_parse_imports():
    """Test parsing import statements."""
    frontend = PythonFrontend()
    code = dedent("""
    import os
    from typing import List, Optional
    import sys as system
    """)
    
    ir = frontend.parse_string(code)
    
    imports = [n for n in ir.root.children if n.node_type == IRNodeType.IMPORT]
    assert len(imports) == 4  # os, List, Optional, sys
    
    # Check regular import
    os_import = next(i for i in imports if i.attributes["name"] == "os")
    assert os_import.attributes["asname"] is None
    
    # Check from import
    list_import = next(i for i in imports if i.attributes["name"] == "List")
    assert list_import.attributes["module"] == "typing"
    
    # Check aliased import
    sys_import = next(i for i in imports if i.attributes["name"] == "sys")
    assert sys_import.attributes["asname"] == "system"


def test_parse_async_function():
    """Test parsing async function."""
    frontend = PythonFrontend()
    code = dedent("""
    async def fetch_data():
        return await some_api_call()
    """)
    
    ir = frontend.parse_string(code)
    
    functions = [n for n in ir.root.children if n.node_type == IRNodeType.FUNCTION]
    assert len(functions) == 1
    assert functions[0].attributes["is_async"] is True


def test_parse_decorated_function():
    """Test parsing decorated function."""
    frontend = PythonFrontend()
    code = dedent("""
    @property
    @deprecated
    def name(self) -> str:
        return self._name
    """)
    
    ir = frontend.parse_string(code)
    
    functions = [n for n in ir.root.children if n.node_type == IRNodeType.FUNCTION]
    assert len(functions) == 1
    assert "property" in functions[0].attributes["decorators"]
    assert "deprecated" in functions[0].attributes["decorators"]


def test_parse_control_flow():
    """Test parsing control flow statements."""
    frontend = PythonFrontend()
    code = dedent("""
    def check(x):
        if x > 0:
            return "positive"
        elif x < 0:
            return "negative"
        else:
            return "zero"
    """)
    
    ir = frontend.parse_string(code)
    
    functions = [n for n in ir.root.children if n.node_type == IRNodeType.FUNCTION]
    assert len(functions) == 1
    
    control_flows = [n for n in functions[0].children if n.node_type == IRNodeType.CONTROL_FLOW]
    assert len(control_flows) > 0


def test_parse_loops():
    """Test parsing loop statements."""
    frontend = PythonFrontend()
    code = dedent("""
    def process():
        for i in range(10):
            print(i)
        
        while True:
            break
    """)
    
    ir = frontend.parse_string(code)
    
    functions = [n for n in ir.root.children if n.node_type == IRNodeType.FUNCTION]
    assert len(functions) == 1
    
    loops = [n for n in functions[0].children if n.node_type == IRNodeType.LOOP]
    assert len(loops) == 2


def test_parse_syntax_error():
    """Test handling of syntax errors."""
    frontend = PythonFrontend()
    code = "def invalid syntax:"
    
    with pytest.raises(ParsingError) as exc_info:
        frontend.parse_string(code)
    # Python's syntax error messages can vary, just verify we get a ParsingError
    assert isinstance(exc_info.value, ParsingError)
    assert exc_info.value.position is not None  # Should have position info


def test_parse_nonexistent_file():
    """Test handling of nonexistent files."""
    frontend = PythonFrontend()
    
    with pytest.raises(FileNotFoundError):
        frontend.parse_file("nonexistent.py")


def test_parse_assignments():
    """Test parsing assignment statements."""
    frontend = PythonFrontend()
    code = dedent("""
    x = 1
    y, z = 2, 3
    obj.attr = "value"
    """)
    
    ir = frontend.parse_string(code)
    
    assignments = [n for n in ir.root.children if n.node_type == IRNodeType.ASSIGNMENT]
    assert len(assignments) == 3


def test_parse_function_calls():
    """Test parsing function calls."""
    frontend = PythonFrontend()
    code = dedent("""
    print("hello")
    func(1, b=2)
    obj.method()
    """)
    
    ir = frontend.parse_string(code)
    
    calls = [n for n in ir.root.children if n.node_type == IRNodeType.CALL]
    assert len(calls) == 3
