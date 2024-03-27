from typing import List

from src.cmp.ast import *
import src.cmp.errors as err
import src.cmp.visitor as visitor
from src.cmp.semantic import *
from src.cmp import ast


class TypeChecker:
    def __init__(self, context: Context, errors: List[str]):
        self.context: Context = context
        self.errors: List[str] = errors
        self.current_type: Type = None
        self.current_method: Method = None

    @visitor.on('node')
    def visit(self, node, scope):
        pass

#---------------------------------DONE
    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode, scope: Scope = None):
        #DONE
        if scope is None:
            scope = Scope()

        for elem in node.statements:
            self.visit(elem, scope.create_child())

        print(f'About to visit the expression')
        for i in node.expression:
            self.visit(i, scope.create_child())
        print(node.expression)
        return scope

    @visitor.when(ast.PrintNode)
    def visit(self, node: PrintNode, scope: Scope):
        print(f'visiting Print')
        self.visit(node.expr, scope)
        return ObjectType

    @visitor.when(ConstantNumNode)
    def visit(self, node: ConstantNumNode, scope: Scope):
        print('Visiting Constant Num')
        return IntType

    @visitor.when(ConstantStringNode)
    def visit(self, node: ConstantStringNode, scope: Scope):
        print('Visiting Constant String')
        return StringType

    @visitor.when(ConstantBoolNode)
    def visit(self, node: ConstantBoolNode, scope: Scope):
        return BoolType

    @visitor.when(StringExpression)
    def visit(self, node: StringExpression, scope: Scope):
        print(f'Visiting string expression')
        expected = [IntType, StringType]
        left_type = self.visit(node.left, scope)
        right_type = self.visit(node.right, scope)
        if left_type in expected:
            if right_type in expected:
                return StringType
            else:
                self.errors.append(err.INCOMPATIBLE_TYPES(right_type, StringType))
        else:
            self.errors.append(err.INCOMPATIBLE_TYPES(left_type, StringType))
        return ErrorType

    @visitor.when(StarNode)
    def visit(self, node: StarNode, scope: Scope):
        print('Visiting Star Node')
        return self._check_int_binary_operation(node, scope, '*', IntType)

    @visitor.when(NegNode)
    def visit(self, node: NegNode, scope: Scope):
        print('Visiting Neg Node')
        return self._check_unary_operation(node, scope, '-', IntType)

    @visitor.when(PlusNode)
    def visit(self, node: PlusNode, scope: Scope):
        print('Visiting Plus Node')
        return self._check_int_binary_operation(node, scope, '+', IntType)

    @visitor.when(MinusNode)
    def visit(self, node: MinusNode, scope: Scope):
        print('Visiting Minus Node')
        return self._check_int_binary_operation(node, scope, '-', IntType)

    #------------------------------------NOT DONE
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

        scope.define_variable(node.idx, attr_type)

    @visitor.when(MethodDeclaration)
    def visit(self, node: MethodDeclaration, scope: Scope):
        self.current_method = self.current_type.get_method(node.idx)

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

    @visitor.when(LetNode)
    #todo fix this
    def visit(self, node: LetNode, scope: Scope):
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

        return self.visit(node.body, scope.create_child())

    @visitor.when(AssignNode)
    def visit(self, node: AssignNode, scope: Scope):
        var_info = scope.find_variable(node.idx)

        expr_type = self.visit(node.expr, scope.create_child())

        if var_info is None:
            self.errors.append(err.VARIABLE_NOT_DEFINED % (node.idx, self.current_method.name))
        else:
            if not expr_type.conforms_to(var_info.type):
                self.errors.append(err.INCOMPATIBLE_TYPES % (expr_type.name, var_info.type.name))

        return expr_type

    @visitor.when(BlockNode)
    def visit(self, node: BlockNode, scope: Scope):
        child_scope = scope.create_child()
        return_type = ErrorType()
        for expr in node.expr_list:
            return_type = self.visit(expr, child_scope)
        return return_type

    @visitor.when(ConditionalNode)
    def visit(self, node: ConditionalNode, scope: Scope):
        if_type = self.visit(node.condition, scope)
        then_type = self.visit(node.then_body, scope)
        else_type = self.visit(node.then_body, scope)
        if if_type != self.context.get_type('Bool'):
            self.errors.append(err.INCOMPATIBLE_TYPES % (if_type.name, 'Bool'))
        return then_type.join(else_type)

    @visitor.when(LoopNode)
    def visit(self, node: LoopNode, scope: Scope):
        condition = self.visit(node.condition, scope)
        if condition != self.context.get_type('Bool'):
            self.errors.append(err.INCOMPATIBLE_TYPES % (condition.name, 'Bool'))

        self.visit(node.body, scope.create_child())
        return self.context.get_type('Object')


    @visitor.when(FuncCallNode)
    #todo also fix this
    def visit(self, node: FuncCallNode, scope: Scope):
        if node.obj_called is None:
            node.obj_called = VariableNode('self')

        obj_type = self.visit(node.obj_called, scope)

        if node.obj_called is not None:
            try:
                ancestor_type = self.context.get_type(node.obj_called.idx)
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





    @visitor.when(IsNode)
    def visit(self, node:IsNode, scope:Scope):
        #see if variable is defined
        pass




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
        return self._check_unary_operation(node, scope, 'not', BoolType)





    @visitor.when(DivNode)
    def visit(self, node: DivNode, scope: Scope):
        return self._check_int_binary_operation(node, scope, '/', IntType)

    @visitor.when(LeqNode)
    def visit(self, node: LeqNode, scope: Scope):
        return self._check_int_binary_operation(node, scope, '<=', BoolType)

    @visitor.when(LessNode)
    def visit(self, node: LessNode, scope: Scope):
        return self._check_int_binary_operation(node, scope, '<', BoolType)

    @visitor.when(EqualNode)
    def visit(self, node: EqualNode, scope: Scope):
        self.visit(node.left, scope)
        self.visit(node.right, scope)
        return BoolType



    def _check_int_binary_operation(self, node: BinaryNode, scope: Scope, operation: str, return_type):
        left_type = self.visit(node.left, scope)
        right_type = self.visit(node.right, scope)

        if left_type == right_type == IntType:
            return return_type
        self.errors.append(err.INVALID_BINARY_OPERATION % (operation, left_type.name, right_type.name))
        return ErrorType()


    def _check_unary_operation(self, node: UnaryNode, scope: Scope, operation: str, expected_type):
        typex = self.visit(node.expr, scope)
        if typex == expected_type:
            return typex
        self.errors.append(err.INVALID_UNARY_OPERATION % (operation, typex.name))
        return ErrorType()

