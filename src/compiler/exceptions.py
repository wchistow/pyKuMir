class SyntaxException(SyntaxError):
    def __init__(self, line: int, token=None, message: str | None = None):
        if message is None:
            message = f'здесь не должно быть "{token}"'
        self.args = (line, token, message)

class RuntimeException(SyntaxError):
    def __init__(self, line: int, message: str):
        self.args = (line, message)
