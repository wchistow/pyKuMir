from collections.abc import Callable

from .ast_classes import (
    StoreVar,
    Output,
    Op,
    AlgStart,
    AlgEnd,
    Call,
    Input,
    IfStart,
    IfEnd,
    ElseStart,
    LoopWithCountStart,
    LoopWithCountEnd,
    LoopWhileStart,
    LoopWhileEnd,
    Statement,
    LoopForStart,
    LoopForEnd,
    Expr,
    LoopUntilStart,
    LoopUntilEnd,
    Exit,
    Assert,
    Stop,
    GetItem,
    SetItem,
    Slice,
    Use,
)
from .bytecode import Bytecode, BytecodeType
from .value import Value


def build_bytecode(
    parsed_code: list,
) -> tuple[list[BytecodeType], dict[str, list[list[BytecodeType], list[int]]]]:
    builder = BytecodeBuilder()
    return builder.build(parsed_code)


class BytecodeBuilder:
    """Преобразует АСД в байт-код."""

    def __init__(self) -> None:
        self.bytecode: list[BytecodeType] = []
        self.algs: dict[
            str,
            tuple[
                list[tuple[str, str, str]],
                str,
                str,
                list[list[BytecodeType], list[int]],
            ],
        ] = {}
        self.cur_tags: list[int] = []
        self.cur_alg: str | None = None
        self.cur_inst_n = 0
        self.cur_ns: list[BytecodeType] = []

        self.main_alg: str | None = None
        self.last_line = 0

        self._actors = {'Файлы'}

        self.loops_with_count_indexes: list[int] = []
        self.loops_while_indexes: list[int] = []
        self.loops_while_stmts: list[Expr] = []
        self.loops_for_indexes: list[int] = []
        self.loops_for: list[tuple[str, Expr, Expr, Expr]] = []
        self.loops_until_indexes: list[int] = []
        self.ifs: list[int] = []
        self.tags: dict[int, list[int]] = {}

        self.HANDLERS: dict[type[Statement], Callable[[Statement], None]] = {
            Use: self._handle_use,
            StoreVar: self._handle_store_var,
            Output: self._handle_output,
            Input: self._handle_input,
            AlgStart: self._handle_alg_start,
            AlgEnd: self._handle_alg_end,
            Call: self._handle_call,
            IfStart: self._handle_if_start,
            ElseStart: self._handle_else_start,
            IfEnd: self._handle_if_end,
            LoopWithCountStart: self._handle_loop_with_count_start,
            LoopWithCountEnd: self._handle_loop_with_count_end,
            LoopWhileStart: self._handle_loop_while_start,
            LoopWhileEnd: self._handle_loop_while_end,
            LoopForStart: self._handle_loop_for_start,
            LoopForEnd: self._handle_loop_for_end,
            LoopUntilStart: self._handle_loop_until_start,
            LoopUntilEnd: self._handle_loop_until_end,
            Exit: self._handle_exit,
            Assert: self._handle_assert,
            Stop: self._handle_stop,
            SetItem: self._handle_set_item,
        }

    def build(self, parsed_code: list[Statement]) -> tuple[list[BytecodeType], dict]:
        self.tags = _get_all_statements_tags(parsed_code)

        self.bytecode.append((0, Bytecode.USE, ('__builtins__',)))
        self.bytecode.append((0, Bytecode.USE, ('Файлы',)))
        for i, stmt in enumerate(parsed_code):
            if self.cur_alg is not None:
                self.cur_ns = self.algs[self.cur_alg][3][0]
            else:
                self.cur_ns = self.bytecode

            self.HANDLERS[type(stmt)](stmt)

        if self.main_alg is not None:
            self.bytecode.append((self.last_line, Bytecode.CALL, (self.main_alg, 0)))

        return self.bytecode, self.algs

    def _handle_use(self, stmt: Use) -> None:
        name = stmt.name
        if name not in self._actors:
            self.bytecode.append((stmt.lineno, Bytecode.USE, (name,)))
            self._actors.add(name)

    def _handle_store_var(self, stmt: StoreVar) -> None:
        if stmt.typename is not None and 'таб' in stmt.typename:
            for name, value in zip(stmt.names, stmt.value):
                for indexes in value[::-1]:
                    self.cur_ns.extend(self._expr_bc(stmt.lineno, indexes[0]))
                    self.cur_ns.extend(self._expr_bc(stmt.lineno, indexes[1]))
                self.cur_ns.append((stmt.lineno, Bytecode.MAKE_TABLE, (stmt.typename, len(value))))
                self.cur_ns.append((stmt.lineno, Bytecode.STORE, (stmt.typename, name)))
                self.cur_inst_n += 2
            return
        elif stmt.value is not None:
            self.cur_ns.extend(self._expr_bc(stmt.lineno, stmt.value))
        else:
            self.cur_ns.append((stmt.lineno, Bytecode.LOAD_CONST, (None,)))
            self.cur_inst_n += 1
        self.cur_ns.append((stmt.lineno, Bytecode.STORE, (stmt.typename, stmt.names)))
        self.cur_inst_n += 1

    def _handle_output(self, stmt: Output) -> None:
        for expr in stmt.exprs:
            self.cur_ns.extend(self._expr_bc(stmt.lineno, expr))
        self.cur_ns.append((stmt.lineno, Bytecode.OUTPUT, (len(stmt.exprs),)))
        self.cur_inst_n += 1

    def _handle_input(self, stmt: Input) -> None:
        targets = []
        for target in stmt.targets:
            if isinstance(target, str):
                targets.append(target)
            elif isinstance(target, GetItem):
                for index in target.indexes:
                    self.cur_ns.extend(self._expr_bc(stmt.lineno, index))
                targets.append((target.table_name, len(target.indexes)))
        self.cur_ns.append((stmt.lineno, Bytecode.INPUT, tuple(targets)))
        self.cur_inst_n += 1

    def _handle_alg_start(self, stmt: AlgStart) -> None:
        self.algs[stmt.name] = (stmt.args, stmt.ret_type, stmt.ret_name, [[], []])
        self.cur_alg = stmt.name
        if stmt.is_main:
            self.main_alg = stmt.name
        self.cur_inst_n = 0

    def _handle_alg_end(self, stmt: AlgEnd) -> None:
        self.cur_ns.append((stmt.lineno, Bytecode.RET, ()))
        self.cur_inst_n += 1
        self.algs[self.cur_alg][3][1] = self.cur_tags[:]
        self.cur_tags.clear()
        self.cur_alg = None

    def _handle_call(self, stmt: Call) -> None:
        for arg in stmt.args:
            self.cur_ns.extend(self._expr_bc(stmt.lineno, arg))
        self.cur_ns.append((stmt.lineno, Bytecode.CALL, (stmt.alg_name, len(stmt.args))))
        self.cur_inst_n += 1

    def _handle_if_start(self, stmt: IfStart) -> None:
        self.ifs.append(id(stmt))
        self.cur_ns.extend(self._expr_bc(stmt.lineno, stmt.cond))
        self.cur_ns.append((stmt.lineno, Bytecode.JUMP_TAG_IF_FALSE, (self.tags[id(stmt)][0],)))
        self.cur_inst_n += 1

    def _handle_else_start(self, stmt: ElseStart) -> None:
        self.cur_ns.append((stmt.lineno, Bytecode.JUMP_TAG, (self.tags[self.ifs.pop()][-1],)))
        self.cur_inst_n += 1
        self.cur_tags.append(self.cur_inst_n)

    def _handle_if_end(self, _: IfEnd) -> None:
        self.cur_tags.append(self.cur_inst_n)

    def _handle_loop_with_count_start(self, stmt: LoopWithCountStart) -> None:
        self.loops_with_count_indexes.append(id(stmt))
        self.cur_ns.extend(self._expr_bc(stmt.lineno, stmt.count))
        self.cur_ns.append((stmt.lineno, Bytecode.STORE, ('цел', (str(id(stmt)),))))
        self.cur_ns.extend(self._loop_with_count_cond(stmt.lineno, str(id(stmt))))
        self.cur_ns.append((stmt.lineno, Bytecode.JUMP_TAG_IF_FALSE, (self.tags[id(stmt)][1],)))
        self.cur_inst_n += 2
        self.cur_tags.append(self.cur_inst_n)

    def _handle_loop_with_count_end(self, stmt: LoopWithCountEnd) -> None:
        stmt_tags = self.tags[self.loops_with_count_indexes[-1]]
        self.cur_tags.append(self.cur_inst_n)
        self.cur_ns.extend(self._loop_with_count_cond(stmt.lineno, str(self.loops_with_count_indexes.pop())))
        self.cur_ns.append((stmt.lineno, Bytecode.JUMP_TAG_IF_TRUE, (stmt_tags[0],)))
        self.cur_inst_n += 2
        self.cur_tags.append(self.cur_inst_n)

    def _handle_loop_while_start(self, stmt: LoopWhileStart) -> None:
        self.loops_while_stmts.append(stmt.cond)
        self.loops_while_indexes.append(id(stmt))
        self.cur_ns.extend(self._expr_bc(stmt.lineno, stmt.cond))
        self.cur_ns.append((stmt.lineno, Bytecode.JUMP_TAG_IF_FALSE, (self.tags[id(stmt)][1],)))
        self.cur_inst_n += 1
        self.cur_tags.append(self.cur_inst_n)

    def _handle_loop_while_end(self, stmt: LoopWhileEnd) -> None:
        stmt_tags = self.tags[self.loops_while_indexes.pop()]
        self.cur_tags.append(self.cur_inst_n)
        self.cur_ns.extend(self._expr_bc(stmt.lineno, self.loops_while_stmts.pop()))
        self.cur_ns.append((stmt.lineno, Bytecode.JUMP_TAG_IF_TRUE, (stmt_tags[0],)))
        self.cur_inst_n += 2
        self.cur_tags.append(self.cur_inst_n)

    def _handle_loop_for_start(self, stmt: LoopForStart) -> None:
        self.loops_for_indexes.append(id(stmt))
        self.loops_for.append((stmt.target, stmt.from_expr, stmt.to_expr, stmt.step))
        self.cur_ns.extend(self._expr_bc(stmt.lineno, stmt.from_expr))
        self.cur_ns.append((stmt.lineno, Bytecode.STORE, ('цел', (stmt.target,))))
        self.cur_ns.append((stmt.lineno, Bytecode.LOAD_NAME, (stmt.target,)))
        self.cur_ns.extend(self._expr_bc(stmt.lineno, stmt.to_expr))
        self.cur_ns.append((stmt.lineno, Bytecode.BIN_OP, ('<=',)))
        self.cur_ns.append((stmt.lineno, Bytecode.JUMP_TAG_IF_FALSE, (self.tags[id(stmt)][1],)))
        self.cur_inst_n += 4
        self.cur_tags.append(self.cur_inst_n)

    def _handle_loop_for_end(self, stmt: LoopForEnd) -> None:
        stmt_tags = self.tags[self.loops_for_indexes.pop()]
        loop = self.loops_for.pop()
        self.cur_tags.append(self.cur_inst_n)
        self.cur_ns.extend(self._expr_bc(stmt.lineno, loop[1]))
        self.cur_ns.extend(self._loop_for_cond(stmt.lineno, loop[0], loop[2], loop[3]))
        self.cur_ns.append((stmt.lineno, Bytecode.JUMP_TAG_IF_TRUE, (stmt_tags[0],)))
        self.cur_inst_n += 2
        self.cur_tags.append(self.cur_inst_n)

    def _handle_loop_until_start(self, stmt: LoopUntilStart) -> None:
        self.loops_until_indexes.append(id(stmt))
        self.cur_tags.append(self.cur_inst_n)

    def _handle_loop_until_end(self, stmt: LoopUntilEnd) -> None:
        stmt_tags = self.tags[self.loops_until_indexes.pop()]
        self.cur_ns.extend(self._expr_bc(stmt.lineno, stmt.cond))
        self.cur_ns.append((stmt.lineno, Bytecode.JUMP_TAG_IF_TRUE, (stmt_tags[0],)))
        self.cur_inst_n += 1
        self.cur_tags.append(self.cur_inst_n)

    def _handle_exit(self, stmt: Exit) -> None:
        loops = (
            self.loops_with_count_indexes + self.loops_while_indexes + self.loops_for_indexes + self.loops_until_indexes
        )
        if loops:
            last_loop_i = max(loops)
            loop_tags = self.tags[last_loop_i]
            self.cur_ns.append((stmt.lineno, Bytecode.JUMP_TAG, (loop_tags[-1],)))
            self.cur_inst_n += 1
        else:
            self.cur_ns.append((stmt.lineno, Bytecode.RET, ()))
            self.cur_inst_n += 1

    def _handle_assert(self, stmt: Assert) -> None:
        self.cur_ns.extend(self._expr_bc(stmt.lineno, stmt.expr))
        self.cur_ns.append((stmt.lineno, Bytecode.ASSERT, ()))
        self.cur_inst_n += 1

    def _handle_stop(self, stmt: Stop) -> None:
        self.cur_ns.append((stmt.lineno, Bytecode.STOP, ()))
        self.cur_inst_n += 1

    def _handle_set_item(self, stmt: SetItem) -> None:
        self.cur_ns.extend(self._expr_bc(stmt.lineno, stmt.expr))
        for index in stmt.indexes:
            self.cur_ns.extend(self._expr_bc(stmt.lineno, index))
        self.cur_ns.append((stmt.lineno, Bytecode.SET_ITEM, (stmt.table_name, len(stmt.indexes))))
        self.cur_inst_n += 1

    def _loop_with_count_cond(self, lineno: int, loop_name: str) -> list[BytecodeType]:
        res = [
            (lineno, Bytecode.LOAD_NAME, (loop_name,)),
            (lineno, Bytecode.LOAD_CONST, (Value('цел', 1),)),
            (lineno, Bytecode.BIN_OP, ('-',)),
            (lineno, Bytecode.STORE, (None, (loop_name,))),
            (lineno, Bytecode.LOAD_NAME, (loop_name,)),
            (lineno, Bytecode.LOAD_CONST, (Value('цел', -1),)),
            (lineno, Bytecode.BIN_OP, ('>',)),
        ]
        self.cur_inst_n += 7
        return res

    def _loop_for_cond(self, lineno: int, target: str, to_expr: Expr, step: Expr) -> list[BytecodeType]:
        res = [
            (lineno, Bytecode.LOAD_NAME, (target,)),
            *self._expr_bc(lineno, step),
            (lineno, Bytecode.BIN_OP, ('+',)),
            (lineno, Bytecode.STORE, (None, (target,))),
            (lineno, Bytecode.LOAD_NAME, (target,)),
            *self._expr_bc(lineno, to_expr),
            (lineno, Bytecode.BIN_OP, ('<=',)),
        ]
        self.cur_inst_n += 5
        return res

    def _expr_bc(self, lineno: int, expr: Expr) -> list[BytecodeType]:
        """
        Превращает обратную польскую запись вида `(2, 3, Op(op='+'))`
        в набор команд байт-кода вида `LOAD 2, LOAD 3, BIN_OP +`.
        """
        res: list[BytecodeType] = []
        for v in expr:
            if isinstance(v, Op):
                if v.unary:
                    res.append((lineno, Bytecode.UNARY_OP, (v.op,)))
                else:
                    res.append((lineno, Bytecode.BIN_OP, (v.op,)))
            elif isinstance(v, Call):
                self._handle_call(v)
                self.cur_inst_n -= 1
            elif isinstance(v, GetItem):
                self.cur_ns.append((v.lineno, Bytecode.LOAD_NAME, (v.table_name,)))
                self.cur_inst_n += 1
                for index in v.indexes:
                    self.cur_ns.extend(self._expr_bc(v.lineno, index))
                    self.cur_ns.append((v.lineno, Bytecode.GET_ITEM, ()))
                    self.cur_inst_n += 1
            elif isinstance(v, Slice):
                self.cur_ns.append((v.lineno, Bytecode.LOAD_NAME, (v.name,)))
                self.cur_inst_n += 1
                for index in v.indexes:
                    self.cur_ns.extend(self._expr_bc(v.lineno, index))
                self.cur_ns.append((v.lineno, Bytecode.MAKE_SLICE, (v.name,)))
                self.cur_inst_n += 1
            elif v.typename == 'get-name':
                res.append((lineno, Bytecode.LOAD_NAME, (v.value,)))
            elif isinstance(v, Value):
                res.append((lineno, Bytecode.LOAD_CONST, (v,)))
            self.cur_inst_n += 1
        return res


def _get_all_statements_tags(parsed: list[Statement]) -> dict[int, list[int]]:
    """
    :return: словарь вида `{индекс_инструкции: [список тегов, которые она должна использовать]}`
    """
    res = {}
    ifs = []
    loops = []

    cur_tag_n = 0

    for stmt in parsed:
        if isinstance(stmt, IfStart):
            ifs.append(id(stmt))
            res[id(stmt)] = []
        elif isinstance(stmt, (LoopWithCountStart, LoopWhileStart, LoopForStart, LoopUntilStart)):
            loops.append(id(stmt))
            res[id(stmt)] = [cur_tag_n]
            cur_tag_n += 1

        elif isinstance(stmt, ElseStart):
            res[ifs[-1]].append(cur_tag_n)
            cur_tag_n += 1
        elif isinstance(stmt, IfEnd):
            res[ifs.pop()].append(cur_tag_n)
            cur_tag_n += 1
        elif isinstance(stmt, (LoopWithCountEnd, LoopWhileEnd, LoopForEnd, LoopUntilEnd)):
            res[loops.pop()].append(cur_tag_n)
            cur_tag_n += 1

        if isinstance(stmt, AlgEnd):
            cur_tag_n = 0

    return res
