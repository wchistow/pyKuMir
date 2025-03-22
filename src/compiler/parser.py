from enum import auto, Enum
import re
from typing import Any, Generator, NamedTuple

from .exceptions import _BaseError, SyntaxException

TOKENS = [
        ('START_COMMENT', r'\|'),
        ('NUMBER',        r'\d+(\.\d*)?'),                         # Число
        ('ASSIGNMENT',    r':='),                                  # Присваивание
        ('CHAR',          r"'.?'"),                                # Одиночный символ
        ('ASSIGN',        r'[(:=)\(\)"<>:,\.]'),                   # Оператор
        ('START_BLOCK',   r'нач'),                                 # Начало блока
        ('END_BLOCK',     r'кон'),                                 # Конец блока
        ('CMD',           r'[A-Za-zА-Яа-я_][A-Za-zА-Яа-я_0-9]*'),  # Слово
        ('OP',            r'[+\-*/=]+'),                           # Арифметический оператор
        ('NEWLINE',       r'\n'),                                  # Перевод строки
        ('SKIP',          r'[ \t]'),                               # Пробельный символ
        ('OTHER',         r'.'),                                   # Другое
]
KEYWORDS = {'алг', 'арг', 'рез', 'аргрез', 'дано', 'надо', 'пока', 'если', 'то', 'для', 'от', 'до',
            'нц', 'кц', 'ввод', 'вывод', 'да', 'нет', 'использовать'}
TYPES = {'цел', 'вещ', 'сим', 'лит', 'лог', 'таб'}


class Token(NamedTuple):
    typename: str
    value: Any
    line: int
    column: int


class _State(Enum):
    WAIT = auto()
    COMMENT = auto()
    STRING = auto()


class Parser:
    def __init__(self):
        self.line = 0
        self.column = 0
        self.line_start = 0  # Начало текущей строки кода (в символах от начала программы)
        self.cur_string = ''  # Текущая строка (если есть)
        self.state = _State.WAIT
        self.cur_tok_kind = None
        self.cur_tok_value = None
    
    def reset(self):
        self.__init__()

    def parse(self, text: str) -> Generator[Token | _BaseError]:
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in TOKENS)
        for mo in re.finditer(tok_regex, text):
            self.cur_tok_kind = mo.lastgroup
            self.cur_tok_value = mo.group()
            self.column = mo.start() - self.line_start

            if self.state == _State.COMMENT:  # Сейчас комментарий
                if not self.cur_tok_kind == 'NEWLINE':
                    continue

            if self.cur_tok_value == '"':
                if self.state == _State.STRING:  # Строка закончилась
                    self.state = _State.WAIT
                    yield Token('STR', self.cur_string, self.line, self.column)
                    self.cur_string = ''
                else:  # Строка началась
                    self.state = _State.STRING
                continue

            if self.state == _State.STRING:  # Сейчас строка
                self.cur_string += self.cur_tok_value
                continue

            match self.cur_tok_kind:
                case 'START_COMMENT':
                    if self.state != _State.STRING:  # Символ "|" не находится в строке.
                        self.state = _State.COMMENT
                    else:
                        self.cur_string += self.cur_tok_value
                    continue
                case 'NEWLINE':
                    yield Token('NEWLINE', self.cur_tok_value, self.line, self.column)
                    self.line += 1
                    self.line_start = mo.end()
                    self.state = _State.WAIT
                    continue
                case 'CMD':
                    if self.cur_tok_value in KEYWORDS:
                        self.cur_tok_kind = 'KEYWORD'
                    elif self.cur_tok_value in TYPES:
                        self.cur_tok_kind = 'TYPE'
                case 'CHAR':
                    yield Token('CHAR', self.cur_tok_value[1:-1], self.line, self.column)
                    continue
                case 'NUMBER':
                    self.cur_tok_value = float(self.cur_tok_value) if '.' in self.cur_tok_value else int(self.cur_tok_value)
                case 'SKIP':
                    continue
                case 'OTHER':
                    if self.state == _State.STRING:
                        self.cur_string += self.cur_tok_value
                    else:
                        yield SyntaxException(self.line, self.column, self.cur_tok_value,
                                              f'неизвестный символ: {self.cur_tok_value!r}')
                        continue
            yield Token(self.cur_tok_kind, self.cur_tok_value, self.line, self.column)

        if self.state == _State.STRING:  # До конца кода продолжается строка.
            yield SyntaxException(self.line, len(text) - 1, text[-1], 'незакрытая кавычка')
