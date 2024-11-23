"""
LAPA - LLM Assisted Program Analysis Framework
============================================

A comprehensive program analysis framework that combines traditional static/dynamic
analysis with LLM capabilities.

Core Components
--------------
- IR (Intermediate Representation)
- Analysis Engine
- Language Frontends
- LLM Integration
- Plugin System
"""

__version__ = "0.0.1"
__author__ = "Kim, Sungwoo"

from .analyzer import Analyzer
from .ir import IR
from .plugin import Plugin

__all__ = [
    "Analyzer",
    "IR",
    "Plugin",
]
