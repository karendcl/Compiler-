from src.Lexer.Utils.regexs import Regexs
from src.Lexer.lexer import Lexer

lexer = Lexer(Regexs())
Text = "def \n \n \n plus (a, b) \n 50 + 12.3  \"long string def : let print\" let x = 10 \"Hello World\" 0"
tokens = lexer(Text)

for token in tokens:
    print(f"(Lex: {token.lex} | Type: {token.token_type})")