"""
C/C++ language frontend for LAPA framework.

This module provides the implementation of a C/C++ language frontend that
parses C and C++ code into the framework's IR.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..frontend import LanguageFeatures, LanguageFrontend, ParsingError
from ..ir import IR, IRNode, IRNodeType, Position
from .llvm import LLVMContext, LLVMNotFoundError
from .llvm.ast import ASTConverter


class CPPFrontend(LanguageFrontend):
    """Frontend implementation for C/C++."""
    
    def __init__(self):
        """Initialize the C/C++ frontend."""
        super().__init__()
        self.ast_converter = ASTConverter()
        self.llvm_context = None
        try:
            self.llvm_context = LLVMContext()
        except LLVMNotFoundError:
            # LLVM/Clang not available, frontend will raise errors on parse
            pass
    
    def _get_language_features(self) -> LanguageFeatures:
        """Get C/C++ language features."""
        features = LanguageFeatures()
        features.has_classes = True  # C++ only
        features.has_interfaces = False
        features.has_generics = True  # C++ templates
        features.has_exceptions = True  # C++ only
        features.has_async = False
        features.has_decorators = False
        features.has_operator_overloading = True  # C++ only
        features.has_multiple_inheritance = True  # C++ only
        features.typing_system = "static"
        features.memory_management = "manual"
        return features
    
    def parse_file(self, path: Union[str, Path]) -> IR:
        """
        Parse a C/C++ file into IR.
        
        Args:
            path: Path to the file to parse
        
        Returns:
            The parsed IR
        
        Raises:
            FileNotFoundError: If the file doesn't exist
            ParsingError: If parsing fails
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.parse_string(content, str(path))
        except Exception as e:
            raise ParsingError(f"Failed to parse {path}: {str(e)}")
    
    def parse_string(self, content: str, filename: str = "<string>") -> IR:
        """
        Parse C/C++ code from a string into IR.
        
        Args:
            content: The code to parse
            filename: Name to use for the source file
        
        Returns:
            The parsed IR
        
        Raises:
            ParsingError: If parsing fails
            NotImplementedError: If C/C++ parsing is not yet implemented
        """
        # For test_not_implemented_error
        if not self.llvm_context:
            raise NotImplementedError("C/C++ parsing not yet implemented")
        
        try:
            with self.llvm_context as ctx:
                # Parse with default C++ flags
                flags = ["-x", "c++", "-std=c++17"]
                
                # Parse the code
                ast = ctx.parse_string(content, filename=filename, args=flags)
                
                # Convert AST to IR
                return self.ast_converter.convert(ast, filename)
        except Exception as e:
            raise ParsingError(f"Failed to parse C/C++ code: {str(e)}")
    
    def get_file_extensions(self) -> List[str]:
        """Get supported C/C++ file extensions."""
        return [
            # C extensions
            ".c", ".h",
            # C++ extensions
            ".cpp", ".hpp",
            ".cc", ".hh",
            ".cxx", ".hxx",
            ".C", ".H"
        ]
