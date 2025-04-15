from PyQt6.QtWidgets import QTextEdit

CSS = '''<style>
.sys {
    font-style: italic;
    color: grey;
}
</style>'''


class Console(QTextEdit):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.insertHtml(CSS)
        self.setReadOnly(True)
    
    def output_sys(self, text: str) -> None:
        self.insertHtml(f'<span class="sys">{text.replace("\n", "<br />")}</span>')
    
    def output(self, text: str) -> None:
        self.insertHtml(text)
