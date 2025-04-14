import logging

from PyQt6 import QtWidgets

from .codeinput import CodeInput
from .console import Console

VERSION = '1.0.0a0'


class Interface(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f'pyKuMir v{VERSION}')
        self.resize(800, 600)

        self.menu_bar = QtWidgets.QMenuBar(self)
        self.file_menu = QtWidgets.QMenu('Программа')
        self.file_menu.addAction('Выход', self.close)
        self.menu_bar.addMenu(self.file_menu)

        self.buttons = QtWidgets.QHBoxLayout()
        self.run_button = QtWidgets.QPushButton('запустить')
        self.buttons.addWidget(self.run_button)

        self.codeinput = CodeInput(self)
        self.codeinput.setWhatsThis('ввод кода')

        self.console = Console(self)

        self.grid = QtWidgets.QGridLayout(self)
        self.grid.addWidget(self.menu_bar, 0, 0, 0, 0)
        self.grid.addLayout(self.buttons, 1, 0, 1, 1)
        self.grid.addWidget(self.codeinput, 2, 0, 5, 1)
        self.grid.addWidget(self.console, 7, 0, 2, 1)

        self.setLayout(self.grid)


def run():
    logging.info('Запуск приложения...')

    app = QtWidgets.QApplication([])

    interface = Interface()
    interface.show()

    logging.info('Приложение запущено')

    exit(app.exec())
