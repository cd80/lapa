"""
Operator overloading handling for LLVM/Clang AST conversion.

This module provides specialized handling for C++ operator overloading,
including unary, binary, and conversion operators.
"""

from typing import Any, Dict, List, Optional, Union, cast

from ...ir import IR, IRNode, IRNodeType, Position


class OperatorKind:
    """Kinds of overloadable operators."""
    # Unary operators
    PLUS = "+"
    MINUS = "-"
    NOT = "!"
    TILDE = "~"
    INCREMENT = "++"
    DECREMENT = "--"
    
    # Binary operators
    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    MODULO = "%"
    BITAND = "&"
    BITOR = "|"
    XOR = "^"
    LSHIFT = "<<"
    RSHIFT = ">>"
    
    # Comparison operators
    EQUAL = "=="
    NOT_EQUAL = "!="
    LESS = "<"
    LESS_EQUAL = "<="
    GREATER = ">"
    GREATER_EQUAL = ">="
    
    # Assignment operators
    ASSIGN = "="
    ADD_ASSIGN = "+="
    SUBTRACT_ASSIGN = "-="
    MULTIPLY_ASSIGN = "*="
    DIVIDE_ASSIGN = "/="
    MODULO_ASSIGN = "%="
    BITAND_ASSIGN = "&="
    BITOR_ASSIGN = "|="
    XOR_ASSIGN = "^="
    LSHIFT_ASSIGN = "<<="
    RSHIFT_ASSIGN = ">>="
    
    # Special operators
    SUBSCRIPT = "[]"
    CALL = "()"
    ARROW = "->"
    ARROW_STAR = "->*"
    COMMA = ","
    
    # Conversion operators
    CONVERSION = "conversion"


class OperatorHandler:
    """Handles C++ operator overloading conversion to IR."""
    
    def process_operator(self, node: Any) -> Dict[str, Any]:
        """
        Process an operator overload from an AST node.
        
        Args:
            node: AST node representing an operator overload
        
        Returns:
            Operator information dictionary
        """
        # Get operator kind
        op_kind = self._get_operator_kind(node)
        
        # Get operator attributes
        attributes = {
            "name": node.spelling,
            "kind": op_kind,
            "is_member": self._is_member_operator(node),
            "is_const": node.is_const_method() if hasattr(node, 'is_const_method') else False,
            "return_type": node.result_type.spelling if hasattr(node, 'result_type') else None,
            "parameters": self._get_parameters(node),
            "access": node.access_specifier.name.lower() if hasattr(node, 'access_specifier') else None
        }
        
        # Add conversion target for conversion operators
        if op_kind == OperatorKind.CONVERSION:
            attributes["target_type"] = self._get_conversion_type(node)
        
        return attributes
    
    def create_operator_ir(
        self,
        node: Any,
        position: Position,
        attributes: Dict[str, Any]
    ) -> IRNode:
        """
        Create an IR node for an operator overload.
        
        Args:
            node: AST node
            position: Source position
            attributes: Additional attributes
        
        Returns:
            IR node for the operator
        """
        # Process operator information
        op_info = self.process_operator(node)
        
        # Create operator IR node
        return IRNode(
            node_type=IRNodeType.OPERATOR,
            position=position,
            attributes={**op_info, **attributes}
        )
    
    def _get_operator_kind(self, node: Any) -> str:
        """Get the kind of operator from an AST node."""
        name = node.spelling
        
        # Handle conversion operators
        if name.startswith("operator ") and not any(
            op in name[9:] for op in [
                "+", "-", "*", "/", "%", "&", "|", "^",
                "<", ">", "=", "!", "~", "[", "]", "(", ")",
                ",", "->", "++", "--"
            ]
        ):
            return OperatorKind.CONVERSION
        
        # Map operator name to kind
        op_map = {
            "operator+": OperatorKind.PLUS,
            "operator-": OperatorKind.MINUS,
            "operator!": OperatorKind.NOT,
            "operator~": OperatorKind.TILDE,
            "operator++": OperatorKind.INCREMENT,
            "operator--": OperatorKind.DECREMENT,
            "operator+=": OperatorKind.ADD_ASSIGN,
            "operator-=": OperatorKind.SUBTRACT_ASSIGN,
            "operator*=": OperatorKind.MULTIPLY_ASSIGN,
            "operator/=": OperatorKind.DIVIDE_ASSIGN,
            "operator%=": OperatorKind.MODULO_ASSIGN,
            "operator&=": OperatorKind.BITAND_ASSIGN,
            "operator|=": OperatorKind.BITOR_ASSIGN,
            "operator^=": OperatorKind.XOR_ASSIGN,
            "operator<<=": OperatorKind.LSHIFT_ASSIGN,
            "operator>>=": OperatorKind.RSHIFT_ASSIGN,
            "operator[]": OperatorKind.SUBSCRIPT,
            "operator()": OperatorKind.CALL,
            "operator->": OperatorKind.ARROW,
            "operator->*": OperatorKind.ARROW_STAR,
            "operator,": OperatorKind.COMMA
        }
        
        return op_map.get(name, name[8:])  # Remove "operator" prefix
    
    def _is_member_operator(self, node: Any) -> bool:
        """Check if an operator is a member function."""
        return hasattr(node, 'is_instance_method') and node.is_instance_method()
    
    def _get_parameters(self, node: Any) -> List[Dict[str, Any]]:
        """Get parameters of an operator function."""
        params = []
        for param in node.get_arguments():
            params.append({
                "name": param.spelling,
                "type": param.type.spelling,
                "is_const": param.type.is_const_qualified() if hasattr(param.type, 'is_const_qualified') else False
            })
        return params
    
    def _get_conversion_type(self, node: Any) -> str:
        """Get target type for a conversion operator."""
        # Remove "operator " prefix and any qualifiers
        name = node.spelling[9:]
        qualifiers = ["const", "volatile", "&", "&&", "*"]
        for qual in qualifiers:
            name = name.replace(qual, "").strip()
        return name
