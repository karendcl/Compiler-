from src.Lexer.Utils.regexs import Regexs
from src.Lexer.lexer import Lexer

lexer = Lexer(Regexs())
Text = "let a = 60 \"Long string : def fnction\" print(sqrt(144)) \"Hello World\""
tokens = lexer(Text)

for token in tokens:
    print(f"(Lex: {token.lex} | Type: {token.token_type})")