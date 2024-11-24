from typing import Union
from pathlib import Path

from lapa.frontend import Frontend, LanguageFeature, ParsingError
from lapa.ir import IR

from tree_sitter import Language, Parser
from .grammars import get_language, create_parser
# Initialize the tree-sitter C++ language

class CppFrontend(Frontend):
    """Frontend for C/C++ code analysis using tree-sitter."""

    def __init__(self):
        """Initialize C/C++ frontend."""
        super().__init__()

        # Initialize tree-sitter parser for C++
        self.parser = create_parser("cpp")

        # Register supported features
        self.features = {
            LanguageFeature.FUNCTIONS,
            LanguageFeature.CLASSES,
            LanguageFeature.INHERITANCE,
            LanguageFeature.TEMPLATES,
            LanguageFeature.OPERATOR_OVERLOADING,
            LanguageFeature.NAMESPACES,
            LanguageFeature.POINTERS,
            LanguageFeature.REFERENCES,
            LanguageFeature.MEMORY_MANAGEMENT,
            LanguageFeature.EXCEPTIONS,
            LanguageFeature.PREPROCESSOR,
            LanguageFeature.INLINE_ASSEMBLY,
            LanguageFeature.FRIEND_FUNCTIONS,
            LanguageFeature.MULTIPLE_INHERITANCE,
            LanguageFeature.VIRTUAL_FUNCTIONS,
            LanguageFeature.CONST_CORRECTNESS,
            LanguageFeature.RVALUE_REFERENCES,
            LanguageFeature.MOVE_SEMANTICS,
            LanguageFeature.VARIADIC_TEMPLATES,
            LanguageFeature.TYPE_INFERENCE,
            LanguageFeature.LAMBDA_FUNCTIONS,
            LanguageFeature.MODULES,
            LanguageFeature.CONCEPTS,
            LanguageFeature.RANGES,
            LanguageFeature.CONSTEXPR,
            LanguageFeature.ATTRIBUTES,
            LanguageFeature.STRUCTURED_BINDINGS,
            LanguageFeature.FOLD_EXPRESSIONS,
            LanguageFeature.DESIGNATED_INITIALIZERS,
            LanguageFeature.THREE_WAY_COMPARISON
        }

        # Register supported file extensions
        self.file_extensions = {
            ".c", ".h",  # C
            ".cpp", ".hpp", ".cxx", ".hxx", ".cc", ".hh",  # C++
            ".c++", ".h++", ".tpp", ".txx",  # Additional C++
            ".ipp", ".ixx",  # Implementation files
            ".inl"  # Inline files
        }

    def parse_file(self, path: Union[str, Path], ir: IR) -> None:
        """
        Parse a C/C++ source file and update the IR.

        Args:
            path: Path to source file
            ir: IR to update

        Raises:
            FileNotFoundError: If file doesn't exist
            ParsingError: If parsing fails
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        with open(path, 'rb') as f:
            source_code = f.read()
        self.parse_string(source_code, ir)

    def parse_string(self, source: Union[str, bytes], ir: IR) -> None:
        """
        Parse C/C++ source code string and update the IR.

        Args:
            source: Source code string
            ir: IR to update

        Raises:
            ParsingError: If parsing fails
        """
        if isinstance(source, str):
            source = source.encode('utf8')
        tree = self.parser.parse(source)
        root_node = tree.root_node
        self._walk_tree(root_node, ir, source)

    def _walk_tree(self, node, ir: IR, source: bytes) -> None:
        """
        Recursively walk the syntax tree and update the IR.

        Args:
            node: Current node in the syntax tree
            ir: IR to update
            source: Source code bytes
        """
        if node.type == 'function_definition':
            # Extract function name
            declarator = node.child_by_field_name('declarator')
            if declarator:
                function_name = self._get_node_text(declarator, source)
                ir.add_function(function_name.strip())
        elif node.type == 'class_specifier':
            # Extract class name
            class_name_node = node.child_by_field_name('name')
            if class_name_node:
                class_name = self._get_node_text(class_name_node, source)
                ir.add_class(class_name.strip())

        # Recursively process child nodes
        for child in node.children:
            self._walk_tree(child, ir, source)

    def _get_node_text(self, node, source: bytes) -> str:
        """
        Get the text corresponding to a node.

        Args:
            node: Node in the syntax tree
            source: Source code bytes

        Returns:
            Text content of the node
        """
        return source[node.start_byte:node.end_byte].decode('utf8')
