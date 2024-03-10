class Token:
    def __init__(self, lex, token_type, value=None):
        self.lex = lex
        self.value = value
        if self.value is None:
            self.value = lex
        self.token_type = token_type

    def __str__(self):
        return f"(Type: {self.token_type} | Lex: '{self.lex}')"

    def __repr__(self):
        return str(self)

    @property
    def is_valid(self):
        return True