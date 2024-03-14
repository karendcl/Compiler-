from src.parser.parser import LR1Parser, evaluate_reverse_parse
from src.cmp.grammar import Grammar
from src.lexer.lexer import Lexer
from src.lexer.utils.token import Token


def main():
    class Node:
        pass

        def __repr__(self):
            attrs = [f'{attr}={value}' for attr, value in self.__dict__.items()]
            classname = self.__class__.__name__
            return f'{classname}({", ".join(attrs)})'

    class ProgramNode(Node):
        def __init__(self, statements):
            self.statements = statements

    class StatementNode(Node):
        pass

    class ExpressionNode(Node):
        pass

    class VarDeclarationNode(StatementNode):
        def __init__(self, idx, expr):
            self.id = idx
            self.expr = expr

    class FuncDeclarationNode(StatementNode):
        def __init__(self, idx, params, body):
            self.id = idx
            self.params = params
            self.body = body

    class PrintNode(StatementNode):
        def __init__(self, expr):
            self.expr = expr

    class AtomicNode(ExpressionNode):
        def __init__(self, lex):
            self.lex = lex

    class BinaryNode(ExpressionNode):
        def __init__(self, left, right):
            self.left = left
            self.right = right

    class ConstantNumNode(AtomicNode):
        pass

    class VariableNode(AtomicNode):
        pass

    class CallNode(AtomicNode):
        def __init__(self, idx, args):
            AtomicNode.__init__(self, idx)
            self.args = args

    class PlusNode(BinaryNode):
        pass

    class MinusNode(BinaryNode):
        pass

    class StarNode(BinaryNode):
        pass

    class DivNode(BinaryNode):
        pass

    G = Grammar()

    program = G.NonTerminal('<program>', startSymbol=True)
    stat_list, stat = G.NonTerminals('<stat_list> <stat>')
    let_var, def_func, print_stat, arg_list = G.NonTerminals('<let-var> <def-func> <print-stat> <arg-list>')
    expr, term, factor, atom = G.NonTerminals('<expr> <term> <factor> <atom>')
    func_call, expr_list = G.NonTerminals('<func-call> <expr-list>')

    let, defx, printx = G.Terminals('let def print')
    semi, comma, opar, cpar, arrow = G.Terminals('; , ( ) ->')
    equal, plus, minus, star, div = G.Terminals('= + - * /')
    idx, num = G.Terminals('id int')

    program %= stat_list, lambda h, s: ProgramNode(s[1])

    stat_list %= stat + semi, lambda h, s: [s[1]]  # Your code here!!! (add rule)
    stat_list %= stat + semi + stat_list, lambda h, s: [s[1]] + s[3]  # Your code here!!! (add rule)

    stat %= let_var, lambda h, s: s[1]  # Your code here!!! (add rule)
    stat %= def_func, lambda h, s: s[1]  # Your code here!!! (add rule)
    stat %= print_stat, lambda h, s: s[1]  # Your code here!!! (add rule)

    let_var %= let + idx + equal + expr, lambda h, s: VarDeclarationNode(s[2], s[4])  # Your code here!!! (add rule)

    def_func %= defx + idx + opar + arg_list + cpar + arrow + expr, lambda h, s: FuncDeclarationNode(s[2], s[4], s[
        7])  # Your code here!!! (add rule)

    print_stat %= printx + expr, lambda h, s: PrintNode(s[2])

    arg_list %= idx, lambda h, s: [s[1]]  # Your code here!!! (add rule)
    arg_list %= idx + comma + arg_list, lambda h, s: [s[1]] + s[3]  # Your code here!!! (add rule)

    expr %= expr + plus + term, lambda h, s: PlusNode(s[1], s[3])  # Your code here!!! (add rule)
    expr %= expr + minus + term, lambda h, s: MinusNode(s[1], s[3])
    expr %= term, lambda h, s: s[1]

    term %= term + star + factor, lambda h, s: StarNode(s[1], s[3])  # Your code here!!! (add rule)
    term %= term + div + factor, lambda h, s: DivNode(s[1], s[3])  # Your code here!!! (add rule)
    term %= factor, lambda h, s: s[1]  # Your code here!!! (add rule)

    factor %= atom, lambda h, s: s[1]  # Your code here!!! (add rule)
    factor %= opar + expr + cpar, lambda h, s: s[2]  # Your code here!!! (add rule)

    atom %= num, lambda h, s: ConstantNumNode(s[1])  # Your code here!!! (add rule)
    atom %= idx, lambda h, s: VariableNode(s[1])  # Your code here!!! (add rule)
    atom %= func_call, lambda h, s: s[1]  # Your code here!!! (add rule)

    func_call %= idx + opar + expr_list + cpar, lambda h, s: CallNode(s[1], s[3])  # Your code here!!! (add rule)

    expr_list %= expr, lambda h, s: [s[1]]  # Your code here!!! (add rule)
    expr_list %= expr + comma + expr_list, lambda h, s: [s[1]] + s[3]  # Your code here!!! (add rule)

    print(G)

    tokens = [
        Token('print', printx),
        Token('1', num),
        Token('-', minus),
        Token('1', num),
        Token('-', minus),
        Token('1', num),
        Token(';', semi),
        Token('let', let),
        Token('x', idx),
        Token('=', equal),
        Token('58', num),
        Token(';', semi),
        Token('def', defx),
        Token('f', idx),
        Token('(', opar),
        Token('a', idx),
        Token(',', comma),
        Token('b', idx),
        Token(')', cpar),
        Token('->', arrow),
        Token('5', num),
        Token('+', plus),
        Token('6', num),
        Token(';', semi),
        Token('print', printx),
        Token('F', idx),
        Token('(', opar),
        Token('5', num),
        Token('+', plus),
        Token('x', idx),
        Token(',', comma),
        Token('7', num),
        Token('+', plus),
        Token('y', idx),
        Token(')', cpar),
        Token(';', semi),
        Token('$', G.EOF),
    ]

    pars = LR1Parser(G)

    parse, operations = pars([t.token_type for t in tokens], get_shift_reduce=True)

    print(f'output: {parse} \noperations: {operations}')

    ast = evaluate_reverse_parse(parse, operations, tokens)

    print(ast)









if __name__ == "__main__":
    main()

