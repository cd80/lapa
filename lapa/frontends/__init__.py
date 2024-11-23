"""
Language frontend implementations for LAPA framework.

This package contains the implementations of language-specific frontends
that parse different programming languages into the framework's IR.
"""

from .python import PythonFrontend
from .javascript import JavaScriptFrontend

__all__ = [
    "PythonFrontend",
    "JavaScriptFrontend",
]
