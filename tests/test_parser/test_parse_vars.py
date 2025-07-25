import importlib
from pathlib import Path
import sys

import pytest

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

interpreter = importlib.import_module('interpreter')
Parser, SyntaxException, Value = (
    interpreter.Parser,
    interpreter.SyntaxException,
    interpreter.value.Value,
)
ast_classes = interpreter.ast_classes


def test_simple_var_def():
    code = 'цел а := 2'
    parser = Parser(code)
    parsed = parser.parse()
    assert parsed == [ast_classes.StoreVar(0, 'цел', ['а'], [Value('цел', 2)])]


def test_float_number():
    code = 'вещ а := 2.5'
    parser = Parser(code)
    parsed = parser.parse()
    assert parsed == [
        ast_classes.StoreVar(0, 'вещ', ['а'], [Value('вещ', 2.5)]),
    ]


def test_var_def_with_expr():
    code = 'цел а := 2 + б'
    parser = Parser(code)
    parsed = parser.parse()
    assert parsed == [
        ast_classes.StoreVar(
            0,
            'цел',
            ['а'],
            [Value('цел', 2), Value('get-name', 'б'), ast_classes.Op(op='+')],
        )
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


def test_var_with_space_in_name():
    code = 'цел а б := 5'
    parser = Parser(code)
    parsed = parser.parse()
    assert parsed == [ast_classes.StoreVar(0, 'цел', ['а б'], [Value('цел', 5)])]


def test_parse_slice():
    code = 'вывод а[2:5]'
    parser = Parser(code)
    parsed = parser.parse()
    assert parsed == [
        ast_classes.Output(
            lineno=0,
            exprs=[
                [
                    ast_classes.Slice(
                        lineno=1,
                        name='а',
                        indexes=[
                            [Value(typename='цел', value=2)],
                            [Value(typename='цел', value=5)],
                        ],
                    )
                ]
            ],
        )
    ]


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


def test_two_ops_in_expr_error():
    parser = Parser('цел а = 2 + * 2')
    with pytest.raises(SyntaxException):
        parser.parse()


def test_two_vals_in_expr_error():
    parser = Parser('цел а = 2 + f 2')
    with pytest.raises(SyntaxException):
        parser.parse()
