"""
Integration tests for LLVM/Clang functionality.
"""

import pytest
from pathlib import Path

from lapa.frontends.llvm import (
    LLVMContext,
    LLVMNotFoundError,
    cursor_kind_name,
    type_kind_name,
    access_specifier_name
)


def test_llvm_context_error_handling():
    """Test error handling when LLVM/Clang is not available."""
    # Temporarily override LLVM_AVAILABLE
    from lapa.frontends import llvm
    original_availability = llvm.LLVM_AVAILABLE
    llvm.LLVM_AVAILABLE = False
    try:
        with pytest.raises(LLVMNotFoundError):
            LLVMContext()
    finally:
        llvm.LLVM_AVAILABLE = original_availability


def test_llvm_context_compiler_args():
    """Test handling of compiler arguments."""
    try:
        with LLVMContext() as ctx:
            tu = ctx.parse_string("int main() {}", args=["-std=c++17", "-Wall"])
            assert tu is not None
    except LLVMNotFoundError:
        pytest.skip("LLVM/Clang not available")


def test_llvm_context_parse_error():
    """Test handling of parsing errors."""
    try:
        with LLVMContext() as ctx:
            with pytest.raises(Exception) as exc_info:
                ctx.parse_string("invalid code")
            assert "Failed to parse code" in str(exc_info.value)
    except LLVMNotFoundError:
        pytest.skip("LLVM/Clang not available")


def test_llvm_context_multiple_files():
    """Test parsing multiple files in the same context."""
    try:
        with LLVMContext() as ctx:
            tu1 = ctx.parse_string("int x = 1;")
            tu2 = ctx.parse_string("int y = 2;")
            assert tu1 is not None
            assert tu2 is not None
    except LLVMNotFoundError:
        pytest.skip("LLVM/Clang not available")


def test_llvm_context_include_paths():
    """Test handling of include paths."""
    include_paths = ["/usr/include", "/usr/local/include"]
    try:
        with LLVMContext(include_paths=include_paths) as ctx:
            tu = ctx.parse_string('#include <vector>')
            assert tu is not None
    except LLVMNotFoundError:
        pytest.skip("LLVM/Clang not available")


def test_llvm_context_preprocessor_definitions():
    """Test handling of preprocessor definitions."""
    definitions = {"DEBUG": "1", "VERSION": "\"1.0\""}
    try:
        with LLVMContext(definitions=definitions) as ctx:
            tu = ctx.parse_string('#ifdef DEBUG\nint x;\n#endif')
            assert tu is not None
    except LLVMNotFoundError:
        pytest.skip("LLVM/Clang not available")


def test_llvm_context_language_standard():
    """Test handling of language standard selection."""
    standards = ["c++11", "c++14", "c++17", "c++20"]
    try:
        for std in standards:
            with LLVMContext() as ctx:
                tu = ctx.parse_string(
                    'template<typename T> void f() {}',
                    args=[f"-std={std}"]
                )
                assert tu is not None
    except LLVMNotFoundError:
        pytest.skip("LLVM/Clang not available")


def test_llvm_context_optimization_flags():
    """Test handling of optimization flags."""
    opt_flags = ["-O0", "-O1", "-O2", "-O3"]
    try:
        for flag in opt_flags:
            with LLVMContext() as ctx:
                tu = ctx.parse_string('int f() { return 42; }', args=[flag])
                assert tu is not None
    except LLVMNotFoundError:
        pytest.skip("LLVM/Clang not available")


def test_llvm_context_warning_flags():
    """Test handling of warning flags."""
    warning_flags = ["-Wall", "-Wextra", "-Werror", "-Wpedantic"]
    try:
        with LLVMContext() as ctx:
            tu = ctx.parse_string('int f() { return 42; }', args=warning_flags)
            assert tu is not None
    except LLVMNotFoundError:
        pytest.skip("LLVM/Clang not available")


def test_llvm_context_diagnostic_handling():
    """Test handling of diagnostics."""
    try:
        with LLVMContext() as ctx:
            with pytest.raises(Exception) as exc_info:
                # Intentionally malformed code
                ctx.parse_string('int main() { return')
            assert "Failed to parse code" in str(exc_info.value)
    except LLVMNotFoundError:
        pytest.skip("LLVM/Clang not available")


