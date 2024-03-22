from src.cmp.grammar import *

#Change when the Real Grammar is finished
def Regexs():

    return [
        (let, "let"),
        (inx, "in"),
        (ifx, "if"),
        (elsex, "else"),
        (elifx, "elif"),
        (whilex, "while"),
        (forx, "for"),
        (function, "function"),
        (sqrt, "sqrt"),
        (cos, "cos"),
        (sin, "sin"),
        (expon, "expon"),
        (log, "log"),
        (rand, "rand"),
        (typex, "type"),
        (new, "new"),
        (inherits, "inherits"),
        (isx, "is"),
        (asx, "asx"),
        (protocol, "protocol"),
        (extends, "extends"),
        (true, "true"),
        (false, "false"),
        (boolx, "bool"),
        (rangex, "range"),
        (printx, "print"),
        (PI, "PI"),
        (E, "E"),
        (plus, "\+"),
        (minus, "-"),
        (star, "\*"),
        (div, "/"),
        (mod, "%"),
        (pow, "^"),
        (curly_o, "{"),
        (curly_c, "}"),
        (square_o, "\["),
        (square_c, "\]"),
        (opar, "\("),
        (cpar, "\)"),
        (semi_colon, ";"),
        (colon, ":"),
        (comma, ","),
        (dot, "\."),
        (rarrow, "=>"),
        (mut, ":="),
        (equals, "=="),
        (equal, "="),
        (orx, "\|"),
        (given, "\|\|"),
        (leq, "<="),
        (less, "<"),
        (geq, ">="),
        (greater, ">"),
        (neq, "!="),
        (notx, "!"),
        (andx, "&"),
        (concat_space, "@@"),
        (concat, "@"),
        (idx, "([a~z]|[A~Z]|_)([a~z]|[A~Z]|_|[0~9])*"),
        (strx, "\"((\\\\\")|(\°))*\""),
        (num, "([0~9]+\.)?[0~9]+")
    ]