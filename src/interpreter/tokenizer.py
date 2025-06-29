import re
from dataclasses import dataclass
from typing import Iterator

from .constants import TYPES, KEYWORDS

TOKEN_SPECIFICATION = [
    ('COMMENT',       r'\|.*'),
    ('STRING',        r'"[^"\n]*"'),
    ('CHAR',          r"'.'"),
    ('NUMBER',        r'\d+(\.\d*)?'),
    # В Python <= 3.11 символов `\` в f-строках быть не может
    ('TYPE',          r'(\b' + r'\b|\b'.join(TYPES) + r'\b)'),
    ('KEYWORD',       r'(\b' + r'\b|\b'.join(KEYWORDS) + r'\b)'),
    ('OP',            r'(\*\*|\+|\-|\*|/|>=|<=|<>|>|<|\(|\)|\bили\b|\bи\b|\bне\b)'),
    ('TABLE_BRACKET', r'(\[|\])'),
    ('NAME',          r'[A-Za-zА-Яа-я_][A-Za-zА-Яа-я_0-9]*'),
    ('ASSIGN',        r':='),
    ('EQ',            r'='),
    ('COLON',         r':'),
    ('COMMA',         r','),
    ('NEWLINE',       r'[\n;]'),
    ('SKIP',          r'[ \t]+'),
    ('OTHER',         r'.'),
]
TOK_REGEX = '|'.join(f'(?P<{name}>{regex})' for name, regex in TOKEN_SPECIFICATION)


@dataclass
class Token:
    kind: str
    value: str


class Tokenizer:
    def __init__(self, code: str) -> None:
        self.code = code

        self._cur_word = ''
        self._in_word = False

    def tokenize(self) -> Iterator[Token]:
        for mo in re.finditer(TOK_REGEX, self.code):
            kind, value = mo.lastgroup, mo.group()
            if kind == 'NAME' and not self._in_word:
                self._cur_word += value
                self._in_word = True
                continue
            elif kind in ('SKIP', 'NUMBER', 'NAME') and self._in_word:
                self._cur_word += value
                continue
            elif self._in_word:
                yield Token('NAME', self._cur_word.strip())
                self._cur_word = ''
                self._in_word = False

            if kind not in ('SKIP', 'COMMENT'):
                yield Token(kind, value)
