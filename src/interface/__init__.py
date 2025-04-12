from PyQt6 import QtWidgets

from .codeinput import CodeInput

VERSION = '1.0.0a0'


class Interface(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f'pyKuMir v{VERSION}')
        self.codeinput = CodeInput()
        self.grid = QtWidgets.QVBoxLayout()
        self.grid.addWidget(self.codeinput)
        self.setLayout(self.grid)


def run():
    app = QtWidgets.QApplication([])

    interface = Interface()
    interface.show()

    exit(app.exec())
