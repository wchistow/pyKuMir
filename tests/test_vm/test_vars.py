from pathlib import Path
import sys

import pytest

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

from compiler import RuntimeException, VM

from utils import bc_from_source, wrap_code_into_main


def create_vm(bc, algs):
    return VM(bc, output_f=lambda: None, algs=algs)


@pytest.mark.skip('cannot check local vars')
def test_set_one_var():
    bytecode = bc_from_source(wrap_code_into_main('цел а := 5'))
    vm = create_vm(*bytecode)
    vm.execute()
    assert vm.glob_vars == []


@pytest.mark.skip('cannot check local vars')
def test_def_and_assign():
    bytecode = bc_from_source(wrap_code_into_main('цел а\nа := 5'))
    vm = create_vm(*bytecode)
    vm.execute()
    assert vm.glob_vars == []


@pytest.mark.skip('cannot check local vars')
def test_def_one():
    bytecode = bc_from_source('цел а')
    vm = create_vm(*bytecode)
    vm.execute()
    assert vm.glob_vars == []


@pytest.mark.skip('cannot check local vars')
def test_def_two():
    bytecode = bc_from_source('цел а, б')
    vm = create_vm(*bytecode)
    vm.execute()
    assert vm.glob_vars == []


@pytest.mark.skip('cannot check local vars')
def test_count():
    bytecode = bc_from_source(wrap_code_into_main('цел а := 5 + 6'))
    vm = create_vm(*bytecode)
    vm.execute()
    assert vm.glob_vars == []


@pytest.mark.skip('cannot check local vars')
def test_count_with_var():
    bytecode = bc_from_source(wrap_code_into_main('цел а := 5\nцел б := а + 1'))
    vm = create_vm(*bytecode)
    vm.execute()
    assert vm.glob_vars == []

# --- тесты ошибок ---

def test_assign_to_not_defined_error():
    bytecode = bc_from_source(wrap_code_into_main('а := 5'))
    vm = create_vm(*bytecode)
    with pytest.raises(RuntimeException):
        vm.execute()


def test_define_with_wrong_type_error():
    bytecode = bc_from_source(wrap_code_into_main('цел а := "привет"'))
    vm = create_vm(*bytecode)
    with pytest.raises(RuntimeException):
        vm.execute()


def test_use_without_value_error():
    bytecode = bc_from_source(wrap_code_into_main('цел а\nцел б := а + 1'))
    vm = create_vm(*bytecode)
    with pytest.raises(RuntimeException):
        vm.execute()


def test_use_without_define_error():
    bytecode = bc_from_source(wrap_code_into_main('цел б := а + 1'))
    vm = create_vm(*bytecode)
    with pytest.raises(RuntimeException):
        vm.execute()


def test_op_with_different_types_error():
    bytecode = bc_from_source(wrap_code_into_main('цел а := 1 + "привет"'))
    vm = create_vm(*bytecode)
    with pytest.raises(RuntimeException):
        vm.execute()
