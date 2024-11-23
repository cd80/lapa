"""
Tests for the LAPA plugin system.
"""

import pytest
from pathlib import Path
from lapa.plugin import (
    Plugin,
    PluginType,
    PluginMetadata,
    PluginManager
)


class TestPlugin(Plugin):
    """Test plugin implementation."""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.metadata = PluginMetadata(
            name="test_plugin",
            version="0.1.0",
            plugin_type=PluginType.ANALYZER,
            description="Test plugin",
            author="Test Author",
            dependencies=["dep1", "dep2"]
        )
        self.initialized = False
        self.cleaned_up = False

    def initialize(self) -> None:
        self.initialized = True

    def cleanup(self) -> None:
        self.cleaned_up = True


def test_plugin_metadata():
    """Test plugin metadata creation and access."""
    metadata = PluginMetadata(
        name="test",
        version="1.0.0",
        plugin_type=PluginType.ANALYZER,
        description="Test plugin",
        author="Test Author",
        dependencies=["dep1"]
    )
    
    assert metadata.name == "test"
    assert metadata.version == "1.0.0"
    assert metadata.plugin_type == PluginType.ANALYZER
    assert metadata.description == "Test plugin"
    assert metadata.author == "Test Author"
    assert metadata.dependencies == ["dep1"]


def test_plugin_initialization():
    """Test basic plugin initialization."""
    plugin = TestPlugin()
    assert not plugin.initialized
    assert not plugin.cleaned_up
    assert plugin.enabled
    assert plugin.config == {}


def test_plugin_with_config():
    """Test plugin initialization with config."""
    config = {"test_key": "test_value"}
    plugin = TestPlugin(config=config)
    assert plugin.config == config


def test_plugin_lifecycle():
    """Test plugin lifecycle methods."""
    plugin = TestPlugin()
    
    # Test initialize
    plugin.initialize()
    assert plugin.initialized
    assert not plugin.cleaned_up
    
    # Test cleanup
    plugin.cleanup()
    assert plugin.initialized
    assert plugin.cleaned_up


def test_plugin_enabled_property():
    """Test plugin enabled property."""
    plugin = TestPlugin()
    assert plugin.enabled
    
    plugin.enabled = False
    assert not plugin.enabled
    
    plugin.enabled = True
    assert plugin.enabled


def test_plugin_metadata_property():
    """Test plugin metadata property."""
    plugin = TestPlugin()
    
    assert plugin.metadata.name == "test_plugin"
    assert plugin.metadata.version == "0.1.0"
    assert plugin.metadata.plugin_type == PluginType.ANALYZER
    
    # Test missing metadata
    plugin._metadata = None
    with pytest.raises(ValueError):
        _ = plugin.metadata


def test_plugin_manager_initialization():
    """Test plugin manager initialization."""
    manager = PluginManager()
    assert len(manager._plugins) == 0
    assert len(manager._plugin_types) == 0


def test_plugin_type_registration():
    """Test registering plugin types."""
    manager = PluginManager()
    
    # Register valid plugin type
    manager.register_plugin_type("test", TestPlugin)
    assert "test" in manager._plugin_types
    assert manager._plugin_types["test"] == TestPlugin
    
    # Try registering invalid type
    with pytest.raises(ValueError):
        manager.register_plugin_type("invalid", str)


def test_plugin_loading_errors():
    """Test plugin loading error cases."""
    manager = PluginManager()
    
    # Test non-existent plugin
    with pytest.raises(ImportError):
        manager.load_plugin(Path("nonexistent.py"))


def test_plugin_management():
    """Test plugin management operations."""
    manager = PluginManager()
    
    # Test getting non-existent plugin
    assert manager.get_plugin("nonexistent") is None
    
    # Test getting plugins by type
    plugins = manager.get_plugins_by_type(PluginType.ANALYZER)
    assert isinstance(plugins, list)
    assert len(plugins) == 0
    
    # Test getting all plugins
    all_plugins = manager.get_all_plugins()
    assert isinstance(all_plugins, list)
    assert len(all_plugins) == 0


def test_plugin_unloading_errors():
    """Test plugin unloading error cases."""
    manager = PluginManager()
    
    # Try unloading non-existent plugin
    with pytest.raises(KeyError):
        manager.unload_plugin("nonexistent")


def test_plugin_type_enum():
    """Test PluginType enumeration."""
    # Verify all expected plugin types exist
    assert hasattr(PluginType, "ANALYZER")
    assert hasattr(PluginType, "PARSER")
    assert hasattr(PluginType, "TRANSFORMER")
    assert hasattr(PluginType, "OPTIMIZER")
    assert hasattr(PluginType, "VISUALIZER")
    assert hasattr(PluginType, "LLM")
    assert hasattr(PluginType, "REPORTER")
    assert hasattr(PluginType, "CUSTOM")


def test_plugin_dependencies():
    """Test plugin dependency handling."""
    plugin = TestPlugin()
    assert "dep1" in plugin.metadata.dependencies
    assert "dep2" in plugin.metadata.dependencies
    assert len(plugin.metadata.dependencies) == 2


def test_plugin_type_comparison():
    """Test plugin type comparison."""
    assert PluginType.ANALYZER != PluginType.PARSER
    assert PluginType.ANALYZER == PluginType.ANALYZER
    
    plugin = TestPlugin()
    assert plugin.metadata.plugin_type == PluginType.ANALYZER
    assert plugin.metadata.plugin_type != PluginType.PARSER
