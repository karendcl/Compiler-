from .automata import State
from .Keywords import HULK_keywords
import string

UnaryOperators = "+-*/%^"

Punctuation = ",;.{}()[]"

BinaryOperators = {
    "=": ["=", ">"],
    "!": ["="],
    "<": ["="],
    ">": ["="],
    ":": ["="],
    "&": ["&"],
    "@": ["@"],
    "|": ["|"],
    "*": ["*"], 
}

Letters = string.ascii_letters
Digits = string.digits

Digits_and_Letters = Digits + Letters
Digits_Letters_and_Underscore = Digits_and_Letters + "_"
Letters_and_Underscore = Letters + "_"


class BuilderATM:

    @staticmethod
    def WhitespaceATM():
        ws_state = State("Whitespace")
        for ws_char in " \t\n":
            ws_state.add_transition(ws_char, ws_state)
        return ws_state


    @staticmethod
    def KeywordATM(Keywords: dict[str, str] = HULK_keywords):
        Keyword_start = State("Keyword_start")
        for keyword, tag in Keywords.items():
            current_state = Keyword_start
            for char in keyword[:-1]:
                next_state = current_state.transitions.get(char)
                if next_state is None:
                    next_state = State(f"{char}")
                    current_state.add_transition(char, next_state)
                else:
                    next_state = next_state[0]
                current_state = next_state

            final_state = State(f"{keyword}_final", True)
            final_state.tag = tag
            current_state.add_transition(keyword[-1], final_state)

        return Keyword_start


    @staticmethod
    def NumberATM():
        num_state = State("Numb")
        num_int_part = State("IntPart", True)
        num_int_part.tag = "Number"
        num_decimal_part = State("DecimalPart")
        num_decimal_part_final = State("FinalDecimalPart", True)
        num_decimal_part_final.tag = "Number"
        num_exp_part = State("ExpPart")
        num_exp_sign = State("ExpSign")
        num_state_final = State("FinalNumb", True)
        num_state_final.tag = "Number"
        sign_state = State("Sign")

        num_state.add_transition("-", sign_state)
        num_state.add_transition("+", sign_state)
        for i in Digits:
            sign_state.add_transition(i, num_int_part)
            num_state.add_transition(i, num_int_part)
            num_int_part.add_transition(i, num_int_part)

        num_int_part.add_transition("e", num_exp_part)
        num_int_part.add_transition("E", num_exp_part)
        num_int_part.add_transition("e", num_exp_part)
        num_int_part.add_transition("E", num_exp_part)

        num_int_part.add_transition(".", num_decimal_part)

        for digit in Digits:
            num_decimal_part.add_transition(digit, num_decimal_part_final)
            num_decimal_part_final.add_transition(digit, num_decimal_part_final)

        num_decimal_part_final.add_transition("e", num_exp_part)
        num_decimal_part_final.add_transition("E", num_exp_part)
        num_decimal_part_final.add_transition("e", num_exp_part)
        num_decimal_part_final.add_transition("E", num_exp_part)

        num_exp_part.add_transition("+", num_exp_sign)
        num_exp_part.add_transition("-", num_exp_sign)
        for digit in Digits:
            num_exp_sign.add_transition(digit, num_exp_part)
            num_exp_part.add_transition(digit, num_state_final)
            num_state_final.add_transition(digit, num_state_final)

        return num_state


    @staticmethod
    def VarNameATM():
        id_state = State("ID")
        id_state_final = State("FinalID", True)
        id_state_final.tag = "Var Name"
        for i in Letters_and_Underscore:
            id_state.add_transition(i, id_state_final)
        for i in Digits_Letters_and_Underscore:
            id_state_final.add_transition(i, id_state_final)
        return id_state


    @staticmethod
    def OperatorATM():
        optr_state = State("Operator")

        optr_unary_final_states = {
            optr: State(f"Operator_{optr}_final", True) for optr in UnaryOperators
        }

        for optr, state in optr_unary_final_states.items():
            state.tag = "Operator"
            optr_state.add_transition(optr, state)

        optr_binary_final_states = {}
        optr_binary_intermediate_states = {}

        for optr, next_chars in BinaryOperators.items():
            for next_char in next_chars:
                if optr not in optr_binary_intermediate_states:
                    optr_binary_intermediate_states[optr] = State(
                        f"Operator_{optr}_intermediate", True)
                    
                    optr_binary_intermediate_states[optr].tag = "Operator"

                final_state = State(f"Operator_{optr}{next_char}_final", True)
                final_state.tag = "Operator"

                optr_binary_final_states[f"{optr}{next_char}"] = final_state

                optr_state.add_transition(optr, optr_binary_intermediate_states[optr])

                optr_binary_intermediate_states[optr].add_transition(next_char, final_state)

        return optr_state
    

    @staticmethod
    def PunctuationATM(PunctuationSigns=Punctuation):
        punctuation_state = State("Punctuation")
        punctuation_state_final = State("FinalPunctuation", True)
        punctuation_state_final.tag = "Punctuation Sign"
        for sign in PunctuationSigns:
            punctuation_state.add_transition(sign, punctuation_state_final)
        return punctuation_state
    

    @staticmethod
    def LiteralATM():
        literal_start_state = State("LiteralStart")
        literal_content_state = State("LiteralContent")
        literal_escape_state = State("LiteralEscape")
        literal_end_state = State("FinalLiteral", True)
        literal_end_state.tag = "Literal"

        literal_start_state.add_transition('"', literal_content_state)

        for char in (Digits_and_Letters + string.punctuation.replace('"', "") + " "):
            literal_content_state.add_transition(char, literal_content_state)

        literal_content_state.add_transition("\\", literal_escape_state)
        literal_escape_state.add_transition('"', literal_content_state)

        for char in ("\\", '"', "n", "t", "r"):
            literal_escape_state.add_transition(char, literal_content_state)

        literal_content_state.add_transition('"', literal_end_state)

        return literal_start_state