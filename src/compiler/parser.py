from enum import auto, Enum
import re
from typing import Any, Generator, NamedTuple

from .exceptions import _BaseError, SyntaxException

TOKENS = [
        ('START_COMMENT', r'\|'),
        ('NUMBER',        r'\d+(\.\d*)?'),                         # Число
        ('ASSIGNMENT',    r':='),                                  # Присваивание
        ('ASSIGN',        r'[(:=)\(\)"<>:,\.]'),                   # Оператор
        ('START_BLOCK',   r'нач'),                                 # Начало блока
        ('END_BLOCK',     r'кон'),                                 # Конец блока
        ('CMD',           r'[A-Za-zА-Яа-я_][A-Za-zА-Яа-я_0-9]*'),  # Слово
        ('OP',            r'[+\-*/=]+'),                           # Арифметический оператор
        ('NEWLINE',       r'\n'),                                  # Перевод строки
        ('SKIP',          r'[ \t]'),                               # Пробельный символ
        ('OTHER',         r'.'),                                   # Другое
]
KEYWORDS = {'алг', 'арг', 'рез', 'аргрез', 'дано', 'надо', 'пока', 'если'}
TYPES = {'цел', 'вещ', 'сим', 'лит', 'лог'}


class Token(NamedTuple):
    typename: str
    value: Any
    line: int
    column: int


class _State(Enum):
    WAIT = auto()
    COMMENT = auto()
    STRING = auto()


def parse(text: str) -> Generator[Token | _BaseError]:
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in TOKENS)
    line = 0
    column = 0
    line_start = 0  # Начало текущей строки кода (в символах от начала программы)
    cur_string = ''  # Текущая строка (если есть)
    state = _State.WAIT
    for mo in re.finditer(tok_regex, text):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start
        print(kind, value)

        if state == _State.COMMENT:  # Сейчас комментарий
            if not kind == 'NEWLINE':
                continue

        if value == '"':
            if state == _State.STRING:  # Строка закончилась
                state = _State.WAIT
                yield Token('STR', cur_string, line, column)
                cur_string = ''
            else:  # Строка началась
                state = _State.STRING
            continue

        if state == _State.STRING:  # Сейчас строка
            cur_string += value
            continue

        match kind:
            case 'START_COMMENT':
                if state != _State.STRING:  # Символ "|" не находится в строке.
                    state = _State.COMMENT
                else:
                    cur_string += value
                continue
            case 'NEWLINE':
                line += 1
                line_start = mo.end()
                state = _State.WAIT
                continue
            case 'CMD':
                if value in KEYWORDS:
                    kind = 'KEYWORD'
                elif value in TYPES:
                    kind = 'TYPE'
            case 'NUMBER':
                value = float(value) if '.' in value else int(value)
            case 'SKIP':
                continue
            case 'OTHER':
                if state == _State.STRING:
                    cur_string += value
                else:
                    yield SyntaxException(line, column, value, f'неизвестный символ: {value!r}')
                    continue
        yield Token(kind, value, line, column)

    if state == _State.STRING:  # До конца кода продолжается строка.
        yield SyntaxException(line, len(text) - 1, text[-1], 'незакрытая кавычка')
