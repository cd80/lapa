"""
Tests for tree-sitter grammar handling with pip-installed packages.
"""

import pytest

from lapa.frontends.grammars import (
    get_language,
    create_parser
)
from tree_sitter import Language, Parser


def test_get_language():
    """Test getting tree-sitter language."""
    try:
        language = get_language("javascript")
        assert isinstance(language, Language)
    except RuntimeError as e:
        pytest.fail(f"Failed to get language: {e}")


def test_create_parser():
    """Test creating parser."""
    try:
        parser = create_parser("javascript")
        assert isinstance(parser, Parser)
    except RuntimeError as e:
        pytest.fail(f"Failed to create parser: {e}")


def test_create_parser_error():
    """Test handling of parser creation error."""
    with pytest.raises(RuntimeError):
        create_parser("nonexistent")
