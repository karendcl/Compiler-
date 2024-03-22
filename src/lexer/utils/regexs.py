from src.Lexer.Utils.toy_hulk_grammar import *

#Change when the Real Grammar is finished
def Regexs():

    return [
        (let, "let"),
        (defx, "def"),
        (printx, "print"),
        (plus, "\+"),
        (minus, "-"),
        (star, "\*"),
        (div, "/"),
        (equal, "="),
        (opar, "\("),
        (cpar, "\)"),
        (comma, ","),
        (semi, ";"),
        (arrow, "->"),
        (idx, "([a~z]|[A~Z]|_)([a~z]|[A~Z]|_|[0~9])*"),
        (strx, "\"((\\\\\")|(\°))*\""),
        (num, "([0~9]+\.)?[0~9]+")
    ]