from enum import auto, Enum
from dataclasses import dataclass
import re
from typing import Iterable

from .ast_classes import AlgStart, AlgEnd, Statement, StoreVar, Op, Output
from .constants import KEYWORDS, TYPES, ValueType
from .exceptions import SyntaxException

token_specification = [
            ('COMMENT',       r'\|.*'),
            ('STRING',        r'"[^".]*"'),
            ('NUMBER',        r'\d+(\.\d*)?'),
            ('TYPE',          rf'({"|".join(TYPES)})'),
            ('NAME',           r'[A-Za-zА-Яа-я_][A-Za-zА-Яа-я_0-9]*'),
            ('ASSIGN',        r':='),
            ('EQ',            r'='),
            ('OP',            r'(\+|\-|\*|/|\*\*|>=|<=|<>|\(|\))'),
            ('COMMA',         r','),
            ('NEWLINE',       r'\n'),
            ('SKIP',          r'[ \t]'),
            ('OTHER',         r'.'),
]
TOK_REGEX = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)


@dataclass
class Token:
    kind: str
    value: str


class Env(Enum):
    """Окружение, в котором мы сейчас находимся."""
    INTRODUCTION = auto()
    MAIN = auto()
    ALG_HEADER = auto()


class Parser:
    def __init__(self, code: str, debug: bool = False) -> None:
        self.debug = debug

        self.envs = [Env.INTRODUCTION]
        self.cur_expr: list[ValueType | Op] = []
        self.line = 0
        self.cur_cls: Statement | None = None
        self.res: list[Statement] = []

        # на будущее, для других алгоритмов
        self._was_alg = False

        self.tokens = re.finditer(TOK_REGEX, code+'\n')

    def reset(self) -> None:
        self.envs.clear()
        self.cur_expr.clear()
        self.line = 0
        self.cur_cls = None
        self.res.clear()

        self._was_alg = False

    def _next_token(self) -> None:
        mo = next(self.tokens)
        self.cur_token = Token(mo.lastgroup, mo.group())
        if self.cur_token.kind == 'SKIP':
            self._next_token()
        elif self.cur_token.kind == 'NEWLINE':
            self.line += 1

        if self.debug:
            print(f'{self.line} {self.cur_token.kind:10} {self.cur_token.value!r}')

    def parse(self) -> list[Statement]:
        try:
            self._parse()
        except StopIteration:
            if self.envs and self.envs[-1] == Env.MAIN:
                raise SyntaxException(self.line, '\n', 'нет "кон" после "нач"') from None
            if self.debug:
                print('-' * 40)

        return self.res

    def _parse(self) -> None:
        while True:
            self._next_token()

            if self.envs:
                if self.envs[-1] == Env.INTRODUCTION:
                    if self.cur_token.value == 'алг':  # введение закончилось
                        self.envs.pop()
                        self.envs.append(Env.MAIN)

                        self._handle_alg_header(is_main=True)

                        self._was_alg = True
                        continue
                elif self.envs[-1] == Env.MAIN:
                    if self.cur_token.value == 'кон':
                        self.res.append(AlgEnd())
                        self.envs.pop()
                        continue

            self._handle_statement()

    def _handle_alg_header(self, is_main: bool):
        alg_name = []

        self._next_token()
        if self.cur_token.kind == 'NAME':
            if self.cur_token.value == 'нач':
                self.res.append(AlgStart(is_main=is_main, name=''))
                return
            alg_name.append(self.cur_token.value)
        elif self.cur_token.kind != 'NEWLINE':
            raise SyntaxException(self.line, self.cur_token.value)
        self._next_token()
        while (self.cur_token.kind in ('NAME', 'NUMBER', 'TYPE')
                    and self.cur_token.value != 'нач'):
            if self.cur_token.kind == 'NAME':
                alg_name.append(self.cur_token.value)
            self._next_token()
        if self.cur_token.value != 'нач':
            raise SyntaxException(self.line, self.cur_token.value, 'после "алг" нет "нач"')

        self.res.append(AlgStart(is_main=is_main, name=' '.join(alg_name)))

    def _handle_statement(self) -> None:
        if self.cur_token.kind == 'TYPE':  # объвление переменной(ых)
            self._handle_var_def()
        elif self.cur_token.kind == 'NAME' and self.cur_token.value == 'вывод':
            self._handle_output()
        elif self.cur_token.kind == 'NAME':  # присваивание
            name = self.cur_token.value
            self._next_token()
            if self.cur_token.kind == 'ASSIGN':
                self._handle_var_assign(name)
            else:
                raise SyntaxException(self.line, self.cur_token.value)
        elif self.cur_token.kind != 'NEWLINE':
            raise SyntaxException(self.line, self.cur_token.value)

    def _handle_var_def(self) -> None:
        typename = self.cur_token.value
        name_s: list[str] = []

        self._next_token()
        while self.cur_token.kind in ('NAME', 'COMMA'):
            if self.cur_token.kind == 'NAME':
                if self.cur_token.value in KEYWORDS:
                    raise SyntaxException(self.line, self.cur_token.value, 'ключевое слово в имени')
                name_s.append(self.cur_token.value)
            self._next_token()

        if self.cur_token.kind == 'ASSIGN' and Env.INTRODUCTION not in self.envs:
            expr = self._handle_expr()
        elif self.cur_token.kind == 'EQ':
            expr = self._handle_const_expr()
            self._next_token()
            if self.cur_token.kind != 'NEWLINE':
                raise SyntaxException(self.line, self.cur_token.value, 'это не константа')
            self.res.append(StoreVar(self.line - 1, typename, tuple(name_s), expr))
            return
        elif self.cur_token.kind == 'NEWLINE':
            self.res.append(StoreVar(self.line - 1, typename, tuple(name_s), None))
            return
        else:
            raise SyntaxException(self.line, self.cur_token.value)

        if len(name_s) > 1 and expr:
            raise SyntaxException(self.line, ':=', 'здесь не должно быть ":="')

        self.res.append(StoreVar(self.line, typename, tuple(name_s), expr))

    def _handle_var_assign(self, name: str) -> None:
        self.res.append(StoreVar(self.line - 1, None, (name,), self._handle_expr()))

    def _handle_output(self) -> None:
        exprs: list[list[ValueType | Op]] = [[]]

        self._next_token()
        while self.cur_token.kind in ('NUMBER', 'STRING', 'NAME', 'OP', 'COMMA'):
            if self.cur_token.kind == 'COMMA':
                exprs.append([])
            else:
                exprs[-1].append(self._get_val(self.cur_token.kind, self.cur_token.value))
            self._next_token()
        if self.cur_token.kind != 'NEWLINE' or exprs == [[]]:
            raise SyntaxException(self.line, self.cur_token.value)

        if not all(e for e in exprs):
            raise SyntaxException(self.line, self.cur_token.value)
        self.res.append(Output(self.line - 1, [tuple(e) for e in exprs]))

    def _handle_expr(self) -> tuple[ValueType | Op]:
        expr = []

        self._next_token()
        while self.cur_token.kind in ('STRING', 'NAME', 'NUMBER', 'OP'):
            expr.append(self._get_val(self.cur_token.kind, self.cur_token.value))
            self._next_token()
        if self.cur_token.kind != 'NEWLINE' or not expr:
            raise SyntaxException(self.line, self.cur_token.value)

        return tuple(expr)

    def _handle_const_expr(self) -> tuple[ValueType]:
        self._next_token()
        if self.cur_token.kind in ('STRING', 'NAME', 'NUMBER'):
            return (self._get_val(self.cur_token.kind, self.cur_token.value),)
        else:
            raise SyntaxException(self.line, self.cur_token.value)

    def _get_val(self, kind: str, value: str) -> ValueType | Op:
        if kind == 'NUMBER':
            if '.' in value:
                return float(value)
            else:
                return int(value)
        elif kind == 'NAME' and value in ('да', 'нет'):
            return value == 'да'
        elif kind == 'OP':
            return Op(value)
        else:
            return value


