import re
from collections.abc import Callable
from pathlib import Path
from typing import TypeAlias, Any, TextIO

from .actors import actors
from .actors.base import KumirFunc, KumirValue
from .bytecode import Bytecode, BytecodeType
from .exceptions import RuntimeException
from .value import Value

Namespace: TypeAlias = dict[str, tuple[str, Value | None]]


class VM:
    def __init__(
        self,
        bytecode: list[BytecodeType],
        output_f: Callable[[str], None],
        input_f: Callable[[], str],
        algs: dict[
            str,
            tuple[
                list[tuple[str, str, str]],
                str,
                list[list[BytecodeType], list[int]],
            ],
        ]
        | None = None,
        work_dir: str = Path.home() / 'Kumir',
        cur_dir: str | None = None,
        cur_file: str | None = None,
    ) -> None:
        """
        :param bytecode: список команд байт-кода
        :param output_f: функция, в неё передаётся строка для вывода
        :param input_f: функция, вызывается для получения ввода пользователя
        :param algs: словарь алгоритмов в программе
        """
        self.output_f = output_f
        self.input_f = input_f
        self.bytecode = bytecode
        self.algs = algs or {}
        self.actors_algs: dict[
            str,
            tuple[
                list[tuple[str, str, str]],
                str,
                Callable[[list[Value]], Value | None] | Callable[[list[KumirValue], Any], KumirValue | None],
            ],
        ] = {}

        self.work_dir = work_dir
        self.cur_dir = cur_dir
        self.cur_file = cur_file

        self.glob_vars: Namespace = {'нс': ('лит', Value('лит', '\n'))}
        self.stack: list[Value | None] = []

        # Локальные переменные текущих функций
        self.call_stack: list[Namespace] = []
        self.in_alg = False

        self.cur_tags: list[int] = []

        self.cur_algs: list[str] = []
        self.cur_algs_inst_n: list[int] = [0]

        self.res_vars: list[str] = []

        self.stopped = False

        self.CALL_TRANSITIONS = {
            Bytecode.LOAD_CONST: lambda inst: self.stack.append(inst[2][0]),
            Bytecode.LOAD_NAME: lambda inst: self.load_name(inst[0], inst[2][0]),
            Bytecode.MAKE_TABLE: lambda inst: self.make_table(*inst[2]),
            Bytecode.BIN_OP: lambda inst: self.bin_op(inst[0], inst[2][0]),
            Bytecode.UNARY_OP: lambda inst: self.unary_op(inst[0], inst[2][0]),
            Bytecode.STORE: lambda inst: self.store_var(inst[0], inst[2][0], inst[2][1]),
            Bytecode.OUTPUT: lambda inst: self.output(inst[0], inst[2][0]),
            Bytecode.INPUT: lambda inst: self.input(inst[0], inst[2]),
            Bytecode.SET_RES_VAR: lambda inst: self.res_vars.append(inst[2][0]),
            Bytecode.CALL: lambda inst: self.call(inst[0], inst[2][0]),
            Bytecode.RET: lambda inst: self.ret(inst[0]),
            Bytecode.JUMP_TAG: lambda inst: self.jump_tag(inst[2][0]),
            Bytecode.JUMP_TAG_IF_FALSE: lambda inst: self.jump_tag_if_false(inst[0], inst[2][0]),
            Bytecode.JUMP_TAG_IF_TRUE: lambda inst: self.jump_tag_if_true(inst[0], inst[2][0]),
            Bytecode.ASSERT: lambda inst: self.assert_(inst[0]),
            Bytecode.STOP: lambda inst: self.stop(),
            Bytecode.GET_ITEM: lambda inst: self.get_item(inst[0]),
            Bytecode.SET_ITEM: lambda inst: self.set_item(inst[0], *inst[2]),
            Bytecode.MAKE_SLICE: lambda inst: self.slice(inst[0]),
            Bytecode.USE: lambda inst: self.use(inst[2][0]),
        }

        self.INSTS_WITHOUT_INCREASE_COUNTER = {
            Bytecode.JUMP_TAG,
            Bytecode.JUMP_TAG_IF_FALSE,
            Bytecode.JUMP_TAG_IF_TRUE,
        }

    def execute(self) -> None:
        self._execute(self.bytecode)

    def _execute(self, bc: list[BytecodeType]) -> None:
        while self.cur_algs_inst_n[-1] < len(bc):
            inst = bc[self.cur_algs_inst_n[-1]]
            self.CALL_TRANSITIONS[inst[1]](inst)
            if inst[1] == Bytecode.RET:
                break
            elif inst[1] == Bytecode.STOP:
                self.stopped = True
                break
            if inst[1] not in self.INSTS_WITHOUT_INCREASE_COUNTER:
                self.cur_algs_inst_n[-1] += 1

            if self.stopped:
                break

    def store_var(self, lineno: int, typename: str | None, names: tuple[str]) -> None:
        """
        Обрабатывает инструкцию STORE
        :param lineno: номер текущей строки
        :param typename: тип переменной(ых), `None`, если нужно сохранить значения в уже объявленную переменную
        :param names: имя/имена переменной(ых)
        """
        if self.cur_algs:
            for arg in self.algs[self.cur_algs[-1]][0]:
                if arg[0] == 'арг' and arg[2] in names:
                    raise RuntimeException(lineno, 'нельзя присвоить аргументу')
        value = self.stack.pop()
        if typename is None:  # сохранение значения в уже объявленную переменную
            if not self._var_defined(names[0]):
                raise RuntimeException(lineno, f'имя "{names[0]}" не определено')
            var = self._get_all_namespaces()[names[0]]
            self._save_var(lineno, var[0], names[0], value)
            return
        if len(names) == 1:
            self._save_var(lineno, typename, names[0], value)
        else:  # объявление нескольких переменных (`цел а, б`)
            for name in names:
                self._save_var(lineno, typename, name, None)

    def load_name(self, lineno: int, name: str) -> None:
        try:
            var = self.get_var(lineno, name)
        except RuntimeException as e1:
            if re.fullmatch(r'имя "[\w ]+" не определено \(строка \d+\)', e1.args[0]) is not None:
                try:
                    self.call(lineno, name)
                except RuntimeException as e2:
                    raise e2 from None
            else:
                raise e1 from None
        else:
            self.stack.append(var)

    def make_table(self, typename: str, length: int) -> None:
        indexes: list[tuple[int, int]] = []
        for _ in range(length):
            last_i = self.stack.pop().value
            first_i = self.stack.pop().value
            indexes.append((first_i, last_i))
        self.stack.append(Value(typename, self._build_table(indexes, len(indexes))))

    def _build_table(self, indexes: list[tuple[int, int]], depth: int):
        start_i, last_i = indexes[0]
        return {
            i: None if depth == 1 else self._build_table(indexes[1:], depth - 1) for i in range(start_i, last_i + 1)
        }

    def bin_op(self, lineno: int, op: str) -> None:
        """
        Обрабатывает инструкцию BIN_OP
        :param lineno: номер текущей строки
        :param op: оператор, например `'+'`
        """
        a = self.stack.pop()
        b = self.stack.pop()
        typename = a.typename

        # операции над разными типами можно проводить, только если это цел или вещ
        if sorted((a.typename, b.typename)) == ['вещ', 'цел']:
            typename = 'вещ'
        elif sorted((a.typename, b.typename)) == ['лит', 'сим']:
            typename = 'лит'
        elif a.typename != b.typename:
            raise RuntimeException(lineno, f'нельзя "{b.typename} {op} {a.typename}"')

        if op == '+' and a.typename in ('цел', 'вещ', 'лит'):
            self.stack.append(Value(typename, b.value + a.value))
        elif op == '+' and a.typename in ('сим', 'лит'):
            self.stack.append(Value('лит', b.value + a.value))  # <сим> + <сим> = <лит>
        elif op == '-' and a.typename in ('цел', 'вещ'):
            self.stack.append(Value(typename, b.value - a.value))
        elif op == '*' and a.typename in ('цел', 'вещ'):
            self.stack.append(Value(typename, b.value * a.value))
        elif op == '/' and a.typename in ('цел', 'вещ'):
            self.stack.append(Value('вещ', b.value / a.value))
        elif op == '**' and a.typename in ('цел', 'вещ'):
            self.stack.append(Value(typename, b.value**a.value))
        elif op == '>=' and a.typename in ('цел', 'вещ'):
            self.stack.append(Value('лог', _bool_to_str(b.value >= a.value)))
        elif op == '<=' and a.typename in ('цел', 'вещ'):
            self.stack.append(Value('лог', _bool_to_str(b.value <= a.value)))
        elif op == '=':
            self.stack.append(Value('лог', _bool_to_str(b.value == a.value)))
        elif op == '<>':
            self.stack.append(Value('лог', _bool_to_str(b.value != a.value)))
        elif op == '>':
            self.stack.append(Value('лог', _bool_to_str(b.value > a.value)))
        elif op == '<':
            self.stack.append(Value('лог', _bool_to_str(b.value < a.value)))
        elif op == 'или' and typename == 'лог':
            self.stack.append(Value('лог', _bool_to_str(_str_to_bool(b.value) or _str_to_bool(a.value))))
        elif op == 'и' and typename == 'лог':
            self.stack.append(Value('лог', _bool_to_str(_str_to_bool(b.value) and _str_to_bool(a.value))))
        else:
            raise RuntimeException(lineno, f'нельзя "{b.typename} {op} {a.typename}"')

    def unary_op(self, lineno: int, op: str) -> None:
        a = self.stack.pop()
        if op == 'не':
            if a.typename != 'лог':
                raise RuntimeException(lineno, f'нельзя "не {a.typename}"')
            self.stack.append(Value('лог', _bool_to_str(not _str_to_bool(a.value))))
        elif op in ('+', '-'):
            if a.typename not in ('цел', 'вещ'):
                raise RuntimeException(lineno, f'нельзя "{op}{a.typename}"')

            if op == '-':
                self.stack.append(Value(a.typename, -a.value))
            else:
                self.stack.append(a)

    def output(self, lineno: int, exprs_num: int) -> None:
        """
        Обрабатывает инструкцию OUTPUT
        :param exprs_num: количество выражений, которых нужно вывести (они загружаются из стека)
        """
        to_file: TextIO | None = None
        exprs = [self.stack.pop() for _ in range(exprs_num)][::-1]
        if exprs[0].typename == 'файл':
            to_file = exprs[0].value
            exprs = exprs[1:]
        if any('таб' in expr.typename for expr in exprs):
            raise RuntimeException(lineno, 'нет индексов у таблицы')

        text = ''.join(map(lambda e: str(e.value), exprs))
        if to_file is None:
            self.output_f(text)
        else:
            to_file.write(text)

    def input(self, lineno: int, targets: list[str | tuple[str, int]]) -> None:
        """
        Обрабатывает инструкцию INPUT
        :param lineno: номер текущей строки кода
        :param targets: список имён переменных, в которые необходимо записать ввод пользователя
        """
        from_file: str | None = None

        cur_target_i = 0
        while cur_target_i < len(targets):
            indexes = []
            target = targets[cur_target_i]

            (target_var, target_var_type, target_var_name, new_indexes) = self._get_target(lineno, target)
            indexes.extend(new_indexes)

            if cur_target_i == 0 and target_var_type == 'файл':
                from_file = target_var[1].value
                cur_target_i += 1
                continue

            if from_file is None:
                inputted = self.input_f()
            else:
                inputted = from_file.read()

            if target_var_type == 'лит':
                self._save_inputted(
                    lineno,
                    target_var_type,
                    target_var_name,
                    _convert_string_to_type(lineno, inputted, target_var_type),
                    indexes,
                )
                cur_target_i += 1
            elif 'таб' in target_var_type:
                self._save_inputted(
                    lineno,
                    target_var_type,
                    target_var_name,
                    _convert_string_to_type(lineno, inputted, target_var_type.removesuffix('таб')),
                    indexes,
                )
                cur_target_i += 1
            else:
                for text in inputted.split(' '):
                    if cur_target_i >= len(targets):
                        break
                    target = targets[cur_target_i]
                    (target_var, target_var_type, target_var_name, new_indexes) = self._get_target(lineno, target)
                    self._save_inputted(
                        lineno,
                        target_var_type,
                        target_var_name,
                        _convert_string_to_type(lineno, text, target_var_type),
                        indexes,
                    )
                    cur_target_i += 1

    def _get_target(self, lineno: int, target: str | tuple[str, int]):
        indexes = []
        if isinstance(target, str):
            try:
                target_var = self._get_all_namespaces()[target]
            except KeyError:
                raise RuntimeException(lineno, f'имя "{target}" не определено') from None
            target_var_type = target_var[0]
            target_var_name = target
        else:
            target_var_name = target[0]
            for _ in range(target[1]):
                index = self.stack.pop()
                if index.typename != 'цел':
                    raise RuntimeException(lineno, 'индекс - не целое число')
                indexes.append(index.value)
            target_var = self._get_all_namespaces()[target_var_name]
            target_var_type = target_var[0]

        return target_var, target_var_type, target_var_name, indexes

    def _save_inputted(
        self,
        lineno: int,
        var_type: str,
        var_name: str,
        value: Value,
        indexes: list[int],
    ) -> None:
        if indexes:
            var = self._get_all_namespaces()[var_name][1]
            self._set_item_table(lineno, var_name, indexes, value, var)
        else:
            self._save_var(lineno, var_type, var_name, value)

    def call(self, lineno: int, name: str) -> None:
        """
        Обрабатывает инструкцию CALL
        :param lineno: номер текущей строки кода
        :param name: имя алгоритма, который нужно вызвать
        """
        if name in self.algs:
            alg = self.algs[name]
            self.call_stack.append(self._load_args(lineno, alg[0]))
            if alg[1]:  # ret_type
                self.call_stack[-1]['знач'] = (alg[1], None)

            for arg in alg[0]:
                if arg[0] == 'рез':
                    self.call_stack[-1][arg[2]] = (arg[1], None)

            self.in_alg = True
            self.cur_tags = alg[2][1]
            self.cur_algs.append(name)
            self.cur_algs_inst_n.append(0)
            self._execute(alg[2][0])
        elif name in self.actors_algs:
            alg = self.actors_algs[name]
            args = self._load_args(lineno, alg[0])
            py_args = [arg[1] for arg in args.values()]
            try:
                ret_v = alg[2](py_args, **self._get_extra_args(name))
            except RuntimeException as e:
                raise RuntimeException(lineno, ' '.join(e.args[0].split()[:-2])) from None
            else:
                if isinstance(ret_v, Value):
                    self.stack.append(ret_v)
                elif isinstance(ret_v, dict):
                    self.stack.append(ret_v['знач'])
                    for arg in self.actors_algs[name][0]:
                        if arg[0] == 'рез':
                            self.call_stack[-1][arg[2]] = (arg[1], ret_v[arg[2]])
        else:
            raise RuntimeException(lineno, f'имя "{name}" не определено')

    def ret(self, lineno: int):
        ret_type = self.algs[self.cur_algs[-1]][1]
        if ret_type:
            ret_v = self.call_stack[-1]['знач'][1]
            if ret_v is not None:
                self.stack.append(ret_v)
            else:
                raise RuntimeException(lineno, 'функция должна возвращать значение')
        for arg in self.algs[self.cur_algs[-1]][0]:
            if 'рез' in arg[0]:
                if arg[2] in self.call_stack[-1]:
                    self.call_stack[-2][self.res_vars.pop()] = self.call_stack[-1][arg[2]]

        self.cur_algs.pop()
        if self.cur_algs:
            self.cur_tags = self.algs[self.cur_algs[-1]][2][1]
        self.cur_algs_inst_n.pop()
        self.call_stack.pop()

    def jump_tag(self, tag: int) -> None:
        self.cur_algs_inst_n[-1] = self.cur_tags[tag]

    def jump_tag_if_false(self, lineno: int, tag: int) -> None:
        cond = self.stack.pop()
        if cond.typename != 'лог':
            raise RuntimeException(lineno, 'условие не логическое')
        if cond.value == 'нет':
            self.jump_tag(tag)
        else:
            self.cur_algs_inst_n[-1] += 1

    def jump_tag_if_true(self, lineno: int, tag: int) -> None:
        cond = self.stack.pop()
        if cond.typename != 'лог':
            raise RuntimeException(lineno, 'условие не логическое')
        if cond.value == 'да':
            self.jump_tag(tag)
        else:
            self.cur_algs_inst_n[-1] += 1

    def assert_(self, lineno: int) -> None:
        cond = self.stack.pop()
        if cond.typename != 'лог':
            raise RuntimeException(lineno, 'условие не логическое')
        if cond.value == 'нет':
            raise RuntimeException(lineno, 'условие ложно')

    def stop(self) -> None:
        self.output_f('СТОП.')

    def get_item(self, lineno: int) -> None:
        index = self.stack.pop()
        _check_index_type(lineno, index)

        var = self.stack.pop()
        if 'таб' in var.typename:
            _check_table_index(lineno, index.value, var.value)
            res = var.value[index.value]
            if isinstance(res, dict):
                res = Value(var.typename, res)
        elif var.typename == 'лит':
            _check_str_index(lineno, index, var.value)
            res = Value('сим', var.value[index.value - 1])
        else:
            raise RuntimeException(lineno, 'лишние индексы')

        if res is None:
            raise RuntimeException(lineno, 'значение элемента таблицы не определено')
        self.stack.append(res)

    def set_item(self, lineno: int, name: str, len_indexes: int) -> None:
        indexes: list[int] = []
        for _ in range(len_indexes):
            index = self.stack.pop()
            _check_index_type(lineno, index)
            indexes.append(index.value)
        indexes.reverse()

        value = self.stack.pop()
        var = self.get_var(lineno, name)
        if 'таб' in var.typename:
            self._set_item_table(lineno, name, indexes, value, var)
        elif var.typename == 'лит':
            if len(indexes) > 1:
                raise RuntimeException(lineno, 'лишние индексы')
            self._set_item_str(lineno, name, indexes[0], value, var)
        else:
            raise RuntimeException(lineno, 'лишние индексы')

    def _set_item_table(self, lineno: int, var_name: str, indexes: list[int], value: Value, var: Value) -> None:
        table_type = var.typename.removesuffix('таб')
        if table_type != value.typename:
            raise RuntimeException(lineno, f'нельзя "{table_type} := {value.typename}"')

        table_part = var.value
        for index in indexes[:-1]:
            _check_table_index(lineno, index, table_part)
            table_part = table_part[index]

        _check_table_index(lineno, indexes[-1], table_part)
        table_part[indexes[-1]] = value

        self._save_var(lineno, var.typename, var_name, Value(var.typename, var.value))

    def _set_item_str(self, lineno: int, var_name: str, index: int, value: Value, var: Value) -> None:
        if value.typename == 'сим' or (value.typename == 'лит' and len(value.value) == 1):
            new_val = var.value
            new_val = new_val[: index - 1] + value.value + new_val[index:]
            self._save_var(lineno, var.typename, var_name, Value('лит', new_val))
        else:
            raise RuntimeException(lineno, f'нельзя "сим := {value.typename}"')

    def slice(self, lineno: int) -> None:
        end = self.stack.pop()
        start = self.stack.pop()

        var = self.stack.pop()
        if var.typename != 'лит':
            raise RuntimeException(lineno, 'лишние индексы')

        _check_str_index(lineno, start, var.value)
        _check_str_index(lineno, end, var.value)

        if start.value > end.value:
            res = ''
        else:
            res = var.value[start.value - 1 : end.value]

        self.stack.append(Value('лит', res))

    def use(self, actor_name: str) -> None:
        self._load_actors_vars(actors[actor_name].vars)
        self._load_actors_algs(actors[actor_name].funcs)

    def _load_actors_vars(self, actor_vars: dict[str, tuple[str, KumirValue]]) -> None:
        for name, var in actor_vars.items():
            self.glob_vars[name] = var

    def _load_actors_algs(self, funcs: dict[str, KumirFunc]) -> None:
        for name, func in funcs.items():
            self.actors_algs[name] = (func.args, func.ret_type, func.py_func)

    def _load_args(self, lineno: int, args: list[tuple[str, str, str]]) -> Namespace:
        res: Namespace = {}
        args_values = []
        for arg in args:
            if arg[0] != 'рез':
                args_values.append(self.stack.pop())
        for arg, value in zip(args, args_values[::-1]):
            if arg[1] != value.typename:
                raise RuntimeException(lineno, 'неправильный тип аргумента')
            res[arg[2]] = (arg[1], value)
        return res

    def _save_var(self, lineno: int, typename: str, name: str, value: Value | None) -> None:
        """
        Создаёт переменную
        :param lineno: номер текущей строки кода
        :param typename: тип переменной
        :param name: имя переменной
        :param value: значение переменной (`None` - объявлена, но не определена)
        """
        namespace = self.call_stack[-1] if self.in_alg else self.glob_vars
        if value is None:
            namespace[name] = (typename, None)
            return
        value_type = value.typename
        if value_type == typename:  # типы целевой переменной и значения совпадают
            namespace[name] = (typename, value)
        else:
            raise RuntimeException(lineno, message=f'нельзя "{typename} := {value_type}"')

    def get_var(self, lineno: int, name: str) -> Value:
        """
        :param lineno: номер текущей строки кода
        :param name: имя переменной
        :return: экземпляр класса `Value` - значение переменной
        :raise: RuntimeException - если имя не определено
        """
        var = _find_var_in_namespace(lineno, name, self._get_all_namespaces())
        if var is not None:
            return var
        raise RuntimeException(lineno, f'имя "{name}" не определено')

    def _var_defined(self, name: str) -> bool:
        """
        :param name: имя переменной
        :return: `True`, если имя объявлено, иначе `False`
        """
        return name in self._get_all_namespaces()

    def _get_all_namespaces(self) -> Namespace:
        """
        :return: словарь - все доступные переменные
        """
        res = self.glob_vars
        if self.call_stack:
            res |= self.call_stack[-1]
        return res

    def _get_extra_args(self, name: str) -> dict[str, ...]:
        extra_args = {}
        if name in ('РАБОЧИЙ КАТАЛОГ', 'создать каталог', 'полный путь'):
            extra_args['work_dir'] = self.work_dir
        elif name == 'КАТАЛОГ ПРОГРАММЫ':
            extra_args['prog_dir'] = self.cur_dir
        return extra_args


