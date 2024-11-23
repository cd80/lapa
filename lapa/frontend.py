"""
Language frontend module for LAPA framework.

This module provides the base classes and interfaces for language-specific
frontends that parse source code into the framework's IR.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union

from .ir import IR, IRNode, Position


class LanguageFeatures:
    """Represents supported features of a programming language."""
    
    def __init__(self):
        self.has_classes = False
        self.has_interfaces = False
        self.has_generics = False
        self.has_exceptions = False
        self.has_async = False
        self.has_decorators = False
        self.has_operator_overloading = False
        self.has_multiple_inheritance = False
        self.typing_system = "dynamic"  # or "static", "gradual"
        self.memory_management = "gc"   # or "manual", "reference_counting"


class ParsingError(Exception):
    """Base class for parsing-related errors."""
    
    def __init__(self, message: str, position: Optional[Position] = None):
        super().__init__(message)
        self.position = position


class LanguageFrontend(ABC):
    """
    Base class for language-specific frontends.
    
    Each supported programming language should implement this interface
    to provide parsing capabilities into the framework's IR.
    """

    def __init__(self):
        """Initialize the language frontend."""
        self.features = self._get_language_features()
        self.ir = IR()

    @abstractmethod
    def _get_language_features(self) -> LanguageFeatures:
        """
        Get the features supported by this language.
        
        Returns:
            LanguageFeatures instance describing supported features
        """
        pass

    @abstractmethod
    def parse_file(self, path: Union[str, Path]) -> IR:
        """
        Parse a source file into IR.

        Args:
            path: Path to the source file

        Returns:
            IR instance representing the parsed code

        Raises:
            ParsingError: If parsing fails
            FileNotFoundError: If file doesn't exist
        """
        pass

    @abstractmethod
    def parse_string(self, content: str, filename: str = "<string>") -> IR:
        """
        Parse source code from a string into IR.

        Args:
            content: Source code string
            filename: Optional name for error reporting

        Returns:
            IR instance representing the parsed code

        Raises:
            ParsingError: If parsing fails
        """
        pass

    def supports_feature(self, feature_name: str) -> bool:
        """
        Check if a specific language feature is supported.

        Args:
            feature_name: Name of the feature to check

        Returns:
            True if feature is supported, False otherwise
        """
        return hasattr(self.features, feature_name) and getattr(self.features, feature_name)

    @abstractmethod
    def get_file_extensions(self) -> List[str]:
        """
        Get list of file extensions supported by this frontend.

        Returns:
            List of supported file extensions (e.g., ['.py', '.pyw'])
        """
        pass


class FrontendRegistry:
    """
    Registry for language frontends.
    
    Manages the available language frontends and their mappings
    to file extensions.
    """

    def __init__(self):
        """Initialize the frontend registry."""
        self._frontends: Dict[str, Type[LanguageFrontend]] = {}
        self._extension_map: Dict[str, str] = {}

    def register_frontend(self, language: str, frontend_class: Type[LanguageFrontend]) -> None:
        """
        Register a language frontend.

        Args:
            language: Language identifier (e.g., 'python', 'java')
            frontend_class: Frontend class to register

        Raises:
            ValueError: If frontend is invalid
        """
        if not issubclass(frontend_class, LanguageFrontend):
            raise ValueError(f"Invalid frontend class: {frontend_class}")

        self._frontends[language] = frontend_class
        
        # Register file extensions
        frontend = frontend_class()
        for ext in frontend.get_file_extensions():
            self._extension_map[ext] = language

    def get_frontend(self, language: str) -> Optional[Type[LanguageFrontend]]:
        """
        Get frontend class for a language.

        Args:
            language: Language identifier

        Returns:
            Frontend class if found, None otherwise
        """
        return self._frontends.get(language)

    def get_frontend_for_file(self, path: Union[str, Path]) -> Optional[Type[LanguageFrontend]]:
        """
        Get appropriate frontend for a file based on extension.

        Args:
            path: Path to the file

        Returns:
            Frontend class if found, None otherwise
        """
        ext = Path(path).suffix.lower()
        language = self._extension_map.get(ext)
        if language:
            return self._frontends.get(language)
        return None

    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported languages.

        Returns:
            List of supported language identifiers
        """
        return list(self._frontends.keys())

    def get_supported_extensions(self) -> List[str]:
        """
        Get list of supported file extensions.

        Returns:
            List of supported file extensions
        """
        return list(self._extension_map.keys())
