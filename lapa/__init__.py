"""
LAPA (LLM Assisted Program Analysis) framework.

This module provides the main entry points and exports for the framework.
"""

from .frontend import (
    Frontend,
    LanguageFeature,
    FrontendRegistry,
    ParsingError
)

from .analyzer import Analyzer
from .plugin import Plugin, PluginManager, PluginType

__version__ = "0.0.1-dev"
