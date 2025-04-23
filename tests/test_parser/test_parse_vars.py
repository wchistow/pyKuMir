from pathlib import Path
import sys

import pytest

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

from compiler.ast_classes import StoreVar, Op
from compiler import SyntaxException, Parser

parser = Parser()

def setup_function(function):
    parser.reset()


def test_simple_var_def():
    code = 'цел а := 2'
    parsed = parser.parse(code)
    assert parsed == [StoreVar(0, 'цел', ('а',), (2,))]

def test_var_def_with_expr():
    code = 'цел а := 2 + б'
    parsed = parser.parse(code)
    assert parsed == [StoreVar(0, 'цел', ('а',), (2, Op(op='+'), 'б'))]

def test_single_var_declare():
    code = 'цел а'
    parsed = parser.parse(code)
    assert parsed == [StoreVar(0, 'цел', ('а',), None)]

def test_multiple_vars_declare():
    code = 'цел а, б'
    parsed = parser.parse(code)
    assert parsed == [StoreVar(0, 'цел', ('а', 'б'), None)]

def test_const():
    code = 'цел а = 5'
    parsed = parser.parse(code)
    assert parsed == [StoreVar(0, 'цел', ('а',), (5,))]

# --- тесты ошибок ---

def test_keyword_in_name_error():
    with pytest.raises(SyntaxException):
        parser.parse('цел нач := 0')


def test_two_vars_with_value_error():
    with pytest.raises(SyntaxException):
        parser.parse('цел а, б := 2')
