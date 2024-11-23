"""
Tests for Python frontend.
"""

import ast
from pathlib import Path
import pytest
from unittest.mock import MagicMock

from lapa.frontend import LanguageFeature, ParsingError
from lapa.frontends.python import PythonFrontend
from lapa.ir import IR


def test_python_frontend_features():
    """Test Python frontend features."""
    frontend = PythonFrontend()
    features = frontend._get_language_features()
    
    assert LanguageFeature.FUNCTIONS in features
    assert LanguageFeature.CLASSES in features
    assert LanguageFeature.INHERITANCE in features
    assert LanguageFeature.DECORATORS in features
    assert LanguageFeature.ANNOTATIONS in features
    assert LanguageFeature.GENERATORS in features
    assert LanguageFeature.ASYNC_AWAIT in features
    assert LanguageFeature.EXCEPTIONS in features
    assert LanguageFeature.GARBAGE_COLLECTION in features
    assert LanguageFeature.MODULES in features
    assert LanguageFeature.PACKAGES in features
    assert LanguageFeature.TYPE_INFERENCE in features
    assert LanguageFeature.LAMBDA_FUNCTIONS in features
    assert LanguageFeature.REFLECTION in features
    assert LanguageFeature.COMPILE_TIME_EVALUATION in features


def test_python_frontend_file_extensions():
    """Test Python frontend file extensions."""
    frontend = PythonFrontend()
    extensions = frontend.get_file_extensions()
    
    assert ".py" in extensions
    assert ".pyi" in extensions
    assert ".pyx" in extensions
    assert ".pxd" in extensions


def test_parse_simple_function():
    """Test parsing simple function."""
    frontend = PythonFrontend()
    ir = IR()
    
    code = """
def hello(name: str) -> str:
    return f"Hello {name}!"
"""
    
    frontend.parse_string(code, ir)
    # TODO: Add assertions about IR content


def test_parse_class():
    """Test parsing class definition."""
    frontend = PythonFrontend()
    ir = IR()
    
    code = """
class Person:
    def __init__(self, name: str):
        self.name = name

    def greet(self) -> str:
        return f"Hello, I'm {self.name}!"
"""
    
    frontend.parse_string(code, ir)
    # TODO: Add assertions about IR content


def test_parse_imports():
    """Test parsing import statements."""
    frontend = PythonFrontend()
    ir = IR()
    
    code = """
import os
from typing import List, Optional
import sys as system
"""
    
    frontend.parse_string(code, ir)
    # TODO: Add assertions about IR content


def test_parse_async_function():
    """Test parsing async function."""
    frontend = PythonFrontend()
    ir = IR()
    
    code = """
async def fetch_data():
    return await some_api_call()
"""
    
    frontend.parse_string(code, ir)
    # TODO: Add assertions about IR content


def test_parse_decorated_function():
    """Test parsing decorated function."""
    frontend = PythonFrontend()
    ir = IR()
    
    code = """
@property
@deprecated
def name(self) -> str:
    return self._name
"""
    
    frontend.parse_string(code, ir)
    # TODO: Add assertions about IR content


def test_parse_control_flow():
    """Test parsing control flow statements."""
    frontend = PythonFrontend()
    ir = IR()
    
    code = """
def check(x):
    if x > 0:
        return "positive"
    elif x < 0:
        return "negative"
    else:
        return "zero"
"""
    
    frontend.parse_string(code, ir)
    # TODO: Add assertions about IR content


def test_parse_loops():
    """Test parsing loop statements."""
    frontend = PythonFrontend()
    ir = IR()
    
    code = """
def process():
    for i in range(10):
        print(i)

    while True:
        break
"""
    
    frontend.parse_string(code, ir)
    # TODO: Add assertions about IR content


def test_parse_syntax_error():
    """Test handling of syntax errors."""
    frontend = PythonFrontend()
    ir = IR()
    code = "def invalid syntax:"
    
    with pytest.raises(ParsingError):
        frontend.parse_string(code, ir)


def test_parse_nonexistent_file():
    """Test handling of nonexistent files."""
    frontend = PythonFrontend()
    ir = IR()
    
    with pytest.raises(FileNotFoundError):
        frontend.parse_file("nonexistent.py", ir)


def test_parse_assignments():
    """Test parsing assignment statements."""
    frontend = PythonFrontend()
    ir = IR()
    
    code = """
x = 1
y, z = 2, 3
obj.attr = "value"
"""
    
    frontend.parse_string(code, ir)
    # TODO: Add assertions about IR content


def test_parse_function_calls():
    """Test parsing function calls."""
    frontend = PythonFrontend()
    ir = IR()
    
    code = """
print("hello")
func(1, b=2)
obj.method()
"""
    
    frontend.parse_string(code, ir)
    # TODO: Add assertions about IR content
