import importlib
from pathlib import Path
import sys

import pytest

PATH_TO_SRC = Path(__file__).parent.parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

compiler = importlib.import_module('compiler')
Parser, SyntaxException = compiler.Parser, compiler.SyntaxException
ast_classes = compiler.ast_classes


def test_simple_output():
    code = 'вывод 2'
    parser = Parser(code)
    parsed = parser.parse()
    assert parsed == [ast_classes.Output(0, [(2,)])]

def test_output_with_expr():
    code = 'вывод 2 + 5'
    parser = Parser(code)
    parsed = parser.parse()
    assert parsed == [ast_classes.Output(0, [(2, ast_classes.Op(op='+'), 5)])]

def test_output_multiple():
    code = 'вывод 2, 5'
    parser = Parser(code)
    parsed = parser.parse()
    assert parsed == [ast_classes.Output(0, [(2,), (5,)])]

# --- тесты ошибок ---

def test_too_many_commas():
    code = 'вывод 5,,'
    parser = Parser(code)
    with pytest.raises(SyntaxException):
        parser.parse()
