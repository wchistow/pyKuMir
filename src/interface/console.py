from PyQt6.QtWidgets import QTextEdit


class Console(QTextEdit):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setPlainText('Консоль')
        self.setReadOnly(True)
