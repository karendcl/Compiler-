from typing import Union
from src.semantic_checker.toold.types import SemanticError, Type, Protocol
from src.semantic_checker.toold.Context import Context
import src.cmp.visitor as visitor
from src.cmp.ast import *

class TypeCollector(object):
    def __init__(self, context):
        self.errors: list[str] = []
        self.ctx = context

    @visitor.on("node")
    def visit(self, node, context):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode):
        for child in node.statements:
            if not isinstance(child, FuncDeclarationNode):
                self.visit(child)

        return self.errors

    @visitor.when(TypeDeclarationNode)
    def visit(self, node: TypeDeclarationNode):
        try:
            self.ctx.create_type(node.idx)
        except SemanticError as se:
            self.errors.append(se.text)

    @visitor.when(ProtocolDeclarationNode)
    def visit(self, node: ProtocolDeclarationNode):
        try:
            self.ctx.create_protocol(node.idx)
        except SemanticError as se:
            self.errors.append(se.text)
