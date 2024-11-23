"""
Plugin system module for LAPA framework.

This module provides the base Plugin class and plugin management functionality
for extending the framework's capabilities.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
from enum import Enum, auto
import importlib
import inspect
from pathlib import Path


class PluginType(Enum):
    """Enumeration of possible plugin types."""
    ANALYZER = auto()      # Analysis plugins
    PARSER = auto()        # Language parsing plugins
    TRANSFORMER = auto()   # IR transformation plugins
    OPTIMIZER = auto()     # Optimization plugins
    VISUALIZER = auto()    # Visualization plugins
    LLM = auto()          # LLM integration plugins
    REPORTER = auto()      # Report generation plugins
    CUSTOM = auto()        # Custom plugin types


class PluginMetadata:
    """Metadata for plugin registration and management."""

    def __init__(
        self,
        name: str,
        version: str,
        plugin_type: PluginType,
        description: str,
        author: Optional[str] = None,
        dependencies: Optional[List[str]] = None
    ):
        """
        Initialize plugin metadata.

        Args:
            name: Plugin name
            version: Plugin version
            plugin_type: Type of plugin
            description: Plugin description
            author: Optional plugin author
            dependencies: Optional list of plugin dependencies
        """
        self.name = name
        self.version = version
        self.plugin_type = plugin_type
        self.description = description
        self.author = author
        self.dependencies = dependencies or []


class Plugin(ABC):
    """
    Base class for all LAPA plugins.
    
    This class defines the interface that all plugins must implement
    and provides common functionality for plugin management.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize plugin with optional configuration.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self._enabled = True
        self._metadata: Optional[PluginMetadata] = None

    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the plugin.
        
        This method is called when the plugin is first loaded.
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """
        Clean up plugin resources.
        
        This method is called when the plugin is being unloaded.
        """
        pass

    @property
    def enabled(self) -> bool:
        """Check if plugin is enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Set plugin enabled state."""
        self._enabled = value

    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        if self._metadata is None:
            raise ValueError("Plugin metadata not set")
        return self._metadata

    @metadata.setter
    def metadata(self, value: PluginMetadata) -> None:
        """Set plugin metadata."""
        self._metadata = value


class PluginManager:
    """
    Manages plugin loading, unloading, and lifecycle.
    
    This class handles plugin discovery, dependency resolution,
    and plugin lifecycle management.
    """

    def __init__(self):
        """Initialize plugin manager."""
        self._plugins: Dict[str, Plugin] = {}
        self._plugin_types: Dict[str, Type[Plugin]] = {}

    def register_plugin_type(self, name: str, plugin_class: Type[Plugin]) -> None:
        """
        Register a new plugin type.

        Args:
            name: Name of the plugin type
            plugin_class: Plugin class to register
        """
        if not inspect.isclass(plugin_class) or not issubclass(plugin_class, Plugin):
            raise ValueError(f"Invalid plugin class: {plugin_class}")
        self._plugin_types[name] = plugin_class

    def load_plugin(self, plugin_path: Path) -> Plugin:
        """
        Load a plugin from a Python module.

        Args:
            plugin_path: Path to the plugin module

        Returns:
            Loaded plugin instance

        Raises:
            ValueError: If plugin is invalid or incompatible
            ImportError: If plugin cannot be imported
        """
        if not plugin_path.exists():
            raise ImportError(f"Plugin not found: {plugin_path}")

        # Import plugin module
        spec = importlib.util.spec_from_file_location(
            plugin_path.stem,
            plugin_path
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load plugin: {plugin_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Find plugin class
        plugin_class = None
        for item in dir(module):
            obj = getattr(module, item)
            if (inspect.isclass(obj) and
                issubclass(obj, Plugin) and
                obj != Plugin):
                plugin_class = obj
                break

        if plugin_class is None:
            raise ValueError(f"No valid plugin class found in {plugin_path}")

        # Create and initialize plugin
        plugin = plugin_class()
        plugin.initialize()
        
        # Store plugin
        self._plugins[plugin.metadata.name] = plugin
        
        return plugin

    def unload_plugin(self, plugin_name: str) -> None:
        """
        Unload a plugin.

        Args:
            plugin_name: Name of plugin to unload

        Raises:
            KeyError: If plugin is not found
        """
        if plugin_name not in self._plugins:
            raise KeyError(f"Plugin not found: {plugin_name}")

        plugin = self._plugins[plugin_name]
        plugin.cleanup()
        del self._plugins[plugin_name]

    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """
        Get a loaded plugin by name.

        Args:
            plugin_name: Name of plugin to get

        Returns:
            Plugin instance if found, None otherwise
        """
        return self._plugins.get(plugin_name)

    def get_plugins_by_type(self, plugin_type: PluginType) -> List[Plugin]:
        """
        Get all plugins of a specific type.

        Args:
            plugin_type: Type of plugins to get

        Returns:
            List of matching plugins
        """
        return [
            plugin for plugin in self._plugins.values()
            if plugin.metadata.plugin_type == plugin_type
        ]

    def get_all_plugins(self) -> List[Plugin]:
        """
        Get all loaded plugins.

        Returns:
            List of all plugins
        """
        return list(self._plugins.values())
