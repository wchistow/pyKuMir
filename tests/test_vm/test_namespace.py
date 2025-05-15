import importlib
from pathlib import Path
import sys

import pytest

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

interpreter = importlib.import_module('interpreter')
code2bc, RuntimeException, VM = interpreter.code2bc, interpreter.RuntimeException, interpreter.VM

printed_text = ''


def create_vm(bc, algs):
    return VM(bc, output_f=output, algs=algs)


def output(s: str) -> None:
    global printed_text
    printed_text = s


def test_get_glob_var_from_alg():
    bytecode = code2bc('''
    цел а := 5
    алг
    нач
      вывод а
    кон''')
    vm = create_vm(*bytecode)
    vm.execute()
    assert printed_text == '5'


def test_get_local_var_from_another_alg_error():
    bytecode = code2bc('''
    алг
    нач
      тест1
      тест2
    кон
    
    алг тест1
    нач
      а := 5
    кон
    
    алг тест2
    нач
      вывод а
    кон''')
    vm = create_vm(*bytecode)

    with pytest.raises(RuntimeException):
        vm.execute()


def test_get_local_var_from_local_call_error():
    bytecode = code2bc('''алг
    нач
      цел а
      а := 5
      тест
    кон
    
    алг тест
    нач
      вывод а
    кон''')
    vm = create_vm(*bytecode)

    with pytest.raises(RuntimeException):
        vm.execute()
