from src.lexer.utils.regex_builder import RegexBuilder
from src.cmp.grammar import G
from src.lexer.utils.custom_state import State
from src.cmp.utils import Token


class Lexer:
    def __init__(self, table):

        self.regexs = self._build_regexs(table)
        self.automaton = self._build_automaton()

    def _build_regexs(self, table):
        regexs = []
        regex_builder = RegexBuilder()
        for n, (token_type, regex) in enumerate(table):

            RegexAtm = regex_builder.BuildAtm(regex)
            Atm, AtmStates = State.from_nfa(RegexAtm, get_states=True)

            for state in AtmStates:
                if state.final:
                    state.tag = token_type
                else:
                    state.tag = None

            regexs.append(Atm)

        return regexs

    def _build_automaton(self):
        start = State('start')

        for Atm in self.regexs:
            start.add_epsilon_transition(Atm)

        return start.to_deterministic()

    def _walk(self, string):
        state = self.automaton
        final = state if state.final else None
        Final_lex = ""

        for symbol in string:
            if state.has_transition(symbol):
                Final_lex += symbol
                state = state[symbol][0]

                if state.final:
                    final = state
                    final.lex = Final_lex

            else:
                break

        if final:
            return final, final.lex

    def IgnoreSpaceChars(self, lex, text):
        Index = len(lex)
        for i, symbol in enumerate(text):
            if i < Index:
                continue

            if symbol == "\n" or symbol == " ":
                Index += 1

            else:
                break

        return text[Index:]


    def _tokenize(self, text):
        text = self.IgnoreSpaceChars("", text)

        while text:

            try:
                final, TokenLex = self._walk(text)
            except TypeError:
                raise Exception(f"Lexer Exception: Token '{text[0]}' is not valid")

            text = self.IgnoreSpaceChars(TokenLex, text)
            if final:
                yield Token(TokenLex, final.tag)

        yield Token('$', G.EOF)


    def __call__(self, text):
        return [token for token in self._tokenize(text)]