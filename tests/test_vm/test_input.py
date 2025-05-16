import importlib
from pathlib import Path
import sys

import pytest

from mocks import InputMock, PrintMock

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

interpreter = importlib.import_module('interpreter')
code2bc, RuntimeException, VM = interpreter.code2bc, interpreter.RuntimeException, interpreter.VM

input_mock = InputMock()
print_mock = PrintMock()


def create_vm(bc, algs):
    return VM(bc, output_f=print_mock.print, input_f=input_mock.input, algs=algs)


def setup_function(func):
    input_mock.entered_text = ''
    print_mock.printed_text =''


def test_simple_input():
    input_mock.entered_text = '5'
    bytecode = code2bc('цел а\nввод а\nвывод а')
    vm = create_vm(*bytecode)
    vm.execute()
    assert print_mock.printed_text == '5'


def test_input_string():
    input_mock.entered_text = 'привет, мир!'
    bytecode = code2bc('лит а\nввод а\nвывод а')
    vm = create_vm(*bytecode)
    vm.execute()
    assert print_mock.printed_text == 'привет, мир!'

# тесты ошибок

def test_undef_target_input_error():
    input_mock.entered_text = '5'
    bytecode = code2bc('ввод а\nвывод а')
    vm = create_vm(*bytecode)
    with pytest.raises(RuntimeException):
        vm.execute()


def test_input_string_to_int_error():
    input_mock.entered_text = 'тест'
    bytecode = code2bc('цел а\nввод а\nвывод а')
    vm = create_vm(*bytecode)
    with pytest.raises(RuntimeException):
        vm.execute()


def test_input_string_to_float_error():
    input_mock.entered_text = 'тест'
    bytecode = code2bc('вещ а\nввод а\nвывод а')
    vm = create_vm(*bytecode)
    with pytest.raises(RuntimeException):
        vm.execute()


def test_input_string_to_char_error():
    input_mock.entered_text = 'тест'
    bytecode = code2bc('сим а\nввод а\nвывод а')
    vm = create_vm(*bytecode)
    with pytest.raises(RuntimeException):
        vm.execute()
