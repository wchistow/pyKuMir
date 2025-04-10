class SyntaxException(SyntaxError):
    def __init__(self, line: int, token, expected):
        self.args = (line, token, expected)
