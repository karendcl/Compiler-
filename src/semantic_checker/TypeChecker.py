from typing import List

from src.cmp.ast import *
import src.cmp.errors as err
import src.cmp.visitor as visitor
from src.cmp.semantic import Context, Type, Method, Scope, ErrorType, SemanticError


class TypeChecker:
    def __init__(self, context: Context, errors: List[str]):
        self.context: Context = context
        self.errors: List[str] = errors
        self.current_type: Type = None
        self.current_method: Method = None

    @visitor.on('node')
    def visit(self, node, scope):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode, scope: Scope = None):
        if scope is None:
            scope = Scope()

        for elem in node.statements:
            self.visit(elem, scope.create_child())

        return scope

    @visitor.when(TypeDeclarationNode)
    def visit(self, node: TypeDeclarationNode, scope: Scope):
        self.current_type = self.context.get_type(node.idx)

        #double checking the type
        attrs = [feature for feature in node.attributes if isinstance(feature, AttrDeclarationNode)]
        functions = [feature for feature in node.functions if isinstance(feature, FuncDeclarationNode)]

        for attr in attrs:
            self.visit(attr, scope)

        for function in functions:
            self.visit(function, scope.create_child())

    @visitor.when(AttrDeclarationNode)
    def visit(self, node: AttrDeclarationNode, scope: Scope):
        if node.idx == 'self':
            self.errors.append(err.SELF_INVALID_ATTRIBUTE_ID)

        attr_type = self.context.get_type(node.type_expected)

        if node.value is not None:
            expr_type = self.visit(node.value, scope.create_child())
            if not expr_type.conforms_to(attr_type):
                self.errors.append(err.INCOMPATIBLE_TYPES % (expr_type.name, attr_type.name))

            if attr_type

        scope.define_variable(node.idx, attr_type)

    @visitor.when(ast.MethodDeclarationNode)
    def visit(self, node: ast.MethodDeclarationNode, scope: Scope):
        self.current_method = self.current_type.get_method(node.id)

        # Parameters can hide the attribute declaration, that's why we are not checking if there is defined,
        # instead we are checking for local declaration. Also it is checked that the static type of a parameter is
        # different of SELF_TYPE.

        scope.define_variable('self', self.current_type)

        for param_name, param_type in zip(self.current_method.param_names, self.current_method.param_types):
            if not scope.is_local(param_name):
                if param_type.name == 'SELF_TYPE':
                    self.errors.append(err.INVALID_PARAM_TYPE % 'SELF_TYPE')
                    scope.define_variable(param_name, ErrorType())
                else:
                    scope.define_variable(param_name, self.context.get_type(param_type.name))
            else:
                self.errors.append(err.LOCAL_ALREADY_DEFINED % (param_name, self.current_method.name))

        return_type = self.context.get_type(node.return_type) if node.return_type != 'SELF_TYPE' else self.current_type

        expr_type = self.visit(node.body, scope)

        if not expr_type.conforms_to(return_type):
            self.errors.append(err.INCOMPATIBLE_TYPES % (expr_type.name, return_type.name))

    @visitor.when(ast.LetNode)
    def visit(self, node: ast.LetNode, scope: Scope):
        for _id, _type, _expr in node.declarations:
            try:
                var_static_type = self.context.get_type(_type) if _type != 'SELF_TYPE' else self.current_type
            except SemanticError as e:
                self.errors.append(e.text)
                var_static_type = ErrorType()

            if scope.is_local(_id):
                self.errors.append(err.LOCAL_ALREADY_DEFINED % (_id, self.current_method.name))
            else:
                scope.define_variable(_id, var_static_type)

            expr_type = self.visit(_expr, scope.create_child()) if _expr is not None else None
            if expr_type is not None and not expr_type.conforms_to(var_static_type):
                self.errors.append(err.INCOMPATIBLE_TYPES % (expr_type.name, var_static_type.name))

        return self.visit(node.expr, scope.create_child())

    @visitor.when(ast.AssignNode)
    def visit(self, node: ast.AssignNode, scope: Scope):
        var_info = scope.find_variable(node.id)

        expr_type = self.visit(node.expr, scope.create_child())

        if var_info is None:
            self.errors.append(err.VARIABLE_NOT_DEFINED % (node.id, self.current_method.name))
        else:
            if not expr_type.conforms_to(var_info.type):
                self.errors.append(err.INCOMPATIBLE_TYPES % (expr_type.name, var_info.type.name))

        return expr_type

    @visitor.when(ast.BlockNode)
    def visit(self, node: ast.BlockNode, scope: Scope):
        child_scope = scope.create_child()
        return_type = ErrorType()
        for expr in node.expressions:
            return_type = self.visit(expr, child_scope)
        return return_type

    @visitor.when(ast.ConditionalNode)
    def visit(self, node: ast.ConditionalNode, scope: Scope):
        if_type = self.visit(node.if_expr, scope)
        then_type = self.visit(node.then_expr, scope)
        else_type = self.visit(node.else_expr, scope)
        if if_type != self.context.get_type('Bool'):
            self.errors.append(err.INCOMPATIBLE_TYPES % (if_type.name, 'Bool'))
        return then_type.join(else_type)

    @visitor.when(ast.WhileNode)
    def visit(self, node: ast.WhileNode, scope: Scope):
        condition = self.visit(node.condition, scope)
        if condition != self.context.get_type('Bool'):
            self.errors.append(err.INCOMPATIBLE_TYPES % (condition.name, 'Bool'))

        self.visit(node.body, scope.create_child())
        return self.context.get_type('Object')

    @visitor.when(ast.SwitchCaseNode)
    def visit(self, node: ast.SwitchCaseNode, scope: Scope):
        self.visit(node.expr, scope)
        types = []
        for _id, _type, _expr in node.cases:
            new_scope = scope.create_child()
            try:
                if _type != 'SELF_TYPE':
                    new_scope.define_variable(_id, self.context.get_type(_type))
                else:
                    self.errors.append(err.INVALID_CASE_TYPE % _type)
            except SemanticError as e:
                new_scope.define_variable(_id, ErrorType())
                self.errors.append(e.text)

            types.append(self.visit(_expr, new_scope))

        return Type.multi_join(types)

    @visitor.when(FuncCallNode)
    def visit(self, node: FuncCallNode, scope: Scope):
        if node.obj_called is None:
            node.obj_called = VariableNode('self')

        obj_type = self.visit(node.obj_called, scope)

        if node.obj_called is not None:
            try:
                ancestor_type = self.context.get_type(node.type)
            except SemanticError as e:
                ancestor_type = ErrorType()
                self.errors.append(e.text)

            if not obj_type.conforms_to(ancestor_type):
                self.errors.append(err.INVALID_ANCESTOR % (obj_type.name, ancestor_type.name))
        else:
            ancestor_type = obj_type

        try:
            method = ancestor_type.get_method(node.id)
        except SemanticError as e:
            self.errors.append(e.text)
            for arg in node.args:
                self.visit(arg, scope)
            return ErrorType()

        if len(node.args) != len(method.param_names):
            self.errors.append(err.METHOD_OVERRIDE_ERROR % (method.name, obj_type.name))

        for i, arg in enumerate(node.args):
            arg_type = self.visit(arg, scope)
            if not arg_type.conforms_to(method.param_types[i]):
                self.errors.append(err.INCOMPATIBLE_TYPES % (arg_type.name, method.param_types[i].name))

        return method.return_type if method.return_type.name != 'SELF_TYPE' else ancestor_type

    @visitor.when(ConstantNumNode)
    def visit(self, node: ConstantNumNode, scope: Scope):
        return self.context.get_type('Int')

    @visitor.when(ConstantStringNode)
    def visit(self, node: ConstantStringNode, scope: Scope):
        return self.context.get_type('String')

    @visitor.when(ConstantBoolNode)
    def visit(self, node:ConstantBoolNode, scope: Scope):
        return self.context.get_type('Bool')

    @visitor.when(VariableNode)
    def visit(self, node: VariableNode, scope: Scope):
        variable = scope.find_variable(node.idx.lex)
        if variable is None:
            self.errors.append(err.VARIABLE_NOT_DEFINED % (node.idx.lex, self.current_method.name))
            return ErrorType()
        return variable.type

    @visitor.when(InstantiateNode)
    def visit(self, node: InstantiateNode, scope: Scope):
        try:
            return self.context.get_type(node.iden) if node.iden != 'self' else self.current_type
        except SemanticError as e:
            self.errors.append(e.text)
            return ErrorType()

    @visitor.when(NotNode)
    def visit(self, node: NotNode, scope: Scope):
        return self._check_unary_operation(node, scope, 'not', self.context.get_type('Bool'))

    @visitor.when(NegNode)
    def visit(self, node: NegNode, scope: Scope):
        return self._check_unary_operation(node, scope, '-', self.context.get_type('Int'))

    @visitor.when(PlusNode)
    def visit(self, node: PlusNode, scope: Scope):
        return self._check_int_binary_operation(node, scope, '+', self.context.get_type('Int'))

    @visitor.when(MinusNode)
    def visit(self, node: MinusNode, scope: Scope):
        return self._check_int_binary_operation(node, scope, '-', self.context.get_type('Int'))

    @visitor.when(StarNode)
    def visit(self, node: StarNode, scope: Scope):
        return self._check_int_binary_operation(node, scope, '*', self.context.get_type('Int'))

    @visitor.when(DivNode)
    def visit(self, node: DivNode, scope: Scope):
        return self._check_int_binary_operation(node, scope, '/', self.context.get_type('Int'))

    @visitor.when(LeqNode)
    def visit(self, node: LeqNode, scope: Scope):
        return self._check_int_binary_operation(node, scope, '<=', self.context.get_type('Bool'))

    @visitor.when(LessNode)
    def visit(self, node: LessNode, scope: Scope):
        return self._check_int_binary_operation(node, scope, '<', self.context.get_type('Bool'))

    @visitor.when(EqualNode)
    def visit(self, node: EqualNode, scope: Scope):
        self.visit(node.left, scope)
        self.visit(node.right, scope)
        return self.context.get_type('Bool')

    def _check_int_binary_operation(self, node: BinaryNode, scope: Scope, operation: str, return_type: Type):
        left_type = self.visit(node.left, scope)
        right_type = self.visit(node.right, scope)

        if left_type == right_type == self.context.get_type('Int'):
            return return_type
        self.errors.append(err.INVALID_BINARY_OPERATION % (operation, left_type.name, right_type.name))
        return ErrorType()

    def _check_unary_operation(self, node: UnaryNode, scope: Scope, operation: str, expected_type: Type):
        typex = self.visit(node.expr, scope)
        if typex == expected_type:
            return typex
        self.errors.append(err.INVALID_UNARY_OPERATION % (operation, typex.name))
        return ErrorType()