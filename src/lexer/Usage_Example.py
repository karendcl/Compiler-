from lexer import Lexer

Text = "123 + 200 = a; print(a)"

lexer = Lexer()
Tokens = lexer.__call__(Text)

for token in Tokens:
    print(token)