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


def test_call_alg():
    bytecode = code2bc('''алг нач
      тест
    кон
    
    алг тест
    нач
      вывод 5
    кон''')
    vm = create_vm(*bytecode)
    vm.execute()
    assert print_mock.printed_text == '5'

def test_call_alg_with_space_in_name():
    bytecode = code2bc('''алг нач
      тест 2
    кон

    алг тест 2
    нач
      вывод 5
    кон''')
    vm = create_vm(*bytecode)
    vm.execute()
    assert print_mock.printed_text == '5'

def test_call_undef_alg_error():
    bytecode = code2bc('алг\nнач\nтест\nкон')
    vm = create_vm(*bytecode)
    with pytest.raises(RuntimeException):
        vm.execute()
