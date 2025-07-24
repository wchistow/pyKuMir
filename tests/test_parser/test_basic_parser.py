import importlib
from pathlib import Path
import sys

import pytest

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

interpreter = importlib.import_module('interpreter')
Parser, SyntaxException, ast_classes, Value = (
    interpreter.Parser,
    interpreter.SyntaxException,
    interpreter.ast_classes,
    interpreter.value.Value,
)


def test_parse_assert():
    parser = Parser('утв да')
    parsed = parser.parse()

    assert parsed == [ast_classes.Assert(0, expr=[Value('лог', 'да')])]


def test_parse_stop():
    parser = Parser('стоп')
    parsed = parser.parse()

    assert parsed == [ast_classes.Stop(0)]


def test_parse_unary_op():
    parser = Parser('вывод не +1 > 0')
    parsed = parser.parse()

    assert parsed == [
        ast_classes.Output(
            lineno=0,
            exprs=[
                [
                    Value(typename='цел', value=1),
                    ast_classes.Op(op='+', unary=True),
                    Value(typename='цел', value=0),
                    ast_classes.Op(op='>', unary=False),
                    ast_classes.Op(op='не', unary=True),
                ]
            ],
        )
    ]


def test_invalid_char_syntax_error():
    parser = Parser('@')
    with pytest.raises(SyntaxException):
        parser.parse()


def test_invalid_char_instead_of_assign():
    parser = Parser('цел а?')
    with pytest.raises(SyntaxException):
        parser.parse()


def test_invalid_char_in_expr_error():
    parser = Parser('цел а := 1 & 2')
    with pytest.raises(SyntaxException):
        parser.parse()
