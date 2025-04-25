class SyntaxException(SyntaxError):
    def __init__(self, line: int, token=None, message: str | None = None):
        self.args = (line, token, message)

class RuntimeException(SyntaxError):
    def __init__(self, line: int, message: str):
        self.args = (line, message)
