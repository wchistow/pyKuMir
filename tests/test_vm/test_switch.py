import importlib
from pathlib import Path
import sys

from mocks import PrintMock

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

interpreter = importlib.import_module('interpreter')
code2bc, RuntimeException, VM = interpreter.code2bc, interpreter.RuntimeException, interpreter.VM

print_mock = PrintMock()


def create_vm(bc, algs):
    return VM(bc, output_f=print_mock.print, input_f=lambda: '', algs=algs)


def setup_function(func) -> None:
    print_mock.printed_text = ''


def test_switch():
    bc = code2bc('''
    алг нач
        цел а := 1
        выбор
            при а = 0: вывод 0
            при а = 1: вывод 1
            при а = 2: вывод 2
            иначе: вывод "что-то другое"
        все
    кон
    ''')
    vm = create_vm(*bc)
    vm.execute()

    assert print_mock.printed_text == '1'
