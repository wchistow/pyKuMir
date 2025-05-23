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
