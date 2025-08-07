class KumirException(Exception): ...


class SyntaxException(KumirException):
    def __init__(self, line: int, token=None, message: str | None = None):
        if message is None:
            if token == '\n':
                pretty_token = 'перевода строки'
            else:
                pretty_token = f'"{token}"'
            message = f'здесь не должно быть {pretty_token}'
        self.args = (message, line, token)


class RuntimeException(KumirException):
    def __init__(self, line: int, message: str):
        self.args = (message, line)
