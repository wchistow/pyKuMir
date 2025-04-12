from pathlib import Path
import sys

from lark import Token
import pytest

PATH_TO_SRC = Path(__file__).parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

from compiler.ast_classes import Op
from compiler.build_bytecode import Bytecode
from compiler.exceptions import SyntaxException, RuntimeException
from compiler.vm import VM, Var

vm = VM()


def setup_function(function):
    vm.reset()


def test_set_one_var():
    # цел а := 5
    bytecode = [Bytecode(start_line=1, command='store', args={'type': 'цел', 'names': ('а',), 'value': (5,)})]
    vm.execute(bytecode)
    assert vm.glob_vars == [Var(typename='цел', name='а', value=5)]


def test_def_and_assign():
    # цел а
    # а := 5
    bytecode = [
                Bytecode(start_line=1, command='store', args={'type': 'цел', 'names': ('а',), 'value': None}),
                Bytecode(start_line=2, command='store', args={'type': None, 'names': ('а',), 'value': (5,)})
            ]
    vm.execute(bytecode)
    assert vm.glob_vars == [Var(typename='цел', name='а', value=5)]


def test_def_one():
    # цел а
    bytecode = [Bytecode(start_line=1, command='store', args={'type': 'цел', 'names': ('а',), 'value': None})]
    vm.execute(bytecode)
    assert vm.glob_vars == [Var(typename='цел', name='а', value=None)]


def test_def_two():
    # цел а, б
    bytecode = [Bytecode(start_line=1, command='store', args={'type': 'цел', 'names': ('а', 'б'), 'value': None})]
    vm.execute(bytecode)
    assert vm.glob_vars == [
                Var(typename='цел', name='а', value=None),
                Var(typename='цел', name='б', value=None)
            ]


def test_count():
    # цел а := 5 + 6
    bytecode = [Bytecode(start_line=1, command='store', args={'type': 'цел', 'names': ('а',), 'value': (5, 6, Op(op='+'))})]
    vm.execute(bytecode)
    assert vm.glob_vars == [Var(typename='цел', name='а', value=5+6)]


def test_count_with_var():
    # цел а := 5
    # цел б := а + 1
    bytecode = [
                Bytecode(start_line=1, command='store', args={'type': 'цел', 'names': ('а',), 'value': (5,)}),
                Bytecode(start_line=2, command='store', args={'type': 'цел', 'names': ('б',), 'value': (Token('NAME', 'а'), 1, Op(op='+'))})
            ]
    vm.execute(bytecode)
    assert vm.glob_vars == [Var(typename='цел', name='а', value=5), Var(typename='цел', name='б', value=5+1)]

# --- тесты ошибок ---

def test_two_vars_with_value_error():
    # цел а, б := 2
    bytecode = [Bytecode(start_line=1, command='store', args={'type': 'цел', 'names': ('а', 'б'), 'value': (2,)})]
    with pytest.raises(SyntaxException):
        vm.execute(bytecode)


def test_assign_to_not_defined_error():
    # а := 5
    bytecode = [Bytecode(start_line=1, command='store', args={'type': None, 'names': ('а',), 'value': (5,)})]
    with pytest.raises(RuntimeException):
        vm.execute(bytecode)


def test_keyword_in_name_error():
    # цел нач := 0
    bytecode = [Bytecode(start_line=1, command='store', args={'type': 'цел', 'names': ('нач',), 'value': (0,)})]
    with pytest.raises(SyntaxException):
        vm.execute(bytecode)


def test_define_with_wrong_type_error():
    # цел а := "привет"
    bytecode = [Bytecode(start_line=1, command='store', args={'type': 'цел', 'names': ('а',), 'value': ("привет",)})]
    with pytest.raises(RuntimeException):
        vm.execute(bytecode)


def test_use_without_value_error():
    # цел а
    # цел б := а + 1
    bytecode = [
                Bytecode(start_line=1, command='store', args={'type': 'цел', 'names': ('а',), 'value': None}),
                Bytecode(start_line=1, command='store', args={'type': 'цел', 'names': ('б',), 'value': (Token('NAME', 'а'), 1, Op(op='+'))})
            ]
    with pytest.raises(RuntimeException):
        vm.execute(bytecode)


def test_use_without_define_error():
    # цел б := а + 1
    bytecode = [Bytecode(start_line=1, command='store', args={'type': 'цел', 'names': ('б',), 'value': (Token('NAME', 'а'), 1, Op(op='+'))})]
    with pytest.raises(RuntimeException):
        vm.execute(bytecode)


def test_op_with_different_types_error():
    # цел а := 1 + "привет"
    bytecode = [Bytecode(start_line=1, command='store', args={'type': 'цел', 'names': ('а',), 'value': (1, "привет", Op(op='+'))})]
    with pytest.raises(RuntimeException):
        vm.execute(bytecode)
