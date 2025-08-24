import importlib
from pathlib import Path
import sys

import pytest

from mocks import PrintMock

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

interpreter = importlib.import_module('interpreter')
code2bc, RuntimeException, VM, Value = (
    interpreter.code2bc,
    interpreter.RuntimeException,
    interpreter.VM,
    interpreter.value.Value,
)


print_mock = PrintMock()

def create_vm(bc, algs):
    return VM(bc, output_f=print_mock.print, input_f=lambda: None, algs=algs)


def setup_function(_) -> None:
    print_mock.printed_text = ''


def test_use():
    bytecode = code2bc('''
    использовать Файлы

    алг нач
        вывод существует("nonexists.txt")
    кон
    ''')
    vm = create_vm(*bytecode)
    vm.execute()
    assert print_mock.printed_text == 'нет'


def test_use_non_exists_actor():
    bytecode = code2bc('''
    использовать InvalidActor
    ''')
    vm = create_vm(*bytecode)

    with pytest.raises(RuntimeException):
        vm.execute()
