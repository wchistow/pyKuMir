from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import QEvent, Qt

from .lexer import highlight_text


class CodeInput(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def keyPressEvent(self, event):
        if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Return:
            print(repr(self.toPlainText()))
            cursor = self.textCursor()
            cursor.insertHtml('<br>')
            self.setTextCursor(cursor)
            print(repr(self.toPlainText()))
        else:
            super().keyPressEvent(event)
        self.highlight_syntax()
        event.accept()

    def highlight_syntax(self) -> None:
        cursor = self.textCursor()
        cursor_pos = cursor.position()
        self.setHtml(highlight_text(self.toPlainText()))
        cursor.setPosition(cursor_pos)
        self.setTextCursor(cursor)
