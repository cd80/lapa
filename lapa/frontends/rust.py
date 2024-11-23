"""
Rust frontend implementation using tree-sitter and Cargo integration.
"""

from typing import Any, Union, List, Dict
from pathlib import Path
import toml

from ..frontend import (
    Frontend,
    LanguageFeature,
    ParsingError,
    FrontendRegistry
)
from ..ir import IR, Function, Struct, Enum, Trait, Macro, Implementation
from .grammars import create_parser


class RustFrontend(Frontend):
    """Frontend for Rust code analysis using tree-sitter and Cargo integration."""

    def __init__(self):
        """Initialize Rust frontend."""
        super().__init__()

        # Register supported features
        self.features = {
            LanguageFeature.FUNCTIONS,
            LanguageFeature.STRUCTS,
            LanguageFeature.ENUMS,
            LanguageFeature.TRAITS,
            LanguageFeature.GENERICS,
            LanguageFeature.MACROS,
            LanguageFeature.OWNERSHIP,
            LanguageFeature.BORROWING,
            LanguageFeature.LIFETIMES,
            LanguageFeature.MATCH_EXPRESSIONS,
            LanguageFeature.ASYNC_AWAIT,
            LanguageFeature.CLOSURES,
            LanguageFeature.CONCURRENCY,
            LanguageFeature.MODULES,
            LanguageFeature.PACKAGES,
            LanguageFeature.ERROR_HANDLING,
            LanguageFeature.CONDITIONAL_COMPILATION,
            LanguageFeature.TYPE_INFERENCE,
            LanguageFeature.PATTERN_MATCHING
        }

        # Register supported file extensions
        self.file_extensions = {".rs"}

        # Initialize parser
        self.parser = None
        self.language = None

    def supports_language(self, language: str) -> bool:
        """Check if frontend supports a language."""
        return language.lower() == "rust"

    def _ensure_parser(self) -> None:
        """Ensure parser is initialized."""
        if self.parser is None:
            try:
                self.parser = create_parser("rust")
            except Exception as e:
                raise RuntimeError(f"Failed to initialize parser: {str(e)}")

    def parse_project(self, path: Union[str, Path], ir: IR) -> None:
        """
        Parse a Rust project directory, handling Cargo integration.

        Args:
            path: Path to the project directory
            ir: IR to update

        Raises:
            FileNotFoundError: If 'Cargo.toml' doesn't exist
            ParsingError: If parsing fails
        """
        path = Path(path)
        cargo_toml = path / "Cargo.toml"
        if not cargo_toml.exists():
            raise FileNotFoundError(f"'Cargo.toml' not found in {path}")

        # Parse Cargo.toml
        try:
            with open(cargo_toml, "r", encoding="utf-8") as f:
                cargo_config = toml.load(f)
            self._process_cargo_config(cargo_config, ir)
        except Exception as e:
            raise ParsingError(f"Failed to parse 'Cargo.toml': {str(e)}")

        # Parse source files in 'src' directory
        src_dir = path / "src"
        if src_dir.exists():
            for file_path in src_dir.rglob("*.rs"):
                self.parse_file(file_path, ir)
        else:
            raise FileNotFoundError(f"'src' directory not found in {path}")

    def _process_cargo_config(self, cargo_config: dict, ir: IR) -> None:
        """
        Process Cargo configuration and update the IR.

        Args:
            cargo_config: Parsed Cargo.toml content
            ir: IR to update
        """
        package_info = cargo_config.get("package", {})
        dependencies = cargo_config.get("dependencies", {})

        ir.metadata["package_name"] = package_info.get("name", "")
        ir.metadata["version"] = package_info.get("version", "")
        ir.metadata["authors"] = package_info.get("authors", [])
        ir.metadata["edition"] = package_info.get("edition", "")

        ir.dependencies = dependencies

    def parse_file(self, path: Union[str, Path], ir: IR) -> None:
        """
        Parse a Rust source file and update the IR.

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

        try:
            with open(path, "r", encoding="utf-8") as f:
                source = f.read()
            self.parse_string(source, ir)
        except Exception as e:
            raise ParsingError(f"Failed to parse {path}: {str(e)}")

    def parse_string(self, source: str, ir: IR) -> None:
        """
        Parse Rust source code string and update the IR.

        Args:
            source: Source code string
            ir: IR to update

        Raises:
            ParsingError: If parsing fails
        """
        try:
            self._ensure_parser()
            tree = self.parser.parse(bytes(source, "utf8"))
            if tree.root_node.has_error:
                raise ParsingError("Syntax error in source code")
            self._process_ast(tree.root_node, ir)
        except Exception as e:
            raise ParsingError(f"Failed to parse source: {str(e)}")

    def _process_ast(self, node: Any, ir: IR) -> None:
        """
        Process Rust AST and update IR.

        Args:
            node: AST node
            ir: IR to update
        """
        # Process current node
        if node.type == "use_declaration":
            self._process_use_declaration(node, ir)
        elif node.type == "struct_item":
            self._process_struct(node, ir)
        elif node.type == "enum_item":
            self._process_enum(node, ir)
        elif node.type == "function_item":
            self._process_function(node, ir)
        elif node.type == "trait_item":
            self._process_trait(node, ir)
        elif node.type == "impl_item":
            self._process_impl(node, ir)
        elif node.type == "macro_definition":
            self._process_macro(node, ir)

        # Process child nodes
        for child in node.children:
            self._process_ast(child, ir)

    def _process_use_declaration(self, node: Any, ir: IR) -> None:
        """Process 'use' declaration."""
        # Extract used path
        used_path = self._get_node_text(node.child_by_field_name("name"))
        if used_path:
            ir.imports.add(used_path)

    def _process_struct(self, node: Any, ir: IR) -> None:
        """Process struct definition."""
        # Extract struct name
        identifier = node.child_by_field_name("name")
        if identifier:
            struct_name = self._get_node_text(identifier)
            struct = Struct(name=struct_name)
            # Extract fields
            fields_node = node.child_by_field_name("body")
            if fields_node:
                struct.fields = self._extract_fields(fields_node)
            ir.structs.append(struct)

    def _process_enum(self, node: Any, ir: IR) -> None:
        """Process enum definition."""
        # Extract enum name
        identifier = node.child_by_field_name("name")
        if identifier:
            enum_name = self._get_node_text(identifier)
            enum = Enum(name=enum_name)
            # Extract variants
            variants_node = node.child_by_field_name("body")
            if variants_node:
                enum.variants = self._extract_variants(variants_node)
            ir.enums.append(enum)

    def _process_function(self, node: Any, ir: IR) -> None:
        """Process function definition."""
        # Extract function name
        identifier = node.child_by_field_name("name")
        if identifier:
            function_name = self._get_node_text(identifier)
            function = Function(name=function_name)
            # Extract parameters
            parameters_node = node.child_by_field_name("parameters")
            if parameters_node:
                function.parameters = self._extract_parameters(parameters_node)
            # Extract return type
            return_type_node = node.child_by_field_name("return_type")
            if return_type_node:
                function.return_type = self._get_node_text(return_type_node)
            ir.functions.append(function)

    def _process_trait(self, node: Any, ir: IR) -> None:
        """Process trait definition."""
        # Extract trait name
        identifier = node.child_by_field_name("name")
        if identifier:
            trait_name = self._get_node_text(identifier)
            trait = Trait(name=trait_name)
            # Extract methods
            trait.items = self._extract_trait_items(node)
            ir.traits.append(trait)

    def _process_impl(self, node: Any, ir: IR) -> None:
        """Process implementation block."""
        # Extract type being implemented
        type_node = node.child_by_field_name("type")
        if type_node:
            type_name = self._get_node_text(type_node)
            impl = Implementation(type_name=type_name)
            # Extract methods
            impl.methods = self._extract_impl_methods(node)
            ir.implementations.append(impl)

    def _process_macro(self, node: Any, ir: IR) -> None:
        """Process macro definition."""
        # Extract macro name
        identifier = node.child_by_field_name("name")
        if identifier:
            macro_name = self._get_node_text(identifier)
            macro = Macro(name=macro_name)
            # Extract macro body
            macro.body = self._get_node_text(node.child_by_field_name("body"))
            ir.macros.append(macro)

    def _extract_fields(self, node: Any) -> List[Dict[str, Any]]:
        """Extract fields from a struct or enum variant."""
        fields = []
        for field_node in node.named_children:
            if field_node.type == "field_declaration":
                field_name_node = field_node.child_by_field_name("name")
                field_type_node = field_node.child_by_field_name("type")
                field_name = self._get_node_text(field_name_node)
                field_type = self._get_node_text(field_type_node)
                fields.append({"name": field_name, "type": field_type})
        return fields

    def _extract_variants(self, node: Any) -> List[Dict[str, Any]]:
        """Extract variants from an enum."""
        variants = []
        for variant_node in node.named_children:
            if variant_node.type == "enum_variant":
                variant_name_node = variant_node.child_by_field_name("name")
                variant_name = self._get_node_text(variant_name_node)
                variants.append({"name": variant_name})
        return variants

    def _extract_parameters(self, node: Any) -> List[Dict[str, Any]]:
        """Extract parameters from a function."""
        parameters = []
        for param_node in node.named_children:
            if param_node.type == "parameter":
                param_name_node = param_node.child_by_field_name("name")
                param_type_node = param_node.child_by_field_name("type")
                param_name = self._get_node_text(param_name_node)
                param_type = self._get_node_text(param_type_node)
                parameters.append({"name": param_name, "type": param_type})
        return parameters

    def _extract_trait_items(self, node: Any) -> List[Any]:
        """Extract items (methods, associated types) from a trait."""
        items = []
        items_node = node.child_by_field_name("body")
        if items_node:
            for item_node in items_node.named_children:
                if item_node.type == "function_item":
                    function = self._process_function(item_node, IR())
                    items.append(function)
        return items

    def _extract_impl_methods(self, node: Any) -> List[Any]:
        """Extract methods from an implementation block."""
        methods = []
        items_node = node.child_by_field_name("body")
        if items_node:
            for item_node in items_node.named_children:
                if item_node.type == "function_item":
                    function = self._process_function(item_node, IR())
                    methods.append(function)
        return methods

    def _get_node_text(self, node: Any) -> str:
        """Helper method to get text of a node."""
        if node is not None:
            return node.text.decode('utf-8')
        return ""

# Register frontend
FrontendRegistry.register("rust", RustFrontend)
