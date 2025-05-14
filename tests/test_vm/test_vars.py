import importlib
from pathlib import Path
import sys

import pytest

from utils import wrap_code_into_main

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

compiler = importlib.import_module('compiler')
code2bc, RuntimeException, VM = compiler.code2bc, compiler.RuntimeException, compiler.VM


printed_text = ''


def create_vm(bc, algs):
    return VM(bc, output_f=output, algs=algs)


def output(s: str) -> None:
    global printed_text
    printed_text = s


def test_set_one_const():
    bytecode = code2bc('цел а = 5')
    vm = create_vm(*bytecode)
    vm.execute()
    assert vm.glob_vars == {'а': ('цел', 5)}


def test_set_one_var():
    bytecode = code2bc('цел а := 5\nвывод а')
    vm = create_vm(*bytecode)
    vm.execute()
    assert printed_text == '5'


def test_def_and_assign():
    bytecode = code2bc('цел а\nа := 5\nвывод а')
    vm = create_vm(*bytecode)
    vm.execute()
    assert printed_text == '5'


def test_def_two():
    bytecode = code2bc('цел а, б\nа := 5\nб := 10\nвывод а, " ", б')
    vm = create_vm(*bytecode)
    vm.execute()
    assert printed_text == '5 10'


def test_count():
    bytecode = code2bc('цел а := 5 + 6\nвывод а')
    vm = create_vm(*bytecode)
    vm.execute()
    assert printed_text == '11'


def test_count_with_var():
    bytecode = code2bc('цел а := 5\nцел б := а + 1\nвывод б')
    vm = create_vm(*bytecode)
    vm.execute()
    assert printed_text == '6'

# --- тесты ошибок ---

def test_assign_to_not_defined_error():
    bytecode = code2bc(wrap_code_into_main('а := 5'))
    vm = create_vm(*bytecode)
    with pytest.raises(RuntimeException):
        vm.execute()


def test_define_with_wrong_type_error():
    bytecode = code2bc(wrap_code_into_main('цел а := "привет"'))
    vm = create_vm(*bytecode)
    with pytest.raises(RuntimeException):
        vm.execute()


def test_use_without_value_error():
    bytecode = code2bc(wrap_code_into_main('цел а\nцел б := а + 1'))
    vm = create_vm(*bytecode)
    with pytest.raises(RuntimeException):
        vm.execute()


def test_use_without_define_error():
    bytecode = code2bc(wrap_code_into_main('цел б := а + 1'))
    vm = create_vm(*bytecode)
    with pytest.raises(RuntimeException):
        vm.execute()


def test_op_with_different_types_error():
    bytecode = code2bc(wrap_code_into_main('цел а := 1 + "привет"'))
    vm = create_vm(*bytecode)
    with pytest.raises(RuntimeException):
        vm.execute()
