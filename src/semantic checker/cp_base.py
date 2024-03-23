#visitor
from src.cmp.ast import *
import src.cmp.visitor as visitor

class FormatVisitor(object):
    @visitor.on('node')
    def visit(self, node, tabs):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__ProgramNode [<stat>; ... <stat>;]'
        statements = '\n'.join(self.visit(child, tabs + 1) for child in node.statements)
        return f'{ans}\n{statements}'

    @visitor.when(PrintNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__PrintNode <expr>'
        expr = self.visit(node.expr, tabs + 1)
        return f'{ans}\n{expr}'

    @visitor.when(VarDeclarationNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__VarDeclarationNode: let {node.id} = <expr>'
        expr = self.visit(node.expr, tabs + 1)
        return f'{ans}\n{expr}'

    @visitor.when(FuncDeclarationNode)
    def visit(self, node, tabs=0):
        params = ', '.join(node.params)
        ans = '\t' * tabs + f'\\__FuncDeclarationNode: def {node.id}({params}) -> <expr>'
        body = self.visit(node.body, tabs + 1)
        return f'{ans}\n{body}'

    @visitor.when(BinaryNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__<expr> {node.__class__.__name__} <expr>'
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        return f'{ans}\n{left}\n{right}'

    @visitor.when(AtomicNode)
    def visit(self, node, tabs=0):
        return '\t' * tabs + f'\\__ {node.__class__.__name__}: {node.lex}'

    @visitor.when(CallNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__CallNode: {node.lex}(<expr>, ..., <expr>)'
        args = '\n'.join(self.visit(arg, tabs + 1) for arg in node.args)
        return f'{ans}\n{args}'


#Contexto

class VariableInfo:
    def __init__(self, name):
        self.name = name


class FunctionInfo:
    def __init__(self, name, params):
        self.name = name
        self.params = params

class Scope:
    def __init__(self, parent=None):
        self.local_vars = []
        self.local_funcs = []
        self.parent = parent
        self.children = []
        self.var_index_at_parent = 0 if parent is None else len(parent.local_vars)
        self.func_index_at_parent = 0 if parent is None else len(parent.local_funcs)

    def create_child_scope(self):
        child_scope = Scope(self)
        self.children.append(child_scope)
        return child_scope

    def define_variable(self, vname):
        self.local_vars.append(VariableInfo(vname))

    def define_function(self, fname, params):
        self.local_funcs.append(FunctionInfo(fname, params))

    def is_var_defined(self, vname):
        return vname in (v.name for v in self.local_vars)

    def is_func_defined(self, fname, n):
        return any(f.name == fname and len(f.params) == n for f in self.local_funcs)

    def is_local_var(self, vname):
        return self.get_local_variable_info(vname) is not None

    def is_local_func(self, fname, n):
        return self.get_local_function_info(fname, n) is not None

    def get_local_variable_info(self, vname):
        return next((v for v in self.local_vars if v.name == vname), None)

    def get_local_function_info(self, fname, n):
        return next((f for f in self.local_funcs if f.name == fname and len(f.params) == n), None)


#Semantic Checker
class SemanticCheckerVisitor(object):
    def __init__(self):
        self.errors = []

    @visitor.on('node')
    def visit(self, node, scope):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node, scope=None):
        if scope is None:
            scope = Scope()
        for statement in node.statements:
            self.visit(statement, scope)

        return self.errors

    @visitor.when(VarDeclarationNode)
    def visit(self, node, scope):
        if scope.is_var_defined(node.id):
            self.errors.append(f'Variable {node.id} already defined.')
        else:
            scope.define_variable(node.id)
        self.visit(node.expr, scope)

    @visitor.when(FuncDeclarationNode)
    def visit(self, node, scope):
        if scope.is_func_defined(node.id, len(node.params)):
            self.errors.append(f'Function {node.id} is already defined with {len(node.params)} arguments.')
        else:
            scope.define_function(node.id, node.params)
        self.visit(node.body, scope.create_child_scope())

    @visitor.when(PrintNode)
    def visit(self, node, scope):
        self.visit(node.expr, scope)

    @visitor.when(ConstantNumNode)
    def visit(self, node, scope):
        pass

    @visitor.when(VariableNode)
    def visit(self, node, scope):
        if not scope.is_var_defined(node.lex):
            self.errors.append(f'Invalid variable: {node.lex}.')

    @visitor.when(CallNode)
    def visit(self, node, scope):
        if not scope.is_func_defined(node.lex, len(node.args)):
            self.errors.append(f'Function {node.lex} is not defined with {len(node.args)} arguments.')
        for arg in node.args:
            self.visit(arg, scope)

    @visitor.when(BinaryNode)
    def visit(self, node, scope):
        self.visit(node.left, scope)
        self.visit(node.right, scope)


