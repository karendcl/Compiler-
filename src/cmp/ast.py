from src.cmp.semantic import Type
from src.cmp.utils import Token, emptyToken
from typing import List, Optional, Tuple, Union
from abc import ABC, abstractmethod





class Node:
    def __init__(self, token: Token = emptyToken):
        self.token = token

    def __repr__(self):
        return f"{self.__class__.__name__}({self.token.lex})"

class StatementNode(Node):
    pass

class ClassDeclarationNode(StatementNode):
    pass



class DeclarationNode(Node):
    pass


class ExpressionNode(Node):
    def __init__(self, token: Token = emptyToken, computed_type: Optional[Type] = None):
        super().__init__(token)
        self.computed_type = computed_type


class FuncDeclarationNode(DeclarationNode):
    def __init__(
        self,
        token: Token,
        params: List[Tuple[Token, Token]],
        body: ExpressionNode,
    ):
        self.id = token.lex
        # `param` is (nameToken, typeToken)
        self.params = params
        self.body = body
        self.token = token


class AttrDeclarationNode(DeclarationNode):
    def __init__(
        self,
        idx: Token,
        typex: Optional[Token] = None,
        expr: Optional[ExpressionNode] = None,
        token: Token = emptyToken,
    ):
        self.id = idx.lex
        self.idToken = idx
        self.typeToken = typex
        self.expr = expr
        self.token = token


class ClassDeclarationNode(DeclarationNode):
    def __init__(
        self,
        idx: Token,
        features: List[Union[FuncDeclarationNode, AttrDeclarationNode]],
        token: Token,
        parent: Optional[Token] = None,
    ):
        self.id = idx.lex
        self.tokenId = idx
        self.token = token
        self.parent = parent
        self.features = features


class ProgramNode(Node):
    def __init__(self, declarations: List[ClassDeclarationNode]):
        super().__init__(emptyToken)
        self.declarations = declarations

    def __repr__(self):
        return f"{self.__class__.__name__}({len(self.declarations)} classes)"


class AssignNode(ExpressionNode):
    def __init__(self, idx: Token, expr: ExpressionNode, token: Token):
        super().__init__(token)
        self.id = idx.lex
        self.idToken = idx
        self.expr = expr


class CallNode(ExpressionNode):
    def __init__(
        self,
        obj_called,
            params
    ):
        super().__init__()
        self.obj_called = obj_called
        self.params = params


class CaseBranchNode(Node):
    def __init__(self, token: Token, idx: Token, typex: Token, expr: ExpressionNode):
        self.token = token
        self.id = idx.lex
        self.idToken = idx
        self.typex = typex.lex
        self.typexToken = typex
        self.expression = expr


class CaseNode(ExpressionNode):
    def __init__(
        self, expr: ExpressionNode, branch_list: List[CaseBranchNode], token: Token
    ):
        super().__init__(token)
        self.expr = expr
        self.branch_list = branch_list


class BlockNode(ExpressionNode):
    def __init__(self, expr_list: List[ExpressionNode], token: Token):
        super().__init__(token)
        self.expr_list = expr_list


class LoopNode(ExpressionNode):
    def __init__(self, cond: ExpressionNode, body: ExpressionNode, token: Token):
        super().__init__(token)
        self.condition = cond
        self.body = body


class ConditionalNode(ExpressionNode):
    def __init__(
        self,
        cond: ExpressionNode,
        then_body: ExpressionNode,
        else_body: ExpressionNode,
        token: Token,
    ):
        super().__init__(token)
        self.condition = cond
        self.then_body = then_body
        self.else_body = else_body

ElseBlockNode = BlockNode
class LetVarNode(Node):
    def __init__(
        self,
        idx: Token,
        typex: Token,
        expr: Optional[ExpressionNode] = None,
        token: Token = emptyToken,
    ):
        self.token = token
        self.id = idx.lex
        self.idToken = idx
        self.typex = typex.lex
        self.typexToken = typex
        self.expression = expr


class LetNode(ExpressionNode):
    def __init__(self, id_list: List[LetVarNode], body: ExpressionNode, token: Token):
        super().__init__(token)
        self.id_list = id_list
        self.body = body


class AtomicNode(ExpressionNode):
    def __init__(self, token: Token, value: Optional[str] = None):
        super().__init__(token)
        self.lex = token.lex


class UnaryNode(ExpressionNode):
    def __init__(self, expr: ExpressionNode, symbol: Token):
        super().__init__(symbol)
        self.expr = expr


class BinaryNode(ExpressionNode):
    def __init__(self, left: ExpressionNode, right: ExpressionNode, symbol: Token):
        super().__init__(symbol)
        self.left = left
        self.right = right


class PrintNode(ExpressionNode):
    def __init__(self, expr: ExpressionNode, token: Token):
        super().__init__(token)
        self.expr = expr


class ArithmeticNode(BinaryNode):
    pass


class ComparisonNode(BinaryNode):
    pass


class ConstantNumNode(AtomicNode):
    pass


class ConstantStringNode(AtomicNode):
    pass


class ConstantBoolNode(AtomicNode):
    pass


class VariableNode(AtomicNode):
    pass


class InstantiateNode(ExpressionNode):
    def __init__(self, type_idx, params: Optional[List[ExpressionNode]], token: Token):
        super().__init__(token)
        self.type_idx = type_idx
        self.params = params


class PlusNode(ArithmeticNode):
    pass


class MinusNode(ArithmeticNode):
    pass


class StarNode(ArithmeticNode):
    pass


class DivNode(ArithmeticNode):
    pass

class PowNode(ArithmeticNode):
    pass

class LeqNode(ComparisonNode):
    pass


class LessNode(ComparisonNode):
    pass


class EqualNode(ComparisonNode):
    pass

class AndNode(ComparisonNode):
    pass

class OrNode(ComparisonNode):
    pass

class VoidNode(UnaryNode):
    pass


class NotNode(UnaryNode):
    pass


class NegNode(UnaryNode):
    pass

class SqrtNode(UnaryNode):
    pass

class CosNode(UnaryNode):
    pass

class SinNode(UnaryNode):
    pass

class ExponEulerNode(UnaryNode):
    pass

class LogNode(BinaryNode):
    pass

class RandNode(AtomicNode):
    pass

class RangeNode(BinaryNode):
    pass

class ForNode(ExpressionNode):
    def __init__(self, iterable: ExpressionNode, body: ExpressionNode, token: Token, varidx):
        super().__init__(token)
        self.iterable = iterable
        self.body = body
        self.varidx = varidx

class IndexationNode(ExpressionNode):
    def __init__(self, obj: ExpressionNode, index: ExpressionNode):
        super().__init__()
        self.obj = obj
        self.index = index

class ModNode(BinaryNode):
    pass