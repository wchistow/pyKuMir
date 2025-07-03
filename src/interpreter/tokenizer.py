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
        self._not_word = False

        self.tokens = re.finditer(TOK_REGEX, self.code)
        self.cur_token = None

    def _next_token(self):
        mo = next(self.tokens)
        self.cur_token = mo.lastgroup, mo.group()

    def tokenize(self) -> Iterator[Token]:
        try:
            while True:
                self._next_token()
                if self.cur_token[0] == 'NAME' and not self._in_word:
                    self._cur_word += self.cur_token[1]
                    self._in_word = True
                    continue
                elif self.cur_token[0] in ('SKIP', 'NUMBER', 'NAME') and self._in_word:
                    self._cur_word += self.cur_token[1]
                    continue
                elif self.cur_token[1] == 'не' and self._in_word:
                    self._not_word = True
                    self._next_token()
                    continue
                elif self._in_word:
                    if self._not_word:
                        yield Token('OP', 'не')
                    yield Token('NAME', self._cur_word.strip())
                    self._cur_word = ''
                    self._in_word = False

                if self.cur_token[0] not in ('SKIP', 'COMMENT'):
                    yield Token(self.cur_token[0], self.cur_token[1])
        except StopIteration:
            pass
