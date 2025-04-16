from typing import Callable, NamedTuple, NoReturn

from lark import Token

from .ast_classes import Op
from .build_bytecode import Bytecode
from .constants import ValueType, KEYWORDS
from .exceptions import SyntaxException, RuntimeException


class Var(NamedTuple):
    typename: str
    name: str
    value: ValueType | None


class VM:
    def __init__(self, output_f: Callable[[str], None]) -> None:
        self.glob_vars: list[Var] = []
        self.output_f = output_f

    def reset(self) -> None:
        self.glob_vars.clear()

    def execute(self, bytecode: list[Bytecode]) -> None:
        for inst in bytecode:
            if inst.command == 'store':
                self.store_var(inst.start_line, inst.args[0], inst.args[1], inst.args[2])
            elif inst.command == 'output':
                self.output(inst.start_line, inst.args[0])

    def store_var(self, lineno: int, typename: str | None, names: tuple[str], value: tuple) -> None:
        if len(names) > 1 and value is not None:
            raise SyntaxException(lineno, message='при нескольких переменных нельзя указывать значение')
        if typename is None:  # сохранение значения в уже объявленную переменную
            var_i = self._var_defined(names[0])
            if var_i == -1:
                raise RuntimeException(lineno, f'имя "{names[0]}" не объявлено')
            var = self.glob_vars.pop(var_i)
            self._save_var(lineno, var.typename, var.name, value)
            return
        if len(names) == 1:
            self._save_var(lineno, typename, names[0], value)
        else:  # объявление нескольких переменных (`цел а, б`)
            for name in names:
                self._save_var(lineno, typename, name, None)

    def output(self, lineno: int, exprs: list[tuple]) -> None:
        res: list[str] = []
        for expr in exprs:
            if len(expr) == 1 and isinstance(expr[0], Token) and \
                    expr[0].type == 'NAME' and expr[0].value == 'нс':
                res.append('\n')
                continue
            res.append(str(self._count(lineno, expr)))
        self.output_f(''.join(res))

    def _save_var(self, lineno: int, typename: str, name: str, value: tuple | None) -> None:
        if name in KEYWORDS:
            raise SyntaxException(lineno, message="ключевое слово в имени")
        if value is None:
            self.glob_vars.append(Var(typename, name, None))
            return
        val = self._count(lineno, value)
        val_type = self._get_type(lineno, val)
        if val_type == typename:  # типы целевой переменной и значения совпадают
            self.glob_vars.append(Var(typename, name, val))
        else:
            raise RuntimeException(lineno, message=f'нельзя "{typename} := {val_type}"')

    def get_var(self, lineno: int, name: str) -> ValueType | NoReturn:
        for var in self.glob_vars:
            if var.name == name:
                if var.value is None:
                    raise RuntimeException(lineno, 'нет значения у величины.')
                return var.value
        raise RuntimeException(lineno, 'имя не объявлено')

    def _var_defined(self, name: str) -> int:
        """
        Возвращает индекс переменой с именем `name` в списке `self.vars`. Если такой нет, возвращает -1.
        """
        for i, var in enumerate(self.glob_vars):
            if var.name == name:
                return i
        return -1

    def _count(self, lineno: int, expr: tuple) -> ValueType | NoReturn:
        """Вычисляет переданное выражение."""
        stack = []
        for tok in expr:
            if isinstance(tok, Token):
                stack.append(self.get_var(lineno, tok.value))
            elif isinstance(tok, ValueType):
                stack.append(tok)
            elif isinstance(tok, Op):
                a = stack.pop()
                b = stack.pop()
                self._check_type_is_eq(lineno, a, b, tok.op)
                stack.append(eval(f'{b} {tok.op} {a}'))
        return stack[0]

    def _check_type_is_eq(self, lineno: int, a: ValueType, b: ValueType, op: str) -> None:
        a_type = self._get_type(lineno, a)
        b_type = self._get_type(lineno, b)
        if a_type != b_type:
            raise RuntimeException(lineno, f'нельзя "{b_type} {op} {a_type}"')

    def _get_type(self, lineno: int, value: ValueType | Token) -> str:
        """"Переводит" типы с python на алгоритмический."""
        if isinstance(value, Token):
            return self._get_type(lineno, self.get_var(lineno, value.value))
        else:
            types = {
                int: 'цел',
                float: 'вещ',
                str: 'лит',
                bool: 'лог'
            }
            return types[type(value)]
