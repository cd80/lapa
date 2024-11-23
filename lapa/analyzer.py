"""
Core analyzer module for LAPA framework.

This module provides the main Analyzer class that serves as the primary interface
for performing program analysis tasks.
"""

from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from .ir import IR
from .plugin import Plugin


class Analyzer:
    """
    Main analyzer class that coordinates program analysis tasks.
    
    This class serves as the primary interface for users of the LAPA framework.
    It coordinates between different components like the IR system, analysis
    plugins, and LLM integration.
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        plugins: Optional[List[Plugin]] = None
    ) -> None:
        """
        Initialize the analyzer with optional configuration and plugins.

        Args:
            config: Optional configuration dictionary
            plugins: Optional list of analysis plugins to load
        """
        self.config = config or {}
        self.plugins = plugins or []
        self.ir = IR()
        
    def load_file(self, path: Union[str, Path]) -> None:
        """
        Load a source file for analysis.

        Args:
            path: Path to the source file
        
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file type is not supported
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        # TODO: Implement file loading and parsing
        raise NotImplementedError("File loading not yet implemented")

    def load_directory(self, path: Union[str, Path]) -> None:
        """
        Load all supported files from a directory for analysis.

        Args:
            path: Path to the directory
        
        Raises:
            NotADirectoryError: If the path is not a directory
        """
        path = Path(path)
        if not path.is_dir():
            raise NotADirectoryError(f"Not a directory: {path}")
        
        # TODO: Implement directory scanning and loading
        raise NotImplementedError("Directory loading not yet implemented")

    def analyze(
        self,
        target: Union[str, Path],
        analysis_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform analysis on loaded code.

        Args:
            target: Path to file or directory to analyze
            analysis_type: Optional specific type of analysis to perform

        Returns:
            Dictionary containing analysis results

        Raises:
            ValueError: If no valid analysis type is specified
            RuntimeError: If analysis fails
        """
        # TODO: Implement analysis pipeline
        raise NotImplementedError("Analysis not yet implemented")

    def get_ir(self) -> IR:
        """
        Get the current Intermediate Representation.

        Returns:
            The current IR instance
        """
        return self.ir

    def add_plugin(self, plugin: Plugin) -> None:
        """
        Add a new analysis plugin.

        Args:
            plugin: Plugin instance to add
        
        Raises:
            ValueError: If plugin is invalid or incompatible
        """
        if not isinstance(plugin, Plugin):
            raise ValueError("Invalid plugin type")
        self.plugins.append(plugin)

    def remove_plugin(self, plugin: Plugin) -> None:
        """
        Remove an analysis plugin.

        Args:
            plugin: Plugin instance to remove
        """
        if plugin in self.plugins:
            self.plugins.remove(plugin)

    def get_plugins(self) -> List[Plugin]:
        """
        Get list of currently loaded plugins.

        Returns:
            List of active plugins
        """
        return self.plugins.copy()

    def reset(self) -> None:
        """Reset the analyzer state."""
        self.ir = IR()
        # TODO: Implement full reset logic
