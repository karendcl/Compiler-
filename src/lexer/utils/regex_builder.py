from src.cmp.automaton import nfa_to_dfa
from src.cmp.automaton_operations import automata_minimization
from src.cmp.utils import Token
from src.Lexer.Utils.format_visitor import FormatVisitor
from src.Lexer.Utils.regex_grammar import G
from src.parser.parser import LR1Parser, evaluate_reverse_parse


class RegexBuilder:

    def __init__(self):
        self.Parser = LR1Parser(G)

    def BuildAtm(self, regex):
        Tokens = []

        for Char in regex:

            token = []
            for i in G.terminals:
                if i.Name == Char:
                    token.append(i)

            if len(token) > 0:
                Tokens.append(token[0])

            else:
                raise Exception(f"Regex Exception: character '{Char}' is not valid")

        Tokens.append(G.EOF)
        Derivations, Operations = self.Parser(Tokens)

        CompleteTokens = []
        for token in Tokens:
            CompleteTokens.append(Token(token.Name, token))

        Ast = evaluate_reverse_parse(Derivations, Operations, CompleteTokens)
        Visitor = FormatVisitor()
        Atm = Visitor.visit(Ast)
        
        FinalAtm = nfa_to_dfa(Atm)
        FinalAtm = automata_minimization(FinalAtm)
        return FinalAtm
