import random
from typing import List

from src.cmp.ast import *
import src.cmp.errors as err
import src.cmp.visitor as visitor
from src.cmp.semantic import *
from src.cmp import ast
from src.cmp.grammar import G
from math import *
from random import *


booleans = {'true': True, 'false': False}
types = {'string': str, 'bool': bool, 'Iterable': list}
class Evaluator:
    def __init__(self, context: Context = None, errors: List[str] = []):
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
        print('Visiting Print Node')
        ans = self.visit(node.expr, scope)
        print(ans)
        return

    @visitor.when(ConstantNumNode)
    def visit(self, node: ConstantNumNode, scope: Scope):
        return float(node.idx)

    @visitor.when(ConstantStringNode)
    def visit(self, node: ConstantStringNode, scope: Scope):
        try:
            a = str(node.value.lex)[1:-1]
            a = a.replace(str('\\"'), '"')
            return a
        except:
            return str(node.value)

    @visitor.when(ConstantBoolNode)
    def visit(self, node: ConstantBoolNode, scope: Scope):
        b = node.value.lex
        return booleans[b]

    @visitor.when(StringExpression)
    def visit(self, node: StringExpression, scope: Scope):
        left = self.visit(node.left, scope)
        right = self.visit(node.right, scope)
        return str(left) + str(right)

    @visitor.when(ModNode)
    def visit(self, node: ArithmeticNode, scope: Scope):
        left = self.visit(node.left, scope)
        right = self.visit(node.right, scope)
        return left % right

    @visitor.when(LogNode)
    def visit(self, node: ArithmeticNode, scope: Scope):
        left = self.visit(node.left, scope)
        right = self.visit(node.right, scope)
        return log(right, left)

    @visitor.when(StarNode)
    def visit(self, node: StarNode, scope: Scope):
        left = self.visit(node.left, scope)
        right = self.visit(node.right, scope)
        return left * right

    @visitor.when(NegNode)
    def visit(self, node: NegNode, scope: Scope):
        expr = self.visit(node.expr, scope)
        return -1 * expr

    @visitor.when(PlusNode)
    def visit(self, node: PlusNode, scope: Scope):
        left = self.visit(node.left, scope)
        right = self.visit(node.right, scope)
        return left + right

    @visitor.when(MinusNode)
    def visit(self, node: MinusNode, scope: Scope):
        left = self.visit(node.left, scope)
        right = self.visit(node.right, scope)
        return left - right

    @visitor.when(PowNode)
    def visit(self, node: MinusNode, scope: Scope):
        left = self.visit(node.left, scope)
        right = self.visit(node.right, scope)
        return left ** right

    @visitor.when(DivNode)
    def visit(self, node: DivNode, scope: Scope):
        left = self.visit(node.left, scope)
        right = self.visit(node.right, scope)
        return left / right

    @visitor.when(NotNode)
    def visit(self, node: NotNode, scope: Scope):
        value = self.visit(node.expr, scope)
        return not booleans[value]

    @visitor.when(LeqNode)
    def visit(self, node: LeqNode, scope: Scope):
        left = self.visit(node.left, scope)
        right = self.visit(node.right, scope)
        return left <= right

    @visitor.when(LessNode)
    def visit(self, node: LessNode, scope: Scope):
        left = self.visit(node.left, scope)
        right = self.visit(node.right, scope)
        return left < right

    @visitor.when(EqualNode)
    def visit(self, node: EqualNode, scope: Scope):
        left = self.visit(node.left, scope)
        right = self.visit(node.right, scope)
        return left == right

    @visitor.when(AndNode)
    def visit(self, node: AndNode, scope: Scope):
        left = self.visit(node.left, scope)
        right = self.visit(node.right, scope)
        return left and right

    @visitor.when(OrNode)
    def visit(self, node: OrNode, scope: Scope):
        left = self.visit(node.left, scope)
        right = self.visit(node.right, scope)
        return left or right

    @visitor.when(BlockNode)
    def visit(self, node: BlockNode, scope: Scope):
        return_type = None
        for expr in node.expr_list:
            return_type = self.visit(expr, scope.create_child())
        return return_type

    @visitor.when(ConditionalNode)
    def visit(self, node: ConditionalNode, scope: Scope):

        condition = self.visit(node.condition, scope)

        if condition is True:
            then_return_type = None
            for i in node.then_body:
                then_return_type = self.visit(i, scope)
            return then_return_type

        return self.visit(node.else_body, scope)


    @visitor.when(LoopNode)
    def visit(self, node: LoopNode, scope: Scope):

        return_ = None
        # todo verify if child scope is necessary
        child_scope = scope.create_child()
        visited_while = False
        while self.visit(node.condition, child_scope) is True:
            for i in node.body:
                visited_while = True
                return_ = self.visit(i, child_scope)

        if visited_while:
            return return_
        else:
            for i in node.else_body:
                return_ = self.visit(i, child_scope)
            return return_

    @visitor.when(ExponEulerNode)
    def visit(self, node: ExponEulerNode, scope: Scope):
        expr = self.visit(node.expr, scope)
        return e ** float(expr)

    @visitor.when(SinNode)
    def visit(self, node: SinNode, scope: Scope):
        expr = self.visit(node.expr, scope)
        return sin(float(expr))

    @visitor.when(CosNode)
    def visit(self, node: CosNode, scope: Scope):
        expr = self.visit(node.expr, scope)
        return cos(float(expr))

    @visitor.when(SqrtNode)
    def visit(self, node: SqrtNode, scope: Scope):
        expr = self.visit(node.expr, scope)
        return sqrt(float(expr))

    @visitor.when(RandNode)
    def visit(self, node: RandNode, scope: Scope):
        return random.random()

    @visitor.when(LetNode)
    def visit(self, node: LetNode, scope: Scope):
        # todo this one
        type_ = None
        for decl in node.assignments:
            type_ = self.visit(decl, scope)

        body_return_type = None

        for i in node.body:

            body_return_type = self.visit(i, scope)

        return body_return_type

    @visitor.when(VariableNode)
    def visit(self, node: VariableNode, scope: Scope):
        var = scope.find_variable(node.idx)
        return var.type

    @visitor.when(AssignNode)
    def visit(self, node: AssignNode, scope: Scope):
        expr_type = self.visit(node.expr, scope)
        print(node.idx, expr_type)
        scope.define_variable(node.idx, expr_type)
        return expr_type

    @visitor.when(DestructiveAssignment)
    def visit(self, node: DestructiveAssignment, scope: Scope):

        expr_type = self.visit(node.expr, scope)
        print(f'new value: {expr_type}')

        if isinstance(node.idx, ast.IndexationNode):
            print(node.idx.obj.lex)
            iterable = scope.find_variable(node.idx.obj.lex)
            # print(iterable)
            index = int(self.visit(node.idx.index, scope))
            # print(f'Iterable: {iterable}, index: {index}')
            scope.change_value_list(node.idx.obj.lex, index, expr_type)
            # iterable[int(self.visit(node.idx.index, scope))] = expr_type
        else:
            var = scope.find_variable(node.idx)
            scope.change_type(node.idx, expr_type)

        return expr_type

    @visitor.when(ConformsNode)
    def visit(self, node: ConformsNode, scope: Scope):

        if node.type_to in G.nonTerminals:
                type_as = self.context.get_type(str(node.type_to))
        else:
                type_as = self.context.get_type(node.type_to.lex)



        type_expr = self.visit(node.exp, scope)

        return type_expr


    @visitor.when(VoidNode)
    def visit(self, node: VoidNode, scope: Scope):
        return

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
      #todo add the parameters
            new_type_ = self.context.get_type(node.iden)
            return new_type_

    @visitor.when(IsNode)
    def visit(self, node: IsNode, scope: Scope):

        # check o q sea ese tipo o q implemente ese protocolo
            type_as = None
            if node.right in G.nonTerminals:
                type_as = self.context.get_type_or_protocol(str(node.right))
            else:
                type_as = self.context.get_type_or_protocol(node.right.lex)

            type_expr = self.visit(node.left, scope)

            if isinstance(type_as, Type):
                if type_as.name in types.keys():
                    return isinstance(type_expr, types[type_as.name])
                else:
                    return common_ancestor(type_as, type_expr) == type_as
            else:
                if isinstance(type_as, Protocol):
                    return type_as.type_implements_me(type_expr)

            return False



    @visitor.when(FuncDeclarationNode)
    def visit(self, node: FuncDeclarationNode, scope: Scope):

        # declare the function in the context, with params
        # functions dont have a return type

            param_types = [self.context.get_type_or_protocol(type_) for _, type_ in node.params]
            param_names = [name for name, _ in node.params]

            for i, k in enumerate(param_names):
                if isinstance(k, VoidNode):
                    param_names.pop(i)
                    param_types.pop(i)

            scope.define_function(node.idx, param_names, param_types, node.body)


    @visitor.when(RangeNode)
    def visit(self, node: RangeNode, scope: Scope):
        left = self.visit(node.left, scope)
        right = self.visit(node.right, scope)
        return range(int(left), int(right))

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

        # check that index is a Number
        index_type = self.visit(node.index, scope)


        # return the type of the elements in the iterable
        return obj_type[int(index_type)]

    @visitor.when(ForNode)
    def visit(self, node: ForNode, scope: Scope):
        # check that it's an Iterable Object
        #iterable is either range, a List Comprehension or a ListNode
        iterable = self.visit(node.iterable, scope)

        # define in a child scope the variable that will be used in the loop as the type of the iterable
        child_scope = scope.create_child()

        #check if variable is not already defined
        var = scope.find_variable(node.varidx.lex)
        # visit the body of the loop

        res = None

        for k in iterable:
            child_scope = scope.create_child()
            child_scope.define_variable(node.varidx.lex, k)
            for i in node.body:
                res = self.visit(i, child_scope)
        else:
            res = self.visit(node.elsex, scope)

        return res


        # body_ret = None
        # if node.body != []:
        #     for i in node.body:
        #
        #         body_ret = self.visit(i, child_scope)
        #     return body_ret
        #
        # else_ret =  None
        # # visit the else body
        # if node.elsex != []:
        #     for i in node.elsex:
        #         else_ret = self.visit(i, child_scope)
        # return else_ret


    @visitor.when(ListNode)
    def visit(self, node: ListNode, scope:Scope):
        return [self.visit(expr, scope.create_child()) for expr in node.obj]


    @visitor.when(List_Comprehension)
    def visit(self, node: List_Comprehension, scope: Scope):
        print('Visiting List Comprehension')
        # for idx in iterable : do exp
        # return iterable of exp.type
        iterable = self.visit(node.expr, scope)

        child_scope = scope.create_child()
         # declare it
        child_scope.define_variable(node.idx.lex, None)

        answer = []

        for k in iterable:
            child_scope = scope.create_child()
            child_scope.define_variable(node.idx.lex, k)
            ans = None
            for i in node.exp_for_idx:
                ans = self.visit(i, child_scope)
            answer.append(ans)


        return answer

    @visitor.when(AttrCallNode)
    def visit(self, node: AttrCallNode, scope: Scope):
        # check if the attribute is defined
        attr = self.current_type.get_attribute(node.attr_called.lex)
        return self.visit(attr.value, scope)


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
                print(f'Visiting base {self.current_type.parent.name}')
                print(f'Cuurent method: {self.current_method}')

                base_type = self.current_type.parent
                #visit the current method in the parent class
                method = base_type.get_method(self.current_method.name)
                print(f'Visiting method {method.expr} in type {base_type.name}')
                return self.visit(method.expr, scope)

            #checking if it's self
            if idx.lex == 'self':
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
                    print('method found')
                except SemanticError as e:
                    self.errors.append(e.text)
                    return ErrorType()


                #select the params that are not void
                params = [type for val, type in node.params if not isinstance(val, VoidNode)]

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

        #todo do the constructor