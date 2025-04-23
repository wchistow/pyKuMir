from pathlib import Path
import sys

import pytest

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

from compiler.ast_classes import Output, Op
from compiler import SyntaxException, Parser

parser = Parser()

def setup_function(function):
    parser.reset()


def test_simple_output():
    code = 'вывод 2'
    parsed = parser.parse(code)
    assert parsed == [Output(0, [(2,)])]

def test_output_with_expr():
    code = 'вывод 2 + 5'
    parsed = parser.parse(code)
    assert parsed == [Output(0, [(2, Op(op='+'), 5)])]

def test_output_multiple():
    code = 'вывод 2, 5'
    parsed = parser.parse(code)
    assert parsed == [Output(0, [(2,), (5,)])]

# --- тесты ошибок ---

def test_too_many_commas():
    code = 'вывод 5,,'
    with pytest.raises(SyntaxException):
        parser.parse(code)
