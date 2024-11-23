"""
Tests for the tree-sitter grammar management module.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from tree_sitter import Language, Parser
from lapa.frontends.grammars import get_grammar_path, get_language, create_parser


class MockParser:
    """Mock Parser class with set_language method."""
    def __init__(self):
        self.language = None
    
    def set_language(self, language):
        self.language = language


def test_get_grammar_path_lib():
    """Test getting grammar path from lib directory."""
    with patch.object(Path, 'exists') as mock_exists:
        # Mock lib path exists
        mock_exists.return_value = True
        path = get_grammar_path('javascript')
        assert path == Path('lib/tree-sitter-javascript.so')
        mock_exists.assert_called_once()


def test_get_grammar_path_build():
    """Test getting grammar path from build directory."""
    with patch.object(Path, 'exists') as mock_exists:
        # Mock lib path doesn't exist but build path does
        mock_exists.side_effect = [False, True]
        path = get_grammar_path('javascript')
        assert path == Path('build/tree-sitter-javascript/src/parser.so')
        assert mock_exists.call_count == 2


def test_get_grammar_path_not_found():
    """Test error when grammar path not found."""
    with patch.object(Path, 'exists') as mock_exists:
        # Mock neither path exists
        mock_exists.return_value = False
        with pytest.raises(FileNotFoundError) as exc_info:
            get_grammar_path('javascript')
        assert "Grammar not found for javascript" in str(exc_info.value)


def test_get_language_cached():
    """Test language caching."""
    mock_language = MagicMock(spec=Language)
    
    with patch('lapa.frontends.grammars._language_cache', {'javascript': mock_language}):
        language = get_language('javascript')
        assert language == mock_language


def test_get_language_new():
    """Test loading new language."""
    mock_language = MagicMock(spec=Language)
    
    with patch('lapa.frontends.grammars.Language') as mock_language_class, \
         patch('lapa.frontends.grammars.get_grammar_path') as mock_get_path:
        # Setup mocks
        mock_get_path.return_value = Path('lib/tree-sitter-javascript.so')
        mock_language_class.return_value = mock_language
        
        # Test
        language = get_language('javascript')
        
        # Verify
        assert language == mock_language
        mock_get_path.assert_called_once_with('javascript')
        mock_language_class.assert_called_once_with(
            str(Path('lib/tree-sitter-javascript.so')),
            'javascript'
        )


def test_get_language_error():
    """Test error handling in language loading."""
    with patch('lapa.frontends.grammars.Language') as mock_language_class, \
         patch('lapa.frontends.grammars.get_grammar_path') as mock_get_path, \
         patch('lapa.frontends.grammars._language_cache', {}):
        # Setup mocks
        mock_get_path.return_value = Path('lib/tree-sitter-javascript.so')
        mock_language_class.side_effect = Exception("Test error")
        
        with pytest.raises(RuntimeError) as exc_info:
            get_language('javascript')
        assert "Failed to load javascript grammar" in str(exc_info.value)


def test_create_parser():
    """Test parser creation."""
    mock_language = MagicMock(spec=Language)
    mock_parser = MockParser()
    
    with patch('lapa.frontends.grammars.Parser') as mock_parser_class, \
         patch('lapa.frontends.grammars.get_language') as mock_get_language:
        # Setup mocks
        mock_parser_class.return_value = mock_parser
        mock_get_language.return_value = mock_language
        
        # Test
        parser = create_parser('javascript')
        
        # Verify
        assert parser == mock_parser
        mock_get_language.assert_called_once_with('javascript')
        assert parser.language == mock_language


def test_create_parser_error():
    """Test error handling in parser creation."""
    with patch('lapa.frontends.grammars.Parser') as mock_parser_class:
        # Setup mock to return parser without set_language method
        mock_parser_class.return_value = object()
        
        with pytest.raises(RuntimeError) as exc_info:
            create_parser('javascript')
        assert "Failed to create parser for javascript" in str(exc_info.value)