def test_cursor_kind_name_mapping():
    """Test cursor kind name mapping."""
    class MockCursorKind:
        def __init__(self, name):
            self.name = name

    cursor_kinds = [
        "UNEXPOSED_DECL",
        "STRUCT_DECL",
        "UNION_DECL",
        "CLASS_DECL",
        "ENUM_DECL",
        "FIELD_DECL",
        "ENUM_CONSTANT_DECL",
        "FUNCTION_DECL",
        "VAR_DECL",
        "PARM_DECL",
        "TEMPLATE_TYPE_PARAM",
        "TEMPLATE_NON_TYPE_PARAM",
        "TEMPLATE_TEMPLATE_PARAM",
        "FUNCTION_TEMPLATE",
        "CLASS_TEMPLATE",
        "CLASS_TEMPLATE_PARTIAL_SPECIALIZATION",
        "NAMESPACE",
        "CONSTRUCTOR",
        "DESTRUCTOR",
        "CONVERSION_FUNCTION",
        "TYPE_REF",
        "TEMPLATE_REF",
        "NAMESPACE_REF",
        "MEMBER_REF",
        "LABEL_REF",
        "OVERLOADED_DECL_REF",
        "VARIABLE_REF",
    ]

    for kind in cursor_kinds:
        mock_kind = MockCursorKind(kind)
        assert cursor_kind_name(mock_kind) == kind.lower()


def test_type_kind_name_mapping():
    """Test type kind name mapping."""
    class MockTypeKind:
        def __init__(self, name):
            self.name = name

    type_kinds = [
        "VOID",
        "BOOL",
        "CHAR_U",
        "UCHAR",
        "CHAR16",
        "CHAR32",
        "USHORT",
        "UINT",
        "ULONG",
        "ULONGLONG",
        "CHAR_S",
        "SCHAR",
        "WCHAR",
        "SHORT",
        "INT",
        "LONG",
        "LONGLONG",
        "FLOAT",
        "DOUBLE",
        "LONGDOUBLE",
        "NULLPTR",
        "OVERLOAD",
        "DEPENDENT",
        "OBJCID",
        "OBJCCLASS",
        "OBJCSEL",
        "COMPLEX",
        "POINTER",
        "BLOCKPOINTER",
        "LVALUEREFERENCE",
        "RVALUEREFERENCE",
        "RECORD",
        "ENUM",
        "TYPEDEF",
        "OBJCINTERFACE",
        "OBJCOBJECTPOINTER",
        "FUNCTIONNOPROTO",
        "FUNCTIONPROTO",
        "CONSTANTARRAY",
        "VECTOR",
        "INCOMPLETEARRAY",
        "VARIABLEARRAY",
        "DEPENDENTSIZEDARRAY",
        "MEMBERPOINTER",
        "AUTO",
        "ELABORATED",
        "PIPE",
        "OCLIMAGE1DRO",
        "OCLIMAGE1DARRAYRO",
        "OCLIMAGE1DBUFFERRO",
        "OCLIMAGE2DRO",
        "OCLIMAGE2DARRAYRO",
        "OCLIMAGE2DDEPTHRO",
        "OCLIMAGE2DARRAYDEPTHRO",
        "OCLIMAGE2DMSAARO",
        "OCLIMAGE2DARRAYMSAARO",
        "OCLIMAGE2DMSAADEPTHRO",
        "OCLIMAGE2DARRAYMSAADEPTHRO",
        "OCLIMAGE3DRO",
        "OCLSAMPLER",
        "OCLEVENT",
        "OCLQUEUE",
        "OCLRESERVEID",
    ]

    for kind in type_kinds:
        mock_kind = MockTypeKind(kind)
        assert type_kind_name(mock_kind) == kind.lower()


def test_access_specifier_name_mapping():
    """Test access specifier name mapping."""
    class MockAccessSpecifier:
        def __init__(self, name):
            self.name = name

    access_specs = [
        "INVALID",
        "PUBLIC",
        "PROTECTED",
        "PRIVATE",
        "NONE",
    ]

    for spec in access_specs:
        mock_spec = MockAccessSpecifier(spec)
        assert access_specifier_name(mock_spec) == spec.lower()
