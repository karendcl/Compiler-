from typing import List

from src.cmp.ast import *
import src.cmp.errors as err
import src.cmp.visitor as visitor
from src.cmp.semantic import *
from src.cmp import ast
from src.cmp.grammar import G


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
            self.current_type = self.visit(elem, scope.create_child())


        print(f'About to visit the expression')
        for i in node.expression:
            print(i)
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
        return BoolType()

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

    @visitor.when(ModNode)
    def visit(self, node: ArithmeticNode, scope: Scope):
        print(f'Visiting {node.__class__.__name__} Node')
        return self._check_int_binary_operation(node, scope, '%', IntType)

    @visitor.when(LogNode)
    def visit(self, node: ArithmeticNode, scope: Scope):
        print(f'Visiting {node.__class__.__name__} Node')
        return self._check_int_binary_operation(node, scope, 'log', IntType)

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

    @visitor.when(PowNode)
    def visit(self, node: MinusNode, scope: Scope):
        print('Visiting Pow Node')
        return self._check_int_binary_operation(node, scope, '^', IntType)

    @visitor.when(DivNode)
    def visit(self, node: DivNode, scope: Scope):
        print('Visiting Div Node')
        return self._check_int_binary_operation(node, scope, '/', IntType)

    @visitor.when(NotNode)
    def visit(self, node: NotNode, scope: Scope):
        print('Visiting Not Node')
        return self._check_unary_operation(node, scope, 'not', BoolType)

    @visitor.when(LeqNode)
    def visit(self, node: LeqNode, scope: Scope):
        print('Visiting Leq Node')
        return self._check_int_binary_operation(node, scope, '<=', BoolType)

    @visitor.when(LessNode)
    def visit(self, node: LessNode, scope: Scope):
        print('Visiting Less Node')
        return self._check_int_binary_operation(node, scope, '<', BoolType)

    @visitor.when(EqualNode)
    def visit(self, node: EqualNode, scope: Scope):
        print('Visiting Equal Node')
        self.visit(node.left, scope)
        self.visit(node.right, scope)
        return BoolType()

    @visitor.when(AndNode)
    def visit(self, node: AndNode, scope: Scope):
        print('Visiting And Node')
        return self._check_bool_binary_operation(node, scope, 'and', BoolType)

    @visitor.when(OrNode)
    def visit(self, node: OrNode, scope: Scope):
        print('Visiting Or Node')
        return self._check_bool_binary_operation(node, scope, 'or', BoolType)

    @visitor.when(BlockNode)
    def visit(self, node: BlockNode, scope: Scope):
        print('Visiting Block Node')
        child_scope = scope.create_child()
        return_type = ErrorType()
        for expr in node.expr_list:
            return_type = self.visit(expr, child_scope)
        return return_type

    @visitor.when(ConditionalNode)
    def visit(self, node: ConditionalNode, scope: Scope):
        print('Visiting Conditional Node')
        condition = self.visit(node.condition, scope)
        if not isinstance(condition, BoolType):
            self.errors.append(err.INCOMPATIBLE_TYPES % (condition.name, 'bool'))
            return ErrorType()

        print('Visiting Then Body')
        then_return_type = ErrorType
        for i in node.then_body:
            then_return_type = self.visit(i, scope)
            if then_return_type == ErrorType:
                return ErrorType

        print('Visiting Else Body')
        else_type: Type = self.visit(node.else_body, scope)
        if else_type == ErrorType:
            return ErrorType

        return common_ancestor(then_return_type, else_type)

    @visitor.when(LoopNode)
    def visit(self, node: LoopNode, scope: Scope):
        print('Visiting Loop Node')
        condition = self.visit(node.condition, scope)
        if condition != BoolType():
            self.errors.append(err.INCOMPATIBLE_TYPES % (condition.name, 'bool'))
            return ErrorType()

        body_return_type = ErrorType()
        child_scope = scope.create_child()
        for i in node.body:
            body_return_type = self.visit(i, child_scope)
            if body_return_type == ErrorType:
                return ErrorType

        else_return_type = ErrorType()
        child_scope = scope.create_child()
        for i in node.else_body:
            else_return_type = self.visit(i, child_scope)
            if else_return_type == ErrorType:
                return ErrorType

        return common_ancestor(body_return_type, else_return_type)

    @visitor.when(ExponEulerNode)
    def visit(self, node: ExponEulerNode, scope: Scope):
        print('Visiting ExponEuler Node')
        return self._check_unary_operation(node, scope, 'e^', IntType)

    @visitor.when(SinNode)
    def visit(self, node: SinNode, scope: Scope):
        print('Visiting Sin Node')
        return self._check_unary_operation(node, scope, 'sin', IntType)

    @visitor.when(CosNode)
    def visit(self, node: CosNode, scope: Scope):
        print('Visiting Cos Node')
        return self._check_unary_operation(node, scope, 'cos', IntType)

    @visitor.when(SqrtNode)
    def visit(self, node: SqrtNode, scope: Scope):
        print('Visiting Sqrt Node')
        return self._check_unary_operation(node, scope, 'sqrt', IntType)

    @visitor.when(RandNode)
    def visit(self, node: RandNode, scope: Scope):
        return IntType()

    @visitor.when(LetNode)
    def visit(self, node: LetNode, scope: Scope):
        print('Visiting Let Node')
        child_scope = scope.create_child()
        for decl in node.assignments:
            self.visit(decl, child_scope)

        body_return_type = ErrorType()
        for i in node.body:
            print(f'Visiting Body Node with scope: {child_scope}')
            body_return_type = self.visit(i, child_scope)
            if body_return_type == ErrorType():
                return ErrorType()
        return body_return_type

    @visitor.when(VariableNode)
    def visit(self, node: VariableNode, scope: Scope):
        print('Visiting Variable Node')
        # find variable in scope
        var = scope.find_variable(node.idx)
        print(f'Variable: {var}')
        if var is None:
            print('Variable not found')
            self.errors.append(err.VARIABLE_NOT_DEFINED % (node.idx))
            return ErrorType()
        return var.type

    @visitor.when(AssignNode)
    def visit(self, node: AssignNode, scope: Scope):
        print('Visiting Assign Node')
        # check if variable is defined in the scope
        var = scope.find_variable(node.idx)
        if var is not None:
            self.errors.append(err.LOCAL_ALREADY_DEFINED % (node.idx))
            return ErrorType()

        # check type of expression
        expr_type = self.visit(node.expr, scope)
        if isinstance(expr_type, ErrorType):
            return ErrorType()

        # define variable in scope
        scope.define_variable(node.idx, expr_type)
        return expr_type

    @visitor.when(DestructiveAssignment)
    def visit(self, node: DestructiveAssignment, scope: Scope):
        print('Visiting Desctructive Node')
        # check if variable is defined in the scope
        var = scope.find_variable(node.idx)
        if var is None:
            self.errors.append(err.VARIABLE_NOT_DEFINED % (node.idx))
            return ErrorType()

        # check type of expression
        expr_type = self.visit(node.expr, scope)
        if isinstance(expr_type, ErrorType):
            return ErrorType()

        # ancestor type between old value and new value
        ancestor = common_ancestor(var.type, expr_type)
        if ancestor != var.type:
            self.errors.append(err.INCOMPATIBLE_TYPES % (expr_type, var.type))
            return ErrorType()

        # update new expr_type
        var.vtype = expr_type
        return expr_type

    @visitor.when(ConformsNode)
    def visit(self, node: ConformsNode, scope: Scope):
        print('Visiting Conforms Node')
        try:
            if node.type_to in G.nonTerminals:
                type_as = self.context.get_type(str(node.type_to))
            else:
                type_as = self.context.get_type(node.type_to.lex)

        except SemanticError as e:
            self.errors.append(e.text)
            return ErrorType()

        try:
            type_expr = self.visit(node.exp, scope)
        except SemanticError as e:
            self.errors.append(e.text)
            return ErrorType()

        anc = common_ancestor(type_as, type_expr)
        if anc == type_as:
            return type_as
        else:
            self.errors.append(err.INCOMPATIBLE_TYPES % (type_expr.name, type_as.name))
            return ErrorType()



    #------------------------------------NOT DONE

    @visitor.when(IsNode)
    def visit(self, node: IsNode, scope: Scope):
        pass

    @visitor.when(IndexationNode)
    def visit(self, node: IndexationNode, scope: Scope):
        pass

    @visitor.when(ForNode)
    def visit(self, node: ForNode, scope: Scope):
        pass

    @visitor.when(RangeNode)
    def visit(self, node: RangeNode, scope: Scope):
        pass

    @visitor.when(List_Comprehension)
    def visit(self, node: List_Comprehension, scope: Scope):
        pass









    @visitor.when(VoidNode)
    def visit(self, node: VoidNode, scope: Scope):
        return VoidType()

    @visitor.when(InstantiateNode)
    def visit(self, node: InstantiateNode, scope: Scope):
        pass

    @visitor.when(AttrCallNode)
    def visit(self, node: AttrCallNode, scope: Scope):
        pass

    @visitor.when(FuncCallNode)
    def visit(self, node: FuncCallNode, scope: Scope):
        pass




    @visitor.when(TypeDeclarationNode)
    def visit(self, node: TypeDeclarationNode, scope: Scope):
        pass

    @visitor.when(ProtocolDeclarationNode)
    def visit(self, node: ProtocolDeclarationNode, scope: Scope):
        pass

    @visitor.when(MethodDeclaration)
    def visit(self, node: MethodDeclaration, scope: Scope):
        pass

    @visitor.when(AttrDeclarationNode)
    def visit(self, node: AttrDeclarationNode, scope: Scope):
        pass

    @visitor.when(FuncDeclarationNode)
    def visit(self, node: FuncDeclarationNode, scope: Scope):
        pass










    # @visitor.when(TypeDeclarationNode)
    # def visit(self, node: TypeDeclarationNode, scope: Scope):
    #     self.current_type = self.context.get_type(node.idx)
    #
    #     #double checking the type
    #     attrs = [feature for feature in node.attributes if isinstance(feature, AttrDeclarationNode)]
    #     functions = [feature for feature in node.functions if isinstance(feature, FuncDeclarationNode)]
    #
    #     for attr in attrs:
    #         self.visit(attr, scope)
    #
    #     for function in functions:
    #         self.visit(function, scope.create_child())
    #
    # @visitor.when(AttrDeclarationNode)
    # def visit(self, node: AttrDeclarationNode, scope: Scope):
    #     if node.idx == 'self':
    #         self.errors.append(err.SELF_INVALID_ATTRIBUTE_ID)
    #
    #     attr_type = self.context.get_type(node.type_expected)
    #
    #     if node.value is not None:
    #         expr_type = self.visit(node.value, scope.create_child())
    #         if not expr_type.conforms_to(attr_type):
    #             self.errors.append(err.INCOMPATIBLE_TYPES % (expr_type.name, attr_type.name))
    #
    #     scope.define_variable(node.idx, attr_type)
    #
    # @visitor.when(MethodDeclaration)
    # def visit(self, node: MethodDeclaration, scope: Scope):
    #     self.current_method = self.current_type.get_method(node.idx)
    #
    #     scope.define_variable('self', self.current_type)
    #
    #     for param_name, param_type in zip(self.current_method.param_names, self.current_method.param_types):
    #         if not scope.is_local(param_name):
    #             if param_type.name == 'SELF_TYPE':
    #                 self.errors.append(err.INVALID_PARAM_TYPE % 'SELF_TYPE')
    #                 scope.define_variable(param_name, ErrorType())
    #             else:
    #                 scope.define_variable(param_name, self.context.get_type(param_type.name))
    #         else:
    #             self.errors.append(err.LOCAL_ALREADY_DEFINED % (param_name, self.current_method.name))
    #
    # @visitor.when(LetNode)
    # #todo fix this
    # def visit(self, node: LetNode, scope: Scope):
    #     for _id, _type, _expr in node.declarations:
    #         try:
    #             var_static_type = self.context.get_type(_type) if _type != 'SELF_TYPE' else self.current_type
    #         except SemanticError as e:
    #             self.errors.append(e.text)
    #             var_static_type = ErrorType()
    #
    #         if scope.is_local(_id):
    #             self.errors.append(err.LOCAL_ALREADY_DEFINED % (_id, self.current_method.name))
    #         else:
    #             scope.define_variable(_id, var_static_type)
    #
    #         expr_type = self.visit(_expr, scope.create_child()) if _expr is not None else None
    #         if expr_type is not None and not expr_type.conforms_to(var_static_type):
    #             self.errors.append(err.INCOMPATIBLE_TYPES % (expr_type.name, var_static_type.name))
    #
    #     return self.visit(node.body, scope.create_child())
    #
    # @visitor.when(AssignNode)
    # def visit(self, node: AssignNode, scope: Scope):
    #     var_info = scope.find_variable(node.idx)
    #
    #     expr_type = self.visit(node.expr, scope.create_child())
    #
    #     if var_info is None:
    #         self.errors.append(err.VARIABLE_NOT_DEFINED % (node.idx, self.current_method.name))
    #     else:
    #         if not expr_type.conforms_to(var_info.type):
    #             self.errors.append(err.INCOMPATIBLE_TYPES % (expr_type.name, var_info.type.name))
    #
    #     return expr_type



    # @visitor.when(ConditionalNode)
    # def visit(self, node: ConditionalNode, scope: Scope):
    #     if_type = self.visit(node.condition, scope)
    #     then_type = self.visit(node.then_body, scope)
    #     else_type = self.visit(node.then_body, scope)
    #     if if_type != self.context.get_type('Bool'):
    #         self.errors.append(err.INCOMPATIBLE_TYPES % (if_type.name, 'Bool'))
    #     return then_type.join(else_type)

    # @visitor.when(LoopNode)
    # def visit(self, node: LoopNode, scope: Scope):
    #     condition = self.visit(node.condition, scope)
    #     if condition != self.context.get_type('Bool'):
    #         self.errors.append(err.INCOMPATIBLE_TYPES % (condition.name, 'Bool'))
    #
    #     self.visit(node.body, scope.create_child())
    #     return self.context.get_type('Object')


    # @visitor.when(FuncCallNode)
    # #todo also fix this
    # def visit(self, node: FuncCallNode, scope: Scope):
    #     if node.obj_called is None:
    #         node.obj_called = VariableNode('self')
    #
    #     obj_type = self.visit(node.obj_called, scope)
    #
    #     if node.obj_called is not None:
    #         try:
    #             ancestor_type = self.context.get_type(node.obj_called.idx)
    #         except SemanticError as e:
    #             ancestor_type = ErrorType()
    #             self.errors.append(e.text)
    #
    #         if not obj_type.conforms_to(ancestor_type):
    #             self.errors.append(err.INVALID_ANCESTOR % (obj_type.name, ancestor_type.name))
    #     else:
    #         ancestor_type = obj_type
    #
    #     try:
    #         method = ancestor_type.get_method(node.id)
    #     except SemanticError as e:
    #         self.errors.append(e.text)
    #         for arg in node.args:
    #             self.visit(arg, scope)
    #         return ErrorType()
    #
    #     if len(node.args) != len(method.param_names):
    #         self.errors.append(err.METHOD_OVERRIDE_ERROR % (method.name, obj_type.name))
    #
    #     for i, arg in enumerate(node.args):
    #         arg_type = self.visit(arg, scope)
    #         if not arg_type.conforms_to(method.param_types[i]):
    #             self.errors.append(err.INCOMPATIBLE_TYPES % (arg_type.name, method.param_types[i].name))
    #
    #     return method.return_type if method.return_type.name != 'SELF_TYPE' else ancestor_type
    #
    #
    #
    #
    #
    # @visitor.when(IsNode)
    # def visit(self, node:IsNode, scope:Scope):
    #     #see if variable is defined
    #     pass
    #
    #
    #
    #
    # @visitor.when(VariableNode)
    # def visit(self, node: VariableNode, scope: Scope):
    #     variable = scope.find_variable(node.idx.lex)
    #     if variable is None:
    #         self.errors.append(err.VARIABLE_NOT_DEFINED % (node.idx.lex, self.current_method.name))
    #         return ErrorType()
    #     return variable.type
    #
    # @visitor.when(InstantiateNode)
    # def visit(self, node: InstantiateNode, scope: Scope):
    #     try:
    #         return self.context.get_type(node.iden) if node.iden != 'self' else self.current_type
    #     except SemanticError as e:
    #         self.errors.append(e.text)
    #         return ErrorType()






    def _check_bool_binary_operation(self, node: BinaryNode, scope: Scope, operation: str, return_type):
        left_type = self.visit(node.left, scope)
        right_type = self.visit(node.right, scope)

        if left_type == right_type == BoolType:
            return return_type
        self.errors.append(err.INVALID_BINARY_OPERATION % (operation, left_type.name, right_type.name))
        return ErrorType()


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

