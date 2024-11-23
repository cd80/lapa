"""
Tests for the LAPA frontend module.
"""

import pytest
from pathlib import Path
from typing import List

from lapa.frontend import (
    LanguageFeatures,
    LanguageFrontend,
    FrontendRegistry,
    ParsingError
)
from lapa.ir import IR


class MockLanguageFrontend(LanguageFrontend):
    """Mock frontend implementation for testing."""
    
    def _get_language_features(self) -> LanguageFeatures:
        features = LanguageFeatures()
        features.has_classes = True
        features.has_interfaces = False
        features.typing_system = "dynamic"
        return features

    def parse_file(self, path: Path) -> IR:
        if not Path(path).exists():
            raise FileNotFoundError(f"File not found: {path}")
        return self.ir

    def parse_string(self, content: str, filename: str = "<string>") -> IR:
        if not content:
            raise ParsingError("Empty content")
        return self.ir

    def get_file_extensions(self) -> List[str]:
        return [".mock", ".test"]


def test_language_features():
    """Test LanguageFeatures initialization and properties."""
    features = LanguageFeatures()
    
    # Test default values
    assert features.has_classes is False
    assert features.has_interfaces is False
    assert features.has_generics is False
    assert features.has_exceptions is False
    assert features.has_async is False
    assert features.typing_system == "dynamic"
    assert features.memory_management == "gc"


def test_mock_frontend_initialization():
    """Test frontend initialization."""
    frontend = MockLanguageFrontend()
    assert frontend is not None
    assert frontend.ir is not None
    
    features = frontend.features
    assert features.has_classes is True
    assert features.has_interfaces is False
    assert features.typing_system == "dynamic"


def test_frontend_feature_support():
    """Test feature support checking."""
    frontend = MockLanguageFrontend()
    
    assert frontend.supports_feature("has_classes") is True
    assert frontend.supports_feature("has_interfaces") is False
    assert frontend.supports_feature("nonexistent_feature") is False


def test_frontend_registry():
    """Test frontend registry operations."""
    registry = FrontendRegistry()
    
    # Register frontend
    registry.register_frontend("mock", MockLanguageFrontend)
    
    # Test language lookup
    frontend_class = registry.get_frontend("mock")
    assert frontend_class is not None
    assert frontend_class == MockLanguageFrontend
    
    # Test extension lookup
    frontend_class = registry.get_frontend_for_file("test.mock")
    assert frontend_class is not None
    assert frontend_class == MockLanguageFrontend
    
    # Test unknown extension
    frontend_class = registry.get_frontend_for_file("test.unknown")
    assert frontend_class is None


def test_frontend_registry_invalid_registration():
    """Test registering invalid frontend."""
    registry = FrontendRegistry()
    
    with pytest.raises(ValueError):
        registry.register_frontend("invalid", str)


def test_frontend_supported_languages():
    """Test getting supported languages."""
    registry = FrontendRegistry()
    registry.register_frontend("mock", MockLanguageFrontend)
    
    languages = registry.get_supported_languages()
    assert "mock" in languages
    assert len(languages) == 1


def test_frontend_supported_extensions():
    """Test getting supported extensions."""
    registry = FrontendRegistry()
    registry.register_frontend("mock", MockLanguageFrontend)
    
    extensions = registry.get_supported_extensions()
    assert ".mock" in extensions
    assert ".test" in extensions
    assert len(extensions) == 2


def test_parsing_error():
    """Test parsing error handling."""
    frontend = MockLanguageFrontend()
    
    with pytest.raises(ParsingError):
        frontend.parse_string("")


def test_file_not_found():
    """Test file not found handling."""
    frontend = MockLanguageFrontend()
    
    with pytest.raises(FileNotFoundError):
        frontend.parse_file("nonexistent.mock")


def test_multiple_frontends():
    """Test registry with multiple frontends."""
    class AnotherMockFrontend(MockLanguageFrontend):
        def get_file_extensions(self) -> List[str]:
            return [".another"]
    
    registry = FrontendRegistry()
    registry.register_frontend("mock1", MockLanguageFrontend)
    registry.register_frontend("mock2", AnotherMockFrontend)
    
    assert len(registry.get_supported_languages()) == 2
    assert len(registry.get_supported_extensions()) == 3
    
    # Test extension mappings
    assert registry.get_frontend_for_file("test.mock") == MockLanguageFrontend
    assert registry.get_frontend_for_file("test.another") == AnotherMockFrontend


def test_case_insensitive_extensions():
    """Test case-insensitive extension handling."""
    registry = FrontendRegistry()
    registry.register_frontend("mock", MockLanguageFrontend)
    
    # Both should work regardless of case
    assert registry.get_frontend_for_file("test.MOCK") == MockLanguageFrontend
    assert registry.get_frontend_for_file("test.mock") == MockLanguageFrontend
