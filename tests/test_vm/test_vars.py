import importlib
from pathlib import Path
import sys

import pytest

from mocks import PrintMock

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

interpreter = importlib.import_module('interpreter')
code2bc, RuntimeException, VM, Value = interpreter.code2bc, interpreter.RuntimeException, interpreter.VM, interpreter.value.Value


print_mock = PrintMock()


def create_vm(bc, algs):
    return VM(bc, output_f=print_mock.print, input_f=lambda: None, algs=algs)


def setup_function(func) -> None:
    print_mock.printed_text = ''


def test_set_one_const():
    bytecode = code2bc('цел а = 5')
    vm = create_vm(*bytecode)
    vm.execute()
    assert ('а', ('цел', Value('цел', 5))) in vm.glob_vars.items()

def test_set_one_var():
    bytecode = code2bc('цел а := 5\nвывод а')
    vm = create_vm(*bytecode)
    vm.execute()
    assert print_mock.printed_text == '5'

def test_def_and_assign():
    bytecode = code2bc('цел а\nа := 5\nвывод а')
    vm = create_vm(*bytecode)
    vm.execute()
    assert print_mock.printed_text == '5'

def test_def_two():
    bytecode = code2bc('цел а, б\nа := 5\nб := 10\nвывод а, " ", б')
    vm = create_vm(*bytecode)
    vm.execute()
    assert print_mock.printed_text == '5 10'

def test_count():
    bytecode = code2bc('цел а := 5 + 6\nвывод а')
    vm = create_vm(*bytecode)
    vm.execute()
    assert print_mock.printed_text == '11'

def test_count_with_var():
    bytecode = code2bc('цел а := 5\nцел б := а + 1\nвывод б')
    vm = create_vm(*bytecode)
    vm.execute()
    assert print_mock.printed_text == '6'

def test_difficult_expr():
    bytecode = code2bc('цел а := (8 * (4 - 3) + 2) ** 2\nвывод а')
    vm = create_vm(*bytecode)
    vm.execute()
    assert print_mock.printed_text == '100'

def test_divide_result_is_float():
    bytecode = code2bc('вещ а := 4 / 2\nвывод а')
    vm = create_vm(*bytecode)
    vm.execute()
    assert print_mock.printed_text == '2.0'

def test_bool_var():
    bytecode = code2bc("лог а := да\nвывод а")
    vm = create_vm(*bytecode)
    vm.execute()
    assert print_mock.printed_text == 'да'

def test_char_plus_char():
    bytecode = code2bc("лит а := 'а' + 'б'\nвывод а")
    vm = create_vm(*bytecode)
    vm.execute()
    assert print_mock.printed_text == 'аб'

def test_var_with_space_in_name():
    bytecode = code2bc('цел а б := 5\nвывод а б')
    vm = create_vm(*bytecode)
    vm.execute()
    assert print_mock.printed_text == '5'

def test_assign_to_not_defined_error():
    bytecode = code2bc('а := 5')
    vm = create_vm(*bytecode)
    with pytest.raises(RuntimeException):
        vm.execute()

def test_define_with_wrong_type_error():
    bytecode = code2bc('цел а := "привет"')
    vm = create_vm(*bytecode)
    with pytest.raises(RuntimeException):
        vm.execute()

def test_use_without_value_error():
    bytecode = code2bc('цел а\nцел б := а + 1')
    vm = create_vm(*bytecode)
    with pytest.raises(RuntimeException):
        vm.execute()

def test_use_without_define_error():
    bytecode = code2bc('цел б := а + 1')
    vm = create_vm(*bytecode)
    with pytest.raises(RuntimeException):
        vm.execute()

def test_op_with_different_types_error():
    bytecode = code2bc('цел а := 1 + "привет"')
    vm = create_vm(*bytecode)
    with pytest.raises(RuntimeException):
        vm.execute()

def test_use_not_assigned_var_error():
    bytecode = code2bc('цел а\nвывод а')
    vm = create_vm(*bytecode)
    with pytest.raises(RuntimeException):
        vm.execute()