def improve(parsed_code: list) -> list:
    for stmt in parsed_code:
        if isinstance(stmt, StoreVar):
            if stmt.value is not None:
                stmt.value = _to_reverse_polish(stmt.value)
        elif isinstance(stmt, Output):
            stmt.exprs = [_to_reverse_polish(expr) for expr in stmt.exprs]
    return parsed_code


def _get_priority(op: Op) -> int:
    """Возвращает приоритет оператора."""
    if op.op in ('*', '/', '**'):
        return 1
    return 0


def _to_reverse_polish(expr: Iterable[ValueType | Op]) -> tuple:
    """Выражение -> обратная польская запись."""
    notation: list[ValueType | Op] = []
    operator_stack: list[Op] = []
    in_parentheses = False
    indent = 0
    code_in_brackets = []
    for token in expr:
        if in_parentheses:
            if token == Op(op='('):
                indent += 1
                code_in_brackets.append(token)
            elif token != Op(op=')'):
                code_in_brackets.append(token)
            elif token == Op(op=')'):
                if indent == 0:
                    in_parentheses = False
                    notation.extend(_to_reverse_polish(code_in_brackets))
                    code_in_brackets.clear()
                else:
                    indent -= 1
                    code_in_brackets.append(token)
        else:
            if isinstance(token, Op):
                if token == Op(op='('):
                    in_parentheses = True
                else:
                    while True:
                        if not operator_stack:
                            break
                        if _get_priority(operator_stack[-1]) >= _get_priority(token):
                            notation.append(Op(operator_stack.pop().op))
                        else:
                            break
                    operator_stack.append(token)
            else:
                notation.append(token)
    for op in operator_stack[::-1]:
        notation.append(Op(op.op))
    return tuple(notation)
