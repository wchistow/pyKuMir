import importlib
from pathlib import Path
import sys

from mocks import PrintMock

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

interpreter = importlib.import_module('interpreter')
code2bc, VM = interpreter.code2bc, interpreter.VM

print_mock = PrintMock()


def create_vm(bc, algs):
    return VM(bc, output_f=print_mock.print, input_f=lambda: None, algs=algs)


def setup_function(func):
    print_mock.printed_text = ''


def test_stop():
    bc = code2bc("""
    вывод 1, нс
    стоп
    вывод 2, нс
    """)
    vm = create_vm(*bc)
    vm.execute()
    assert print_mock.printed_text == '1\nСТОП.'
