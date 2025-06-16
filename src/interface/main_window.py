from threading import Thread
from sys import getdefaultencoding
from platform import python_version, python_implementation, platform

from PyQt6.QtGui import QKeySequence
from PyQt6.QtWidgets import (QWidget, QMenuBar, QMenu, QSplitter, QGridLayout,
                             QMessageBox, QToolBar, QToolButton, QFileDialog)
from PyQt6.QtCore import Qt, QT_VERSION_STR, PYQT_VERSION_STR

from .codeinput import CodeInput
from .console import Console
from .docview import DocView
from .runner import Runner

ABOUT = f'''
Версия Python: {python_version()}
Реализация: {python_implementation()}
Платформа: {platform()}
Кодировка: {getdefaultencoding()}

Версия Qt: {QT_VERSION_STR}
Версия PyQt: {PYQT_VERSION_STR}
'''


class MainWindow(QWidget):
    def __init__(self, program_version: str, parent=None):
        super().__init__(parent)
        self.ABOUT = f'pyKuMir v{program_version}\n{ABOUT}'

        self.cur_file: str | None = None
        self.unsaved_changes = False

        self.update_title()
        self.resize(800, 600)

        self.docview = DocView()

        self.menu_bar = QMenuBar(self)

        self.file_menu = QMenu('Программа')
        self.file_menu.addAction('Новая программа', QKeySequence('Ctrl+N'), self.new_program)
        self.file_menu.addSeparator()
        self.file_menu.addAction('Загрузить', QKeySequence('Ctrl+O'), self.open_file)
        self.file_menu.addSeparator()
        self.file_menu.addAction('Сохранить', QKeySequence('Ctrl+S'), self.save_file)
        self.file_menu.addAction('Сохранить как', self.save_file_as)
        self.file_menu.addSeparator()
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
        self.codeinput.textChanged.connect(self.new_unsaved_changes)
        self.codeinput.textChanged.connect(self.update_title)

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

    def closeEvent(self, event):
        if self.unsaved_changes:
            if self.ask_to_save_or_close('Закрытие текста') == 'reject_close':
                event.ignore()
                return
        if self.runner_thread is not None:
            self.runner_thread.join()
        event.accept()

    def new_unsaved_changes(self):
        self.unsaved_changes = True

    def update_title(self):
        self.setWindowTitle(f'{self.cur_file if self.cur_file is not None else "Новая программа"}'
                            f'{"*" if self.unsaved_changes else ""} - pyKuMir')

    def new_program(self):
        if not self.unsaved_changes:
            self.cur_file = None
            self.codeinput.clear()
            self.unsaved_changes = False
            self.update_title()
        else:
            self.ask_to_save_or_close('Закрытие текста')

    def ask_to_save_or_close(self, title: str):
        ask_window = QMessageBox()
        ask_window.setWindowTitle(title)
        ask_window.setIcon(QMessageBox.Icon.Question)
        ask_window.setText('В этом файле были проведены несохранённые изменения.\n'
                           'При закрытии эти изменения будут потеряны.\nСохранить их?')

        reject_button = ask_window.addButton('Отменить закрытие', QMessageBox.ButtonRole.RejectRole)
        no_save_button = ask_window.addButton('Не сохранять', QMessageBox.ButtonRole.NoRole)
        save_button = ask_window.addButton('Сохранить', QMessageBox.ButtonRole.YesRole)
        ask_window.setDefaultButton(save_button)

        ask_window.exec()

        if ask_window.clickedButton() == save_button:
            self.save_file()
            self.unsaved_changes = False
            self.update_title()
        elif ask_window.clickedButton() == reject_button:
            return 'reject_close'
        elif ask_window.clickedButton() == no_save_button:
            self.cur_file = None
            self.codeinput.clear()
            self.unsaved_changes = False

        self.update_title()

    def open_file(self):
        if self.unsaved_changes:
            self.ask_to_save_or_close('Открытие другого файла')

        new_file = QFileDialog.getOpenFileName(self, 'Загрузить файл', '',
                                               'Файлы КуМир (*.kum);;Все файлы (*)')
        self.cur_file = new_file[0]
        with open(self.cur_file, encoding='utf-8') as f:
            self.codeinput.setPlainText(f.read())
            self.codeinput.highlight_syntax()
            self.unsaved_changes = False

    def save_file(self):
        if self.cur_file is not None:
            with open(self.cur_file, 'w', encoding='utf-8') as f:
                f.write(self.codeinput.toPlainText())
            self.unsaved_changes = False
            self.update_title()
        else:
            self.save_file_as()

    def save_file_as(self):
        new_file = QFileDialog.getSaveFileName(self, 'Сохранить файл', '',
                                               'Файлы КуМир (*.kum);;Все файлы (*)')
        if new_file[0]:
            self.cur_file = new_file[0]
            with open(self.cur_file, 'w', encoding='utf-8') as f:
                f.write(self.codeinput.toPlainText())
            self.unsaved_changes = False
            self.update_title()

    def show_about(self):
        QMessageBox.information(self, 'О программе', self.ABOUT,
                                QMessageBox.StandardButton.Ok)

    def run_code(self):
        if self.runner_thread is not None:
            self.runner_thread.join()

        code = self.codeinput.toPlainText()
        self.runner_thread = Thread(target=self.runner.run, args=(code,))
        self.runner_thread.start()
