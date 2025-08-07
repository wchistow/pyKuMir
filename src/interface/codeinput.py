from PyQt6.QtWidgets import QTextEdit

from .lexer import highlight_text


class CodeInput(QTextEdit):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setPlainText('алг\nнач\n  \nкон')
        self.highlight_syntax()
        cursor = self.textCursor()
        cursor.setPosition(10)
        self.setTextCursor(cursor)

        self.setTabStopDistance(2 * self.fontMetrics().averageCharWidth())

    def error_on(self, lineno: int, message: str):
        cursor = self.textCursor()

        text = self.toPlainText()

        char_format = self.currentCharFormat()
        char_format.setBackground(0xff0000)
        cursor.movePosition(cursor.MoveOperation.Start)
        line = 0
        for char in text:
            cursor.movePosition(cursor.MoveOperation.Right, cursor.MoveMode.KeepAnchor)
            if char == '\n':
                line += 1
                cursor.movePosition(cursor.MoveOperation.Right)
                continue
            if line == lineno:
                cursor.setCharFormat(char_format)
            cursor.movePosition(cursor.MoveOperation.Right)

    def clear(self):
        self.setPlainText('алг\nнач\n  \nкон')
        self.highlight_syntax()
        cursor = self.textCursor()
        cursor.setPosition(10)
        self.setTextCursor(cursor)

    def keyPressEvent(self, event) -> None:
        super().keyPressEvent(event)
        self.highlight_syntax()

    def highlight_syntax(self) -> None:
        cursor = self.textCursor()
        cursor_pos = cursor.position()
        self.setHtml(highlight_text(self.toPlainText()))
        cursor.setPosition(cursor_pos)
        self.setTextCursor(cursor)
