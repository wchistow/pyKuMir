from enum import auto, Enum
from dataclasses import dataclass
import re
from typing import Iterable

from .ast_classes import AlgStart, AlgEnd, Statement, StoreVar, Op, Output, Call, Input
from .constants import KEYWORDS, TYPES
from .value import Value
from .exceptions import SyntaxException

token_specification = [
            ('COMMENT',       r'\|.*'),
            ('STRING',        r'"[^"]*"'),
            ('CHAR',          r"'.'"),
            ('NUMBER',        r'\d+(\.\d*)?'),
            ('TYPE',          rf'({"|".join(TYPES)})'),
            ('NAME',           r'[A-Za-zА-Яа-я_][A-Za-zА-Яа-я_0-9]*'),
            ('ASSIGN',        r':='),
            ('EQ',            r'='),
            ('OP',            r'(\*\*|\+|\-|\*|/|>=|<=|<>|\(|\))'),
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
    ALG = auto()


class Parser:
    def __init__(self, code: str, debug: bool = False) -> None:
        self.debug = debug

        self.envs = [Env.INTRODUCTION]
        self.cur_expr: list[Value | Op] = []
        self.line = 0
        self.cur_cls: Statement | None = None
        self.res: list[Statement] = []

        self._was_alg = False

        self.tokens = re.finditer(TOK_REGEX, code+'\n')

    def _next_token(self) -> None:
        mo = next(self.tokens)
        self.cur_token = Token(mo.lastgroup, mo.group())
        if self.cur_token.kind == 'SKIP':
            self._next_token()
            return
        if self.cur_token.kind == 'NEWLINE':
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
            if self.envs and self.envs[-1] in (Env.MAIN, Env.ALG) and self.cur_token.value == 'кон':
                self.res.append(AlgEnd(self.line))
                self.envs.pop()

            self._next_token()

            if self.envs:
                if self.envs[-1] == Env.INTRODUCTION:
                    if self.cur_token.value == 'алг':  # введение закончилось
                        self.envs.pop()
                        self.envs.append(Env.MAIN)

                        self._handle_alg_header(is_main=True)

                        self._was_alg = True
                        continue
                elif self.envs[-1] in (Env.MAIN, Env.ALG):
                    if self.cur_token.value == 'кон':
                        self.res.append(AlgEnd(self.line))
                        self.envs.pop()
                        continue

            if self.cur_token.value == 'алг':
                self.envs.append(Env.ALG)
                self._handle_alg_header(is_main=False)
                continue

            self._handle_statement()

    def _handle_alg_header(self, is_main: bool):
        self._next_token()

        alg_name = self._handle_alg_name()

        self._next_token()

        self.res.append(AlgStart(self.line - 1 if self.line > 0 else self.line, is_main=is_main, name=alg_name))

    def _handle_alg_name(self) -> str:
        alg_name = []
        if self.cur_token.kind == 'NAME' and self.cur_token.value != 'нач':
            alg_name.append(self.cur_token.value)
            self._next_token()
        while self.cur_token.kind in ('NAME', 'TYPE', 'NUMBER') and self.cur_token.value != 'нач':
            alg_name.append(self.cur_token.value)
            self._next_token()
        while self.cur_token.kind == 'NEWLINE':
            self._next_token()

        if not alg_name and self._was_alg:
            raise SyntaxException(self.line-1, 'алг', 'Не указано имя')

        if self.cur_token.value == 'нач':
            return ' '.join(alg_name)
        elif self.cur_token.kind != 'NEWLINE':
            raise SyntaxException(self.line, self.cur_token.value)

    def _handle_statement(self) -> None:
        if self.cur_token.kind == 'TYPE':  # объявление переменной(ых)
            self._handle_var_def()
        elif self.cur_token.kind == 'NAME' and self.cur_token.value == 'вывод':
            self._handle_output()
        elif self.cur_token.kind == 'NAME' and self.cur_token.value == 'ввод':
            self._handle_input()
        elif self.cur_token.kind == 'NAME':
            name = self.cur_token.value
            self._next_token()
            if self.cur_token.kind == 'ASSIGN':  # присваивание
                self._handle_var_assign(name)
            elif self.cur_token.kind == 'NEWLINE':  # вызов процедуры
                self.res.append(Call(self.line - 1, name))
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

        if self.cur_token.kind == 'ASSIGN':
            expr = self._handle_expr()
        elif self.cur_token.kind == 'EQ':
            expr = self._handle_const_expr()
            self._next_token()
            if self.cur_token.kind != 'NEWLINE':
                raise SyntaxException(self.line, self.cur_token.value, 'это не константа')
            self.res.append(StoreVar(self.line - 1, typename, name_s, expr))
            return
        elif self.cur_token.kind == 'NEWLINE':
            self.res.append(StoreVar(self.line - 1, typename, name_s, None))
            return
        else:
            raise SyntaxException(self.line, self.cur_token.value)

        if len(name_s) > 1 and expr:
            raise SyntaxException(self.line, ':=', 'здесь не должно быть ":="')

        self.res.append(StoreVar(self.line - 1, typename, name_s, expr))

    def _handle_var_assign(self, name: str) -> None:
        self.res.append(StoreVar(self.line - 1, None, [name], self._handle_expr()))

    def _handle_output(self) -> None:
        exprs: list[list[Value | Op]] = [[]]

        self._next_token()
        while self.cur_token.kind in ('NUMBER', 'STRING', 'CHAR', 'NAME', 'OP', 'COMMA'):
            if self.cur_token.kind == 'COMMA':
                exprs.append([])
            else:
                exprs[-1].append(_get_val(self.cur_token.kind, self.cur_token.value))
            self._next_token()
        if self.cur_token.kind != 'NEWLINE' or exprs == [[]]:
            raise SyntaxException(self.line, self.cur_token.value, 'что выводить?')

        if not all(e for e in exprs):
            raise SyntaxException(self.line, self.cur_token.value)
        self.res.append(Output(self.line - 1, exprs))

    def _handle_input(self) -> None:
        targets: list[str] = []

        self._next_token()
        last = self.cur_token.kind
        while self.cur_token.kind in ('NAME', 'COMMA'):
            if self.cur_token.kind == 'NAME':
                targets.append(self.cur_token.value)
            self._next_token()
            if last == self.cur_token.kind:
                raise SyntaxException(self.line, self.cur_token.value)
            last = self.cur_token.kind
        if self.cur_token.kind != 'NEWLINE' or not targets:
            raise SyntaxException(self.line, self.cur_token.value, 'куда вводить?')

        self.res.append(Input(self.line - 1, targets))

    def _handle_expr(self) -> list[Value | Op]:
        expr = []

        self._next_token()
        while self.cur_token.kind in ('STRING', 'NAME', 'CHAR', 'NUMBER', 'OP'):
            expr.append(_get_val(self.cur_token.kind, self.cur_token.value))
            self._next_token()
        if self.cur_token.kind != 'NEWLINE' or not expr:
            raise SyntaxException(self.line, self.cur_token.value)

        return expr

    def _handle_const_expr(self) -> list[Value]:
        self._next_token()
        if self.cur_token.kind in ('STRING', 'NAME', 'CHAR', 'NUMBER'):
            return [_get_val(self.cur_token.kind, self.cur_token.value)]
        else:
            raise SyntaxException(self.line, self.cur_token.value)


def _get_val(kind: str, value: str) -> Value | Op:
    """
    Преобразует значение `value` из `str` в тип `kind`, например:
     + `_get_val('NUMBER', '5')` -> `5`
     + `_get_val('NAME' 'да')` -> `True`
     + `_get_val('OP', '+')` -> `Op('+')`
    """
    if kind == 'NUMBER':
        if '.' in value:
            return Value('вещ', float(value))
        else:
            return Value('цел', int(value))
    elif kind == 'STRING':
        return Value('лит', value[1:-1])
    elif kind == 'CHAR':
        return Value('сим', value[1:-1])
    elif kind == 'NAME' and value in ('да', 'нет'):
        return Value('лог', value == 'да')
    elif kind == 'NAME':
        return Value('get-name', value)
    elif kind == 'OP':
        return Op(value)


def improve(parsed_code: list) -> list[Statement]:
    for stmt in parsed_code:
        if isinstance(stmt, StoreVar):
            if stmt.value is not None:
                print(*stmt.value, sep='\n')
                stmt.value = _to_reverse_polish(stmt.value)
        elif isinstance(stmt, Output):
            stmt.exprs = [_to_reverse_polish(expr) for expr in stmt.exprs]
    return parsed_code


def _get_priority(op: Op) -> int:
    """Возвращает приоритет оператора."""
    if op.op in ('*', '/', '**'):
        return 1
    return 0


def _to_reverse_polish(expr: Iterable[Value | Op]) -> list[Value | Op]:
    """Выражение -> обратная польская запись."""
    notation: list[Value | Op] = []
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
    return notation
