import importlib
from pathlib import Path
import sys

import pytest

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


def test_simple_if():
    bc = code2bc('''
    алг нач
        если да то
            вывод 1
        все
    кон''')
    vm = create_vm(*bc)
    vm.execute()

    assert print_mock.printed_text == '1'

def test_if_with_else():
    bc = code2bc('''
    алг нач
        если 2 < 1 то
            вывод 1
        иначе
            вывод 2
        все
    кон''')
    vm = create_vm(*bc)
    vm.execute()

    assert print_mock.printed_text == '2'

def test_if_with_else_and_code_after():
    bc = code2bc('''
    алг нач
        если 2 < 1 то
            вывод 1
        иначе
            вывод 2
        все
        вывод 0
    кон''')
    vm = create_vm(*bc)
    vm.execute()

    assert print_mock.printed_text == '20'

def test_if_with_inner_if():
    bc = code2bc('''
    алг нач
        если нет то
            вывод 1
        иначе
            если да то
                вывод 2
            все
        все
    кон''')
    vm = create_vm(*bc)
    vm.execute()

    assert print_mock.printed_text == '2'

def test_if_cond_not_bool_error():
    bc = code2bc('''
    алг нач
        если 1 то
            вывод 1
        все
    кон''')
    vm = create_vm(*bc)

    with pytest.raises(RuntimeException):
        vm.execute()
