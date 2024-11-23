"""
Tests for the LAPA IR (Intermediate Representation) module.
"""

import pytest
from lapa.ir import IR, IRNode, IRNodeType, Position


def test_ir_initialization():
    """Test basic IR initialization."""
    ir = IR()
    assert ir is not None
    assert ir.root.node_type == IRNodeType.PROGRAM
    assert len(ir.symbol_table) == 0
    assert len(ir.type_information) == 0
    assert len(ir.dependencies) == 0


def test_ir_node_creation():
    """Test IR node creation and properties."""
    position = Position(line=1, column=0, file="test.py")
    node = IRNode(
        node_type=IRNodeType.FUNCTION,
        position=position,
        attributes={"name": "test_func"}
    )
    
    assert node.node_type == IRNodeType.FUNCTION
    assert node.position == position
    assert node.attributes["name"] == "test_func"
    assert len(node.children) == 0
    assert node.parent is None


def test_ir_node_hierarchy():
    """Test IR node parent-child relationships."""
    parent = IRNode(node_type=IRNodeType.CLASS)
    child1 = IRNode(node_type=IRNodeType.METHOD)
    child2 = IRNode(node_type=IRNodeType.METHOD)
    
    # Add children
    parent.add_child(child1)
    parent.add_child(child2)
    
    # Verify relationships
    assert len(parent.children) == 2
    assert child1.parent == parent
    assert child2.parent == parent
    
    # Remove child
    parent.remove_child(child1)
    assert len(parent.children) == 1
    assert child1.parent is None
    assert child2.parent == parent


def test_ir_clear():
    """Test clearing IR state."""
    ir = IR()
    
    # Add some data
    ir.symbol_table["test"] = "value"
    ir.type_information["test"] = "type"
    ir.dependencies.add("dependency")
    
    # Clear
    ir.clear()
    
    # Verify cleared state
    assert len(ir.symbol_table) == 0
    assert len(ir.type_information) == 0
    assert len(ir.dependencies) == 0
    assert ir.root.node_type == IRNodeType.PROGRAM


def test_ir_validate():
    """Test IR validation."""
    ir = IR()
    assert ir.validate() is True


def test_ir_node_types():
    """Test all IR node types can be created."""
    for node_type in IRNodeType:
        node = IRNode(node_type=node_type)
        assert node.node_type == node_type


def test_position_creation():
    """Test Position dataclass."""
    pos = Position(line=10, column=5, file="test.py")
    assert pos.line == 10
    assert pos.column == 5
    assert pos.file == "test.py"


def test_ir_get_symbols():
    """Test getting symbol table."""
    ir = IR()
    ir.symbol_table["test"] = "value"
    
    symbols = ir.get_symbols()
    assert len(symbols) == 1
    assert symbols["test"] == "value"
    
    # Verify it's a copy
    symbols["new"] = "value"
    assert "new" not in ir.symbol_table


def test_ir_get_types():
    """Test getting type information."""
    ir = IR()
    ir.type_information["test"] = "type"
    
    types = ir.get_types()
    assert len(types) == 1
    assert types["test"] == "type"
    
    # Verify it's a copy
    types["new"] = "type"
    assert "new" not in ir.type_information


def test_ir_get_dependencies():
    """Test getting dependencies."""
    ir = IR()
    ir.dependencies.add("dep1")
    ir.dependencies.add("dep2")
    
    deps = ir.get_dependencies()
    assert len(deps) == 2
    assert "dep1" in deps
    assert "dep2" in deps
    
    # Verify it's a copy
    deps.add("dep3")
    assert "dep3" not in ir.dependencies


def test_build_from_ast_not_implemented():
    """Test build_from_ast raises NotImplementedError."""
    ir = IR()
    with pytest.raises(NotImplementedError):
        ir.build_from_ast(None)


def test_optimize_not_implemented():
    """Test optimize raises NotImplementedError."""
    ir = IR()
    with pytest.raises(NotImplementedError):
        ir.optimize()


def test_to_dot_not_implemented():
    """Test to_dot raises NotImplementedError."""
    ir = IR()
    with pytest.raises(NotImplementedError):
        ir.to_dot()


def test_get_node_by_position():
    """Test getting node by position."""
    ir = IR()
    pos = Position(line=1, column=0, file="test.py")
    result = ir.get_node_by_position(pos)
    assert result is None  # Currently returns None as not implemented
