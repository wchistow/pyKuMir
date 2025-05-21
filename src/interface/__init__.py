from datetime import datetime
import logging

from PyQt6.QtWidgets import (QApplication, QWidget,
                             QMenuBar, QMenu, QSplitter,
                             QHBoxLayout, QGridLayout,
                             QPushButton)
from PyQt6.QtCore import Qt

from .codeinput import CodeInput
from .console import Console
from .docview import DocView

from interpreter import code2bc, SyntaxException, RuntimeException, VM


class Interface(QWidget):
    def __init__(self, program_version: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f'pyKuMir v{program_version}')
        self.resize(800, 600)

        self.menu_bar = QMenuBar(self)

        self.docview = DocView()

        self.file_menu = QMenu('Программа')
        self.file_menu.addAction('Выход', self.close)
        self.menu_bar.addMenu(self.file_menu)

        self.buttons = QHBoxLayout()
        self.run_button = QPushButton('запустить')
        self.run_button.clicked.connect(self.run_code)
        self.buttons.addWidget(self.run_button)

        self.codeinput = CodeInput(self)
        self.codeinput.setWhatsThis('ввод кода')

        self.console = Console(self)

        self.code_and_console = QSplitter(Qt.Orientation.Vertical, self)
        self.code_and_console.addWidget(self.codeinput)
        self.code_and_console.addWidget(self.console)

        self.grid = QGridLayout(self)
        self.grid.addWidget(self.menu_bar, 0, 0, 0, 0)
        self.grid.addLayout(self.buttons, 1, 0, 1, 1)
        self.grid.addWidget(self.code_and_console, 2, 0, 7, 1)

        self.setMinimumSize(600, 500)

        self.setLayout(self.grid)

    def run_code(self):
        code = self.codeinput.toPlainText()
        self.console.output_sys(f'>> {datetime.now().strftime("%H:%M:%S")} - Новая программа - Начало выполнения\n')
        try:
            bc = code_to_bytecode(code)
        except SyntaxException as e:
            print(e.args)
        else:
            vm = VM(self.console.output)
            try:
                for inst in bc:
                    vm.execute([inst])
            except RuntimeException as e:
                print(e.args)
        self.console.output_sys(f'\n>> {datetime.now().strftime("%H:%M:%S")} - Новая программа - Выполнение завершено\n')


def run(program_version: str):
    logging.info('Запуск приложения...')

    app = QApplication([])

    interface = Interface(program_version)
    interface.show()

    logging.info('Приложение запущено')

    exit(app.exec())
