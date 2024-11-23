"""
Tests for the LLVM/Clang integration module.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from lapa.frontends.llvm import (
    LLVMContext,
    LLVMNotFoundError,
    LLVM_AVAILABLE,
    get_cursor_kind_name,
    get_type_kind_name,
    get_access_specifier_name
)


@pytest.mark.skipif(not LLVM_AVAILABLE, reason="LLVM/Clang not available")
def test_llvm_context_initialization():
    """Test LLVM context initialization."""
    with patch('lapa.frontends.llvm.clang.Config.set_library_file') as mock_set_lib:
        context = LLVMContext()
        mock_set_lib.assert_called_once()


def test_llvm_context_missing_library():
    """Test error when libclang is not found."""
    if not LLVM_AVAILABLE:
        with pytest.raises(LLVMNotFoundError):
            LLVMContext()
    else:
        with patch('lapa.frontends.llvm.clang.Config.set_library_file') as mock_set_lib, \
             patch('os.path.exists', return_value=False), \
             patch('lapa.frontends.llvm.clang.conf.get_cindex_library') as mock_get_lib:
            mock_set_lib.side_effect = Exception("Library not found")
            mock_get_lib.side_effect = Exception("Library not found")
            
            with pytest.raises(RuntimeError) as exc_info:
                LLVMContext()
            assert "Could not find libclang" in str(exc_info.value)


@pytest.mark.skipif(not LLVM_AVAILABLE, reason="LLVM/Clang not available")
def test_parse_simple_cpp_file():
    """Test parsing a simple C++ file."""
    code = """
    int add(int a, int b) {
        return a + b;
    }
    """
    
    with LLVMContext() as context:
        tu = context.parse_string(code)
        assert tu is not None
        
        # Find the add function
        cursor = next(
            c for c in tu.cursor.get_children()
            if c.kind.name == "FUNCTION_DECL" and c.spelling == "add"
        )
        assert cursor is not None
        assert cursor.result_type.spelling == "int"
        assert len(list(cursor.get_arguments())) == 2


@pytest.mark.skipif(not LLVM_AVAILABLE, reason="LLVM/Clang not available")
def test_parse_cpp_class():
    """Test parsing a C++ class."""
    code = """
    class MyClass {
    public:
        MyClass() {}
        void method() {}
    private:
        int data;
    };
    """
    
    with LLVMContext() as context:
        tu = context.parse_string(code, filename="test.cpp")
        assert tu is not None
        
        # Find the class
        cursor = next(
            c for c in tu.cursor.get_children()
            if c.kind.name == "CLASS_DECL" and c.spelling == "MyClass"
        )
        assert cursor is not None
        assert len(list(cursor.get_children())) > 0


@pytest.mark.skipif(not LLVM_AVAILABLE, reason="LLVM/Clang not available")
def test_context_manager():
    """Test LLVM context manager."""
    with patch('lapa.frontends.llvm.clang.Index.create') as mock_create:
        mock_index = MagicMock()
        mock_create.return_value = mock_index
        
        with LLVMContext() as context:
            assert context.index == mock_index
        
        assert context.index is None


@pytest.mark.skipif(not LLVM_AVAILABLE, reason="LLVM/Clang not available")
def test_parse_without_context():
    """Test error when parsing without initialized context."""
    context = LLVMContext()
    with pytest.raises(RuntimeError) as exc_info:
        context.parse_file("test.cpp")
    assert "LLVM context not initialized" in str(exc_info.value)


@pytest.mark.skipif(not LLVM_AVAILABLE, reason="LLVM/Clang not available")
def test_parse_with_compiler_args():
    """Test parsing with additional compiler arguments."""
    code = """
    #include <vector>
    std::vector<int> nums;
    """
    
    with LLVMContext() as context:
        tu = context.parse_string(
            code,
            args=["-std=c++17", "-I/usr/include"]
        )
        assert tu is not None


def test_cursor_kind_name():
    """Test getting cursor kind name."""
    if not LLVM_AVAILABLE:
        with pytest.raises(LLVMNotFoundError):
            get_cursor_kind_name(None)
    else:
        mock_cursor = MagicMock()
        mock_cursor.kind.name = "FUNCTION_DECL"
        assert get_cursor_kind_name(mock_cursor) == "FUNCTION_DECL"


def test_type_kind_name():
    """Test getting type kind name."""
    if not LLVM_AVAILABLE:
        with pytest.raises(LLVMNotFoundError):
            get_type_kind_name(None)
    else:
        mock_type = MagicMock()
        mock_type.kind.name = "INT"
        assert get_type_kind_name(mock_type) == "INT"


def test_access_specifier_name():
    """Test getting access specifier name."""
    if not LLVM_AVAILABLE:
        with pytest.raises(LLVMNotFoundError):
            get_access_specifier_name(None)
    else:
        mock_cursor = MagicMock()
        mock_cursor.access_specifier.name = "PRIVATE"
        assert get_access_specifier_name(mock_cursor) == "PRIVATE"


@pytest.mark.skipif(not LLVM_AVAILABLE, reason="LLVM/Clang not available")
def test_parse_template():
    """Test parsing C++ template."""
    code = """
    template<typename T>
    T max(T a, T b) {
        return (a > b) ? a : b;
    }
    """
    
    with LLVMContext() as context:
        tu = context.parse_string(code, filename="test.cpp")
        assert tu is not None
        
        # Find the template function
        cursor = next(
            c for c in tu.cursor.get_children()
            if c.kind.name == "FUNCTION_TEMPLATE" and c.spelling == "max"
        )
        assert cursor is not None


@pytest.mark.skipif(not LLVM_AVAILABLE, reason="LLVM/Clang not available")
def test_parse_namespace():
    """Test parsing C++ namespace."""
    code = """
    namespace test {
        void func() {}
    }
    """
    
    with LLVMContext() as context:
        tu = context.parse_string(code)
        assert tu is not None
        
        # Find the namespace
        cursor = next(
            c for c in tu.cursor.get_children()
            if c.kind.name == "NAMESPACE" and c.spelling == "test"
        )
        assert cursor is not None
