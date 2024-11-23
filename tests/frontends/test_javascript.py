"""
Tests for JavaScript frontend without mocking.
"""

from pathlib import Path
import pytest

from lapa.frontends.javascript import JavaScriptFrontend
from lapa.frontend import ParsingError, Frontend
from lapa.ir import IR


def test_javascript_frontend_features():
    """Test JavaScript frontend feature support."""
    frontend = JavaScriptFrontend()
    
    assert frontend.supports_language("javascript")
    assert frontend.supports_language("JavaScript")
    assert not frontend.supports_language("python")
    
    assert frontend.supports_extension(".js")
    assert frontend.supports_extension(".JS")
    assert not frontend.supports_extension(".py")


def test_javascript_frontend_file_extensions():
    """Test JavaScript frontend file extension handling."""
    frontend = JavaScriptFrontend()
    
    assert frontend.supports_extension(".js")
    assert frontend.supports_extension(".mjs")
    assert frontend.supports_extension(".cjs")
    assert frontend.supports_extension(".jsx")
    assert frontend.supports_extension(".ts")  # TypeScript is supported


def test_parse_nonexistent_file():
    """Test handling of nonexistent file."""
    frontend = JavaScriptFrontend()
    ir = IR()
    
    with pytest.raises(FileNotFoundError):
        frontend.parse_file("nonexistent.js", ir)


def test_parse_simple_function():
    """Test parsing simple function."""
    frontend = JavaScriptFrontend()
    ir = IR()
    
    code = """
    function add(a, b) {
        return a + b;
    }
    """
    
    with pytest.raises(NotImplementedError, match="Function processing not implemented"):
        frontend.parse_string(code, ir)


def test_parse_class():
    """Test parsing class definition."""
    frontend = JavaScriptFrontend()
    ir = IR()
    
    code = """
    class Calculator {
        constructor() {
            this.value = 0;
        }
        
        add(x) {
            this.value += x;
        }
    }
    """
    
    with pytest.raises(NotImplementedError, match="Class processing not implemented"):
        frontend.parse_string(code, ir)


def test_parse_imports():
    """Test parsing import statements."""
    frontend = JavaScriptFrontend()
    ir = IR()
    
    code = """
    import { useState } from 'react';
    import defaultExport from 'module';
    import * as name from 'module';
    """
    
    with pytest.raises(NotImplementedError, match="Import processing not implemented"):
        frontend.parse_string(code, ir)


def test_parse_async_function():
    """Test parsing async function."""
    frontend = JavaScriptFrontend()
    ir = IR()
    
    code = """
    async function fetchData() {
        const response = await fetch('api/data');
        return response.json();
    }
    """
    
    with pytest.raises(NotImplementedError, match="Function processing not implemented"):
        frontend.parse_string(code, ir)


def test_not_implemented_error():
    """Test handling of not implemented features."""
    frontend = JavaScriptFrontend()
    
    with pytest.raises(NotImplementedError):
        frontend.build_ast("test.js")


def test_parse_error():
    """Test handling of parse errors."""
    frontend = JavaScriptFrontend()
    ir = IR()
    
    code = "function() {"
    
    with pytest.raises(ParsingError):
        frontend.parse_string(code, ir)


def test_parse_variable_declarations():
    """Test parsing variable declarations."""
    frontend = JavaScriptFrontend()
    ir = IR()
    
    code = """
    var x = 1;
    let y = 'hello';
    const z = true;
    """
    
    with pytest.raises(NotImplementedError, match="Variable processing not implemented"):
        frontend.parse_string(code, ir)
