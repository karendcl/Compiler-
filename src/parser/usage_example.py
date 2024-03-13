from src.parser.parser import LR1Parser, evaluate_reverse_parse
from src.cmp.grammar import Grammar
from src.lexer.lexer import Lexer
from src.cmp.utils import Token
from src.cmp.ast import PlusNode, MinusNode, StarNode, DivNode, ConstantNumNode

def main():
    G = Grammar()
    E = G.NonTerminal('E', True)
    T, F, X, Y = G.NonTerminals('T F X Y')
    plus, minus, star, div, opar, cpar, num = G.Terminals('+ - * / ( ) num')

    E %= T + X, lambda h, s: s[2], None, lambda h, s: s[1]  #
    X %= plus + T + X, lambda h, s: s[3], None, None, lambda h, s: PlusNode(s[2], h[0])
    X %= minus + T + X, lambda h, s: s[3], None, None, lambda h, s: MinusNode(h[0], s[2])
    X %= G.Epsilon, lambda h, s: h[0]
    T %= F + Y, lambda h, s: s[2], None, lambda h, s: s[1]
    Y %= star + F + Y, lambda h, s: s[3], None, None, lambda h, s: StarNode(h[0], s[2])
    Y %= div + F + Y, lambda h, s: s[3], None, None, lambda h, s: DivNode(h[0], s[2])
    Y %= G.Epsilon, lambda h, s: h[0]
    F %= num, lambda h, s: ConstantNumNode(s[1]), None
    F %= opar + E + cpar, lambda h, s: s[2], None, None, None


    t1 = Token('4',num)
    t2 = Token('+', plus)
    t3 = Token('3',num)
    t4 = Token('$', G.EOF)
    Tokens=[t1,t2,t3, t4]

    pars = LR1Parser(G)

    output,operations = pars(Tokens)

    print(f'output: {output} \noperations: {operations}')









if __name__ == "__main__":
    main()

