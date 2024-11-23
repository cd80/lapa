"""
Unit tests for the ownership system analysis in the Rust frontend.
"""

import pytest
from lapa.frontends.rust import RustFrontend
from lapa.ir import IR
from lapa.frontend import ParsingError
from pathlib import Path


def test_parse_mutable_variable(tmp_path):
    source_code = '''
    fn main() {
        let mut x = 5;
    }
    '''
    test_file = tmp_path / "mutable_variable.rs"
    test_file.write_text(source_code)
    frontend = RustFrontend()
    ir = IR()
    frontend.parse_file(test_file, ir)
    assert len(ir.variables) == 1
    variable = ir.variables[0]
    assert variable.name == "x"
    assert variable.ownership.is_mutable is True


def test_parse_immutable_variable(tmp_path):
    source_code = '''
    fn main() {
        let x = 5;
    }
    '''
    test_file = tmp_path / "immutable_variable.rs"
    test_file.write_text(source_code)
    frontend = RustFrontend()
    ir = IR()
    frontend.parse_file(test_file, ir)
    assert len(ir.variables) == 1
    variable = ir.variables[0]
    assert variable.name == "x"
    assert variable.ownership.is_mutable is False


def test_parse_function_parameter_borrowed(tmp_path):
    source_code = '''
    fn print_value(val: &i32) {
        println!("{}", val);
    }
    '''
    test_file = tmp_path / "borrowed_parameter.rs"
    test_file.write_text(source_code)
    frontend = RustFrontend()
    ir = IR()
    frontend.parse_file(test_file, ir)
    assert len(ir.functions) == 1
    function = ir.functions[0]
    assert len(function.parameters) == 1
    param = function.parameters[0]
    assert param['name'] == "val"
    assert param['ownership'].is_reference is True
    assert param['ownership'].is_mutable is False


def test_parse_function_parameter_mut_borrowed(tmp_path):
    source_code = '''
    fn increment(val: &mut i32) {
        *val += 1;
    }
    '''
    test_file = tmp_path / "mut_borrowed_parameter.rs"
    test_file.write_text(source_code)
    frontend = RustFrontend()
    ir = IR()
    frontend.parse_file(test_file, ir)
    assert len(ir.functions) == 1
    function = ir.functions[0]
    assert len(function.parameters) == 1
    param = function.parameters[0]
    assert param['name'] == "val"
    assert param['ownership'].is_reference is True
    assert param['ownership'].is_mutable is True


def test_parse_lifetime_annotations(tmp_path):
    source_code = '''
    fn get_str<'a>(s: &'a str) -> &'a str {
        s
    }
    '''
    test_file = tmp_path / "lifetime_annotation.rs"
    test_file.write_text(source_code)
    frontend = RustFrontend()
    ir = IR()
    frontend.parse_file(test_file, ir)
    assert len(ir.functions) == 1
    function = ir.functions[0]
    assert len(function.parameters) == 1
    param = function.parameters[0]
    assert param['name'] == "s"
    assert param['ownership'].lifetime == "a"
