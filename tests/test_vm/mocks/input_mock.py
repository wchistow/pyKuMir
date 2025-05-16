class InputMock:
    def __init__(self):
        self.entered_text = ''

    def input(self) -> str:
        return self.entered_text
