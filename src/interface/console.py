from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import QTextEdit

CSS = '''<style>
.sys {
    font-style: italic;
    color: grey;
}
</style>'''


class Console(QTextEdit):
    # TODO: ввод
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.insertHtml(CSS)
        self.setReadOnly(True)

    def _cursor_to_end(self) -> None:
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)

    def output_sys(self, text: str) -> None:
        self._cursor_to_end()
        self.insertHtml(f'<span class="sys">{text.replace("\n", "<br />")}</span>')
    
    def output(self, text: str) -> None:
        self._cursor_to_end()
        self.insertHtml(text)
