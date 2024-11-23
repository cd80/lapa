"""
Tests for frontend interface and registry.
"""

from pathlib import Path
import pytest
from unittest.mock import MagicMock

from lapa.frontend import (
    Frontend,
    LanguageFeature,
    FrontendRegistry,
    ParsingError
)
from lapa.ir import IR


class MockFrontend(Frontend):
    """Mock frontend for testing."""
    
    def __init__(self):
        """Initialize mock frontend."""
        super().__init__()
        self.features = {
            LanguageFeature.FUNCTIONS,
            LanguageFeature.CLASSES
        }
        self.file_extensions = {".mock"}
    
    def parse_file(self, path: Path, ir: IR) -> None:
        """Mock file parsing."""
        if not Path(path).exists():
            raise FileNotFoundError(f"File not found: {path}")
        if str(path).endswith(".error"):
            raise ParsingError("Mock parsing error")
    
    def parse_string(self, source: str, ir: IR) -> None:
        """Mock string parsing."""
        if "error" in source:
            raise ParsingError("Mock parsing error")


def test_language_features():
    """Test language feature enumeration."""
    assert LanguageFeature.FUNCTIONS is not None
    assert LanguageFeature.CLASSES is not None
    assert LanguageFeature.INHERITANCE is not None


def test_mock_frontend_initialization():
    """Test mock frontend initialization."""
    frontend = MockFrontend()
    assert frontend.features == {
        LanguageFeature.FUNCTIONS,
        LanguageFeature.CLASSES
    }
    assert frontend.file_extensions == {".mock"}


def test_frontend_feature_support():
    """Test frontend feature support checking."""
    frontend = MockFrontend()
    assert frontend.supports_feature(LanguageFeature.FUNCTIONS)
    assert frontend.supports_feature(LanguageFeature.CLASSES)
    assert not frontend.supports_feature(LanguageFeature.TEMPLATES)


def test_frontend_registry():
    """Test frontend registry."""
    FrontendRegistry.register("mock", MockFrontend)
    assert FrontendRegistry.get_frontend("mock") == MockFrontend
    assert "mock" in FrontendRegistry.supported_languages()
    assert ".mock" in FrontendRegistry.supported_extensions()


def test_frontend_registry_invalid_registration():
    """Test invalid frontend registration."""
    FrontendRegistry.register("test", MockFrontend)
    with pytest.raises(ValueError):
        FrontendRegistry.register("test", MockFrontend)


def test_frontend_supported_languages():
    """Test getting supported languages."""
    FrontendRegistry.register("lang1", MockFrontend)
    FrontendRegistry.register("lang2", MockFrontend)
    languages = FrontendRegistry.supported_languages()
    assert "lang1" in languages
    assert "lang2" in languages


def test_frontend_supported_extensions():
    """Test getting supported extensions."""
    FrontendRegistry.register("ext1", MockFrontend)
    FrontendRegistry.register("ext2", MockFrontend)
    extensions = FrontendRegistry.supported_extensions()
    assert ".mock" in extensions


def test_parsing_error():
    """Test parsing error handling."""
    frontend = MockFrontend()
    ir = MagicMock()
    with pytest.raises(ParsingError):
        frontend.parse_string("error", ir)


def test_file_not_found():
    """Test file not found error."""
    frontend = MockFrontend()
    ir = MagicMock()
    with pytest.raises(FileNotFoundError):
        frontend.parse_file("nonexistent.mock", ir)


def test_multiple_frontends():
    """Test multiple frontend registration."""
    class Frontend1(MockFrontend):
        def __init__(self):
            super().__init__()
            self.file_extensions = {".f1"}
    
    class Frontend2(MockFrontend):
        def __init__(self):
            super().__init__()
            self.file_extensions = {".f2"}
    
    FrontendRegistry.register("f1", Frontend1)
    FrontendRegistry.register("f2", Frontend2)
    
    extensions = FrontendRegistry.supported_extensions()
    assert ".f1" in extensions
    assert ".f2" in extensions


def test_case_insensitive_extensions():
    """Test case-insensitive extension checking."""
    frontend = MockFrontend()
    assert frontend.supports_extension(".MOCK")
    assert frontend.supports_extension(".mock")
    assert frontend.supports_extension(".MoCk")
