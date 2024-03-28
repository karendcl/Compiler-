from typing import Union
from src.cmp.semantic import *
import src.cmp.visitor as visitor
from src.cmp.ast import *
import src.cmp.errors as err


class TypeBuilder1(object):
    def __init__(self, context, errors=[]):
        self.errors: list[str] = errors
        self.ctx = context
        self.current_type= None

    @visitor.on("node")
    def visit(self, node):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode):
        for declaration in node.statements:
            if not isinstance(declaration, FuncDeclarationNode):
                self.visit(declaration)

        return self.errors

    @visitor.when(TypeDeclarationNode)
    def visit(self, node):
        try:
            self.current_type = self.ctx.get_type(node.idx)
        except SemanticError as se:
            self.errors.append(se.text)

        if node.inherits is not None:
            try:
                parent_type = self.ctx.get_type(node.inherits.lex)
                self.current_type.set_parent(parent_type)
            except SemanticError as se:
                self.errors.append(se.text)

    @visitor.when(ProtocolDeclarationNode)
    def visit(self, node: ProtocolDeclarationNode):
        try:
            self.current_type = self.ctx.get_protocol(node.idx)
        except SemanticError as se:
            self.errors.append(se.text)

        if node.extends is not [] and node.extends is not None:
            for i in node.extends:
                try:
                    parent_type = self.ctx.get_protocol(i.lex)
                    self.current_type.set_parent(parent_type)
                except SemanticError as se:
                    self.errors.append(se.text)


class TypeBuilder2(object):
    def __init__(self, context, errors=[]):
        self.errors: list[str] = errors
        self.ctx = context
        self.current_type= None

    @visitor.on("node")
    def visit(self, node):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode):

        for declaration in node.statements:
            if not isinstance(declaration, FuncDeclarationNode):
                self.visit(declaration)

        return self.errors

    @visitor.when(TypeDeclarationNode)
    def visit(self, node):
        print(f'Visiting {self.current_type}')
        try:
            self.current_type = self.ctx.get_type(node.idx)
        except SemanticError as se:
            self.errors.append(se.text)

        if node.inherits is not None:
            try:
                parent_type = self.ctx.get_type(node.inherits.lex)
                self.current_type.set_parent(parent_type)
            except SemanticError as se:
                self.errors.append(se.text)

        if node.params is not None:
            print(node.params)
            params = []
            try:
                for id, type_ in node.params:
                    print(id, type_)
                    params.append((id, self.ctx.get_type_or_protocol(type_)))
                self.current_type.set_params(params)
            except SemanticError as se:
                self.errors.append(se.text)

        print(f'checking attributes for {node.idx}')
        print(node.attributes)
        for member in node.attributes + node.functions:
            self.visit(member)

    @visitor.when(ProtocolDeclarationNode)
    def visit(self, node: ProtocolDeclarationNode):
        print(f'Visiting {self.current_type}')
        try:
            self.current_type = self.ctx.get_protocol(node.idx)
        except SemanticError as se:
            self.errors.append(se.text)

        if node.extends is not [] and node.extends is not None:
            for i in node.extends:
                try:
                    parent_type = self.ctx.get_protocol(i.lex)
                    self.current_type.set_parent(parent_type)
                except SemanticError as se:
                    self.errors.append(se.text)

        for method_declaration in node.methods:
            self.visit(method_declaration)

    @visitor.when(AttrDeclarationNode)
    def visit(self, node: AttrDeclarationNode):
        try:
            if node.type_expected is None:
                type = 'None'
                type = self.ctx.get_type_or_protocol(type)
            else:
                type = self.ctx.get_type_or_protocol(node.type_expected.lex)

            if node.idx.lex =='self':
                self.errors.append(err.SELF_INVALID_ATTRIBUTE_ID)
            else:
                self.current_type.define_attribute(node.idx.lex, type, node.value)

        except SemanticError as se:
            self.errors.append(se.text)

    @visitor.when(FuncDeclarationNode)
    def visit(self, node: FuncDeclarationNode):
        try:
            param_types = [self.ctx.get_type_or_protocol(type_) for _, type_ in node.params]
            param_names = [name for name, _ in node.params]
            for i, k in enumerate(param_names):
                if isinstance(k, VoidNode):
                    param_names.pop(i)
                    param_types.pop(i)

            self.current_type.define_method(node.idx, param_names, param_types )
        except SemanticError as error:
            self.errors.append(error.text)


    @visitor.when(MethodDeclaration)
    def visit(self, node: MethodDeclaration):
        try:
            param_types = []
            param_names = []
            for i,k in node.params:
                if not isinstance(i, VoidNode):
                    param_names.append(i.lex)
                    param_types.append(self.ctx.get_type_or_protocol(k.lex))

            if node.expected_type is None:
                self.errors.append(err.MISSING_RETURN_TYPE % node.idx.lex)
            else:
                self.current_type.define_method(
                        node.idx.lex, param_names, param_types, self.ctx.get_type_or_protocol(node.expected_type.lex)
                    )
        except SemanticError as se:
            self.errors.append(se.text)