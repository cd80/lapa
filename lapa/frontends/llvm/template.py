"""
Template handling for LLVM/Clang AST conversion.

This module provides specialized handling for C++ templates, including
template parameters, specializations, and instantiations.
"""

from typing import Any, Dict, List, Optional, Union, cast

from ...ir import IR, IRNode, IRNodeType, Position


class TemplateParameter:
    """Represents a template parameter."""
    
    def __init__(self, name: str, kind: str, default: Optional[str] = None):
        """
        Initialize a template parameter.
        
        Args:
            name: Parameter name
            kind: Parameter kind (type, non-type, template)
            default: Optional default value/type
        """
        self.name = name
        self.kind = kind
        self.default = default


class TemplateSpecialization:
    """Represents a template specialization."""
    
    def __init__(self, template_name: str, args: List[str]):
        """
        Initialize a template specialization.
        
        Args:
            template_name: Name of the template being specialized
            args: Template arguments for specialization
        """
        self.template_name = template_name
        self.args = args


class TemplateHandler:
    """Handles C++ template conversion to IR."""
    
    def process_template_parameters(self, node: Any) -> List[Dict[str, Any]]:
        """
        Process template parameters from an AST node.
        
        Args:
            node: AST node containing template parameters
        
        Returns:
            List of parameter information dictionaries
        """
        params = []
        
        for child in node.get_children():
            if child.kind.name == "TEMPLATE_TYPE_PARAMETER":
                param = {
                    "name": child.spelling,
                    "kind": "type",
                    "default": self._get_default_type(child)
                }
                params.append(param)
            
            elif child.kind.name == "TEMPLATE_NON_TYPE_PARAMETER":
                param = {
                    "name": child.spelling,
                    "kind": "non-type",
                    "type": child.type.spelling,
                    "default": self._get_default_value(child)
                }
                params.append(param)
            
            elif child.kind.name == "TEMPLATE_TEMPLATE_PARAMETER":
                param = {
                    "name": child.spelling,
                    "kind": "template",
                    "params": self.process_template_parameters(child),
                    "default": self._get_default_template(child)
                }
                params.append(param)
        
        return params
    
    def process_specialization(self, node: Any) -> Dict[str, Any]:
        """
        Process a template specialization from an AST node.
        
        Args:
            node: AST node representing a template specialization
        
        Returns:
            Specialization information dictionary
        """
        args = []
        
        for child in node.get_children():
            if child.kind.name == "TEMPLATE_TYPE_PARAMETER":
                args.append({
                    "kind": "type",
                    "type": child.type.spelling
                })
            elif child.kind.name == "TEMPLATE_NON_TYPE_PARAMETER":
                args.append({
                    "kind": "non-type",
                    "value": child.spelling,
                    "type": child.type.spelling
                })
            elif child.kind.name == "TEMPLATE_TEMPLATE_PARAMETER":
                args.append({
                    "kind": "template",
                    "template": child.spelling,
                    "args": self.process_specialization(child)["args"]
                })
        
        return {
            "template_name": node.spelling,
            "args": args,
            "is_partial": self._is_partial_specialization(node)
        }
    
    def _get_default_type(self, node: Any) -> Optional[str]:
        """Get default type for a template type parameter."""
        for child in node.get_children():
            if child.kind.name == "TYPE_REF":
                return child.type.spelling
        return None
    
    def _get_default_value(self, node: Any) -> Optional[str]:
        """Get default value for a non-type template parameter."""
        for child in node.get_children():
            if child.kind.name in ["INTEGER_LITERAL", "FLOATING_LITERAL", "CXX_NULL_PTR_LITERAL_EXPR"]:
                return child.spelling
        return None
    
    def _get_default_template(self, node: Any) -> Optional[str]:
        """Get default template for a template template parameter."""
        for child in node.get_children():
            if child.kind.name == "TEMPLATE_REF":
                return child.spelling
        return None
    
    def _is_partial_specialization(self, node: Any) -> bool:
        """Check if a specialization is partial."""
        # Count unspecialized parameters
        unspec_count = sum(
            1 for child in node.get_children()
            if child.kind.name in [
                "TEMPLATE_TYPE_PARAMETER",
                "TEMPLATE_NON_TYPE_PARAMETER",
                "TEMPLATE_TEMPLATE_PARAMETER"
            ]
        )
        return unspec_count > 0
    
    def create_template_ir(
        self,
        node: Any,
        position: Position,
        template_kind: str,
        attributes: Dict[str, Any]
    ) -> IRNode:
        """
        Create an IR node for a template declaration.
        
        Args:
            node: AST node
            position: Source position
            template_kind: Kind of template (class or function)
            attributes: Additional attributes
        
        Returns:
            IR node for the template
        """
        # Process template parameters
        params = self.process_template_parameters(node)
        
        # Create template IR node
        template_ir = IRNode(
            node_type=IRNodeType.TEMPLATE,
            position=position,
            attributes={
                "name": node.spelling,
                "kind": template_kind,
                "parameters": params,
                **attributes
            }
        )
        
        # Check for specializations
        for child in node.get_children():
            if child.kind.name == "CLASS_TEMPLATE_PARTIAL_SPECIALIZATION":
                spec_info = self.process_specialization(child)
                spec_ir = IRNode(
                    node_type=IRNodeType.TEMPLATE,
                    position=position,
                    attributes={
                        "name": child.spelling,
                        "kind": "specialization",
                        "template_name": spec_info["template_name"],
                        "args": spec_info["args"],
                        "is_partial": spec_info["is_partial"],
                        **attributes
                    }
                )
                template_ir.add_child(spec_ir)
        
        return template_ir
