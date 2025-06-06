from threading import Thread
from locale import getencoding
from platform import python_version, python_implementation, platform

from PyQt6.QtWidgets import (QWidget, QMenuBar, QMenu, QSplitter, QGridLayout,
                             QMessageBox, QToolBar, QToolButton)
from PyQt6.QtCore import Qt, QT_VERSION_STR, PYQT_VERSION_STR

from .codeinput import CodeInput
from .console import Console
from .docview import DocView
from .runner import Runner

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

        self.setWindowTitle(f'pyKuMir v{program_version}')
        self.resize(800, 600)

        self.docview = DocView()

        self.menu_bar = QMenuBar(self)

        self.file_menu = QMenu('Программа')
        self.file_menu.addAction('Выход', self.close)
        self.menu_bar.addMenu(self.file_menu)

        self.help_menu = QMenu('Помощь')
        self.help_menu.addAction('Документация', self.docview.show)
        self.help_menu.addAction('О Qt', lambda: QMessageBox.aboutQt(self, 'О Qt'))
        self.help_menu.addAction('О программе', self.show_about)
        self.menu_bar.addMenu(self.help_menu)

        self.buttons = QToolBar()
        self.add_tool_buttons()

        self.codeinput = CodeInput(self)
        self.console = Console(self)

        self.code_and_console = QSplitter(Qt.Orientation.Vertical, self)
        self.code_and_console.addWidget(self.codeinput)
        self.code_and_console.addWidget(self.console)

        self.runner = Runner(self.console)
        self.runner_thread: Thread | None = None

        self.grid = QGridLayout(self)
        self.grid.setMenuBar(self.menu_bar)
        self.grid.addWidget(self.buttons, 0, 0, 1, 1)
        self.grid.addWidget(self.code_and_console, 1, 0, 7, 1)

        self.setMinimumSize(600, 500)

        self.setLayout(self.grid)

    def add_tool_buttons(self):
        run_button = QToolButton()
        run_button.setText('запустить')
        run_button.clicked.connect(self.run_code)
        self.buttons.addWidget(run_button)

    def closeEvent(self, a0):
        if self.runner_thread is not None:
            self.runner_thread.join()
        super().closeEvent(a0)

    def show_about(self):
        QMessageBox.information(self, 'О программе', self.ABOUT,
                                QMessageBox.StandardButton.Ok)

    def run_code(self):
        if self.runner_thread is not None:
            self.runner_thread.join()

        code = self.codeinput.toPlainText()
        self.runner_thread = Thread(target=self.runner.run, args=(code,))
        self.runner_thread.start()
