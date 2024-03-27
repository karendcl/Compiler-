from typing import Union
from src.cmp.semantic import SemanticError, Type, Protocol
from src.cmp.semantic import Context, IntType, VoidType, BoolType, StringType
import src.cmp.visitor as visitor
from src.cmp.ast import *


class TypeCollector(object):
    def __init__(self, errors=[]):
        self.context = None
        self.errors = errors

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode):
        self.context = Context()
        self.context.types['int'] = IntType()
        self.context.types['bool'] = BoolType()
        self.context.types['void'] = VoidType()
        self.context.types['string'] = StringType()
        self.context.types['Object'] = Type('Object')
        self.context.types['None'] = Type('None')
        for statement in node.statements:
            if not isinstance(statement, FuncDeclarationNode):
                self.visit(statement)

    @visitor.when(TypeDeclarationNode)
    def visit(self, node: TypeDeclarationNode):
        try:
            self.context.create_type(node.idx)
        except SemanticError as se:
            self.errors.append(se.text)

    @visitor.when(ProtocolDeclarationNode)
    def visit(self, node: ProtocolDeclarationNode):
        try:
            self.context.create_protocol(node.idx)
        except SemanticError as se:
            self.errors.append(se.text)
