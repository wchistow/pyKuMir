import importlib
from pathlib import Path
import sys

import pytest

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

interpreter = importlib.import_module('interpreter')
Parser, SyntaxException, Value = interpreter.Parser, interpreter.SyntaxException, interpreter.value.Value
ast_classes = interpreter.ast_classes


def test_simple_output():
    code = 'вывод 2'
    parser = Parser(code)
    parsed = parser.parse()
    assert parsed == [ast_classes.Output(0, [[Value('цел', 2)]])]

def test_output_with_expr():
    code = 'вывод 2 + 5'
    parser = Parser(code)
    parsed = parser.parse()
    assert parsed == [ast_classes.Output(0, [[Value('цел', 2), Value('цел', 5), ast_classes.Op(op='+')]])]

def test_output_multiple():
    code = 'вывод 2, 5'
    parser = Parser(code)
    parsed = parser.parse()
    assert parsed == [ast_classes.Output(0, [[Value('цел', 2)], [Value('цел', 5)]])]

def test_too_many_commas_error():
    code = 'вывод 5,,'
    parser = Parser(code)
    with pytest.raises(SyntaxException):
        parser.parse()

def test_empty_output_error():
    parser = Parser('вывод')
    with pytest.raises(SyntaxException):
        parser.parse()
