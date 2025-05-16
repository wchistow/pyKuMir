import importlib
from pathlib import Path
import sys

import pytest

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

interpreter = importlib.import_module('interpreter')
Parser, SyntaxException, Value = interpreter.Parser, interpreter.SyntaxException, interpreter.value.Value
ast_classes = interpreter.ast_classes


def test_simple_var_def():
    code = 'алг\nнач\n цел а := 2\nкон'
    parser = Parser(code)
    parsed = parser.parse()
    assert parsed == [
        ast_classes.AlgStart(lineno=1, is_main=True, name=''),
        ast_classes.StoreVar(2, 'цел', ['а'], [Value('цел', 2)]),
        ast_classes.AlgEnd(lineno=3)
    ]

def test_var_def_with_expr():
    code = 'алг\nнач\n цел а := 2 + б\nкон'
    parser = Parser(code)
    parsed = parser.parse()
    assert parsed == [
        ast_classes.AlgStart(lineno=1, is_main=True, name=''),
        ast_classes.StoreVar(2, 'цел', ['а'], [Value('цел', 2), ast_classes.Op(op='+'), Value('get-name', 'б')]),
        ast_classes.AlgEnd(lineno=3)
    ]

def test_single_var_declare():
    code = 'цел а'
    parser = Parser(code)
    parsed = parser.parse()
    assert parsed == [ast_classes.StoreVar(0, 'цел', ['а'], None)]

def test_multiple_vars_declare():
    code = 'цел а, б'
    parser = Parser(code)
    parsed = parser.parse()
    assert parsed == [ast_classes.StoreVar(0, 'цел', ['а', 'б'], None)]

def test_const():
    code = 'цел а = 5'
    parser = Parser(code)
    parsed = parser.parse()
    assert parsed == [ast_classes.StoreVar(0, 'цел', ['а'], [Value('цел', 5)])]

# --- тесты ошибок ---

def test_keyword_in_name_error():
    parser = Parser('цел нач := 0')
    with pytest.raises(SyntaxException):
        parser.parse()


def test_two_vars_with_value_error():
    parser = Parser('цел а, б := 2')
    with pytest.raises(SyntaxException):
        parser.parse()


def test_const_expr_error():
    parser = Parser('цел а = 2 + 2')
    with pytest.raises(SyntaxException):
        parser.parse()
