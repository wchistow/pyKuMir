from threading import Thread

from PyQt6.QtCore import QEvent, Qt, pyqtSignal
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import QTextEdit

CSS = """<style>
.sys {
    font-style: italic;
    color: grey;
}
</style>"""


class Console(QTextEdit):
    output = pyqtSignal(str)
    output_sys = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.insertHtml(CSS)
        self.setReadOnly(True)

        self.input_completed = False
        self.input_text = ''
        self.inputting = False

        self.output.connect(self._output)
        self.output_sys.connect(self._output_sys)

    def keyPressEvent(self, e):
        super().keyPressEvent(e)
        if self.inputting:
            if e.type() == QEvent.Type.KeyPress:
                if e.key() == Qt.Key.Key_Return:
                    self.inputting = False
                    self.input_completed = True
                else:
                    self.input_text += e.text()

    def _cursor_to_end(self) -> None:
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)

    def _output_sys(self, text: str) -> None:
        self._cursor_to_end()
        html_text = text.replace('\n', '<br />')
        self.insertHtml(f'<span class="sys">{html_text}</span>')

    def _output(self, text: str) -> None:
        self._cursor_to_end()
        self.insertHtml(text)

    def _wait_for_input(self):
        while True:
            if self.input_completed:
                break

    def input(self) -> str:
        self.inputting = True
        self.setReadOnly(False)
        wait_for_input_t = Thread(target=self._wait_for_input)
        wait_for_input_t.start()
        wait_for_input_t.join()

        self.input_completed = False
        self.inputting = False
        self.setReadOnly(True)
        input_text = self.input_text
        self.input_text = ''
        return input_text
