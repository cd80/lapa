"""
Unit tests for the Rust frontend.
"""

import pytest
from lapa.frontends.rust import RustFrontend
from lapa.ir import IR
from lapa.frontend import ParsingError
from pathlib import Path


def test_rust_frontend_initialization():
    frontend = RustFrontend()
    assert frontend is not None


def test_rust_frontend_features():
    frontend = RustFrontend()
    assert len(frontend.features) > 0


def test_rust_frontend_file_extensions():
    frontend = RustFrontend()
    assert ".rs" in frontend.file_extensions


def test_rust_frontend_supports_language():
    frontend = RustFrontend()
    assert frontend.supports_language("rust")
    assert not frontend.supports_language("python")


def test_parse_nonexistent_file():
    frontend = RustFrontend()
    ir = IR()
    with pytest.raises(FileNotFoundError):
        frontend.parse_file("nonexistent.rs", ir)


def test_parse_invalid_syntax(tmp_path):
    source_code = "fn invalid_code("
    test_file = tmp_path / "invalid.rs"
    test_file.write_text(source_code)
    frontend = RustFrontend()
    ir = IR()
    with pytest.raises(ParsingError):
        frontend.parse_file(test_file, ir)


def test_parse_simple_function(tmp_path):
    source_code = '''
    fn add(a: i32, b: i32) -> i32 {
        a + b
    }
    '''
    test_file = tmp_path / "simple_function.rs"
    test_file.write_text(source_code)
    frontend = RustFrontend()
    ir = IR()
    frontend.parse_file(test_file, ir)
    assert len(ir.functions) == 1
    assert ir.functions[0].name == "add"
    assert ir.functions[0].return_type == "i32"


def test_parse_struct(tmp_path):
    source_code = '''
    struct Point {
        x: f64,
        y: f64,
    }
    '''
    test_file = tmp_path / "point.rs"
    test_file.write_text(source_code)
    frontend = RustFrontend()
    ir = IR()
    frontend.parse_file(test_file, ir)
    assert len(ir.structs) == 1
    assert ir.structs[0].name == "Point"
    assert len(ir.structs[0].fields) == 2


def test_parse_enum(tmp_path):
    source_code = '''
    enum Direction {
        North,
        South,
        East,
        West,
    }
    '''
    test_file = tmp_path / "direction.rs"
    test_file.write_text(source_code)
    frontend = RustFrontend()
    ir = IR()
    frontend.parse_file(test_file, ir)
    assert len(ir.enums) == 1
    assert ir.enums[0].name == "Direction"
    assert len(ir.enums[0].variants) == 4


def test_parse_trait(tmp_path):
    source_code = '''
    trait Drawable {
        fn draw(&self);
    }
    '''
    test_file = tmp_path / "drawable.rs"
    test_file.write_text(source_code)
    frontend = RustFrontend()
    ir = IR()
    frontend.parse_file(test_file, ir)
    assert len(ir.traits) == 1
    assert ir.traits[0].name == "Drawable"


def test_parse_macro(tmp_path):
    source_code = '''
    macro_rules! hello_world {
        () => {
            println!("Hello, world!");
        };
    }
    '''
    test_file = tmp_path / "macro.rs"
    test_file.write_text(source_code)
    frontend = RustFrontend()
    ir = IR()
    frontend.parse_file(test_file, ir)
    assert len(ir.macros) == 1
    assert ir.macros[0].name == "hello_world"


def test_parse_project_missing_cargo_toml(tmp_path):
    project_dir = tmp_path / "missing_project"
    project_dir.mkdir()
    frontend = RustFrontend()
    ir = IR()
    with pytest.raises(FileNotFoundError):
        frontend.parse_project(project_dir, ir)


def test_parse_project(tmp_path):
    project_dir = tmp_path / "rust_project"
    project_dir.mkdir()
    cargo_toml_content = '''
    [package]
    name = "rust_project"
    version = "0.1.0"
    authors = ["Author <author@example.com>"]
    edition = "2021"
    '''
    src_dir = project_dir / "src"
    src_dir.mkdir()
    main_rs_content = '''
    fn main() {
        println!("Hello, Rust!");
    }
    '''
    cargo_toml_file = project_dir / "Cargo.toml"
    main_rs_file = src_dir / "main.rs"
    cargo_toml_file.write_text(cargo_toml_content)
    main_rs_file.write_text(main_rs_content)
    frontend = RustFrontend()
    ir = IR()
    frontend.parse_project(project_dir, ir)
    assert ir.metadata["package_name"] == "rust_project"
    assert ir.metadata["version"] == "0.1.0"
    assert "authors" in ir.metadata
    assert len(ir.functions) == 1
    assert ir.functions[0].name == "main"
