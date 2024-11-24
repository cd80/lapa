"""
Initialize frontends and register them with the FrontendRegistry.
"""

from lapa.frontend import FrontendRegistry
from lapa.frontends.python import PythonFrontend
from lapa.frontends.javascript import JavaScriptFrontend
from lapa.frontends.cpp import CppFrontend
from lapa.frontends.rust import RustFrontend
from lapa.frontends.java import JavaFrontend

# Register frontends
FrontendRegistry.register("Python", PythonFrontend)
FrontendRegistry.register("JavaScript", JavaScriptFrontend)
FrontendRegistry.register("Cpp", CppFrontend)
FrontendRegistry.register("Rust", RustFrontend)
FrontendRegistry.register("Java", JavaFrontend)
