"""
Rust frontend implementation using tree-sitter and Cargo integration, with ownership system analysis.
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
from ..ir import (
    IR,
    Function,
    Struct,
    Enum,
    Trait,
    Macro,
    Implementation,
    Variable,
    OwnershipInfo
)
from .grammars import create_parser


class RustFrontend(Frontend):
    """Frontend for Rust code analysis with ownership system analysis."""

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
            LanguageFeature.PATTERN_MATCHING,
            LanguageFeature.MUTABILITY,
            LanguageFeature.LIFETIME_ANNOTATIONS
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
        elif node.type == "let_declaration":
            self._process_variable_declaration(node, ir)

        # Process child nodes
        for child in node.named_children:
            self._process_ast(child, ir)

    def _process_use_declaration(self, node: Any, ir: IR) -> None:
        """Process 'use' declaration."""
        used_path = self._get_node_text(node.child_by_field_name("argument"))
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
            ir.add_struct(struct)

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
            ir.add_enum(enum)

    def _process_trait(self, node: Any, ir: IR) -> None:
        """Process trait definition."""
        # Extract trait name
        identifier = node.child_by_field_name("name")
        if identifier:
            trait_name = self._get_node_text(identifier)
            trait = Trait(name=trait_name)
            # Extract items
            items_node = node.child_by_field_name("body")
            if items_node:
                trait.items = self._extract_trait_items(items_node)
            ir.add_trait(trait)

    def _process_macro(self, node: Any, ir: IR) -> None:
        """Process macro definition."""
        # Extract macro name
        identifier = node.child_by_field_name("name")
        if identifier:
            macro_name = self._get_node_text(identifier)
            macro_body = self._get_node_text(node.child_by_field_name("body"))
            macro = Macro(name=macro_name, body=macro_body)
            ir.add_macro(macro)

    def _process_variable_declaration(self, node: Any, ir: IR) -> None:
        """Process variable declaration with ownership information."""
        variable_name_node = node.child_by_field_name("pattern")
        variable_type_node = node.child_by_field_name("type")
        variable_name = self._get_node_text(variable_name_node)
        variable_type = self._get_node_text(variable_type_node) if variable_type_node else None

        # Analyze ownership (mutability)
        is_mutable = False
        for child in node.children:
            if child.type == "mutable_specifier":
                is_mutable = True
                break

        # Create ownership information
        ownership_info = OwnershipInfo(is_mutable=is_mutable)
        variable = Variable(name=variable_name, var_type=variable_type, ownership=ownership_info)
        ir.add_variable(variable)

    def _process_function(self, node: Any, ir: IR) -> None:
        """Process function definition with ownership analysis."""
        # Extract function name
        identifier = node.child_by_field_name("name")
        if identifier:
            function_name = self._get_node_text(identifier)
            # Extract parameters
            parameters_node = node.child_by_field_name("parameters")
            parameters = self._extract_parameters(parameters_node) if parameters_node else []
            # Extract return type
            return_type_node = node.child_by_field_name("return_type")
            return_type = self._get_node_text(return_type_node) if return_type_node else None
            function = Function(name=function_name, return_type=return_type, parameters=parameters)
            ir.add_function(function)

    def _extract_fields(self, node: Any) -> List[Dict[str, Any]]:
        """Extract fields from a struct."""
        fields = []
        for field_node in node.named_children:
            if field_node.type in {"struct_field", "field_declaration"}:
                field_name_node = field_node.child_by_field_name("name")
                field_type_node = field_node.child_by_field_name("type")
                field_name = self._get_node_text(field_name_node)
                field_type = self._get_node_text(field_type_node)
                if field_name and field_type:
                    fields.append({"name": field_name, "type": field_type})
        return fields

    def _extract_variants(self, node: Any) -> List[Dict[str, Any]]:
        """Extract variants from an enum."""
        variants = []
        for variant_node in node.named_children:
            if variant_node.type == "enum_variant":
                variant_name_node = variant_node.child_by_field_name("name")
                variant_name = self._get_node_text(variant_name_node)
                if variant_name:
                    variants.append({"name": variant_name})
        return variants

    def _extract_parameters(self, node: Any) -> List[Dict[str, Any]]:
        """Extract parameters from a function with ownership info."""
        parameters = []
        for param_node in node.named_children:
            if param_node.type == "parameter":
                param_name_node = param_node.child_by_field_name("pattern")
                param_type_node = param_node.child_by_field_name("type")
                param_name = self._get_node_text(param_name_node)
                param_type = self._get_node_text(param_type_node)

                # Analyze ownership (reference, mutability, lifetime)
                is_reference = False
                is_mutable = False
                lifetime = None

                if param_type_node:
                    type_text = self._get_node_text(param_type_node)
                    if type_text.startswith("&"):
                        is_reference = True
                        if type_text.startswith("&mut"):
                            is_mutable = True
                    # Extract lifetime if present
                    if "<'" in type_text or "&'" in type_text:
                        lifetime_parts = type_text.split("'")
                        if len(lifetime_parts) > 1:
                            lifetime = lifetime_parts[1].split()[0]

                ownership_info = OwnershipInfo(
                    is_reference=is_reference,
                    is_mutable=is_mutable,
                    lifetime=lifetime
                )
                parameters.append({
                    "name": param_name,
                    "type": param_type,
                    "ownership": ownership_info
                })
        return parameters

    def _extract_trait_items(self, node: Any) -> List[Any]:
        """Extract items (methods, associated types) from a trait."""
        items = []
        for item_node in node.named_children:
            if item_node.type == "function_item":
                function_ir = IR()
                self._process_function(item_node, function_ir)
                if function_ir.functions:
                    items.append(function_ir.functions[0])
        return items

    def _process_impl(self, node: Any, ir: IR) -> None:
        """Process implementation block."""
        # Extract type being implemented
        type_node = node.child_by_field_name("type")
        if type_node:
            type_name = self._get_node_text(type_node)
            impl = Implementation(type_name=type_name)
            # Extract methods
            items_node = node.child_by_field_name("body")
            if items_node:
                impl.methods = self._extract_impl_methods(items_node)
            ir.add_implementation(impl)

    def _extract_impl_methods(self, node: Any) -> List[Any]:
        """Extract methods from an implementation block."""
        methods = []
        for item_node in node.named_children:
            if item_node.type == "function_item":
                function_ir = IR()
                self._process_function(item_node, function_ir)
                if function_ir.functions:
                    methods.append(function_ir.functions[0])
        return methods

    def _get_node_text(self, node: Any) -> str:
        """Helper method to get text of a node."""
        if node is not None:
            return node.text.decode('utf-8')
        return ""


# Register frontend
FrontendRegistry.register("rust", RustFrontend)
