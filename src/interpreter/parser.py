from enum import auto, Enum
from typing import Iterable

from .ast_classes import (AlgStart, AlgEnd, Call, Input, IfStart, IfEnd, Statement,
                          StoreVar, Op, Output, ElseStart, LoopWithCountStart, LoopWithCountEnd,
                          LoopWhileStart, LoopWhileEnd, LoopForStart, LoopForEnd, LoopUntilStart,
                          LoopUntilEnd, Exit, Assert, Stop, Expr, GetItem, SetItem)
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
    LOOP_WHILE = auto()
    LOOP_FOR = auto()
    LOOP_UNTIL = auto()

    SWITCH = auto()


LOOP_ENVS = {Env.LOOP_WITH_COUNT, Env.LOOP_WHILE, Env.LOOP_FOR, Env.LOOP_UNTIL}


class Parser:
    def __init__(self, code: str, debug: bool = False) -> None:
        self.debug = debug

        self.envs = [Env.INTRODUCTION]
        self.cur_expr: list[Value | Op] = []
        self.line = 0
        self.cur_cls: Statement | None = None
        self.res: list[Statement] = []

        # Кол-во веток `при` в текущей конструкции `выбор`
        self.switch_cases_n = 0

        self._was_alg = False

        tokenizer = Tokenizer(code+'\n')
        self.tokens = tokenizer.tokenize()

    def _next_token(self) -> None:
        self.cur_token = next(self.tokens)
        if self.cur_token.kind == 'NEWLINE' and self.cur_token.value == '\n':
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

        ret_name = 'знач'
        ret_type = ''
        if self.cur_token.kind == 'TYPE':
            ret_type = self.cur_token.value
            self._next_token()

        if self.cur_token.kind == 'NAME':
            alg_name = self.cur_token.value
            start_line = self.line
        elif self.cur_token.kind == 'NEWLINE':
            alg_name = ''
            start_line = self.line - 1
        elif self.cur_token.value == 'нач':
            if ret_type:
                raise SyntaxException(self.line, self.cur_token.value,
                                      'алгоритм без имени ничего не возвращает')
            self.res.append(AlgStart(self.line, is_main=is_main, name=''))
            return
        else:
            raise SyntaxException(self.line, self.cur_token.value)
        self._next_token()

        args = []
        if self.cur_token.value == '(':
            args, _ret_name, _ret_type = self._handle_alg_args()
            ret_type = _ret_type or ret_type
            ret_name = _ret_name or ret_name
        elif self.cur_token.kind == 'NEWLINE':
            args = []
        elif self.cur_token.value != 'нач':
            raise SyntaxException(self.line, self.cur_token.value)
        else:
            while self.cur_token.kind == 'NEWLINE':
                self._next_token()
            if self.cur_token.value != 'нач':
                raise SyntaxException(self.line, self.cur_token.value)
        if not alg_name and self._was_alg:
            raise SyntaxException(self.line, self.cur_token.value,
                                  'не указано имя алгоритма')
        if ret_type and not alg_name:
            raise SyntaxException(self.line, self.cur_token.value,
                                  'алгоритм без имени ничего не возвращает')

        self._next_token()

        self.res.append(AlgStart(start_line, is_main=is_main, name=alg_name,
                                 ret_type=ret_type, ret_name=ret_name, args=args))

    def _handle_alg_args(self) -> tuple[list, str, str]:
        args = []
        last_kind = 'арг'
        last_type = ''
        arg, ret_type, ret_name = self._handle_arg(last_kind, last_type)
        if arg is not None:
            args.append(arg)
            last_kind = arg[0]
            if not arg[1]:
                raise SyntaxException(self.line, self.cur_token.value, 'не указан тип')
            last_type = arg[1]
        while self.cur_token.kind == 'COMMA':
            arg, ret_type, ret_name = self._handle_arg(last_kind, last_type)
            if arg is not None:
                args.append(arg)
                last_kind = arg[0]
                if not arg[1]:
                    raise SyntaxException(self.line, self.cur_token.value, 'не указан тип')
                last_type = arg[1]
        if self.cur_token.value != ')':
            raise SyntaxException(self.line, self.cur_token.value)
        return args, ret_name, ret_type

    def _handle_arg(self, last_kind: str, last_type: str) -> tuple[list[str] | None, str, str]:
        ret_type = ''
        ret_name = ''
        self._next_token()
        arg = self._parse_arg()
        arg = [arg[0] or last_kind, arg[1] or last_type, arg[2]]
        if 'рез' in arg[0]:
            ret_name = arg[2]
            ret_type = arg[1]
            if arg[0] == 'аргрез':
                return arg, ret_type, ret_name
            return None, ret_type, ret_name
        else:
            return arg, ret_type, ret_name

    def _parse_arg(self) -> tuple[str, str, str]:
        if self.cur_token.value in ('арг', 'рез', 'аргрез'):
            kind = self.cur_token.value
            self._next_token()
        else:
            kind = ''

        if kind == 'арг' and self.cur_token.value == 'рез':
            kind = 'аргрез'
            self._next_token()

        if self.cur_token.kind == 'TYPE':
            typename = self.cur_token.value
            self._next_token()
        else:
            typename = ''

        if self.cur_token.kind != 'NAME':
            raise SyntaxException(self.line, self.cur_token.value)
        else:
            name = self.cur_token.value
        self._next_token()

        return kind, typename, name

    def _handle_statement(self) -> None:
        if self.cur_token.kind == 'TYPE':  # объявление переменной(ых)
            self._handle_var_def()
        elif self.cur_token.value == 'вывод':
            self._handle_output()
        elif self.cur_token.value == 'ввод':
            self._handle_input()
        elif self.cur_token.value == 'утв':
            self._handle_assert()
        elif self.cur_token.value == 'стоп':
            self._handle_stop()
        elif self.cur_token.value == 'выход' and Env.INTRODUCTION not in self.envs:
            self.res.append(Exit(self.line))
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
        elif self.cur_token.value == 'кц' and self.envs[-1] == Env.LOOP_WHILE:
            self.envs.pop()
            self.res.append(LoopWhileEnd(self.line))
        elif self.cur_token.value == 'кц' and self.envs[-1] == Env.LOOP_FOR:
            self.envs.pop()
            self.res.append(LoopForEnd(self.line))
        elif self.cur_token.value in ('кц', 'кц_при') and self.envs[-1] == Env.LOOP_UNTIL:
            self._handle_loop_until_end()
        elif self.cur_token.value == 'выбор' and Env.INTRODUCTION not in self.envs:
            self.envs.append(Env.SWITCH)
        elif self.cur_token.value == 'при' and self.envs[-1] == Env.SWITCH:
            self._handle_switch_case()
        elif self.cur_token.value == 'иначе' and self.envs[-1] == Env.SWITCH:
            self._handle_switch_else()
        elif self.cur_token.value == 'все' and self.envs[-1] == Env.SWITCH:
            self._handle_switch_end()
        elif self.cur_token.kind == 'NAME':
            name = self.cur_token.value
            self._next_token()
            if self.cur_token.kind == 'ASSIGN':  # присваивание
                self._handle_var_assign(name)
            elif self.cur_token.value == '[':  # присваивание элементу таблицы
                self._handle_table_assign(name)
            elif self.cur_token.kind == 'NEWLINE':  # вызов процедуры
                self.res.append(Call(self.line - 1, name))
            elif self.cur_token.value == '(':  # вызов с аргументами
                self._handle_call(name)
            else:
                raise SyntaxException(self.line, self.cur_token.value)
        elif self.cur_token.kind != 'NEWLINE':
            raise SyntaxException(self.line, self.cur_token.value)

    def _handle_var_def(self) -> None:
        typename = self.cur_token.value

        self._next_token()
        if self.cur_token.value == 'таб':
            typename += 'таб'
            self._next_token()

        names: list[str] = []
        tables: list[tuple[str, list[tuple[Expr, Expr]]]] = []

        while self.cur_token.kind in ('NAME', 'COMMA', 'TABLE_BRACKET'):
            if self.cur_token.value == '[':
                indexes = self._parse_table_def()
                tables.append((names.pop(), indexes))
                continue
            if self.cur_token.kind == 'NAME':
                names.append(self.cur_token.value)
            self._next_token()

        if tables:
            if self.cur_token.kind != 'NEWLINE':
                raise SyntaxException(self.line, self.cur_token.value)
            self.res.append(StoreVar(self.line, typename, [table[0] for table in tables],
                                     [table[1] for table in tables]))
            return

        if 'таб' in typename and not tables:
            raise SyntaxException(self.line, self.cur_token.value, 'нет границ')

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

    def _parse_table_def(self) -> list[tuple[Expr, Expr]]:
        self._next_token()
        indexes = [self._parse_indexes_pair()]
        while self.cur_token.kind == 'COMMA':
            self._next_token()
            indexes.append(self._parse_indexes_pair())
        if self.cur_token.kind != 'NEWLINE':
            raise SyntaxException(self.line, self.cur_token.value)
        if len(indexes) > 3:
            raise SyntaxException(self.line, self.cur_token.value,
                                  'таблицы не бывают размерности > 3')
        return indexes

    def _parse_indexes_pair(self) -> tuple[Expr, Expr]:
        """Парсит строку вида `<выражение>:<выражение>`"""
        first_i = self._parse_expr(in_getitem=True)
        if self.cur_token.kind != 'COLON':
            raise SyntaxException(self.line, self.cur_token.value)
        self._next_token()
        last_i = self._parse_expr(in_getitem=True)
        return first_i, last_i

    def _handle_var_assign(self, name: str) -> None:
        self._next_token()
        expr = self._parse_expr()
        if self.cur_token.kind != 'NEWLINE':
            raise SyntaxException(self.line, self.cur_token.value)
        self.res.append(StoreVar(self.line - 1, None, [name], expr))

    def _handle_table_assign(self, name: str) -> None:
        self._next_token()
        indexes = self._parse_table_item_indexes()
        if self.cur_token.kind != 'ASSIGN':
            raise SyntaxException(self.line, self.cur_token.value)
        self._next_token()
        expr = self._parse_expr()
        if self.cur_token.kind != 'NEWLINE':
            raise SyntaxException(self.line, self.cur_token.value)
        self.res.append(SetItem(self.line - 1, name, indexes, expr))

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
        if not targets:
            raise SyntaxException(self.line, self.cur_token.value, 'куда вводить?')
        elif self.cur_token.kind != 'NEWLINE':
            raise SyntaxException(self.line, self.cur_token.value)

        self.res.append(Input(self.line - 1, targets))

    def _handle_assert(self):
        self._next_token()
        expr = self._parse_expr()
        if self.cur_token.kind != 'NEWLINE':
            raise SyntaxException(self.line, self.cur_token.value)

        self.res.append(Assert(self.line - 1, expr))

    def _handle_stop(self):
        self._next_token()
        if self.cur_token.kind != 'NEWLINE':
            raise SyntaxException(self.line, self.cur_token.value)
        self.res.append(Stop(self.line - 1))

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
        if self.cur_token.value == 'пока':
            self._handle_loop_while()
        elif self.cur_token.value == 'для':
            self._handle_loop_for()
        elif self.cur_token.kind == 'NEWLINE':
            self.envs.append(Env.LOOP_UNTIL)
            self.res.append(LoopUntilStart(self.line - 1))
        else:
            self._handle_loop_with_count(self._parse_expr())

    def _handle_loop_with_count(self, count):
        if self.cur_token.value != 'раз':
            raise SyntaxException(self.line, self.cur_token.value)

        self.envs.append(Env.LOOP_WITH_COUNT)
        self.res.append(LoopWithCountStart(self.line, count))

    def _handle_loop_while(self):
        self._next_token()
        cond = self._parse_expr()
        if self.cur_token.kind != 'NEWLINE':
            raise SyntaxException(self.line, self.cur_token.value)
        self.envs.append(Env.LOOP_WHILE)
        self.res.append(LoopWhileStart(self.line - 1, cond))

    def _handle_loop_for(self):
        self._next_token()

        if self.cur_token.kind != 'NAME':
            raise SyntaxException(self.line, self.cur_token.value, 'должно быть имя')
        target = self.cur_token.value

        self._next_token()
        if self.cur_token.value != 'от':
            raise SyntaxException(self.line, self.cur_token.value)
        self._next_token()
        from_expr = self._parse_expr()

        if self.cur_token.value != 'до':
            raise SyntaxException(self.line, self.cur_token.value)
        self._next_token()
        to_expr = self._parse_expr()

        step = [Value('цел', 1)]
        if self.cur_token.value == 'шаг':
            self._next_token()
            step = self._parse_expr()
        if self.cur_token.kind != 'NEWLINE':
            raise SyntaxException(self.line, self.cur_token.value)

        self.envs.append(Env.LOOP_FOR)
        self.res.append(LoopForStart(self.line - 1, target, from_expr, to_expr, step))

    def _handle_loop_until_end(self):
        if self.cur_token.value == 'кц_при':
            until = True
        else:
            until = False
            self._next_token()

        if self.cur_token.kind == 'NEWLINE':
            cond = [Value('лог', 'да')]
        elif self.cur_token.value == 'при' or until:
            self._next_token()
            cond = self._parse_expr()
            if self.cur_token.kind != 'NEWLINE':
                raise SyntaxException(self.line, self.cur_token.value)
        else:
            raise SyntaxException(self.line, self.cur_token.value)

        self.envs.pop()
        self.res.append(LoopUntilEnd(self.line - 1, cond))

    def _handle_switch_case(self):
        self._next_token()

        cond = self._parse_expr()
        if self.cur_token.value != ':':
            raise SyntaxException(self.line, self.cur_token.value)

        if self.switch_cases_n > 0:
            self.res.append(ElseStart(self.line))
        self.switch_cases_n += 1

        self.res.append(IfStart(self.line, cond))

    def _handle_switch_else(self):
        self._next_token()

        if self.cur_token.value != ':':
            raise SyntaxException(self.line, self.cur_token.value)

        self.res.append(ElseStart(self.line))

    def _handle_switch_end(self):
        for _ in range(self.switch_cases_n):
            self.res.append(IfEnd(self.line))

        self.switch_cases_n = 0
        self.envs.pop()

    def _handle_call(self, name: str):
        call = self._parse_call(name)

        if self.cur_token.kind != 'NEWLINE':
            raise SyntaxException(self.line, self.cur_token.value)

        self.res.append(call)

    def _parse_expr(self, in_alg_call=False, in_getitem=False) -> Expr:
        expr = []

        # Переменные должны быть инициализированы разными значениями,
        # чтобы на первой итерации цикла не происходила ошибка
        last_kind = None
        cur_kind = ''
        open_brackets = 0
        close_brackets = 0

        open_table_brackets = 0
        close_table_brackets = 0

        last_name = ''
        while (self.cur_token.kind in ('STRING', 'NAME', 'CHAR', 'NUMBER',
                                       'OP', 'EQ', 'TABLE_BRACKET') or
               self.cur_token.value in ('да', 'нет', 'нс')):
            if self.cur_token.value == '(':
                open_brackets += 1
            elif self.cur_token.value == ')':
                close_brackets += 1
            elif self.cur_token.value == '[':
                open_table_brackets += 1
            elif self.cur_token.value == ']':
                close_table_brackets += 1
            if (in_alg_call and close_brackets - open_brackets == 1) or\
                    (in_getitem and close_table_brackets - open_table_brackets == 1):
                self._next_token()
                break

            if (self.cur_token.kind in ('STRING', 'NAME', 'CHAR', 'NUMBER')
                    or self.cur_token.value in ('да', 'нет', 'нс')):
                cur_kind = 'val'
            elif self.cur_token.value not in ('(', ')'):
                cur_kind = 'op'
            else:
                cur_kind = ''

            if (last_kind == cur_kind and
                    not (last_kind == 'op' and self.cur_token.value in ('+', '-', 'не'))):
                raise SyntaxException(self.line, self.cur_token.value)

            if last_name and self.cur_token.value == '(':
                expr.append(self._parse_call(last_name))
                last_name = ''
                continue
            elif last_name and self.cur_token.value == '[':
                expr.append(self._parse_getitem(last_name))
                last_name = ''
                continue

            if last_name:
                expr.append(_get_val('NAME', last_name))

            if self.cur_token.kind != 'NAME':
                expr.append(_get_val(self.cur_token.kind, self.cur_token.value))

            if self.cur_token.kind == 'NEWLINE':
                break

            last_name = self.cur_token.value if self.cur_token.kind == 'NAME' else ''
            last_kind = cur_kind

            self._next_token()

        if last_name:
            expr.append(_get_val('NAME', last_name))

        if not expr:
            raise SyntaxException(self.line, self.cur_token.value)

        return _to_reverse_polish(expr)

    def _parse_const_expr(self) -> list[Value]:
        self._next_token()
        if self.cur_token.kind in ('STRING', 'NAME', 'CHAR', 'NUMBER'):
            return [_get_val(self.cur_token.kind, self.cur_token.value)]
        raise SyntaxException(self.line, self.cur_token.value)

    def _parse_call(self, name: str) -> Call:
        self._next_token()
        args = [self._parse_expr(in_alg_call=True)]

        while self.cur_token.kind == 'COMMA':
            self._next_token()
            args.append(self._parse_expr(in_alg_call=True))

        return Call(self.line - 1, name, args)

    def _parse_getitem(self, name: str):
        self._next_token()
        indexes = self._parse_table_item_indexes()
        if self.cur_token.kind != 'NEWLINE':
            raise SyntaxException(self.line, self.cur_token.value)
        return GetItem(self.line, name, indexes)

    def _parse_table_item_indexes(self) -> list[Expr]:
        indexes = [self._parse_expr(in_getitem=True)]
        while self.cur_token.value == ',':
            self._next_token()
            indexes.append(self._parse_expr(in_getitem=True))
        return indexes


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


def _get_priority(op: Op, unary: bool) -> int:
    """Возвращает приоритет оператора."""
    if unary and op.op in ('-', '+'):
        return 4
    elif unary and op.op == 'не':
        return 1
    if op.op in ('*', '/', '**'):
        return 3
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
    prev = None
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
                if token.op == '(':
                    in_parentheses = True
                else:
                    while operator_stack:
                        unary = ((prev is None or (isinstance(prev, Op) and prev.op != ')'))
                            and token.op in ('+', '-', 'не'))
                        op_from_stack = operator_stack[-1]
                        if (_get_priority(op_from_stack, op_from_stack.unary)
                                >= _get_priority(token, unary=unary)):
                            notation.append(Op(op_from_stack.op, unary=op_from_stack.unary))
                            operator_stack.pop()
                        else:
                            break
                    if ((prev is None or (isinstance(prev, Op) and prev.op != ')'))
                            and token.op in ('+', '-', 'не')):
                        token.unary = True
                    operator_stack.append(token)
            else:
                notation.append(token)
        prev = token
    for op in operator_stack[::-1]:
        notation.append(Op(op.op, op.unary))
    return notation
