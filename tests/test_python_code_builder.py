from pathlib import Path
import sys

PATH_TO_SRC = Path(__file__).parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

from compiler.parser import Parser
from compiler.exceptions import SyntaxException
from compiler.python_builder import TokensToPythonCodeTranslater

parser = Parser()
translater = TokensToPythonCodeTranslater()


def setup_function(function):
    parser.reset()
    translater.reset()


def test_simple_var():
    code = 'цел а := 1'
    expected = 'а: int = 1'
    assert translater.translate(parser.parse(code)) == expected


def test_var_with_expr():
    code = 'цел а := 1+2*(3+4)'
    expected = 'а: int = 1+2*(3+4)'
    assert translater.translate(parser.parse(code)) == expected


def test_assignment_without_var_def():
    code = ':='
    expected = SyntaxException(0, 0, ':=', 'неправильное использование присваивания')
    assert translater.translate(parser.parse(code)) == expected


def test_invalid_type_usage():
    code = 'цел вещ а := 1'
    expected = SyntaxException(0, 4, 'вещ', "неправильное использование ключевого слова 'вещ'")
    assert translater.translate(parser.parse(code)) == expected


def test_invalid_var_def():
    code = 'цел а :='
    expected = SyntaxException(0, 6, ':=', 'неверный синтаксис')
    assert translater.translate(parser.parse(code)) == expected


def test_invalid_var_def_with_newline():
    code = 'цел а :=\n'
    expected = SyntaxException(0, 8, '\n', 'неверный синтаксис')
    assert translater.translate(parser.parse(code)) == expected
