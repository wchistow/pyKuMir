class PrintMock:
    def __init__(self):
        self.printed_text = ''

    def print(self, s: str) -> None:
        self.printed_text = s
