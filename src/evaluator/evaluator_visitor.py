import random

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

    @visitor.when(MethodDeclaration)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__MethodDeclaration: {node.idx}  {node.params} -> {node.expected_type}'
        # statements = '\n'.join(self.visit(child, tabs + 1) for child in node.expressions)
        return f'{ans}'

    @visitor.when(AttrDeclarationNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__AttributeDeclaration: {node.idx} : {node.expected_type} = {node.value}'
        # statements = '\n'.join(self.visit(child, tabs + 1) for child in node.expressions)
        return f'{ans}'

    @visitor.when(ProtocolDeclarationNode)
    def visit(self,node,tabs=0):
        ans = '\t' * tabs + f'\\__ProtocolDeclaration: {node.idx} extends {node.extends}'
        statements = '\n'.join(self.visit(child, tabs + 1) for child in node.methods)
        return f'{ans}\n{statements}'

    @visitor.when(TypeDeclarationNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__TypeDeclaration: {node.idx} inherits {node.inherits}'
        functions = '\n'.join(self.visit(child, tabs + 1) for child in node.functions)
        attrs = '\n'.join(self.visit(child, tabs + 1) for child in node.attributes)
        return f'{ans}\n{functions}\n{attrs}'

    @visitor.when(AssignNode)
    def visit(self,node,tabs=0):
        # ans = '\t' * tabs + f'\\__Assign: {node.idx}'
        statements = self.visit(node.expr, tabs + 1)


    @visitor.when(DestructiveAssignment)
    def visit(self, node, tabs=0):
        # ans = '\t' * tabs + f'\\__DesAssign: {node.idx} = {node.expr}'
        statements = '\n'.join(self.visit(child, tabs + 1) for child in node.expr)



    @visitor.when(ProgramNode)
    def visit(self, node, tabs=0):
        statements = '\n'.join(self.visit(child, tabs + 1) for child in node.statements)
        expr = '\n'.join(str(self.visit(child, tabs + 1)) for child in node.expression)
        return f'{statements}\n{expr}'

    @visitor.when(FuncCallNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__FuncCallNode:'
        args = '\n'.join(self.visit(arg, tabs + 1) for arg in node.params)
        return f'{ans}\n{args}'

    @visitor.when(AttrCallNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__AttrCallNode: {node.idx}.{node.attr_called}'
        # args = '\n'.join(self.visit(arg, tabs + 1) for arg in node.params)
        return f'{ans}'

    @visitor.when(PrintNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__PrintNode <expr>'
        expr = self.visit(node.expr, tabs + 1)
        return f'{ans}\n{expr}'

    @visitor.when(BlockNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__BlockNode:'
        args = '\n'.join(self.visit(arg, tabs + 1) for arg in node.expr_list)
        return f'{ans}\n{args}'

    @visitor.when(LoopNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__LoopNode:'
        cond = self.visit(node.condition, tabs+1)
        args = '\n'.join(self.visit(arg, tabs + 1) for arg in node.body)
        return f'{ans}\n{cond}\n{args}'

    @visitor.when(ConditionalNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__ConditionalNode:'
        cond = self.visit(node.condition, tabs + 1)
        then = '\n'.join(self.visit(arg, tabs + 1) for arg in node.then_body)
        else_ = self.visit(node.else_body, tabs+1)
        return f'{ans}\n{cond}\n{then}\n{else_}'

    @visitor.when(LetNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__LetNode:'
        ass = '\n'.join(self.visit(arg, tabs + 1) for arg in node.assignments)
        args = '\n'.join(self.visit(arg, tabs + 1) for arg in node.body)
        return f'{ans}\n{ass}\n{args}'

    @visitor.when(UnaryNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__{node.__class__.__name__} <expr>'
        left = self.visit(node.expr, tabs + 1)
        return f'{ans}\n{left}'

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

    @visitor.when(List_Comprehension)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__ListNode: '
        expr_for = '\n'.join(self.visit(arg, tabs + 1) for arg in node.exp_for_idx)
        list_ = self.visit(node.expr, tabs + 1)
        return f'{ans}\n{expr_for}\n{node.idx.lex}\n{list_}'

    @visitor.when(ForNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__ForNode: '
        iterable = self.visit(node.iterable, tabs+1)
        body = '\n'.join(self.visit(arg, tabs + 1) for arg in node.body)
        elsex = self.visit(node.elsex, tabs+1)
        return f'{ans}\n{'\t' * (tabs+1)}{node.varidx.lex}\n{iterable}\n{body}\n{elsex}'

    @visitor.when(IndexationNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__IndexationNode: '
        iterable = self.visit(node.obj, tabs+1)
        index = self.visit(node.index, tabs+1)
        return f'{ans}\n{iterable}\n{index}'

    @visitor.when(FuncDeclarationNode)
    def visit(self, node, tabs=0):
        params = '\n'.join(self.visit(arg, tabs + 1) for arg in node.params)
        ans = '\t' * tabs + f'\\__FuncDeclarationNode: def {node.idx})'
        body = self.visit(node.body, tabs + 1)
        return f'{ans}\n{params}\n{body}'


    @visitor.when(BinaryNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__<expr> {node.__class__.__name__} <expr>'
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        return f'{ans}\n{left}\n{right}'

    @visitor.when(StringExpression)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__<expr> {node.__class__.__name__} <expr>'
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        return f'{ans}\n{left}\n{right}'

    @visitor.when(AtomicNode)
    def visit(self, node, tabs=0):
        return node.value

    @visitor.when(ConstantStringNode)
    def visit(self, node, tabs=0):
        return node.value

    @visitor.when(VariableNode)
    def visit(self, node, tabs=0):
        return node.idx

    @visitor.when(RandNode)
    def visit(self, node, tabs=0):
        return random.random()


    @visitor.when(VoidNode)
    def visit(self, node, tabs=0):
        return

    @visitor.when(ConstantNumNode)
    def visit(self, node, tabs=0):
        return node.idx

    @visitor.when(ConstantBoolNode)
    def visit(self, node, tabs=0):
        return self.booleans[node.value]

    @visitor.when(InstantiateNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__InstantiateNode: {node.idx.lex}'
        args = '\n'.join(self.visit(arg, tabs + 1) for arg in node.params)
        return f'{ans}\n{args}'

    @visitor.when(AndNode)
    def visit(self, node, tabs=0):
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        try:
            left = self.booleans[left.value]
            right = self.booleans[right.value]
            return left and right
        except:
            raise Exception('Boolean Expression expected')


    @visitor.when(OrNode)
    def visit(self, node, tabs=0):

        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        try:
            left = self.booleans[left.value]
            right = self.booleans[right.value]
            return left or right
        except:
            raise Exception('Boolean Expression expected')


    @visitor.when(NotNode)
    def visit(self, node, tabs=0):
        left = self.visit(node.expr, tabs + 1)
        try:
            expr = self.booleans[left]
            return not expr
        except:
            raise RunTimeException

    @visitor.when(LessNode)
    def visit(self, node, tabs=0):
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        try:
            return left < right
        except:
            raise RunTimeException

    @visitor.when(LeqNode)
    def visit(self, node, tabs=0):
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        try:
            return left <= right
        except:
            raise RunTimeException

    @visitor.when(StarNode)
    def visit(self, node, tabs=0):
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        try:
            return left * right
        except:
            raise RunTimeException
    @visitor.when(PlusNode)
    def visit(self, node, tabs=0):
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        try:
            return left + right
        except:
            raise RunTimeException

    @visitor.when(EqualNode)
    #DONE
    def visit(self, node, tabs=0):
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        try:
            return left == right
        except:
            raise RunTimeException

    @visitor.when(IsNode)
    #DONE
    def visit(self, node, tabs=0):
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        try:
            return left is right
        except:
            raise RunTimeException

    @visitor.when(NegNode)
    #DONE
    def visit(self, node, tabs=0):
        left = self.visit(node.expr, tabs + 1)
        try:
            return left * -1
        except:
            raise RunTimeException

