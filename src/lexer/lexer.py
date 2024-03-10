from utils.token import Token
from utils.automata import State
from utils.Builder_ATM import BuilderATM


class Lexer:
    def __init__(self):
        self.eof = "$"
        self.regexs = self._build_regex()
        self.automaton = self._build_automaton()


    def _build_regex(self):
        builderATM = BuilderATM()

        whitespaceATM = builderATM.WhitespaceATM()
        keywordATM = builderATM.KeywordATM()
        numberATM= builderATM.NumberATM()
        varnameATM = builderATM.VarNameATM()
        operatorATM = builderATM.OperatorATM()
        punctuationATM = builderATM.PunctuationATM()
        literalATM = builderATM.LiteralATM()

        regexs = [
            whitespaceATM,
            keywordATM,
            numberATM,
            varnameATM,
            operatorATM,
            punctuationATM,
            literalATM,
        ]

        return regexs


    def _build_automaton(self):
        start = State("start")

        for state in self.regexs:
            start.add_epsilon_transition(state)
        return start.to_deterministic()

    def _walk(self, string):
        state = self.automaton
        final = state if state.final else None
        lex = ""

        for symbol in string:
            if state.has_transition(symbol):
                lex += symbol
                state = state[symbol][0]

                if state.final:
                    final = state
                    final.lex = lex
            else:
                break

        if final:
            return final, final.lex

        return None, lex
    

    def _tokenize(self, text):
        while text:
            final, lex = self._walk(text)
            text = text[len(lex) :]
            if final:
                yield Token(lex, final.tag)

        yield Token("$", self.eof)
        

    def __call__(self, text):
        return [token for token in self._tokenize(text)]
