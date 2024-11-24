"""
Java Frontend for LAPA Framework.

This module provides the frontend implementation for Java, including parsing
Java source code using Tree-sitter and converting it into the intermediate
representation (IR) used by the LAPA framework.
"""

from lapa.frontend import Frontend, LanguageFeature, ParsingError
from lapa.ir import IRNode, IRNodeType, IR
from lapa.frontends.grammars import get_language, create_parser
from typing import Any, Union
import tree_sitter
import os


class JavaFrontend(Frontend):
    """
    Java language frontend for the LAPA framework.
    """

    def __init__(self):
        super().__init__()
        self.language_name = "Java"
        self.features = {
            LanguageFeature.FUNCTIONS,
            LanguageFeature.CLASSES,
            LanguageFeature.INTERFACES,
            LanguageFeature.ENUMS,
            LanguageFeature.EXCEPTIONS,
            LanguageFeature.GENERICS,
            LanguageFeature.ANNOTATIONS,
            LanguageFeature.LAMBDA_FUNCTIONS,
            LanguageFeature.IMPORTS,
            LanguageFeature.PACKAGES,
        }
        self.file_extensions = {".java"}
        self.language = get_language("java")
        self.parser = create_parser("java")

    def supports_language(self, language: str) -> bool:
        """
        Check if the frontend supports a language.

        Args:
            language: The language to check.

        Returns:
            True if the language is supported, False otherwise.
        """
        return language.lower() == "java"

    def supports_file_extension(self, extension: str) -> bool:
        """
        Check if the frontend supports a file extension.

        Args:
            extension: The file extension to check (with dot).

        Returns:
            True if the extension is supported.
        """
        return extension.lower() in self.file_extensions

    def supports_extension(self, extension: str) -> bool:
        """
        Check if the frontend supports a file extension.

        Args:
            extension: The file extension to check (with dot).

        Returns:
            True if the extension is supported.
        """
        return self.supports_file_extension(extension)

    def supports_feature(self, feature: LanguageFeature) -> bool:
        """
        Check if the frontend supports a language feature.

        Args:
            feature: The language feature to check.

        Returns:
            True if the feature is supported.
        """
        return feature in self.features

    def parse(self, code: Union[str, os.PathLike], ir: IR) -> None:
        """
        Parses Java code from a string or file and updates the IR.

        Args:
            code: The Java source code as a string or path to a file.
            ir: The intermediate representation to update.

        Raises:
            ParsingError: If parsing fails.
        """
        if isinstance(code, str):
            self.parse_string(code, ir)
        else:
            self.parse_file(code, ir)

    def parse_file(self, path: Union[str, os.PathLike], ir: IR) -> None:
        """
        Parses a Java source file and updates the IR.

        Args:
            path: The path to the Java source file.
            ir: The intermediate representation to update.

        Raises:
            FileNotFoundError: If the file does not exist.
            ParsingError: If parsing fails.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")

        with open(path, "r", encoding="utf-8") as file:
            code = file.read()
        self.parse_string(code, ir)

    def parse_string(self, source: str, ir: IR) -> None:
        """
        Parses Java code from a string and updates the IR.

        Args:
            source: The Java source code as a string.
            ir: The intermediate representation to update.

        Raises:
            ParsingError: If parsing fails.
        """
        if not self.parser:
            raise RuntimeError("Parser not initialized for Java.")

        tree = self.parser.parse(bytes(source, "utf8"))
        if tree.root_node.has_error:
            raise ParsingError("Syntax error in Java code.")

        ir_node = self.ast_to_ir(tree)
        ir.root.add_child(ir_node)

    def ast_to_ir(self, ast: Any) -> IRNode:
        """
        Converts the AST into the intermediate representation (IR).

        Args:
            ast: The abstract syntax tree obtained from parsing.

        Returns:
            The root IRNode representing the code.
        """
        root_node = ast.root_node
        ir_node = self._convert_node(root_node)
        return ir_node

    def _convert_node(self, node: tree_sitter.Node) -> IRNode:
        """
        Recursively converts a Tree-sitter node into an IRNode.

        Args:
            node: The Tree-sitter node to convert.

        Returns:
            The corresponding IRNode.
        """
        node_type = self._map_node_type(node.type)
        ir_node = IRNode(
            node_type=node_type,
            name=self._get_node_name(node),
            position=self._get_position(node),
            attributes={}
        )

        for child in node.children:
            child_ir_node = self._convert_node(child)
            ir_node.add_child(child_ir_node)

        return ir_node

    def _map_node_type(self, node_type_str: str) -> IRNodeType:
        """
        Maps a Tree-sitter node type string to an IRNodeType.

        Args:
            node_type_str: The node type as a string from Tree-sitter.

        Returns:
            The corresponding IRNodeType.
        """
        mapping = {
            "program": IRNodeType.PROGRAM,
            "class_declaration": IRNodeType.CLASS,
            "method_declaration": IRNodeType.METHOD,
            "constructor_declaration": IRNodeType.CONSTRUCTOR,
            "variable_declarator": IRNodeType.VARIABLE,
            "interface_declaration": IRNodeType.CLASS,  # Interfaces are treated as classes with special attributes
            "enum_declaration": IRNodeType.ENUM,
            "field_declaration": IRNodeType.FIELD,
            "annotation": IRNodeType.MACRO,  # Annotations can be treated similarly to macros
            "package_declaration": IRNodeType.NAMESPACE,
            "import_declaration": IRNodeType.IMPORT,
            "lambda_expression": IRNodeType.FUNCTION,  # Lambdas are functions
            "expression_statement": IRNodeType.NO_OP,
            "if_statement": IRNodeType.IF,
            "while_statement": IRNodeType.WHILE,
            "for_statement": IRNodeType.FOR,
            "return_statement": IRNodeType.RETURN,
            "binary_expression": IRNodeType.BINARY_OP,  # Changed from BINARY_OPERATION
            "method_invocation": IRNodeType.FUNCTION_CALL,
            # Add more mappings as needed
        }
        return mapping.get(node_type_str, IRNodeType.NO_OP)

    def _get_node_name(self, node: tree_sitter.Node) -> str:
        """
        Retrieves the name of an AST node if it has one.

        Args:
            node: The Tree-sitter node.

        Returns:
            The name of the node or an empty string.
        """
        if "identifier" in [child.type for child in node.children]:
            for child in node.children:
                if child.type == "identifier":
                    return self._get_node_text(child)
        return ""

    def _get_node_text(self, node: tree_sitter.Node) -> str:
        """
        Retrieves the text corresponding to the node.

        Args:
            node: The Tree-sitter node.

        Returns:
            The text content of the node.
        """
        return node.text.decode("utf8")

    def _get_position(self, node: tree_sitter.Node):
        """
        Retrieves the position of the node in the source code.

        Args:
            node: The Tree-sitter node.

        Returns:
            A Position object with line, column, and file information.
        """
        return None  # Position information can be added if available


# Register the Java frontend
from lapa.frontend import FrontendRegistry

FrontendRegistry.register("java", JavaFrontend)
