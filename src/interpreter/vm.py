from typing import Callable, NoReturn

from .bytecode import Bytecode, BytecodeType
from .constants import ValueType
from .exceptions import SyntaxException, RuntimeException


class VM:
    TYPES = {
            int: 'цел',
            float: 'вещ',
            str: 'лит',
            bool: 'лог'
    }

    def __init__(self,
                 bytecode: list[BytecodeType],
                 output_f: Callable[[str], None],
                 algs: dict[str, list[BytecodeType]] | None = None) -> None:
        self.output_f = output_f
        self.bytecode = bytecode
        self.algs = algs or {}

        self.glob_vars: dict[str, tuple[str, ValueType]] = {}
        self.stack: list[ValueType | None] = []

        # Локальные переменные текущих функций
        self.call_stack: list[dict[str, tuple[str, ValueType]]] = []
        self.in_alg = False

    def reset(self) -> None:
        """Сбрасывает состояние виртуальной машины."""
        self.glob_vars.clear()
        self.call_stack.clear()
        self.stack.clear()

    def execute(self) -> None:
        self._execute(self.bytecode)

    def _execute(self, bc: list[BytecodeType]) -> None:
        for inst in bc:
            if inst[1] == Bytecode.LOAD:
                self.stack.append(inst[2][0])
            elif inst[1] == Bytecode.LOAD_NAME:
                self.stack.append(self.get_var(inst[0], inst[2][0]))
            elif inst[1] == Bytecode.BIN_OP:
                self.bin_op(inst[0], inst[2][0])
            elif inst[1] == Bytecode.STORE:
                self.store_var(inst[0], inst[2][0], inst[2][1])
            elif inst[1] == Bytecode.OUTPUT:
                self.output(inst[2][0])
            elif inst[1] == Bytecode.CALL:
                self.call(inst[0], inst[2][0])
            elif inst[1] == Bytecode.RET:
                self.call_stack.pop()
                return

    def store_var(self, lineno: int, typename: str | None, names: tuple[str]) -> None:
        """Обрабатывает инструкцию STORE"""
        value = self.stack.pop()
        if len(names) > 1 and value is not None:
            raise SyntaxException(lineno, message='при нескольких переменных нельзя указывать значение')
        if typename is None:  # сохранение значения в уже объявленную переменную
            if not self._var_defined(names[0]):
                raise RuntimeException(lineno, f'имя "{names[0]}" не объявлено')
            var = self._get_all_namespaces()[names[0]]
            self._save_var(lineno, var[0], names[0], value)
            return
        if len(names) == 1:
            self._save_var(lineno, typename, names[0], value)
        else:  # объявление нескольких переменных (`цел а, б`)
            for name in names:
                self._save_var(lineno, typename, name, None)

    def bin_op(self, lineno: int, op: str) -> None:
        a = self.stack.pop()
        b = self.stack.pop()
        self._check_type_is_eq(lineno, a, b, op)
        self.stack.append(eval(f'{b} {op} {a}'))

    def output(self, exprs_num: int) -> None:
        res: list[str] = []
        for _ in range(exprs_num):
            res.append(str(self.stack.pop()))
        self.output_f(''.join(res[::-1]))

    def call(self, lineno: int, name: str) -> None:
        if name in self.algs:
            self.in_alg = True
            self.call_stack.append({})
            self._execute(self.algs[name])
        else:
            raise RuntimeException(lineno, f'имя {name} не определено')

    def _save_var(self, lineno: int, typename: str, name: str, value: ValueType | None) -> None:
        """
        Создаёт переменную типа `typename` с именем `name`
        и значением `value` (`None` - объявлена, но не определена).
        """
        namespace = self.call_stack[-1] if self.in_alg else self.glob_vars
        if value is None:
            namespace[name] = (typename, None)
            return
        value_type = self.TYPES[type(value)]
        if value_type == typename:  # типы целевой переменной и значения совпадают
            namespace[name] = (typename, value)
        else:
            raise RuntimeException(lineno, message=f'нельзя "{typename} := {value_type}"')

    def get_var(self, lineno: int, name: str) -> ValueType | NoReturn:
        var = self._find_var(lineno, name, self._get_all_namespaces())
        if var is not None:
            return var
        raise RuntimeException(lineno, 'имя не объявлено')

    def _find_var(self, lineno: int, name: str, namespace: dict) -> ValueType | None | NoReturn:
        if name == 'нс':
            return '\n'
        if name not in namespace:
            return None
        var = namespace[name]
        if var is None:
            raise RuntimeException(lineno, 'нет значения у величины')
        return var[1]

    def _var_defined(self, name: str) -> bool:
        """
        Возвращает индекс переменой с именем `name`.
        Если такой нет, возвращает -1.
        """
        if name in self._get_all_namespaces():
            return True
        return False

    def _check_type_is_eq(self, lineno: int, a: ValueType, b: ValueType, op: str) -> None:
        a_type = self.TYPES[type(a)]
        b_type = self.TYPES[type(b)]
        if a_type != b_type:
            raise RuntimeException(lineno, f'нельзя "{b_type} {op} {a_type}"')

    def _get_all_namespaces(self) -> dict:
        res = {}
        res |= self.glob_vars
        for alg_ns in self.call_stack:
            res |= alg_ns
        return res
