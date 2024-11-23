"""
Tests for the JavaScript/TypeScript language frontend.
"""

import pytest
from pathlib import Path
from textwrap import dedent

from lapa.frontends.javascript import JavaScriptFrontend
from lapa.frontend import ParsingError
from lapa.ir import IRNodeType


def test_javascript_frontend_features():
    """Test JavaScript/TypeScript frontend language features."""
    frontend = JavaScriptFrontend()
    features = frontend.features
    
    assert features.has_classes is True
    assert features.has_interfaces is True  # TypeScript support
    assert features.has_generics is True    # TypeScript support
    assert features.has_exceptions is True
    assert features.has_async is True
    assert features.has_decorators is True  # TypeScript support
    assert features.has_operator_overloading is False
    assert features.has_multiple_inheritance is False
    assert features.typing_system == "gradual"  # Due to TypeScript
    assert features.memory_management == "gc"


def test_javascript_frontend_file_extensions():
    """Test JavaScript/TypeScript frontend supported file extensions."""
    frontend = JavaScriptFrontend()
    extensions = frontend.get_file_extensions()
    
    assert ".js" in extensions
    assert ".jsx" in extensions
    assert ".ts" in extensions
    assert ".tsx" in extensions
    assert len(extensions) == 4


def test_parse_nonexistent_file():
    """Test handling of nonexistent files."""
    frontend = JavaScriptFrontend()
    
    with pytest.raises(FileNotFoundError):
        frontend.parse_file("nonexistent.js")


@pytest.mark.skip(reason="JavaScript parsing not yet implemented")
def test_parse_simple_function():
    """Test parsing a simple JavaScript function."""
    frontend = JavaScriptFrontend()
    code = dedent("""
    function hello(name) {
        return `Hello, ${name}!`;
    }
    """)
    
    ir = frontend.parse_string(code)
    
    # Check function node
    functions = [n for n in ir.root.children if n.node_type == IRNodeType.FUNCTION]
    assert len(functions) == 1
    func = functions[0]
    assert func.attributes["name"] == "hello"
    assert func.attributes["is_async"] is False


@pytest.mark.skip(reason="JavaScript parsing not yet implemented")
def test_parse_class():
    """Test parsing a JavaScript class."""
    frontend = JavaScriptFrontend()
    code = dedent("""
    class Person {
        constructor(name) {
            this.name = name;
        }
        
        greet() {
            return `Hello, I'm ${this.name}!`;
        }
    }
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
    assert any(m.attributes["name"] == "constructor" for m in methods)
    assert any(m.attributes["name"] == "greet" for m in methods)


@pytest.mark.skip(reason="JavaScript parsing not yet implemented")
def test_parse_typescript_interface():
    """Test parsing a TypeScript interface."""
    frontend = JavaScriptFrontend()
    code = dedent("""
    interface Person {
        name: string;
        age: number;
        greet(): string;
    }
    """)
    
    ir = frontend.parse_string(code)
    
    # This will need to be implemented when TypeScript support is added
    assert ir is not None


@pytest.mark.skip(reason="JavaScript parsing not yet implemented")
def test_parse_imports():
    """Test parsing import statements."""
    frontend = JavaScriptFrontend()
    code = dedent("""
    import { useState } from 'react';
    import * as utils from './utils';
    import defaultExport from 'module';
    """)
    
    ir = frontend.parse_string(code)
    
    imports = [n for n in ir.root.children if n.node_type == IRNodeType.IMPORT]
    assert len(imports) == 3


@pytest.mark.skip(reason="JavaScript parsing not yet implemented")
def test_parse_async_function():
    """Test parsing async function."""
    frontend = JavaScriptFrontend()
    code = dedent("""
    async function fetchData() {
        return await fetch('api/data');
    }
    """)
    
    ir = frontend.parse_string(code)
    
    functions = [n for n in ir.root.children if n.node_type == IRNodeType.FUNCTION]
    assert len(functions) == 1
    assert functions[0].attributes["is_async"] is True


@pytest.mark.skip(reason="JavaScript parsing not yet implemented")
def test_parse_typescript_decorators():
    """Test parsing TypeScript decorators."""
    frontend = JavaScriptFrontend()
    code = dedent("""
    @Component({
        selector: 'app-root'
    })
    class AppComponent {
        @Input() title: string;
    }
    """)
    
    ir = frontend.parse_string(code)
    
    classes = [n for n in ir.root.children if n.node_type == IRNodeType.CLASS]
    assert len(classes) == 1
    assert "Component" in classes[0].attributes["decorators"]


def test_not_implemented_error():
    """Test that unimplemented features raise NotImplementedError."""
    frontend = JavaScriptFrontend()
    
    with pytest.raises(NotImplementedError):
        frontend.parse_string("const x = 1;")


@pytest.mark.skip(reason="JavaScript parsing not yet implemented")
def test_parse_jsx():
    """Test parsing JSX syntax."""
    frontend = JavaScriptFrontend()
    code = dedent("""
    function App() {
        return (
            <div>
                <h1>Hello, World!</h1>
            </div>
        );
    }
    """)
    
    ir = frontend.parse_string(code)
    
    functions = [n for n in ir.root.children if n.node_type == IRNodeType.FUNCTION]
    assert len(functions) == 1
    assert functions[0].attributes["name"] == "App"


@pytest.mark.skip(reason="JavaScript parsing not yet implemented")
def test_parse_typescript_generics():
    """Test parsing TypeScript generics."""
    frontend = JavaScriptFrontend()
    code = dedent("""
    function identity<T>(arg: T): T {
        return arg;
    }
    """)
    
    ir = frontend.parse_string(code)
    
    functions = [n for n in ir.root.children if n.node_type == IRNodeType.FUNCTION]
    assert len(functions) == 1
    assert "generics" in functions[0].attributes
