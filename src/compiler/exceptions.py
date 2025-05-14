class KumirException(Exception): ...


class SyntaxException(KumirException):
    def __init__(self, line: int, token=None, message: str | None = None):
        if message is None:
            message = f'здесь не должно быть "{token}"'
        self.line = line
        self.token = token
        self.args = (message + f' (строка {line})',)


class RuntimeException(KumirException):
    def __init__(self, line: int, message: str):
        self.line = line
        self.args = (message + f' (строка {line})',)
