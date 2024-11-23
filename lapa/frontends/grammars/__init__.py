"""
Tree-sitter grammar handling using pip-installed packages.
"""

from typing import Dict
from tree_sitter import Parser, Language

# Import the pip-installed tree-sitter language packages
import tree_sitter_python
import tree_sitter_c
import tree_sitter_cpp
import tree_sitter_rust
import tree_sitter_java
import tree_sitter_javascript
import tree_sitter_typescript

# Map language names to their modules
_language_modules = {
    'python': tree_sitter_python,
    'c': tree_sitter_c,
    'cpp': tree_sitter_cpp,
    'rust': tree_sitter_rust,
    'java': tree_sitter_java,
    'javascript': tree_sitter_javascript,
    'typescript': tree_sitter_typescript,
}

# Cache for loaded languages
_language_cache: Dict[str, Language] = {}


def get_language(name: str) -> Language:
    """
    Get tree-sitter language.

    Args:
        name: Language name

    Returns:
        Tree-sitter Language object

    Raises:
        RuntimeError: If language loading fails
    """
    if name in _language_cache:
        return _language_cache[name]

    try:
        module = _language_modules.get(name)
        if module is None:
            raise ValueError(f"No module found for language '{name}'")

        # Create the Language object using module.language()
        language = Language(module.language())
        _language_cache[name] = language
        return language
    except Exception as e:
        raise RuntimeError(f"Failed to load language {name}: {str(e)}") from e


def create_parser(language_name: str) -> Parser:
    """
    Create tree-sitter parser.

    Args:
        language_name: Language name

    Returns:
        Tree-sitter Parser

    Raises:
        RuntimeError: If parser creation fails
    """
    try:
        language_obj = get_language(language_name)

        parser = Parser(language_obj)
        parser.language = get_language(language_name)
        return parser
    except Exception as e:
        raise RuntimeError(f"Failed to create parser for {language_name}: {str(e)}") from e
