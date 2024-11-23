"""
LLVM/Clang integration for LAPA framework.

This module provides integration with LLVM and Clang for parsing and analyzing
C and C++ code. It handles the low-level interaction with the LLVM infrastructure
and provides a high-level interface for the C/C++ frontend.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast

# Flag to track if LLVM/Clang is available
LLVM_AVAILABLE = False

try:
    import clang.cindex as clang
    LLVM_AVAILABLE = True
except ImportError:
    clang = None


class LLVMError(Exception):
    """Base class for LLVM-related errors."""
    pass


class LLVMNotFoundError(LLVMError):
    """Error raised when LLVM/Clang is not available."""
    
    def __init__(self):
        super().__init__(
            "python-clang bindings not found. Please install libclang and python-clang-dev:\n"
            "  Ubuntu/Debian: apt-get install libclang-dev python3-clang\n"
            "  macOS: brew install llvm && pip install clang\n"
            "  Windows: pip install clang"
        )


class LLVMContext:
    """Context manager for LLVM/Clang operations."""
    
    def __init__(self):
        """Initialize LLVM context."""
        if not LLVM_AVAILABLE:
            raise LLVMNotFoundError()
        
        self.index = None
        self._find_libclang()
    
    def _find_libclang(self) -> None:
        """Find and load libclang library."""
        if not LLVM_AVAILABLE:
            raise LLVMNotFoundError()
        
        # Common library paths
        paths = [
            # macOS Homebrew
            "/usr/local/opt/llvm/lib/libclang.dylib",
            "/opt/homebrew/opt/llvm/lib/libclang.dylib",
            # Linux
            "/usr/lib/llvm-*/lib/libclang.so",
            "/usr/lib/libclang.so",
            # Windows
            "C:/Program Files/LLVM/bin/libclang.dll",
        ]
        
        # Try each path
        for path in paths:
            if "*" in path:
                # Handle wildcard paths (e.g., llvm-*)
                import glob
                candidates = glob.glob(path)
                for candidate in sorted(candidates, reverse=True):
                    if os.path.exists(candidate):
                        try:
                            clang.Config.set_library_file(candidate)
                            return
                        except:
                            continue
            elif os.path.exists(path):
                try:
                    clang.Config.set_library_file(path)
                    return
                except:
                    continue
        
        # If no path works, try default loading
        try:
            clang.conf.get_cindex_library()
        except:
            raise RuntimeError(
                "Could not find libclang. Please ensure LLVM and Clang are installed."
            )
    
    def __enter__(self) -> 'LLVMContext':
        """Enter the context."""
        if not LLVM_AVAILABLE:
            raise LLVMNotFoundError()
        
        self.index = clang.Index.create()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context."""
        self.index = None
    
    def parse_file(self, path: Union[str, Path], args: Optional[List[str]] = None) -> Any:
        """
        Parse a C/C++ file using Clang.
        
        Args:
            path: Path to the file to parse
            args: Additional compiler arguments
        
        Returns:
            clang.TranslationUnit: The parsed translation unit
        
        Raises:
            RuntimeError: If parsing fails
            LLVMNotFoundError: If LLVM/Clang is not available
        """
        if not LLVM_AVAILABLE:
            raise LLVMNotFoundError()
        
        if self.index is None:
            raise RuntimeError("LLVM context not initialized")
        
        path = str(path)
        args = args or []
        
        try:
            return self.index.parse(path, args)
        except Exception as e:
            raise RuntimeError(f"Failed to parse {path}: {str(e)}")
    
    def parse_string(self, content: str, filename: str = "input.cpp", args: Optional[List[str]] = None) -> Any:
        """
        Parse C/C++ code from a string using Clang.
        
        Args:
            content: The code to parse
            filename: Name to use for the temporary file
            args: Additional compiler arguments
        
        Returns:
            clang.TranslationUnit: The parsed translation unit
        
        Raises:
            RuntimeError: If parsing fails
            LLVMNotFoundError: If LLVM/Clang is not available
        """
        if not LLVM_AVAILABLE:
            raise LLVMNotFoundError()
        
        if self.index is None:
            raise RuntimeError("LLVM context not initialized")
        
        args = args or []
        
        try:
            # Create an unsaved file for the content
            unsaved_files = [(filename, content)]
            return self.index.parse(
                filename,
                args,
                unsaved_files=unsaved_files,
                options=clang.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD
            )
        except Exception as e:
            raise RuntimeError(f"Failed to parse code: {str(e)}")


def get_cursor_kind_name(cursor: Any) -> str:
    """Get the string name of a cursor kind."""
    if not LLVM_AVAILABLE:
        raise LLVMNotFoundError()
    return cursor.kind.name


def get_type_kind_name(type_obj: Any) -> str:
    """Get the string name of a type kind."""
    if not LLVM_AVAILABLE:
        raise LLVMNotFoundError()
    return type_obj.kind.name


def get_access_specifier_name(cursor: Any) -> str:
    """Get the string name of an access specifier."""
    if not LLVM_AVAILABLE:
        raise LLVMNotFoundError()
    return cursor.access_specifier.name
