from enum import auto, Enum
import re
from typing import Iterable

from .ast_classes import Statement, StoreVar, Op, Output
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


class State(Enum):
    """Следующий токен, ожидаемый парсером"""
    WAIT = auto()

    # объявление и присваивание
    VAR_NAME = auto()
    VAR_ASSIGN = auto()  # знак присваивания (`:=` или `=`)
    VAR_EXPR = auto()  # значение переменной
    VAR_CONST_EXPR = auto()  # значение константы

    OUTPUT_EXPR = auto()  # выражение после `вывод`

    NEWLINE = auto()


class Env(Enum):
    """Окружение, в котором мы сейчас находимся."""
    VAR_DEF = auto()  # объявление переменной
    VAR_ASSIGN = auto()  # присваивание
    OUTPUT = auto()  # вывод


class Parser:
    def __init__(self, debug: bool = False) -> None:
        self.debug = debug

        self.state = State.WAIT
        self.envs = []
        self.cur_expr: list[ValueType | Op] = []
        self.line = 0
        self.cur_cls: Statement | None = None
        self.res: list[Statement] = []

    def reset(self) -> None:
        self.state = State.WAIT
        self.envs.clear()
        self.cur_expr.clear()
        self.line = 0
        self.cur_cls = None
        self.res.clear()

    def parse(self, code: str) -> list[Statement]:
        for mo in re.finditer(TOK_REGEX, code):
            kind = mo.lastgroup
            value = mo.group()

            if kind == 'SKIP':  # пропускаем пробелы
                continue
            elif kind == 'NEWLINE':
                self._handle_newline()
                continue

            if self.debug:
                print(f'{self.state:20} {kind:10} {value}')

            if self.state == State.NEWLINE:
                raise SyntaxException(self.line, value)
            elif self.state == State.WAIT:
                self._handle_first(kind, value)
            elif self.state == State.VAR_NAME:
                if kind == 'NAME':
                    self._handle_var_name(value)
                else:
                    raise SyntaxException(self.line, value)
            elif self.state == State.VAR_ASSIGN:
                self._handle_var_assign(kind, value)
            elif self.state == State.VAR_EXPR:
                self._handle_expr(kind, value)
            elif self.state == State.VAR_CONST_EXPR:
                self._handle_const_expr(kind, value)
            elif self.state == State.OUTPUT_EXPR:
                if kind == 'COMMA':
                    if self.cur_expr:
                        self.cur_cls.exprs.append(tuple(self.cur_expr))
                    else:
                        raise SyntaxException(self.line, value)
                    self.cur_expr.clear()
                else:
                    self._handle_expr(kind, value)

        self._handle_newline()

        if self.debug:
            print('-' * 40)

        return self.res

    def _handle_first(self, kind: str, value: str) -> None:
        """Обрабатвает первый токен в строке."""
        if kind == 'TYPE':  # объвление переменной(ых)
            self.cur_cls = StoreVar(self.line, value, tuple(), None)
            self.envs.append(Env.VAR_DEF)
            self.state = State.VAR_NAME
        elif kind == 'NAME' and value == 'вывод':
            self.cur_cls = Output(self.line, [])
            self.envs.append(Env.OUTPUT)
            self.state = State.OUTPUT_EXPR
        elif kind == 'NAME':  # присваивание
            self.cur_cls = StoreVar(self.line, None, (value,), None)
            self.envs.append(Env.VAR_ASSIGN)
            self.state = State.VAR_ASSIGN
        else:
            raise SyntaxException(self.line, value)

    def _handle_var_name(self, name: str) -> None:
        if name in KEYWORDS or name in TYPES:
            raise SyntaxException(self.line, name, message='ключевое слово в имени')
        if self.cur_cls.names != tuple():  # уже есть имена
            self.cur_cls.names = (*self.cur_cls.names, name)
            self.res.append(self.cur_cls)
            # это объявление нескольких переменных - значения быть не может
            self.state = State.NEWLINE
        else:
            self.cur_cls.names = (name,)
            self.state = State.VAR_ASSIGN
    
    def _handle_var_assign(self, tok_kind: str, tok_value: str) -> None:
        if self.envs[-1] == Env.VAR_DEF:
            if tok_kind == 'ASSIGN':
                self.state = State.VAR_EXPR
            elif tok_kind == 'EQ':
                self.state = State.VAR_CONST_EXPR
            elif tok_kind == 'COMMA':  # name, name
                self.state = State.VAR_NAME
            else:
                raise SyntaxException(self.line, tok_value)
        elif self.envs[-1] == Env.VAR_ASSIGN:
            if tok_kind == 'ASSIGN':
                self.state = State.VAR_EXPR
            else:
                raise SyntaxException(self.line, tok_value)

    def _handle_newline(self) -> None:
        """Обрабатывает конец строки."""
        self.line += 1
        if self.state == State.VAR_EXPR:
            if not self.cur_expr:
                raise SyntaxException(self.line, '\n')
            self.cur_cls.value = tuple(self.cur_expr)
            self.res.append(self.cur_cls)
        elif self.state == State.VAR_ASSIGN:  # объявление переменной без значения
            self.res.append(self.cur_cls)
        elif self.state == State.OUTPUT_EXPR:
            if self.cur_expr:
                self.cur_cls.exprs.append(tuple(self.cur_expr))
                self.res.append(self.cur_cls)
            else:
                raise SyntaxException(self.line, '\n')
        elif self.state not in (State.NEWLINE, State.WAIT):
            raise SyntaxException(self.line, '\n')
        self.cur_cls = None
        self.cur_expr.clear()
        self.state = State.WAIT
        self.envs.pop()

    def _handle_expr(self, tok_kind: str, tok_value: str) -> None:
        if tok_kind in ('STRING', 'NAME'):
            self.cur_expr.append(tok_value)
        elif tok_kind == 'NUMBER':
            self.cur_expr.append(self._get_number(tok_value))
        elif tok_kind == 'OP':
            self.cur_expr.append(Op(tok_value))
        else:
            raise SyntaxException(self.line, tok_value)

    def _handle_const_expr(self, tok_kind: str, tok_value: str) -> None:
        if tok_kind in ('STRING', 'NAME'):
            self.cur_cls.value = (tok_value,)
        elif tok_kind == 'NUMBER':
            self.cur_cls.value = (self._get_number(tok_value),)
        else:
            raise SyntaxException(self.line, tok_value)
        self.res.append(self.cur_cls)
        self.cur_cls = None
        self.state = State.NEWLINE
    
    def _get_number(self, value: str) -> int | float:
        if '.' in value:
            return float(value)
        else:
            return int(value)


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
