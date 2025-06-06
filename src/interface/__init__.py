import logging
import sys
from traceback import format_exception

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QMessageBox

from src.interface.main_window import ABOUT, MainWindow


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


def run(program_version: str):
    logging.info('Запуск приложения...')
    logging.info(ABOUT)

    app = QApplication([])

    interface = MainWindow(program_version)
    interface.show()

    logging.info('Приложение запущено')

    code = app.exec()
    logging.info('Приложение остановлено')
    exit(code)
