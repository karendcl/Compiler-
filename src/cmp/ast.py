from src.cmp.semantic import Type
from src.cmp.utils import Token, emptyToken
from typing import List, Optional, Tuple, Union
from abc import ABC, abstractmethod


class Node(ABC):
    pass


class Statement(Node):
    pass


class DeclarationNode(Node):
    pass


class ExpressionNode(Node):
    pass



# -------------Declaration Nodes


class FuncDeclarationNode(DeclarationNode):
    
    def __init__(
            self,
            token,
            params: List[Tuple],
            body
    ):
        self.token = token
        self.idx = token.lex
        self.params = params
        for i,k in params:
            if isinstance(i,VoidNode):
                self.params = []
                break
        self.body = body

class MethodDeclaration(DeclarationNode):

    def __init__(
            self,
            idx,
            params,
            expected_type
    ):
        self.idx = idx
        self.params = params
        self.expected_type = expected_type


class AttrDeclarationNode(DeclarationNode):
    
    def __init__(
            self,
            idx,
            value=None,
            type_expected=None

    ):
        self.idx = idx
        self.value = value
        self.type_expected = type_expected


class ProtocolDeclarationNode(DeclarationNode):

    def __init__(
            self,
            token,
            methods: Optional[List[MethodDeclaration]] = [],
            extends=None
    ):
        self.token = token
        self.idx = token.lex
        self.methods = methods
        self.extends = extends


class TypeDeclarationNode(DeclarationNode):

    def __init__(
            self,
            token,
            body: Optional[List[Union[FuncDeclarationNode, AttrDeclarationNode]]] = None,
            inherits=None,
            params: List[Tuple] = None
    ):
        self.token = token
        self.idx = token.lex
        self.functions = [x for x in body if isinstance(x,FuncDeclarationNode)] if body is not None else []
        self.attributes = [x for x in body if isinstance(x,AttrDeclarationNode)] if body is not None else []
        self.inherits = inherits
        self.params = params


class AssignNode(ExpressionNode):
    def __init__(
            self,
            token: Token,
            expr: ExpressionNode
    ):
        self.token = token
        self.idx = token.lex
        self.expr = expr

class DestructiveAssignment(AssignNode):
    pass
class ProgramNode(Node):
    def __init__(
            self,
            statements,
            expression
    ):
        self.statements = statements
        self.expression = expression

    def __repr__(self):
        return f"{self.__class__.__name__}({len(self.statements)} statements)"


class CallNode(ExpressionNode):
    pass

class FuncCallNode(CallNode):
    
    def __init__(
            self,
            obj_called,
            params: List[Tuple]
    ):
        self.obj_called = obj_called
        self.params = params

class AttrCallNode(CallNode):
    
    def __init__(
            self,
            idx,
            attr_called
    ):
        assert idx.lex == 'self', 'Error: attributes are private'
        self.idx = idx.lex
        self.attr_called = attr_called



class BlockNode(ExpressionNode):
    #check done
    def __init__(self, expr_list: List[ExpressionNode]):
        self.expr_list = expr_list

class LoopNode(ExpressionNode):
    #check done
    def __init__(
            self,
            cond,
            body,
            else_body
    ):
        self.condition = cond
        self.body = body
        self.else_body = else_body


class ConditionalNode(ExpressionNode):
    #check done
    def __init__(
            self,
            cond,
            then_body: [ExpressionNode],
            else_body: ExpressionNode,
    ):
        self.condition = cond
        self.then_body = then_body
        self.else_body = else_body


ElseBlockNode = BlockNode

class LetNode(ExpressionNode):
    def __init__(
            self,
            assignments,
            body
    ):
        self.assignments = assignments
        self.body = body



class AtomicNode(ExpressionNode):
    def __init__(self, value=None):
        self.value = value

class UnaryNode(ExpressionNode):
    def __init__(self, expr: ExpressionNode):
        self.expr = expr


class BinaryNode(ExpressionNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right


class PrintNode(ExpressionNode):
    #Check done
    def __init__(self, expr: ExpressionNode):
        self.expr = expr


class ArithmeticNode(BinaryNode):
    pass


class ConstantNumNode(AtomicNode):
    #Check done
    def __init__(self,token):
        super().__init__(token)
        self.idx = token.lex


class ConstantStringNode(AtomicNode):
    # Check done
    pass


class ConstantBoolNode(AtomicNode):
    # Check done
    pass



class VariableNode(AtomicNode):
    def __init__(self,value):
        super().__init__(value)
        self.idx = value.lex


class InstantiateNode(ExpressionNode):

    def __init__(
            self,
            idx,
            params
    ):
        self.idx = idx
        self.iden = idx.lex
        self.params = params
        for i,k in params:
            if isinstance(i,VoidNode):
                self.params = []
                break


class VoidNode(UnaryNode):
    def __init__(self, expr):
        super().__init__(expr)
        self.lex = 'None'

class ConformsNode(ExpressionNode):
    def __init__(
            self,
            exp,
            type_to
    ):
        self.exp = exp
        self.type_to = type_to


class RandNode(AtomicNode):
    #Check done
    pass

class List_Comprehension():
    def __init__(
            self,
            idx,
            exp_for_idx,
            exp
    ):
        self.idx = idx
        self.exp_for_idx = exp_for_idx
        self.expr = exp

class RangeNode(BinaryNode):
    pass


class ForNode(ExpressionNode):
    def __init__(self,
                 iterable,
                 body,
                 varidx,
                 elsex
                 ):

        self.iterable = iterable
        self.body = body
        self.varidx = varidx
        self.elsex = elsex


class IndexationNode(ExpressionNode):
    def __init__(self, obj: ExpressionNode, index: ExpressionNode):
        self.obj = obj
        self.index = index


# --------UNARY NODES---------------------
class NotNode(UnaryNode):
    #check done
    pass


class NegNode(UnaryNode):
    #check done
    pass


class SqrtNode(UnaryNode):
    #check done
    pass


class CosNode(UnaryNode):
    #check done
    pass


class SinNode(UnaryNode):
    #check done
    pass


class ExponEulerNode(UnaryNode):
    #check done
    pass


# --------ARITHMETIC NODES----------------
class ModNode(ArithmeticNode):
    #check done
    pass


class LogNode(ArithmeticNode):
    #check done
    pass


class PlusNode(ArithmeticNode):
    #check done
    pass


class MinusNode(ArithmeticNode):
    #check done
    pass


class StarNode(ArithmeticNode):
    #check done
    pass


class DivNode(ArithmeticNode):
    #check done
    pass


class PowNode(ArithmeticNode):
    #Check done
    pass


# --------COMPARISON NODES------------

class ComparisonNode(BinaryNode):
    pass


class LeqNode(ComparisonNode):
    #blind test done
    pass


class LessNode(ComparisonNode):
    #blind test done
    pass


class EqualNode(ComparisonNode):
    #blind test done
    pass


class AndNode(ComparisonNode):
    #blind test done
    pass


class OrNode(ComparisonNode):
    #blind test done
    pass


class IsNode(ComparisonNode):
    pass

class StringExpression(BinaryNode):
    #Check done
    pass

