"""
Tests for LLVM/Clang functionality.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from lapa.frontends.llvm import (
    LLVMContext,
    LLVMNotFoundError,
    LLVM_AVAILABLE,
    cursor_kind_name as get_cursor_kind_name,
    type_kind_name as get_type_kind_name,
    access_specifier_name as get_access_specifier_name
)


def test_llvm_context_initialization():
    """Test LLVM context initialization."""
    if not LLVM_AVAILABLE:
        pytest.skip("LLVM/Clang not available")
    
    with LLVMContext() as ctx:
        assert ctx.index is not None
        assert isinstance(ctx.include_paths, list)
        assert isinstance(ctx.definitions, dict)


def test_llvm_context_missing_library():
    """Test error when LLVM/Clang is missing."""
    with patch('lapa.frontends.llvm.LLVM_AVAILABLE', False):
        with pytest.raises(LLVMNotFoundError):
            LLVMContext()


def test_parse_simple_cpp_file():
    """Test parsing simple C++ file."""
    if not LLVM_AVAILABLE:
        pytest.skip("LLVM/Clang not available")
    
    code = """
    int main() {
        return 0;
    }
    """
    
    with LLVMContext() as ctx:
        tu = ctx.parse_string(code)
        assert tu is not None


def test_parse_cpp_class():
    """Test parsing C++ class."""
    if not LLVM_AVAILABLE:
        pytest.skip("LLVM/Clang not available")
    
    code = """
    class MyClass {
    public:
        MyClass() {}
        ~MyClass() {}
        
        void method() {}
        
    private:
        int field;
    };
    """
    
    with LLVMContext() as ctx:
        tu = ctx.parse_string(code)
        assert tu is not None


def test_context_manager():
    """Test context manager functionality."""
    if not LLVM_AVAILABLE:
        pytest.skip("LLVM/Clang not available")
    
    with LLVMContext() as ctx:
        assert ctx is not None


def test_parse_without_context():
    """Test parsing without context manager."""
    if not LLVM_AVAILABLE:
        pytest.skip("LLVM/Clang not available")
    
    ctx = LLVMContext()
    tu = ctx.parse_string("int x = 42;")
    assert tu is not None


def test_parse_with_compiler_args():
    """Test parsing with compiler arguments."""
    if not LLVM_AVAILABLE:
        pytest.skip("LLVM/Clang not available")
    
    code = """
    #ifdef DEBUG
    int debug_var = 1;
    #else
    int debug_var = 0;
    #endif
    """
    
    with LLVMContext() as ctx:
        tu = ctx.parse_string(code, args=["-DDEBUG"])
        assert tu is not None


def test_cursor_kind_name():
    """Test cursor kind name mapping."""
    class MockCursorKind:
        def __init__(self, name):
            self.name = name
    
    kind = MockCursorKind("FUNCTION_DECL")
    assert get_cursor_kind_name(kind) == "function_decl"


def test_type_kind_name():
    """Test type kind name mapping."""
    class MockTypeKind:
        def __init__(self, name):
            self.name = name
    
    kind = MockTypeKind("INT")
    assert get_type_kind_name(kind) == "int"


def test_access_specifier_name():
    """Test access specifier name mapping."""
    class MockAccessSpecifier:
        def __init__(self, name):
            self.name = name
    
    access = MockAccessSpecifier("PUBLIC")
    assert get_access_specifier_name(access) == "public"


def test_parse_template():
    """Test parsing C++ template."""
    if not LLVM_AVAILABLE:
        pytest.skip("LLVM/Clang not available")
    
    code = """
    template<typename T>
    class Container {
    public:
        T value;
        Container(T v) : value(v) {}
    };
    """
    
    with LLVMContext() as ctx:
        tu = ctx.parse_string(code)
        assert tu is not None


def test_parse_namespace():
    """Test parsing C++ namespace."""
    if not LLVM_AVAILABLE:
        pytest.skip("LLVM/Clang not available")
    
    code = """
    namespace test {
        class MyClass {};
        void function() {}
    }
    """
    
    with LLVMContext() as ctx:
        tu = ctx.parse_string(code)
        assert tu is not None
