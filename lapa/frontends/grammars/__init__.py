"""
Tree-sitter grammar management for LAPA frontends.

This module handles the loading and management of tree-sitter grammars
for different programming languages.
"""

from pathlib import Path
from typing import Dict, Optional
from tree_sitter import Language, Parser

# Cache for loaded languages
_language_cache: Dict[str, Language] = {}

def get_grammar_path(language: str) -> Path:
    """Get the path to a language's grammar library."""
    lib_name = f"tree-sitter-{language}.so"
    if Path(f"lib/{lib_name}").exists():
        return Path(f"lib/{lib_name}")
    elif Path(f"build/tree-sitter-{language}/src/parser.so").exists():
        return Path(f"build/tree-sitter-{language}/src/parser.so")
    else:
        raise FileNotFoundError(f"Grammar not found for {language}")

def get_language(name: str) -> Language:
    """
    Get a tree-sitter Language instance for a specific language.
    
    Args:
        name: Language name (e.g., 'javascript', 'python')
    
    Returns:
        tree_sitter.Language instance
    
    Raises:
        RuntimeError: If grammar loading fails
    """
    if name in _language_cache:
        return _language_cache[name]
    
    grammar_path = get_grammar_path(name)
    try:
        language = Language(str(grammar_path), name)
        _language_cache[name] = language
        return language
    except Exception as e:
        raise RuntimeError(f"Failed to load {name} grammar: {e}")

def create_parser(language: str) -> Parser:
    """
    Create a tree-sitter Parser for a specific language.
    
    Args:
        language: Language name (e.g., 'javascript', 'python')
    
    Returns:
        tree_sitter.Parser instance configured for the language
    
    Raises:
        RuntimeError: If parser creation fails
    """
    try:
        parser = Parser()
        # Ensure the parser has the set_language method
        if not hasattr(parser, 'set_language'):
            raise AttributeError("Parser does not support set_language")
        
        lang = get_language(language)
        parser.set_language(lang)
        return parser
    except Exception as e:
        raise RuntimeError(f"Failed to create parser for {language}: {e}")
