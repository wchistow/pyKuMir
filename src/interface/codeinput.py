from PyQt6.QtWidgets import QTextEdit

from .lexer import highlight_text


class CodeInput(QTextEdit):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    def keyPressEvent(self, event) -> None:
        super().keyPressEvent(event)
        self.highlight_syntax()

    def highlight_syntax(self) -> None:
        cursor = self.textCursor()
        cursor_pos = cursor.position()
        self.setHtml(highlight_text(self.toPlainText()))
        cursor.setPosition(cursor_pos)
        self.setTextCursor(cursor)
