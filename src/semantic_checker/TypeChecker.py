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
            self.visit(elem, scope)

        print(f'About to visit the expression')
        self.current_type = None

        for i in node.expression:
            ans = self.visit(i, scope.create_child())

        return scope

    @visitor.when(ast.PrintNode)
    def visit(self, node: PrintNode, scope: Scope):
        print(f'visiting Print')
        ans = self.visit(node.expr, scope)
        return ObjectType() if not isinstance(ans,ErrorType) else ErrorType()

    @visitor.when(ConstantNumNode)
    def visit(self, node: ConstantNumNode, scope: Scope):
        print('Visiting Constant Num')
        return IntType()

    @visitor.when(ConstantStringNode)
    def visit(self, node: ConstantStringNode, scope: Scope):
        print('Visiting Constant String')
        return StringType()

    @visitor.when(ConstantBoolNode)
    def visit(self, node: ConstantBoolNode, scope: Scope):
        return BoolType()

    @visitor.when(StringExpression)
    def visit(self, node: StringExpression, scope: Scope):
        print(f'Visiting string expression')
        expected = [IntType(), StringType()]
        left_type = self.visit(node.left, scope)
        right_type = self.visit(node.right, scope)
        if isinstance(left_type, ErrorType) or isinstance(right_type, ErrorType):
            return ErrorType()

        if left_type in expected:
            if right_type in expected:
                return StringType()
            else:
                self.errors.append(err.INCOMPATIBLE_TYPES(right_type, StringType))
        else:
            self.errors.append(err.INCOMPATIBLE_TYPES(left_type, StringType))
        return ErrorType()

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
        return_type = ErrorType()
        for expr in node.expr_list:
            return_type = self.visit(expr, scope.create_child())
            if isinstance(return_type, ErrorType):
                return ErrorType()
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
            if isinstance(then_return_type, ErrorType):
                return ErrorType()

        print('Visiting Else Body')
        else_type: Type = self.visit(node.else_body, scope)

        print('Finishing Else Body')
        if isinstance(else_type, ErrorType):
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
            if isinstance(body_return_type, ErrorType):
                return ErrorType()


        else_return_type = ErrorType()
        child_scope = scope.create_child()
        for i in node.else_body:
            else_return_type = self.visit(i, child_scope)
            if isinstance(else_return_type, ErrorType):
                return ErrorType()

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

        type_ = ErrorType()
        for decl in node.assignments:
            type_ = self.visit(decl, scope)
            if isinstance(type_, ErrorType):
                return ErrorType()

        body_return_type = ErrorType()

        for i in node.body:
            print(f'Visiting Body Node with scope: {scope}')
            body_return_type = self.visit(i, scope)
            if isinstance(body_return_type, ErrorType):
                return ErrorType()
        return body_return_type

    @visitor.when(VariableNode)
    def visit(self, node: VariableNode, scope: Scope):
        print('Visiting Variable Node')
        # find variable in scope
        var = scope.find_variable(node.idx)
        print(f'Variable: {var}')
        if var is None:
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
        if isinstance(node.idx, ast.IndexationNode):
            var = self.visit(node.idx, scope)
        else:
            var = scope.find_variable(node.idx)

        if var is None:
            self.errors.append(err.VARIABLE_NOT_DEFINED % node.idx)
            return ErrorType()

        # check type of expression
        expr_type = self.visit(node.expr, scope)
        if isinstance(expr_type, ErrorType):
            return ErrorType()

        var.type = expr_type
        print(var.type)
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

    @visitor.when(VoidNode)
    def visit(self, node: VoidNode, scope: Scope):
        return VoidType()

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

    @visitor.when(InstantiateNode)
    def visit(self, node: InstantiateNode, scope: Scope):
        print('Visiting Instantiate Node')
        try:
            new_type_ = self.context.get_type(node.iden)

            #check that it's the same amount of params
            if new_type_.params:
                if len(node.params) != len(new_type_.params):
                    self.errors.append(err.WRONG_NUMBER_OF_ARGUMENTS % (len(new_type_.params), len(node.params)))
                    return ErrorType()

            #check that the types of the params are the same as the ones in the declaration
            if len(node.params) == 0:
                return new_type_

            for i, param in enumerate(node.params):
                paramid, param_type = param
                if param_type is None:
                    #variable is a variable or expr
                    try:
                        param_type = self.visit(paramid, scope)
                    except:
                        param_type = scope.find_variable(paramid).type
                        if param_type is None:
                            self.errors.append(err.VARIABLE_NOT_DEFINED % paramid)
                            return ErrorType()

                    exp_id, exp_type = new_type_.params[i]
                    if isinstance(exp_type, NoneType):
                        continue
                    else:
                        anc = common_ancestor(param_type, exp_type)
                        if anc != new_type_.params[i]:
                            self.errors.append(err.INCOMPATIBLE_TYPES % (param_type.name, exp_type.name))
                            return ErrorType()

        except SemanticError as e:
            self.errors.append(e.text)
            return ErrorType()
        print(new_type_)
        return new_type_

    @visitor.when(IsNode)
    def visit(self, node: IsNode, scope: Scope):
        print('Visiting Is Node')
        # check o q sea ese tipo o q implemente ese protocolo
        try:
            if node.right in G.nonTerminals:
                type_as = self.context.get_type_or_protocol(str(node.right))
            else:
                type_as = self.context.get_type_or_protocol(node.right.lex)

        except SemanticError as e:
            self.errors.append(e.text)
            return ErrorType()

        try:
            type_expr = self.visit(node.left, scope)
        except SemanticError as e:
            self.errors.append(e.text)
            return ErrorType()

        print(type_as, type_expr)
        if isinstance(type_as, Type):
            anc = common_ancestor(type_as, type_expr)

            if anc == type_as:
                return BoolType()
        else:
            if isinstance(type_as, Protocol):
                if type_as.type_implements_me(type_expr):
                    return BoolType()
                else:
                    self.errors.append(err.INCOMPATIBLE_TYPES % (type_expr.name, type_as.name))
                    return ErrorType()



    @visitor.when(FuncDeclarationNode)
    def visit(self, node: FuncDeclarationNode, scope: Scope):
        print('Visiting Func Declaration Node')
        # declare the function in the context, with params
        # functions dont have a return type
        try:
            param_types = [self.context.get_type_or_protocol(type_) for _, type_ in node.params]
            param_names = [name for name, _ in node.params]

            for i, k in enumerate(param_names):
                if isinstance(k, VoidNode):
                    param_names.pop(i)
                    param_types.pop(i)
            try:
                scope.define_function(node.idx, param_names, param_types, node.body)
            except SemanticError as error:
                self.errors.append(error.text)
        except SemanticError as error:
            self.errors.append(error.text)

    @visitor.when(RangeNode)
    def visit(self, node: RangeNode, scope: Scope):
        print('Visiting Range Node')
        # check that both inputs are int
        res = self._check_int_binary_operation(node, scope, 'range', IntType)
        return IterableType(res) if isinstance(res, IntType) else ErrorType()

    @visitor.when(IndexationNode)
    def visit(self, node: IndexationNode, scope: Scope):
        print('Visiting Indexation Node')
        # check that obj is Iterable
        try:
            # checking if I am indexing on a defined variable
            obj_type = scope.find_variable(node.obj.lex).type
        except:
            # visit the object I am indexing on
            obj_type = self.visit(node.obj, scope)

        if not isinstance(obj_type, IterableType):
            self.errors.append(err.INCOMPATIBLE_TYPES % (obj_type.name, 'Iterable'))
            return ErrorType()

        # check that index is a Number
        index_type = self.visit(node.index, scope)
        if index_type != IntType():
            self.errors.append(err.INCOMPATIBLE_TYPES % (index_type.name, 'Int'))
            return ErrorType()

        # return the type of the elements in the iterable
        return obj_type.elem_type

    @visitor.when(ForNode)
    def visit(self, node: ForNode, scope: Scope):
        # check that it's an Iterable Object
        print('Visiting For Node')
        #iterable is either range, a List Comprehension or a ListNode
        obj_type = self.visit(node.iterable, scope)
        if not isinstance(obj_type, IterableType):
            self.errors.append(err.INCOMPATIBLE_TYPES % (obj_type.name, 'Iterable'))
            return ErrorType()

        # define in a child scope the variable that will be used in the loop as the type of the iterable
        child_scope = scope.create_child()
        child_scope.locals = scope.locals

        #check if variable is not already defined
        var = scope.find_variable(node.varidx.lex)
        if var is not None:
            self.errors.append(err.LOCAL_ALREADY_DEFINED %var.name)
            return ErrorType()
        child_scope.define_variable(node.varidx.lex, obj_type.elem_type)

        # visit the body of the loop
        body_ret = ErrorType()
        if node.body != []:
            for i in node.body:
                body_ret = self.visit(i, child_scope)
                if isinstance(body_ret, ErrorType):
                    return ErrorType()

        else_ret = ErrorType()
        # visit the else body
        if node.elsex != []:
            for i in node.elsex:
                else_ret = self.visit(i, child_scope)
                if isinstance(else_ret, ErrorType):
                    return ErrorType()

        return common_ancestor(body_ret, else_ret)

    @visitor.when(ListNode)
    def visit(self, node: ListNode, scope:Scope):
        ret_type = [self.visit(expr, scope.create_child()) for expr in node.obj]
        if len(set(ret_type)) != 1:
            self.errors.append(err.VECTOR_DIFF_TYPES)
            return ErrorType()
        return IterableType(ret_type[0])

    @visitor.when(List_Comprehension)
    def visit(self, node: List_Comprehension, scope: Scope):
        print('Visiting List Comprehension')
        # for idx in iterable : do exp
        # return iterable of exp.type
        iterable_type = self.visit(node.expr, scope)
        if not isinstance(iterable_type, IterableType):
            return ErrorType()

        id_type = iterable_type.elem_type

        child_scope = scope.create_child()

        # see if variable is already defined
        var = child_scope.find_variable(node.idx.lex)
        if var is not None:
            self.errors.append(err.LOCAL_ALREADY_DEFINED % node.idx.lex)
            return ErrorType()

        # declare it
        child_scope.define_variable(node.idx.lex, id_type)

        ret_type = ErrorType()

        for i in node.exp_for_idx:
            ret_type = self.visit(i, child_scope)
            if isinstance(ret_type, ErrorType):
                print('List Comprehension failed')
                return ErrorType()

        return IterableType(ret_type)

    @visitor.when(AttrCallNode)
    def visit(self, node: AttrCallNode, scope: Scope):
        # the only attribute I can call is self.something from inside a type
        print('Visiting Attr Call Node')
        if node.idx != 'self':
            self.errors.append(err.ATTRIBUTES_PRIVATE % node.idx)
            return ErrorType()

        # check if in a class
        if self.current_type is None:
            self.errors.append(err.SELF_OUTSIDE_CLASS)
            return ErrorType()

        # check if the attribute is defined
        try:
            attr = self.current_type.get_attribute(node.attr_called.lex)
        except SemanticError as e:
            self.errors.append(e.text)
            return ErrorType()

        print(f'returning {attr.type}')
        return attr.type


    #------------------------------------NOT DONE

    @visitor.when(FuncCallNode)
    def visit(self, node: FuncCallNode, scope: Scope):
        print('Visiting Func Call Node')

        #objcalled is either an idx(type) or a base().something or self.a() or a.b() a function call
        #if objcalled is a idx then:
        #type.() or self.() or base() or method()
        try:
            idx = node.obj_called
            print(f'IDX: {idx.lex}')
            print(self.current_type)

            #checking if it's base
            if idx.lex == 'base':
                if self.current_type is None:
                    print('Base outside class')
                    self.errors.append(err.BASE_OUTSIDE_CLASS)
                    return ErrorType()
                if self.current_type.parent is None:
                    print('Base without inheritance')
                    self.errors.append(err.BASE_WITHOUT_INHERITANCE)
                    return ErrorType()

                print(f'Visiting base {self.current_type.parent.name}')
                print(f'Cuurent method: {self.current_method}')

                base_type = self.current_type.parent

                #visit the current method in the parent class
                try:
                    method = base_type.get_method(self.current_method.name)
                except SemanticError as e:
                    self.errors.append(e.text)
                    return ErrorType()
                print(f'Visiting method {method.expr} in type {base_type.name}')
                return self.visit(method.expr, scope)

            #checking if it's self
            if idx.lex == 'self':
                if self.current_type is None:
                    self.errors.append(err.SELF_OUTSIDE_CLASS)
                    return ErrorType()
                #it's a function call to a method in the current class
                return self.visit(node.params[0], scope)


            #checking if it's a method or a type defined
            if self.current_type is None:
            # this means that it's calling a function or a type
                try:
                    print(f'Looking for type {idx.lex}')
                    a = scope.find_variable(idx.lex).type

                    #if it's here it's because it'a a type call
                    old_type = self.current_type
                    self.current_type = a
                    ans = self.visit(node.params[0], scope)
                    self.current_type = old_type
                    return ans

                except:
                    #it means it is a function call
                    func = scope.find_function(idx.lex)

                    print(f'Found function {func.name}')

                    #check params
                    if func is None:
                        print('Function not defined')
                        self.errors.append(err.FUNCTION_NOT_DEFINED % idx.lex)
                        return ErrorType()

                    print(f'Function: {func.body}')

                    params = []

                    for var, type in node.params:
                        if isinstance(var, VoidNode):
                            continue
                        try:
                            params.append(self.visit(var, scope))
                        except:
                            params.append(scope.find_variable(var).type)


                    print(f'Params given: {params}\nParams expected: {func.param_types}')
                    ok = self.check_parameters(params, func.param_types)
                    print('parameters checked')
                    if ok is False:
                        return ErrorType()

                    #create child scope
                    child_scope = scope.create_child()

                    #define the parameters in the local scope with the names of the expected, and the types of the given
                    for i,name in enumerate(func.param_names):
                        #see if it's defined
                        var = child_scope.find_variable(name.idx)
                        if var is None:
                            child_scope.define_variable(name.idx, params[i])
                        else:
                            child_scope.change_type(name.idx, params[i])


                    print(f'Visiting function {func.name} with scope {child_scope}')

                    return self.visit(func.body, child_scope)
            else:
                #check if it's a method of the current type
                try:
                    method = self.current_type.get_method(idx.lex)
                except SemanticError as e:
                    self.errors.append(e.text)
                    return ErrorType()


                #select the params that are not void
                params = [type for val, type in node.params if not isinstance(val, VoidNode)]

                ok = self.check_parameters(params, method.param_types)
                if ok is False:
                    return ErrorType()

                self.current_method = method
                print(f'Visiting method {method.expr} in type {self.current_type.name}')
                return self.visit(method.expr, scope)

        except:
            #this means that the object called is a function call,
            #it can only be b().a()
            #so I need to visit the object called first
            obj_type = self.visit(node.obj_called, scope)
            if isinstance(obj_type, ErrorType):
                return ErrorType()

            return self.visit(node.params, scope)

            #this means that the object called is a function call
            #so it can be a nested func call, the original func call must return a type



        #FuncCallNode can be a.b() / b() / base.func() / self.func()

        #check if

    @visitor.when(TypeDeclarationNode)
    def visit(self, node: TypeDeclarationNode, scope: Scope):
        print('Visiting Type Declaration Node')
        type = self.context.get_type(node.idx)
        self.current_type = type

        #set the type of all its attributes
        for i in type.attributes:
            if i.value is None:
                continue

            value_t = self.visit(i.value, scope)

            if i.type is None or isinstance(i.type, NoneType):
                i.type = value_t
            else:
                ancestor = common_ancestor(value_t, i.type)
                #if the value conforms to the specified value
                if ancestor != i.type:
                    self.errors.append(err.INCOMPATIBLE_TYPES %(value_t, i.type))
                    return ErrorType()

        return

















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
    # @visitor.when(InstantiateNode)
    # def visit(self, node: InstantiateNode, scope: Scope):
    #     try:
    #         return self.context.get_type(node.iden) if node.iden != 'self' else self.current_type
    #     except SemanticError as e:
    #         self.errors.append(e.text)
    #         return ErrorType()


    def check_parameters(self, params_given, params_expected):
        if len(params_given) != len(params_expected):
            self.errors.append(err.WRONG_NUMBER_OF_ARGUMENTS % (len(params_expected), len(params_given)))
            return False
        print(params_expected)
        for arg, param in zip(params_given, params_expected):
            if param is None:
                continue
            if not arg.conforms_to(param):
                self.errors.append(err.INCOMPATIBLE_TYPES % (arg.name, param.name))
                return False
        return True



    def _check_bool_binary_operation(self, node: BinaryNode, scope: Scope, operation: str, return_type):
        left_type = self.visit(node.left, scope)
        right_type = self.visit(node.right, scope)

        if left_type == right_type == BoolType:
            return return_type()
        self.errors.append(err.INVALID_BINARY_OPERATION % (operation, left_type.name, right_type.name))
        return ErrorType()


    def _check_int_binary_operation(self, node: BinaryNode, scope: Scope, operation: str, return_type):
        left_type = self.visit(node.left, scope)
        right_type = self.visit(node.right, scope)

        if left_type == right_type == IntType:
            return return_type()
        self.errors.append(err.INVALID_BINARY_OPERATION % (operation, left_type.name, right_type.name))
        return ErrorType()


    def _check_unary_operation(self, node: UnaryNode, scope: Scope, operation: str, expected_type):
        typex = self.visit(node.expr, scope)
        if typex == expected_type:
            return expected_type()
        self.errors.append(err.INVALID_UNARY_OPERATION % (operation, typex.name))
        return ErrorType()

