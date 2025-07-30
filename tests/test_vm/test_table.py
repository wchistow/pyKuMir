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


def setup_function(_):
    print_mock.printed_text = ''


def test_flat_table():
    bc = code2bc("""
    цел таб а[0:5]
    а[1] := 5
    вывод а[1]
    """)
    vm = create_vm(*bc)
    vm.execute()

    assert print_mock.printed_text == '5'


def test_3d_table():
    bc = code2bc("""
    цел таб а[0:5, 1:6, 2:7]
    а[0, 1, 2] := 5
    вывод а[0, 1, 2]
    """)
    vm = create_vm(*bc)
    vm.execute()

    assert print_mock.printed_text == '5'
