from datetime import datetime
import logging
import sys
from traceback import format_exception

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QApplication, QWidget, QMenuBar, QMenu, QSplitter,
                             QHBoxLayout, QGridLayout, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt, QT_VERSION_STR, PYQT_VERSION_STR


def on_error(err_type, err, tb):
    err_msg = ''.join(format_exception(err_type, err, tb))
    logging.critical('\n' + err_msg)

    font = QFont()
    font.setFamily('Monospace')

    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setText(err_msg)
    msg.setWindowTitle('Критическая ошибка в программе')
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.setFont(font)
    msg.exec()
    exit(1)


sys.excepthook = on_error

from .codeinput import CodeInput
from .console import Console
from .docview import DocView

from interpreter import code2bc, SyntaxException, RuntimeException, VM


ABOUT = f'''
Версия Python: {sys.version}
Реализация: {sys.implementation.name}
Платформа: {sys.platform}
Кодировка: {sys.getdefaultencoding()}

Версия Qt: {QT_VERSION_STR}
Версия PyQt: {PYQT_VERSION_STR}
'''


class Interface(QWidget):
    def __init__(self, program_version: str, parent=None):
        super().__init__(parent)
        self.ABOUT = f'pyKuMir v{program_version}\n{ABOUT}'

        self.inputted_text = ''

        self.setWindowTitle(f'pyKuMir v{program_version}')
        self.resize(800, 600)

        self.menu_bar = QMenuBar(self)

        self.docview = DocView()

        self.file_menu = QMenu('Программа')
        self.file_menu.addAction('Выход', self.close)
        self.menu_bar.addMenu(self.file_menu)

        self.help_menu = QMenu('Помощь')
        self.help_menu.addAction('Документация', self.docview.show)
        self.help_menu.addAction('О Qt', lambda: QMessageBox.aboutQt(self, 'О Qt'))
        self.help_menu.addAction('О программе', self.show_about)
        self.menu_bar.addMenu(self.help_menu)

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

    def show_about(self):
        QMessageBox.information(self, 'О программе', self.ABOUT,
                                QMessageBox.StandardButton.Close)

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


def run(program_version: str):
    logging.info('Запуск приложения...')

    app = QApplication([])

    interface = Interface(program_version)
    interface.show()

    logging.info('Приложение запущено')

    exit(app.exec())
