"""
Tests for the LAPA analyzer module.
"""

import pytest
from pathlib import Path
from lapa import Analyzer
from lapa.plugin import Plugin, PluginType, PluginMetadata


class MockPlugin(Plugin):
    """Mock plugin for testing."""
    
    def __init__(self):
        super().__init__()
        self.metadata = PluginMetadata(
            name="mock_plugin",
            version="0.1.0",
            plugin_type=PluginType.ANALYZER,
            description="Mock plugin for testing"
        )
        self.initialized = False
        self.cleaned_up = False

    def initialize(self) -> None:
        self.initialized = True

    def cleanup(self) -> None:
        self.cleaned_up = True


def test_analyzer_initialization():
    """Test basic analyzer initialization."""
    analyzer = Analyzer()
    assert analyzer is not None
    assert analyzer.plugins == []
    assert analyzer.config == {}


def test_analyzer_with_config():
    """Test analyzer initialization with config."""
    config = {"test_key": "test_value"}
    analyzer = Analyzer(config=config)
    assert analyzer.config == config


def test_analyzer_with_plugins():
    """Test analyzer initialization with plugins."""
    plugin = MockPlugin()
    analyzer = Analyzer(plugins=[plugin])
    assert len(analyzer.plugins) == 1
    assert analyzer.plugins[0] == plugin


def test_add_remove_plugin():
    """Test adding and removing plugins."""
    analyzer = Analyzer()
    plugin = MockPlugin()
    
    # Add plugin
    analyzer.add_plugin(plugin)
    assert len(analyzer.plugins) == 1
    assert analyzer.plugins[0] == plugin
    
    # Remove plugin
    analyzer.remove_plugin(plugin)
    assert len(analyzer.plugins) == 0


def test_invalid_plugin():
    """Test adding invalid plugin."""
    analyzer = Analyzer()
    with pytest.raises(ValueError):
        analyzer.add_plugin("not a plugin")


def test_load_file_not_found():
    """Test loading non-existent file."""
    analyzer = Analyzer()
    with pytest.raises(FileNotFoundError):
        analyzer.load_file("nonexistent.py")


def test_load_directory_not_found():
    """Test loading non-existent directory."""
    analyzer = Analyzer()
    with pytest.raises(NotADirectoryError):
        analyzer.load_directory("nonexistent_dir")


def test_get_ir():
    """Test getting IR instance."""
    analyzer = Analyzer()
    ir = analyzer.get_ir()
    assert ir is not None


def test_reset():
    """Test analyzer reset."""
    analyzer = Analyzer()
    plugin = MockPlugin()
    analyzer.add_plugin(plugin)
    
    # Verify initial state
    assert len(analyzer.plugins) == 1
    
    # Reset
    analyzer.reset()
    
    # Verify IR is reset but plugins remain
    assert len(analyzer.plugins) == 1


def test_analyze_not_implemented():
    """Test analyze method raises NotImplementedError."""
    analyzer = Analyzer()
    with pytest.raises(NotImplementedError):
        analyzer.analyze("test.py")


def test_get_plugins():
    """Test getting plugins list."""
    analyzer = Analyzer()
    plugin1 = MockPlugin()
    plugin2 = MockPlugin()
    
    analyzer.add_plugin(plugin1)
    analyzer.add_plugin(plugin2)
    
    plugins = analyzer.get_plugins()
    assert len(plugins) == 2
    assert plugin1 in plugins
    assert plugin2 in plugins
    
    # Verify it's a copy
    plugins.clear()
    assert len(analyzer.plugins) == 2
