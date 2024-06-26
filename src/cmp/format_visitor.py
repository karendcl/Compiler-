import src.cmp.visitor as visitor
from src.cmp.ast import *

class FormatVisitor(object):
    @visitor.on('node')
    def visit(self, node, tabs):
        pass

    # @visitor.when(StringExpression)
    # def visit(self, node, tabs=0):
    #     ans = '\t' * tabs + f'\\__StringExpression: [{len(node.expressions)} expressions]'
    #     statements = '\n'.join(self.visit(child, tabs + 1) for child in node.right)
    #     return f'{ans}\n{statements}'

    @visitor.when(MethodDeclaration)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__MethodDeclaration: {node.idx.lex} -> {node.expected_type.lex}'
        params = ''
        for i,k in node.params:
            if not isinstance(i, VoidNode):
                params += f'{i.lex} : {k.lex}\n'
        return f'{ans}\n{params}'

    @visitor.when(AttrDeclarationNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__AttributeDeclaration: {node.idx} : {node.type_expected}'
        # statements = '\n'.join(self.visit(child, tabs + 1) for child in node.value)
        expr = self.visit(node.value, tabs + 1)
        return f'{ans}\n{expr}'

    @visitor.when(ProtocolDeclarationNode)
    def visit(self,node,tabs=0):
        ans = '\t' * tabs + f'\\__ProtocolDeclaration: {node.idx} extends {'None'}'
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
        try:
            args = '\n'.join(self.visit(arg, tabs + 1) for arg, type_ in node.params)
        except:
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
        args = '\n'.join(self.visit(arg, tabs + 1) for arg, type_ in node.params)
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
        params = '\n'.join(self.visit(arg, tabs + 1) for arg, type_ in node.params)
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
        return '\t' * tabs + f'\\__ {node.__class__.__name__}: {node.value}'

    @visitor.when(ConstantStringNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__<expr> {node.__class__.__name__}: {node.value}'
        return ans

    @visitor.when(ComparisonNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__<expr> {node.__class__.__name__} <expr>'
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        return f'{ans}\n{left}\n{right}'

    @visitor.when(VariableNode)
    def visit(self, node, tabs=0):
        return '\t' * tabs + f'\\__ {node.__class__.__name__}: {node.idx}'

    @visitor.when(RandNode)
    def visit(self, node, tabs=0):
        return '\t' * tabs + f'\\__ {node.__class__.__name__}: {node.value}'

    @visitor.when(VoidNode)
    def visit(self, node, tabs=0):
        return '\t' * tabs + f'\\__ {node.__class__.__name__}'

    @visitor.when(ConstantNumNode)
    def visit(self, node, tabs=0):
        return '\t' * tabs + f'\\__ {node.__class__.__name__}: {node.idx}'

    @visitor.when(ConstantBoolNode)
    def visit(self, node, tabs=0):
        return '\t' * tabs + f'\\__ {node.__class__.__name__}: {node.value}'

    @visitor.when(InstantiateNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__InstantiateNode: {node.idx.lex}'
        args = '\n'.join(self.visit(arg, tabs + 1) for arg, type_ in node.params)
        return f'{ans}\n{args}'

    @visitor.when(AndNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__AndNode:'
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        return f'{ans}\n{left}\n{right}'

    @visitor.when(OrNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__OrNode:'
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        return f'{ans}\n{left}\n{right}'

    @visitor.when(NotNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__NotNode:'
        left = self.visit(node.expr, tabs + 1)
        return f'{ans}\n{left}'

    @visitor.when(LessNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__LessNode:'
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        return f'{ans}\n{left}\n{right}'

    @visitor.when(LeqNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__LeqNode:'
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        return f'{ans}\n{left}\n{right}'

    @visitor.when(EqualNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__EqualNode:'
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        return f'{ans}\n{left}\n{right}'

    @visitor.when(IsNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__IsNode:'
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        return f'{ans}\n{left}\n{right}'

    @visitor.when(NegNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__NegNode:'
        left = self.visit(node.expr, tabs + 1)
        return f'{ans}\n{left}'












