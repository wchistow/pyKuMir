from datetime import datetime
from locale import getencoding
from platform import python_version, python_implementation, platform

from PyQt6.QtWidgets import (QWidget, QMenuBar, QMenu, QSplitter, QHBoxLayout,
                             QGridLayout, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt, QT_VERSION_STR, PYQT_VERSION_STR

from .codeinput import CodeInput
from .console import Console
from .docview import DocView

from interpreter import code2bc, SyntaxException, RuntimeException, VM

ABOUT = f'''
Версия Python: {python_version()}
Реализация: {python_implementation()}
Платформа: {platform()}
Кодировка: {getencoding()}

Версия Qt: {QT_VERSION_STR}
Версия PyQt: {PYQT_VERSION_STR}
'''


class MainWindow(QWidget):
    def __init__(self, program_version: str, parent=None):
        super().__init__(parent)
        self.ABOUT = f'pyKuMir v{program_version}\n{ABOUT}'

        self.inputted_text = ''

        self.setWindowTitle(f'pyKuMir v{program_version}')
        self.resize(800, 600)

        self.docview = DocView()

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
        self.build_menu()
        self.grid.addLayout(self.buttons, 1, 0, 1, 1)
        self.grid.addWidget(self.code_and_console, 2, 0, 7, 1)

        self.setMinimumSize(600, 500)

        self.setLayout(self.grid)

    def build_menu(self):
        self.menu_bar = QMenuBar(self)

        self.file_menu = QMenu('Программа')
        self.file_menu.addAction('Выход', self.close)
        self.menu_bar.addMenu(self.file_menu)

        self.help_menu = QMenu('Помощь')
        self.help_menu.addAction('Документация', self.docview.show)
        self.help_menu.addAction('О Qt', lambda: QMessageBox.aboutQt(self, 'О Qt'))
        self.help_menu.addAction('О программе', self.show_about)
        self.menu_bar.addMenu(self.help_menu)

        self.grid.addWidget(self.menu_bar, 0, 0, 0, 0)

    def show_about(self):
        QMessageBox.information(self, 'О программе', self.ABOUT,
                                QMessageBox.StandardButton.Ok)

    def _input_from_console(self) -> str:
        # self.console.input_line = self.console.toPlainText().count('\n')
        # self.console.input_completed = False
        # while True:
        #     if self.console.input_completed:
        #         return self.inputted_text
        QMessageBox.warning(self, 'Не поддерживаемая функциональность',
                            'В данный момент ключевое слово "ввод" не поддерживается.',
                            buttons=QMessageBox.StandardButton.Ok)
        return self.inputted_text

    def run_code(self):
        code = self.codeinput.toPlainText()
        self.console.output_sys(f'>> {datetime.now().strftime("%H:%M:%S")} - Новая программа - Начало выполнения\n')
        try:
            bc = code2bc(code)
        except SyntaxException as e:
            print(e.args)
        else:
            vm = VM(bytecode=bc[0],
                    output_f=self.console.output,
                    input_f=self._input_from_console,
                    algs=bc[1])
            try:
                vm.execute()
            except RuntimeException as e:
                print(e.args)
        self.console.output_sys(f'\n>> {datetime.now().strftime("%H:%M:%S")} - Новая программа - Выполнение завершено\n')
