import src.cmp.visitor as visitor
from src.cmp.ast import *

class FormatVisitor(object):
    @visitor.on('node')
    def visit(self, node, tabs):
        pass

    @visitor.when(StringExpression)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__StringExpression: [{len(node.expressions)} expressions]'
        statements = '\n'.join(self.visit(child, tabs + 1) for child in node.expressions)
        return f'{ans}\n{statements}'

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
        return f'{ans}\nFunctions: {functions}\nAttributes: {attrs}'

    @visitor.when(AssignNode)
    def visit(self,node,tabs=0):
        ans = '\t' * tabs + f'\\__Assign: {node.idx}'
        statements = self.visit(node.expr, tabs + 1)
        return f'{ans}\n{statements}'

    @visitor.when(DestructiveAssignment)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__DesAssign: {node.idx} = {node.expr}'
        # statements = '\n'.join(self.visit(child, tabs + 1) for child in node.expressions)
        return f'{ans}'


    @visitor.when(ProgramNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__ProgramNode [{len(node.statements)} statements]'
        statements = '\n'.join(self.visit(child, tabs + 1) for child in node.statements)
        expr = '\n'.join(self.visit(child, tabs + 1) for child in node.expression)
        return f'{ans}\n{statements}\n{expr}'

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
        return f'{ans}\nwhile: {cond}\ndo: {args}'

    @visitor.when(ConditionalNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__ConditionalNode:'
        cond = self.visit(node.condition, tabs + 1)
        then = '\n'.join(self.visit(arg, tabs + 1) for arg in node.then_body)
        else_ = '\n'.join(self.visit(arg, tabs + 1) for arg in node.else_body)
        return f'{ans}\nif: {cond}\ndo: {then}\nelse: {else_}'

    @visitor.when(LetNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__LetNode:'
        ass = '\n'.join(self.visit(arg, tabs + 1) for arg in node.assignments)
        args = '\n'.join(self.visit(arg, tabs + 1) for arg in node.body)
        return f'{ans}\nassignments: {ass}\nin: {args}'

    @visitor.when(UnaryNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__{node.__class__.__name__} <expr>'
        left = self.visit(node.expr, tabs + 1)
        return f'{ans}\n{left}'

    @visitor.when(InstantiateNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__InstantiateNode: {node.idx.lex}'
        args = '\n'.join(self.visit(arg, tabs + 1) for arg in node.params)
        return f'{ans}\nassignments: {args}'

    @visitor.when(ConformsNode)
    def visit(self, node, tabs=0):
        ass = self.visit(node.exp, tabs + 1)
        ans = '\t' * tabs + f'\\__Conforms: {ass} to {node.type_to.lex}'
        return f'{ans}'

    @visitor.when(List_Comprehension)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__ListNode: '
        expr_for = '\n'.join(self.visit(arg, tabs + 1) for arg in node.exp_for_idx)
        list_ = '\n'.join(self.visit(arg, tabs + 1) for arg in node.exp)
        return f'{ans}{expr_for} for {node.idx.lex} in {list_}'

    @visitor.when(ForNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__ForNode: '
        iterable = '\n'.join(self.visit(arg, tabs + 1) for arg in node.iterable)
        body = '\n'.join(self.visit(arg, tabs + 1) for arg in node.body)
        return f'{ans}\nfor {node.idx.lex} in {iterable} : {body}'

    @visitor.when(IndexationNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__IndexationNode: '
        iterable = self.visit(node.obj, tabs+1)
        index = self.visit(node.index, tabs+1)
        return f'{ans}\n iterable: {iterable}\nat: {index}'

    @visitor.when(FuncDeclarationNode)
    def visit(self, node, tabs=0):
        params = '\n'.join(self.visit(arg, tabs + 1) for arg in node.params)
        ans = '\t' * tabs + f'\\__FuncDeclarationNode: def {node.idx})'
        body = self.visit(node.body, tabs + 1)
        return f'{ans}\nparams {params}\nbody: {body}'

    @visitor.when(Param)
    def visit(self,node,tabs=0):
        expr = self.visit(node.expr, tabs+1)
        ans = '\t' * tabs + f'\\__ParamNode: '
        return f'{ans}\nexpr {expr}'

    @visitor.when(BinaryNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__<expr> {node.__class__.__name__} <expr>'
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        return f'{ans}\n{left}\n{right}'

    @visitor.when(AtomicNode)
    def visit(self, node, tabs=0):
        return '\t' * tabs + f'\\__ {node.__class__.__name__}: {node.value}'
