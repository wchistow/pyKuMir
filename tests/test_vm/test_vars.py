from pathlib import Path
import sys

import pytest

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

from compiler import RuntimeException, VM
from compiler.vm import Var

from utils import bc_from_source

vm = VM(output_f=lambda s: ...)


def setup_function(function):
    vm.reset()


def test_set_one_var():
    bytecode = bc_from_source('цел а := 5')
    vm.execute(bytecode)
    assert vm.glob_vars == [Var(typename='цел', name='а', value=5)]


def test_def_and_assign():
    bytecode = bc_from_source('цел а\nа := 5')
    vm.execute(bytecode)
    assert vm.glob_vars == [Var(typename='цел', name='а', value=5)]


def test_def_one():
    bytecode = bc_from_source('цел а')
    vm.execute(bytecode)
    assert vm.glob_vars == [Var(typename='цел', name='а', value=None)]


def test_def_two():
    bytecode = bc_from_source('цел а, б')
    vm.execute(bytecode)
    assert vm.glob_vars == [
                Var(typename='цел', name='а', value=None),
                Var(typename='цел', name='б', value=None)
            ]


def test_count():
    bytecode = bc_from_source('цел а := 5 + 6')
    vm.execute(bytecode)
    assert vm.glob_vars == [Var(typename='цел', name='а', value=5+6)]


def test_count_with_var():
    bytecode = bc_from_source('цел а := 5\nцел б := а + 1')
    vm.execute(bytecode)
    assert vm.glob_vars == [Var(typename='цел', name='а', value=5), Var(typename='цел', name='б', value=5+1)]

# --- тесты ошибок ---

def test_assign_to_not_defined_error():
    bytecode = bc_from_source('а := 5')
    with pytest.raises(RuntimeException):
        vm.execute(bytecode)


def test_define_with_wrong_type_error():
    bytecode = bc_from_source('цел а := "привет"')
    with pytest.raises(RuntimeException):
        vm.execute(bytecode)


def test_use_without_value_error():
    bytecode = bc_from_source('цел а\nцел б := а + 1')
    with pytest.raises(RuntimeException):
        vm.execute(bytecode)


def test_use_without_define_error():
    bytecode = bc_from_source('цел б := а + 1')
    with pytest.raises(RuntimeException):
        vm.execute(bytecode)


def test_op_with_different_types_error():
    bytecode = bc_from_source('цел а := 1 + "привет"')
    with pytest.raises(RuntimeException):
        vm.execute(bytecode)
