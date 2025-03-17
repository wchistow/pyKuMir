from pathlib import Path
import sys

PATH_TO_SRC = Path(__file__).parent.parent.absolute() / 'src'

sys.path.append(str(PATH_TO_SRC.absolute()))

from compiler.parser import parse, Token
from compiler.exceptions import SyntaxException


def test_comment():
    code = '| Это комментарий'
    assert list(parse(code)) == []


def test_comment_ending():
    code = '| Это комментарий\nкоманда'
    assert list(parse(code)) == [
        Token('NEWLINE', '\n', 0, 17),
        Token('CMD', 'команда', 1, 0)
    ]


def test_number():
    code = '5'
    assert list(parse(code)) == [Token('NUMBER', 5, 0, 0)]


def test_skip():
    code = '\t   \t'
    assert list(parse(code)) == []


def test_char():
    code = "'a'"
    assert list(parse(code)) == [Token('CHAR', 'a', 0, 0)]


def test_string():
    code = '"Это строка"'
    assert list(parse(code)) == [Token('STR', 'Это строка', 0, len(code) - 1)]


def test_string_not_closed():
    code = '"Это строка'
    assert list(parse(code)) == [SyntaxException(0, len(code) - 1, 'а', 'незакрытая кавычка')]


def test_syntax_exception():
    code = '@'
    assert list(parse(code)) == [SyntaxException(0, 0, '@', "неизвестный символ: '@'")]


def test_block_start_and_end():
    code = 'нач кон'
    assert list(parse(code)) == [
        Token('START_BLOCK', 'нач', 0, 0),
        Token('END_BLOCK', 'кон', 0, 4)
    ]


def test_assignment():
    code = ':='
    assert list(parse(code)) == [Token('ASSIGNMENT', ':=', 0, 0)]


def test_assign():
    code = '('
    assert list(parse(code)) == [Token('ASSIGN', '(', 0, 0)]


def test_op():
    code = '+'
    assert list(parse(code)) == [Token('OP', '+', 0, 0)]


def test_cmd():
    code = 'какая_то_команда'
    assert list(parse(code)) == [Token('CMD', 'какая_то_команда', 0, 0)]


def test_keyword():
    code = 'алг'
    assert list(parse(code)) == [Token('KEYWORD', 'алг', 0, 0)]


def test_type():
    code = 'цел'
    assert list(parse(code)) == [Token('TYPE', 'цел', 0, 0)]
