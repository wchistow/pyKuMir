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


def test_simple_loop_with_count():
    bc = code2bc('''
    алг нач
        нц 5 раз
            вывод "тест", нс
        кц
    кон
    ''')
    vm = create_vm(*bc)
    vm.execute()

    assert print_mock.printed_text == 'тест\n' * 5

def test_loop_with_count_with_expr():
    bc = code2bc('''
    алг нач
        нц 5+2 раз
            вывод "тест", нс
        кц
    кон
    ''')
    vm = create_vm(*bc)
    vm.execute()

    assert print_mock.printed_text == 'тест\n' * (5 + 2)

def test_loop_with_inner_if():
    bc = code2bc('''
    алг нач
        нц 2 раз
            если да то
                вывод 1
            все
        кц
    кон''')
    vm = create_vm(*bc)
    vm.execute()

    assert print_mock.printed_text == '11'

def test_loop_with_inner_loop():
    bc = code2bc('''
    алг нач
        нц 2 раз
            нц 2 раз
                вывод 1
            кц
        кц
    кон''')
    vm = create_vm(*bc)
    vm.execute()

    assert print_mock.printed_text == '1111'

def test_loop_with_count_expr_not_int_error():
    bc = code2bc('''
    алг нач
        нц "5" раз
            вывод "тест", нс
        кц
    кон
    ''')
    vm = create_vm(*bc)

    with pytest.raises(RuntimeException):
        vm.execute()
