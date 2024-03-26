from typing import Union
from src.semantic_checker.toold.types import SemanticError, Type, Protocol
from src.semantic_checker.toold.Context import Context
import src.cmp.visitor as visitor
from src.cmp.ast import *


class TypeCollector(object):
    def __init__(self, errors=[]):
        self.context = None
        self.errors = errors
        self.context = Context()
        self.context.create_type('int')
        self.context.create_type('string')
        self.context.create_type('bool')
        self.context.create_type('void')

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode):
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
