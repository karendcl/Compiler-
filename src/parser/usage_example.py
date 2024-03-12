from src.parser.parser import LR1Parser
from src.cmp.grammar import Grammar
from src.lexer.lexer import Lexer

import pandas

def main():
    lexer = Lexer()
    tokens = lexer.__call__('4 + 3')

    G = Grammar()
    E = G.NonTerminal('E', True)
    T, F = G.NonTerminals('T F')
    plus, mult, lpar, rpar, num = G.Terminals('+ * ( ) num')

    E %= E + plus + T, lambda h, s: s[1] + s[2] + s[3]
    E %= T, lambda h, s: s[1]
    T %= T + mult + F, lambda h, s: s[1] + s[2] + s[3]
    T %= F, lambda h, s: s[1]
    F %= lpar + E + rpar, lambda h, s: s[2]
    F %= num, lambda h, s: s[1]

    parser = LR1Parser(G, True)
    parser.__call__(tokens, True)

    print(parser.action)
    print(parser.goto)






if __name__ == "__main__":
    main()

