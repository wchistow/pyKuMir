import logging
from traceback import format_exc

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QMessageBox

from .main_window import ABOUT, MainWindow


def run(program_version: str):
    logging.info('Запуск приложения...')
    logging.info(ABOUT)

    try:
        app = QApplication([])

        interface = MainWindow(program_version)
        interface.show()

        logging.info('Приложение запущено')

        exit(app.exec())
    except Exception:
        err_msg = ''.join(format_exc())
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
    finally:
        logging.info('Приложение остановлено')
