"""
Frontend interface and registry.
"""

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Dict, Optional, Set, Type, Union
from pathlib import Path


class ParsingError(Exception):
    """Raised when parsing fails."""
    pass


class LanguageFeature(Enum):
    """Supported language features."""
    # Basic features
    FUNCTIONS = auto()
    CLASSES = auto()
    INHERITANCE = auto()
    INTERFACES = auto()
    GENERICS = auto()
    TEMPLATES = auto()
    STRUCTS = auto()
    ENUMS = auto()
    TRAITS = auto()
    PROTOCOLS = auto()
    MACROS = auto()
    OPERATOR_OVERLOADING = auto()
    NAMESPACES = auto()
    MODULES = auto()
    PACKAGES = auto()
    IMPORTS = auto()
    EXTENSIONS = auto()  # Added EXTENSIONS here

    # Memory management
    POINTERS = auto()
    REFERENCES = auto()
    MEMORY_MANAGEMENT = auto()
    GARBAGE_COLLECTION = auto()
    OWNERSHIP = auto()
    BORROWING = auto()
    LIFETIMES = auto()
    MUTABILITY = auto()
    LIFETIME_ANNOTATIONS = auto()

    # Control flow
    EXCEPTIONS = auto()
    ASYNC_AWAIT = auto()
    GENERATORS = auto()
    COROUTINES = auto()
    PATTERN_MATCHING = auto()
    MATCH_EXPRESSIONS = auto()
    ERROR_HANDLING = auto()
    CONDITIONAL_COMPILATION = auto()
    CONCURRENCY = auto()
    CLOSURES = auto()
    LAMBDA_FUNCTIONS = auto()

    # Language-specific
    PREPROCESSOR = auto()
    INLINE_ASSEMBLY = auto()
    FRIEND_FUNCTIONS = auto()
    MULTIPLE_INHERITANCE = auto()
    VIRTUAL_FUNCTIONS = auto()
    CONST_CORRECTNESS = auto()
    RVALUE_REFERENCES = auto()
    MOVE_SEMANTICS = auto()
    VARIADIC_TEMPLATES = auto()
    TYPE_INFERENCE = auto()
    CONCEPTS = auto()
    RANGES = auto()
    CONSTEXPR = auto()
    ATTRIBUTES = auto()
    STRUCTURED_BINDINGS = auto()
    FOLD_EXPRESSIONS = auto()
    DESIGNATED_INITIALIZERS = auto()
    THREE_WAY_COMPARISON = auto()
    ANNOTATIONS = auto()

    # Decorators and annotations
    DECORATORS = auto()

    # Metaprogramming
    REFLECTION = auto()
    COMPILE_TIME_EVALUATION = auto()


class Frontend(ABC):
    """Base class for language frontends."""

    def __init__(self):
        """Initialize frontend."""
        self.features: Set[LanguageFeature] = set()
        self.file_extensions: Set[str] = set()

    def _get_language_features(self) -> Set[LanguageFeature]:
        """Get supported language features."""
        return self.features

    def get_file_extensions(self) -> Set[str]:
        """Get supported file extensions."""
        return self.file_extensions

    @abstractmethod
    def parse_file(self, path: Union[str, Path], ir: Any) -> None:
        """
        Parse a source file and update the IR.

        Args:
            path: Path to source file
            ir: IR to update

        Raises:
            FileNotFoundError: If file doesn't exist
            NotImplementedError: If parsing is not implemented
            ParsingError: If parsing fails
        """
        pass

    @abstractmethod
    def parse_string(self, source: str, ir: Any) -> None:
        """
        Parse source code string and update the IR.

        Args:
            source: Source code string
            ir: IR to update

        Raises:
            NotImplementedError: If parsing is not implemented
            ParsingError: If parsing fails
        """
        pass

    def supports_feature(self, feature: LanguageFeature) -> bool:
        """
        Check if frontend supports a language feature.

        Args:
            feature: Feature to check

        Returns:
            True if feature is supported
        """
        return feature in self.features

    def supports_extension(self, extension: str) -> bool:
        """
        Check if frontend supports a file extension.

        Args:
            extension: File extension to check (with dot)

        Returns:
            True if extension is supported
        """
        return extension.lower() in {ext.lower() for ext in self.file_extensions}


class FrontendRegistry:
    """Registry for language frontends."""

    _frontends: Dict[str, Type[Frontend]] = {}

    @classmethod
    def register(cls, language: str, frontend_class: Type[Frontend]) -> None:
        """
        Register a frontend for a language.

        Args:
            language: Language name
            frontend_class: Frontend class

        Raises:
            ValueError: If language already registered
        """
        if language in cls._frontends:
            raise ValueError(f"Frontend already registered for {language}")
        cls._frontends[language] = frontend_class

    @classmethod
    def get_frontend(cls, language: str) -> Optional[Type[Frontend]]:
        """
        Get frontend class for a language.

        Args:
            language: Language name

        Returns:
            Frontend class if registered, None otherwise
        """
        return cls._frontends.get(language)

    @classmethod
    def supported_languages(cls) -> Set[str]:
        """
        Get set of supported languages.

        Returns:
            Set of language names
        """
        return set(cls._frontends.keys())

    @classmethod
    def supported_extensions(cls) -> Set[str]:
        """
        Get set of supported file extensions.

        Returns:
            Set of file extensions
        """
        extensions = set()
        for frontend_class in cls._frontends.values():
            frontend = frontend_class()
            extensions.update(frontend.get_file_extensions())
        return extensions