def _str_to_bool(v: str) -> bool:
    return v == 'да'


def _bool_to_str(b: bool) -> str:
    return 'да' if b else 'нет'


def _check_str_index(lineno: int, index: Value, string: str) -> None:
    _check_index_type(lineno, index)
    val = index.value
    if val > len(string):
        raise RuntimeException(lineno, 'индекс символа больше длины строки')
    if val < 0:
        raise RuntimeException(lineno, 'отрицательный индекс')


def _check_table_index(lineno: int, index: int, table: dict[int, Value | None]) -> None:
    if index not in table:
        raise RuntimeException(lineno, 'выход за границу таблицы')


def _check_index_type(lineno: int, index: Value) -> None:
    if index.typename != 'цел':
        raise RuntimeException(lineno, 'индекс - не целое число')


def _convert_string_to_type(lineno: int, string: str, var_type: str) -> Value:
    """
    Преобразует строку в значение языка КуМир в зависимости от переданного типа
    :param string: исходная строка
    :param var_type: тип, в которые необходимо преобразовать строку
    :return: экземпляр класса `Value` - значение
    """
    if var_type == 'цел':
        try:
            return Value('цел', int(string))
        except ValueError:
            raise RuntimeException(lineno, 'ошибка ввода целого числа') from None
    elif var_type == 'вещ':
        try:
            return Value('вещ', float(string))
        except ValueError:
            raise RuntimeException(lineno, 'ошибка ввода вещественного числа') from None
    elif var_type == 'лог':
        return Value('лог', string)
    elif var_type == 'лит':
        return Value('лит', string)
    elif var_type == 'сим':
        if len(string) > 1:
            raise RuntimeException(lineno, 'ошибка ввода: введено лишнее')
        return Value('сим', string)


def _find_var_in_namespace(lineno: int, name: str, namespace: Namespace) -> Value | None:
    """
    :param name: имя переменной
    :param namespace: словарь всех переменных
    :return: `None` если переменная не найдена, иначе `Value`
    :raise: RuntimeException - если переменная объявлена, но ей не присвоено значение
    """
    try:
        var = namespace[name]
    except KeyError:
        return None
    if var[1] is None:
        raise RuntimeException(lineno, 'нет значения у величины')
    return var[1]
