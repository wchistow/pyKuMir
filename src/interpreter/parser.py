from enum import auto, Enum
from typing import Iterable

from .ast_classes import (AlgStart, AlgEnd, Call, Input, IfStart, IfEnd, Statement,
                          StoreVar, Op, Output, ElseStart, LoopWithCountStart, LoopWithCountEnd)
from .value import Value
from .tokenizer import Tokenizer
from .exceptions import SyntaxException


class Env(Enum):
    """Окружение, в котором мы сейчас находимся."""
    INTRODUCTION = auto()
    MAIN = auto()
    ALG = auto()
    IF = auto()
    LOOP_WITH_COUNT = auto()


class Parser:
    def __init__(self, code: str, debug: bool = False) -> None:
        self.debug = debug

        self.envs = [Env.INTRODUCTION]
        self.cur_expr: list[Value | Op] = []
        self.line = 0
        self.cur_cls: Statement | None = None
        self.res: list[Statement] = []

        self._was_alg = False

        tokenizer = Tokenizer(code+'\n')
        self.tokens = tokenizer.tokenize()

    def _next_token(self) -> None:
        self.cur_token = next(self.tokens)
        if self.cur_token.kind == 'NEWLINE':
            self.line += 1

        if self.debug:
            print(f'{self.line} {self.cur_token.kind:10} {self.cur_token.value!r}')

    def parse(self) -> list[Statement]:
        try:
            self._parse()
        except StopIteration:
            if self.envs and self.envs[-1] == Env.MAIN:
                raise SyntaxException(self.line, '\n',
                                      'нет "кон" после "нач"') from None
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

        if self.cur_token.kind == 'NAME':
            alg_name = self.cur_token.value
            start_line = self.line
        elif self.cur_token.kind == 'NEWLINE':
            alg_name = ''
            start_line = self.line - 1
        elif self.cur_token.value == 'нач':
            self.res.append(AlgStart(self.line, is_main=is_main, name=''))
            return
        else:
            raise SyntaxException(self.line, self.cur_token.value)
        self._next_token()

        while self.cur_token.kind == 'NEWLINE':
            self._next_token()
        if self.cur_token.value != 'нач':
            raise SyntaxException(self.line, self.cur_token.value)
        if not alg_name and self._was_alg:
            raise SyntaxException(self.line, self.cur_token.value,
                                  'не указано имя алгоритма')

        self._next_token()

        self.res.append(AlgStart(start_line, is_main=is_main, name=alg_name))

    def _handle_statement(self) -> None:
        if self.cur_token.kind == 'TYPE':  # объявление переменной(ых)
            self._handle_var_def()
        elif self.cur_token.value == 'вывод':
            self._handle_output()
        elif self.cur_token.value == 'ввод':
            self._handle_input()
        elif self.cur_token.value == 'если' and Env.INTRODUCTION not in self.envs:
            self._handle_if()
        elif self.cur_token.value == 'иначе' and self.envs[-1] == Env.IF:
            self.res.append(ElseStart(self.line))
        elif self.cur_token.value == 'все' and self.envs[-1] == Env.IF:
            self.envs.pop()
            self.res.append(IfEnd(self.line))
        elif self.cur_token.value == 'нц' and Env.INTRODUCTION not in self.envs:
            self._handle_loop()
        elif self.cur_token.value == 'кц' and self.envs[-1] == Env.LOOP_WITH_COUNT:
            self.envs.pop()
            self.res.append(LoopWithCountEnd(self.line))
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

        self._next_token()
        names: list[str] = []

        while self.cur_token.kind in ('NAME', 'COMMA'):
            if self.cur_token.kind == 'NAME':
                names.append(self.cur_token.value)
            self._next_token()

        if self.cur_token.kind == 'ASSIGN':
            self._next_token()
            expr = self._parse_expr()
            if self.cur_token.kind != 'NEWLINE':
                raise SyntaxException(self.line, self.cur_token.value)
        elif self.cur_token.kind == 'EQ':
            expr = self._parse_const_expr()
            self._next_token()
            if self.cur_token.kind != 'NEWLINE':
                raise SyntaxException(self.line, self.cur_token.value, 'это не константа')
            self.res.append(StoreVar(self.line - 1, typename, names, expr))
            return
        elif self.cur_token.kind == 'NEWLINE':
            self.res.append(StoreVar(self.line - 1, typename, names, None))
            return
        else:
            raise SyntaxException(self.line, self.cur_token.value)

        if len(names) > 1 and expr:
            raise SyntaxException(self.line, ':=', 'здесь не должно быть ":="')

        self.res.append(StoreVar(self.line - 1, typename, names, expr))

    def _handle_var_assign(self, name: str) -> None:
        self._next_token()
        expr = self._parse_expr()
        if self.cur_token.kind != 'NEWLINE':
            raise SyntaxException(self.line, self.cur_token.value)
        self.res.append(StoreVar(self.line - 1, None, [name], expr))

    def _handle_output(self) -> None:
        exprs: list[list[Value | Op]] = []

        self._next_token()
        exprs.append(self._parse_expr())
        while self.cur_token.kind == 'COMMA':
            self._next_token()
            exprs.append(self._parse_expr())
        if exprs == [[]]:
            raise SyntaxException(self.line, self.cur_token.value, 'что выводить?')
        elif self.cur_token.kind != 'NEWLINE':
            raise SyntaxException(self.line, self.cur_token.value)

        self.res.append(Output(self.line - 1, [_to_reverse_polish(expr) for expr in exprs]))

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
        if not targets:
            raise SyntaxException(self.line, self.cur_token.value, 'куда вводить?')
        elif self.cur_token.kind != 'NEWLINE':
            raise SyntaxException(self.line, self.cur_token.value)

        self.res.append(Input(self.line - 1, targets))

    def _handle_if(self):
        self._next_token()
        expr = self._parse_expr()
        if self.cur_token.value != 'то':
            raise SyntaxException(self.line, self.cur_token.value)

        self.envs.append(Env.IF)
        self.res.append(IfStart(self.line, expr))
        self._next_token()

    def _handle_loop(self):
        self._next_token()
        try:
            count = self._parse_expr()
        except SyntaxException:
            # другие циклы или ошибки
            raise SyntaxException(self.line, self.cur_token.value) from None
        else:
            self._handle_loop_with_count(count)

    def _handle_loop_with_count(self, count):
        if self.cur_token.value != 'раз':
            raise SyntaxException(self.line, self.cur_token.value)

        self.envs.append(Env.LOOP_WITH_COUNT)
        self.res.append(LoopWithCountStart(self.line, count))

    def _parse_expr(self) -> list[Value | Op]:
        expr = []

        # Переменные должны быть инициализированы разными значениями,
        # чтобы на первой итерации цикла не происходила ошибка
        last_kind = None
        cur_kind = ''
        while (self.cur_token.kind in ('STRING', 'NAME', 'CHAR', 'NUMBER', 'OP', 'EQ') or
               self.cur_token.value in ('да', 'нет', 'нс')):
            if self.cur_token.kind in ('STRING', 'NAME', 'CHAR', 'NUMBER'):
                cur_kind = 'val'
            elif self.cur_token.value not in ('(', ')'):
                cur_kind = 'op'
            else:
                cur_kind = ''

            if last_kind == cur_kind:
                raise SyntaxException(self.line, self.cur_token.value)

            expr.append(_get_val(self.cur_token.kind, self.cur_token.value))
            self._next_token()

            last_kind = cur_kind

        if not expr:
            raise SyntaxException(self.line, self.cur_token.value)

        return _to_reverse_polish(expr)

    def _parse_const_expr(self) -> list[Value]:
        self._next_token()
        if self.cur_token.kind in ('STRING', 'NAME', 'CHAR', 'NUMBER'):
            return [_get_val(self.cur_token.kind, self.cur_token.value)]
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
        return Value('цел', int(value))
    elif kind == 'STRING':
        return Value('лит', value[1:-1])
    elif kind == 'NAME':
        return Value('get-name', value)
    elif kind == 'OP' or kind == 'EQ':
        return Op(value)
    elif kind == 'CHAR':
        return Value('сим', value[1:-1])
    elif kind == 'KEYWORD' and value in ('да', 'нет'):
        return Value('лог', value)
    elif kind == 'KEYWORD' and value == 'нс':
        return Value('get-name', value)


def _get_priority(op: Op) -> int:
    """Возвращает приоритет оператора."""
    if op.op in ('*', '/', '**'):
        return 1
    elif op.op in ('>', '<', '=', '>=', '<=', '<>'):
        return 2
    elif op.op in ('или', 'и'):
        return 3
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
