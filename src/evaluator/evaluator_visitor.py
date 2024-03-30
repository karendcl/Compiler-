import random
import math
from src.evaluator.context import Context

import src.cmp.visitor as visitor
from src.cmp.ast import *

class RunTimeException(Exception):
    @property
    def text(self):
        return 'Run Time Error :('

class EvaluatorVisitor(object):

    booleans = {'true': True, 'false': False}
    

    @visitor.on('node')
    def visit(self, node, tabs):
        pass

    #-------------Not Done-------------------

    @visitor.when(MethodDeclaration)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__MethodDeclaration: {node.idx}  {node.params} -> {node.expected_type}'
        # statements = '\n'.join(self.visit(child, tabs + 1) for child in node.expressions)
        return f'{ans}'        

    @visitor.when(ProtocolDeclarationNode)
    def visit(self,node,tabs=0):
        ans = '\t' * tabs + f'\\__ProtocolDeclaration: {node.idx} extends {node.extends}'
        statements = '\n'.join(self.visit(child, tabs + 1) for child in node.methods)
        return f'{ans}\n{statements}'

    @visitor.when(LetNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__LetNode:'
        ass = '\n'.join(self.visit(arg, tabs + 1) for arg in node.assignments)
        args = '\n'.join(self.visit(arg, tabs + 1) for arg in node.body)
        return f'{ans}\n{ass}\n{args}'

    @visitor.when(InstantiateNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__InstantiateNode: {node.idx.lex}'
        args = '\n'.join(self.visit(arg, tabs + 1) for arg in node.params)
        return f'{ans}\n{args}'

    @visitor.when(ConformsNode)
    def visit(self, node, tabs=0):
        ass = self.visit(node.exp, tabs + 1)
        ans = '\t' * tabs + f'\\__Conforms: \n{ass}\n {'\t' * (tabs+1)} \\__to  {node.type_to.lex}'
        return f'{ans}'

    
    #----------------"""DONE"""------------------

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode, context:Context):
        
        context = Context()
        
        context.def_function("print", lambda x: print(x[0]))
        context.def_function("sqrt", lambda x: math.sqrt(x[0]))
        context.def_function("sin", lambda x: math.sin(x[0]))
        context.def_function("cos", lambda x: math.cos(x[0]))
        context.def_function("exp", lambda x: math.e ** x[0])
        context.def_function("log", lambda x: math.log(x[1],x[0]))
        context.def_function("rand", lambda x: random.random())
        
        for n in node.statements: 
            current = self.visit(n, context)
            if type(n) is TypeDeclarationNode:
                context.def_type(n.idx , current)

            if type(n) is FuncDeclarationNode:
                context.def_function(n.idx, current)

        self.visit(node.expression, context)
    
    #Returbio
    @visitor.when(TypeDeclarationNode)
    def visit(self, node: TypeDeclarationNode, context: Context):
        TypeContext = Context(context)
        
        class NewType:
            def __init__(self, parameters):
                ConsContext=Context(context)

                for i in len(node.params):
                    ConsContext.def_variable(node.params[i].idx, parameters[i])
                
                for a in node.attributes:
                    current = self.visit(a, ConsContext)
                    TypeContext.def_variable(a.idx, current)
                
                for f in node.functions:
                    current = self.visit(f,TypeContext)
                    TypeContext.def_function(f.idx, current)
            
            def callfunc(self, name, parameters):
                return TypeContext.get_function(name,False)(parameters)
            
            def callattr(self, name):
                return TypeContext.get_variable(name)
        
        return NewType
        
    #Returbio 2.0
    @visitor.when(FuncDeclarationNode)
    def visit(self, node: FuncDeclarationNode, context: Context):
        FunctionContext=Context(context)

        def new_function(parameters):
            for i in len(node.params):
                FunctionContext.def_variable(node.params[i][0], parameters[i])

            return self.visit(node.body, FunctionContext)
        
        return new_function
    
    @visitor.when(AttrDeclarationNode)
    def visit(self, node: AttrDeclarationNode, context: Context):
        value = self.visit(node.value, context)

        return value
    
    @visitor.when(AssignNode)
    def visit(self, node: AssignNode, context:Context):
        exp = self.visit(node.expr, context)
        context.def_variable(node.idx, exp)

        return exp

    @visitor.when(DestructiveAssignment)
    def visit(self, node: DestructiveAssignment, context: Context):
        exp = self.visit(node.expr, context)
        context.edit_var_value(node.idx, exp)

        return exp
        
    @visitor.when(FuncCallNode)
    def visit(self, node: FuncCallNode, context: Context):
        params = []

        for par in node.params:
            params.append(self.visit(par, context))

        func = context.get_function(node.obj_called)
        return func(params)

    @visitor.when(AttrCallNode)
    def visit(self, node: AttrCallNode, context: Context):
        type_ = context.get_type(node.idx)
        attr = type_.callattr(node.attr_called)

        return attr

    @visitor.when(LoopNode)
    def visit(self, node: LoopNode, context: Context):
        cond = self.visit(node.condition, context)

        if not cond:
            else_ = self.visit(node.else_body, context)
            return else_
        
        while(cond):
            return_value = self.visit(node.body, context)
            cond = self.visit(node.condition, context)

        return return_value
    
    @visitor.when(ForNode)
    def visit(self, node: ForNode, context: Context):
        iter_ = self.visit(node.iterable, context) 
        
        if len(iter_) == 0:
            else_ = self.visit(node.elsex, context)
            return else_
    
        ForContext=Context(context)
        ForContext.def_variable(node.varidx.lex, None)

        for x in iter_:
            ForContext.edit_variable(node.varidx.lex, x)
            return_value = self.visit(node.body, ForContext)

        return return_value

    @visitor.when(ConditionalNode)
    def visit(self, node: ConditionalNode, context: Context):
        cond = self.visit(node.condition, context)
        then = '\n'.join(self.visit(arg, context) for arg in node.then_body)
        else_ = self.visit(node.else_body, context)

        if(cond):
            return then
        else:
            return else_
    
    @visitor.when(PrintNode)
    def visit(self, node: PrintNode, context: Context):
        expr = self.visit(node.expr, context)

        print(expr)
        return str(expr)

    @visitor.when(ConstantNumNode)
    def visit(self, node: ConstantNumNode, context: Context):
        return node.idx

    @visitor.when(ConstantStringNode)
    def visit(self, node: ConstantStringNode, context: Context):
        return node.value
    
    @visitor.when(ConstantBoolNode)
    def visit(self, node: ConstantBoolNode, context: Context):
        return self.booleans[node.value]

    @visitor.when(VariableNode)
    def visit(self, node: VariableNode, context: Context):
        return node.idx
    
    @visitor.when(VoidNode)
    def visit(self, node: VoidNode, context: Context):
        return

    @visitor.when(RandNode)
    def visit(self, node: RandNode, context: Context):
        return random.random()
    
    @visitor.when(List_Comprehension)
    def visit(self, node: List_Comprehension, context: Context):
        expr_for = self.visit(node.exp_for_idx, context)
        list_ = self.visit(node.expr, context)

        try:
            return [expr_for for node.idx in list_]
        except:
            raise RunTimeException

    @visitor.when(RangeNode)
    def visit(self, node: RangeNode, context: Context):
        left = self.visit(node.left, context)
        right = self.visit(node.right, context)

        try:
            return range(left, right)
        except:
            raise RunTimeException
        
    @visitor.when(IndexationNode)
    def visit(self, node: IndexationNode, context: Context):

        iterable = self.visit(node.obj, context)
        index = self.visit(node.index, context)
        return iterable[index]
    
    @visitor.when(NotNode)
    def visit(self, node: NotNode, context: Context):
        left = self.visit(node.expr, context)
        try:
            expr = self.booleans[left]
            return not expr
        except:
            raise RunTimeException

    @visitor.when(NegNode)
    def visit(self, node: NegNode, context: Context):
        left = self.visit(node.expr, context)
        try:
            return left * -1
        except:
            raise RunTimeException
        
    @visitor.when(SqrtNode)
    def visit(self, node: SqrtNode, context: Context):
        left = self.visit(node.expr, context)
        try:
            return math.sqrt(left)
        except:
            raise RunTimeException

    @visitor.when(CosNode)
    def visit(self, node: CosNode, context: Context):
        left = self.visit(node.expr, context)
        try:
            return math.cos(left)
        except:
            raise RunTimeException

    @visitor.when(SinNode)
    def visit(self, node: SinNode, context: Context):
        left = self.visit(node.expr, context)
        try:
            return math.sin(left)
        except:
            raise RunTimeException

    @visitor.when(ExponEulerNode)
    def visit(self, node: ExponEulerNode, context: Context):
        left = self.visit(node.expr, context)
        try:
            return math.e ** left
        except:
            raise RunTimeException

    @visitor.when(ModNode)
    def visit(self, node: ModNode, context: Context):
        left = self.visit(node.left, context)
        right = self.visit(node.right, context)
        try:
            return left % right
        except:
            raise RunTimeException

    @visitor.when(LogNode)
    def visit(self, node: LogNode, context: Context):
        left = self.visit(node.left, context)
        right = self.visit(node.right, context)
        try:
            return math.log(right, left)
        except:
            raise RunTimeException

    @visitor.when(PlusNode)
    def visit(self, node: PlusNode, context: Context):
        left = self.visit(node.left, context)
        right = self.visit(node.right, context)
        try:
            return left + right
        except:
            raise RunTimeException
        
    @visitor.when(MinusNode)
    def visit(self, node: MinusNode, context: Context):
        left = self.visit(node.left, context)
        right = self.visit(node.right, context)
        try:
            return left - right
        except:
            raise RunTimeException

    @visitor.when(StarNode)
    def visit(self, node: StarNode, context: Context):
        left = self.visit(node.left, context)
        right = self.visit(node.right, context)
        try:
            return left * right
        except:
            raise RunTimeException
        
    @visitor.when(DivNode)
    def visit(self, node: DivNode, context: Context):
        left = self.visit(node.left, context)
        right = self.visit(node.right, context)
        try:
            return left/right
        except:
            raise RunTimeException

    @visitor.when(PowNode)
    def visit(self, node: PowNode, context: Context):
        left = self.visit(node.left, context)
        right = self.visit(node.right, context)
        try:
            return left ** right
        except:
            raise RunTimeException

    @visitor.when(LeqNode)
    def visit(self, node: LeqNode, context: Context):
        left = self.visit(node.left, context)
        right = self.visit(node.right, context)
        try:
            return left <= right
        except:
            raise RunTimeException

    @visitor.when(LessNode)
    def visit(self, node: LessNode, context: Context):
        left = self.visit(node.left, context)
        right = self.visit(node.right, context)
        try:
            return left < right
        except:
            raise RunTimeException
        
    @visitor.when(EqualNode)
    def visit(self, node: EqualNode, context: Context):
        left = self.visit(node.left, context)
        right = self.visit(node.right, context)
        try:
            return left == right
        except:
            raise RunTimeException

    @visitor.when(AndNode)
    def visit(self, node: AndNode, context: Context):
        left = self.visit(node.left, context)
        right = self.visit(node.right, context)
        try:
            left = self.booleans[left.value]
            right = self.booleans[right.value]
            return left and right
        except:
            raise Exception('Boolean Expression expected')

    @visitor.when(OrNode)
    def visit(self, node: OrNode, context: Context):

        left = self.visit(node.left, context)
        right = self.visit(node.right, context)
        try:
            left = self.booleans[left.value]
            right = self.booleans[right.value]
            return left or right
        except:
            raise Exception('Boolean Expression expected')
        
    @visitor.when(IsNode)
    def visit(self, node: IsNode, context: Context):
        left = self.visit(node.left, context)
        right = self.visit(node.right, context)
        try:
            return left is right
        except:
            raise RunTimeException

    @visitor.when(StringExpression)
    def visit(self, node: StringExpression, context: Context):
        left = self.visit(node.left, context)
        right = self.visit(node.right, context)

        return f"{str(left)}" + f"{str(right)}"