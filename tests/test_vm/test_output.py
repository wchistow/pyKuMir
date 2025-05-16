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
    return VM(bc, output_f=print_mock.print, input_f = lambda: None, algs=algs)


def setup_function(func):
    print_mock.printed_text = ''


def test_output_simple_text():
    bytecode = code2bc('вывод "привет"')
    vm = create_vm(*bytecode)
    vm.execute()
    assert print_mock.printed_text == 'привет'


def test_output_expr():
    bytecode = code2bc('вывод 5 + 6')
    vm = create_vm(*bytecode)
    vm.execute()
    assert print_mock.printed_text == '11'


def test_output_with_newline():
    bytecode = code2bc('вывод "привет", нс')
    vm = create_vm(*bytecode)
    vm.execute()
    assert print_mock.printed_text == 'привет\n'


def test_output_many_exprs():
    bytecode = code2bc('вывод "привет", ", мир!"')
    vm = create_vm(*bytecode)
    vm.execute()
    assert print_mock.printed_text == 'привет, мир!'
