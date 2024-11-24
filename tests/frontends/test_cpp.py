"""
Tests for C/C++ frontend.
"""

from pathlib import Path
import pytest

from lapa.frontend import LanguageFeature, ParsingError
from lapa.frontends.cpp import CppFrontend
from lapa.ir import IR


def test_cpp_frontend_features():
    """Test C/C++ frontend features."""
    frontend = CppFrontend()
    features = frontend._get_language_features()
    
    assert LanguageFeature.FUNCTIONS in features
    assert LanguageFeature.CLASSES in features
    assert LanguageFeature.INHERITANCE in features
    assert LanguageFeature.TEMPLATES in features
    assert LanguageFeature.OPERATOR_OVERLOADING in features
    assert LanguageFeature.NAMESPACES in features
    assert LanguageFeature.POINTERS in features
    assert LanguageFeature.REFERENCES in features
    assert LanguageFeature.MEMORY_MANAGEMENT in features
    assert LanguageFeature.EXCEPTIONS in features
    assert LanguageFeature.PREPROCESSOR in features
    assert LanguageFeature.INLINE_ASSEMBLY in features
    assert LanguageFeature.FRIEND_FUNCTIONS in features
    assert LanguageFeature.MULTIPLE_INHERITANCE in features
    assert LanguageFeature.VIRTUAL_FUNCTIONS in features
    assert LanguageFeature.CONST_CORRECTNESS in features
    assert LanguageFeature.RVALUE_REFERENCES in features
    assert LanguageFeature.MOVE_SEMANTICS in features
    assert LanguageFeature.VARIADIC_TEMPLATES in features
    assert LanguageFeature.TYPE_INFERENCE in features
    assert LanguageFeature.LAMBDA_FUNCTIONS in features
    assert LanguageFeature.CONCEPTS in features
    assert LanguageFeature.RANGES in features
    assert LanguageFeature.CONSTEXPR in features
    assert LanguageFeature.ATTRIBUTES in features
    assert LanguageFeature.STRUCTURED_BINDINGS in features
    assert LanguageFeature.FOLD_EXPRESSIONS in features
    assert LanguageFeature.DESIGNATED_INITIALIZERS in features
    assert LanguageFeature.THREE_WAY_COMPARISON in features


def test_cpp_frontend_file_extensions():
    """Test C/C++ frontend file extensions."""
    frontend = CppFrontend()
    extensions = frontend.get_file_extensions()
    
    # C extensions
    assert ".c" in extensions
    assert ".h" in extensions
    
    # C++ extensions
    assert ".cpp" in extensions
    assert ".hpp" in extensions
    assert ".cxx" in extensions
    assert ".hxx" in extensions
    assert ".cc" in extensions
    assert ".hh" in extensions
    assert ".c++" in extensions
    assert ".h++" in extensions
    assert ".tpp" in extensions
    assert ".txx" in extensions
    assert ".ipp" in extensions
    assert ".ixx" in extensions
    assert ".inl" in extensions


def test_parse_nonexistent_file():
    """Test handling of nonexistent files."""
    frontend = CppFrontend()
    ir = IR()
    
    with pytest.raises(FileNotFoundError):
        frontend.parse_file("nonexistent.cpp", ir)


@pytest.mark.skip("C/C++ parsing not yet fully implemented")
def test_parse_simple_function():
    """Test parsing simple function."""
    frontend = CppFrontend()
    ir = IR()
    
    code = """
    int add(int a, int b) {
        return a + b;
    }
    """
    
    frontend.parse_string(code, ir)
    # TODO: Add assertions about IR content


@pytest.mark.skip("C/C++ parsing not yet fully implemented")
def test_parse_class():
    """Test parsing class definition."""
    frontend = CPPFrontend()
    ir = IR()
    
    code = """
    class Person {
    public:
        Person(std::string name) : name_(name) {}
        
        std::string getName() const {
            return name_;
        }
        
    private:
        std::string name_;
    };
    """
    
    frontend.parse_string(code, ir)
    # TODO: Add assertions about IR content


@pytest.mark.skip("C/C++ parsing not yet fully implemented")
def test_parse_template():
    """Test parsing template."""
    frontend = CPPFrontend()
    ir = IR()
    
    code = """
    template<typename T>
    class Container {
    public:
        void add(const T& item) {
            items_.push_back(item);
        }
        
    private:
        std::vector<T> items_;
    };
    """
    
    frontend.parse_string(code, ir)
    # TODO: Add assertions about IR content


@pytest.mark.skip("C/C++ parsing not yet fully implemented")
def test_parse_includes():
    """Test parsing include directives."""
    frontend = CPPFrontend()
    ir = IR()
    
    code = """
    #include <vector>
    #include <string>
    #include "myheader.h"
    """
    
    frontend.parse_string(code, ir)
    # TODO: Add assertions about IR content


@pytest.mark.skip("C/C++ parsing not yet fully implemented")
def test_parse_namespace():
    """Test parsing namespace."""
    frontend = CPPFrontend()
    ir = IR()
    
    code = """
    namespace utils {
        int add(int a, int b) {
            return a + b;
        }
    }
    """
    
    frontend.parse_string(code, ir)
    # TODO: Add assertions about IR content


@pytest.mark.skip("C/C++ parsing not yet fully implemented")
def test_parse_operator_overload():
    """Test parsing operator overloading."""
    frontend = CPPFrontend()
    ir = IR()
    
    code = """
    class Complex {
    public:
        Complex operator+(const Complex& other) const {
            return Complex(real + other.real, imag + other.imag);
        }
        
    private:
        double real;
        double imag;
    };
    """
    
    frontend.parse_string(code, ir)
    # TODO: Add assertions about IR content


@pytest.mark.skip("C/C++ parsing not yet fully implemented")
def test_parse_multiple_inheritance():
    """Test parsing multiple inheritance."""
    frontend = CPPFrontend()
    ir = IR()
    
    code = """
    class A {};
    class B {};
    class C : public A, public B {};
    """
    
    frontend.parse_string(code, ir)
    # TODO: Add assertions about IR content


@pytest.mark.skip("C/C++ parsing not yet fully implemented")
def test_parse_friend():
    """Test parsing friend declarations."""
    frontend = CPPFrontend()
    ir = IR()
    
    code = """
    class A {
        friend class B;
        friend void func(A&);
    };
    """
    
    frontend.parse_string(code, ir)
    # TODO: Add assertions about IR content
