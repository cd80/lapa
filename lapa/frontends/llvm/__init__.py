"""
LLVM/Clang integration module.

This module provides integration with LLVM/Clang for parsing C/C++ code.
"""

from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import os
import sys
import platform

try:
    import clang.cindex as clang

    # Attempt to set the library path for libclang if not already loaded
    if not clang.Config.loaded:
        system = platform.system()
        if system == "Darwin":
            # macOS
            possible_paths = [
                "/usr/local/opt/llvm/lib",     # Common Homebrew path on Intel Macs
                "/opt/homebrew/opt/llvm/lib",  # Common Homebrew path on Apple Silicon Macs
                "/usr/local/lib",              # Alternate paths
                "/usr/lib",
            ]
            for path in possible_paths:
                libclang_path = Path(path) / "libclang.dylib"
                if libclang_path.exists():
                    clang.Config.set_library_file(str(libclang_path))
                    break
        elif system == "Linux":
            # Linux
            possible_paths = [
                "/usr/lib/llvm/lib",
                "/usr/lib",
                "/usr/local/lib",
            ]
            for path in possible_paths:
                libclang_path = Path(path) / "libclang.so"
                if libclang_path.exists():
                    clang.Config.set_library_file(str(libclang_path))
                    break
        elif system == "Windows":
            # Windows
            possible_paths = [
                "C:\\Program Files\\LLVM\\bin",
                "C:\\LLVM\\bin",
            ]
            for path in possible_paths:
                libclang_path = Path(path) / "libclang.dll"
                if libclang_path.exists():
                    clang.Config.set_library_file(str(libclang_path))
                    break

    if not clang.Config.loaded:
        raise ImportError("Could not load libclang. Please ensure libclang is installed and accessible.")

    HAVE_LIBCLANG = True
    LLVM_AVAILABLE = True
except ImportError:
    HAVE_LIBCLANG = False
    LLVM_AVAILABLE = False


class LLVMNotFoundError(Exception):
    """Raised when LLVM/Clang is not available."""
    pass


def cursor_kind_name(kind: Any) -> str:
    """
    Get string name of cursor kind.

    Args:
        kind: Cursor kind from libclang

    Returns:
        String name of the cursor kind
    """
    return kind.name.lower()


def type_kind_name(kind: Any) -> str:
    """
    Get string name of type kind.

    Args:
        kind: Type kind from libclang

    Returns:
        String name of the type kind
    """
    return kind.name.lower()


def access_specifier_name(access: Any) -> str:
    """
    Get string name of access specifier.

    Args:
        access: Access specifier from libclang

    Returns:
        String name of the access specifier
    """
    return access.name.lower()


class LLVMContext:
    """Context manager for LLVM/Clang operations."""

    def __init__(
        self,
        include_paths: Optional[List[str]] = None,
        definitions: Optional[Dict[str, str]] = None
    ):
        """
        Initialize LLVM context.

        Args:
            include_paths: Additional include paths
            definitions: Preprocessor definitions

        Raises:
            LLVMNotFoundError: If LLVM/Clang is not available
        """
        if not LLVM_AVAILABLE:
            raise LLVMNotFoundError(
                "LLVM/Clang not available. Please ensure libclang is installed and accessible."
            )

        self.index = clang.Index.create()
        self.include_paths = include_paths or []
        self.definitions = definitions or {}

    def __enter__(self):
        """Enter context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        # Clean up if needed
        pass

    def _get_compiler_args(self, args: Optional[List[str]] = None) -> List[str]:
        """
        Get compiler arguments.

        Args:
            args: Additional compiler arguments

        Returns:
            List of compiler arguments
        """
        compiler_args = []

        # Add include paths
        for path in self.include_paths:
            compiler_args.append(f"-I{path}")

        # Add preprocessor definitions
        for name, value in self.definitions.items():
            compiler_args.append(f"-D{name}={value}")

        # Add additional arguments
        if args:
            compiler_args.extend(args)

        return compiler_args

    def parse_string(
        self,
        source: str,
        filename: str = "<string>",
        args: Optional[List[str]] = None
    ) -> Any:
        """
        Parse source code string.

        Args:
            source: Source code to parse
            filename: Name to use for the source file
            args: Additional compiler arguments

        Returns:
            Clang translation unit

        Raises:
            Exception: If parsing fails
        """
        try:
            compiler_args = self._get_compiler_args(args)

            # Create temporary file
            unsaved_files = [(filename, source)]

            # Parse the code
            return self.index.parse(
                filename,
                args=compiler_args,
                unsaved_files=unsaved_files
            )
        except Exception as e:
            raise Exception(f"Failed to parse code: {str(e)}") from e

    def parse_file(
        self,
        path: Union[str, Path],
        args: Optional[List[str]] = None
    ) -> Any:
        """
        Parse source file.

        Args:
            path: Path to source file
            args: Additional compiler arguments

        Returns:
            Clang translation unit

        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: If parsing fails
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        try:
            compiler_args = self._get_compiler_args(args)
            return self.index.parse(str(path), args=compiler_args)
        except Exception as e:
            raise Exception(f"Failed to parse {path}: {str(e)}") from e
