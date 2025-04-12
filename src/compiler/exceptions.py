class SyntaxException(SyntaxError):
    def __init__(self, line: int, token=None, expected=None, message: str | None = None):
        self.args = (line, token, expected, message)

class RuntimeException(SyntaxError):
    def __init__(self, line: int, message: str):
        self.args = (line, message)
