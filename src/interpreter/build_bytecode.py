from .ast_classes import (StoreVar, Output, Op, AlgStart, AlgEnd, Call,
                          Input, IfStart, IfEnd, ElseStart, LoopWithCountStart,
                          LoopWithCountEnd, LoopWhileStart, LoopWhileEnd, Statement, LoopForStart,
                          LoopForEnd, Expr)
from .bytecode import Bytecode, BytecodeType
from .value import Value


def build_bytecode(
        parsed_code: list
                   ) -> tuple[list[BytecodeType], dict[str, list[list[BytecodeType], list[int]]]]:
    builder = BytecodeBuilder()
    return builder.build(parsed_code)


class BytecodeBuilder:
    """Преобразует АСД в байт-код."""
    def __init__(self) -> None:
        self.bytecode: list[BytecodeType] = []
        self.algs: dict[str, list[list[BytecodeType], list[int]]] = {}
        self.cur_tags: list[int] = []
        self.cur_alg: str | None = None
        self.cur_inst_n = 0

    def build(self, parsed_code: list[Statement]) -> tuple[list[BytecodeType], dict]:
        main_alg: str | None = None
        last_line = 0

        loops_with_count = []
        loops_while_indexes = []
        loops_while_stmts = []
        loops_for_indexes = []
        loops_for = []
        ifs = []

        tags = _get_all_statements_tags(parsed_code)

        for i, stmt in enumerate(parsed_code):
            if self.cur_alg is not None:
                cur_ns = self.algs[self.cur_alg][0]
            else:
                cur_ns = self.bytecode
            if isinstance(stmt, StoreVar):
                if stmt.value is not None:
                    cur_ns.extend(self._expr_bc(stmt.lineno, stmt.value))
                else:
                    cur_ns.append((stmt.lineno, Bytecode.LOAD_CONST, (None,)))
                    self.cur_inst_n += 1
                cur_ns.append((stmt.lineno, Bytecode.STORE, (stmt.typename, stmt.names)))
                self.cur_inst_n += 1
            elif isinstance(stmt, Output):
                for expr in stmt.exprs:
                    cur_ns.extend(self._expr_bc(stmt.lineno, expr))
                cur_ns.append((stmt.lineno, Bytecode.OUTPUT, (len(stmt.exprs),)))
                self.cur_inst_n += 1
            elif isinstance(stmt, Input):
                cur_ns.append((stmt.lineno, Bytecode.INPUT, tuple(stmt.targets)))
                self.cur_inst_n += 1
            elif isinstance(stmt, AlgStart):
                self.algs[stmt.name] = [[], []]
                self.cur_alg = stmt.name
                if stmt.is_main:
                    main_alg = stmt.name
                self.cur_inst_n = 0
            elif isinstance(stmt, AlgEnd):
                cur_ns.append((stmt.lineno, Bytecode.RET, ()))
                self.cur_inst_n += 1
                self.algs[self.cur_alg][1] = self.cur_tags[:]
                self.cur_tags.clear()
                self.cur_alg = None
            elif isinstance(stmt, Call):
                cur_ns.append((stmt.lineno, Bytecode.CALL, (stmt.alg_name,)))
                self.cur_inst_n += 1
            elif isinstance(stmt, IfStart):
                ifs.append(i)
                cur_ns.extend(self._expr_bc(stmt.lineno, stmt.cond))
                cur_ns.append((stmt.lineno, Bytecode.JUMP_TAG_IF_FALSE, (tags[i][0],)))
                self.cur_inst_n += 1
            elif isinstance(stmt, ElseStart):
                cur_ns.append((stmt.lineno, Bytecode.JUMP_TAG, (tags[ifs.pop()][1],)))
                self.cur_inst_n += 1
                self.cur_tags.append(self.cur_inst_n)
            elif isinstance(stmt, IfEnd):
                self.cur_tags.append(self.cur_inst_n)
            elif isinstance(stmt, LoopWithCountStart):
                loops_with_count.append(i)
                cur_ns.extend(self._expr_bc(stmt.lineno, stmt.count))
                cur_ns.append((stmt.lineno, Bytecode.STORE, ('цел', (str(i),))))
                cur_ns.extend(self._loop_with_count_cond(stmt.lineno, str(i)))
                cur_ns.append((stmt.lineno, Bytecode.JUMP_TAG_IF_FALSE, (tags[i][2],)))
                self.cur_inst_n += 2
                self.cur_tags.append(self.cur_inst_n)
            elif isinstance(stmt, LoopWithCountEnd):
                stmt_tags = tags[loops_with_count[-1]]
                self.cur_tags.append(self.cur_inst_n)
                cur_ns.extend(self._loop_with_count_cond(stmt.lineno, str(loops_with_count.pop())))
                cur_ns.append((stmt.lineno, Bytecode.JUMP_TAG_IF_FALSE, (stmt_tags[2],)))
                cur_ns.append((stmt.lineno, Bytecode.JUMP_TAG, (stmt_tags[0],)))
                self.cur_inst_n += 2
                self.cur_tags.append(self.cur_inst_n)
            elif isinstance(stmt, LoopWhileStart):
                loops_while_stmts.append(stmt.cond)
                loops_while_indexes.append(i)
                cur_ns.extend(self._expr_bc(stmt.lineno, stmt.cond))
                cur_ns.append((stmt.lineno, Bytecode.JUMP_TAG_IF_FALSE, (tags[i][2],)))
                self.cur_inst_n += 1
                self.cur_tags.append(self.cur_inst_n)
            elif isinstance(stmt, LoopWhileEnd):
                stmt_tags = tags[loops_while_indexes.pop()]
                self.cur_tags.append(self.cur_inst_n)
                cur_ns.extend(self._expr_bc(stmt.lineno, loops_while_stmts.pop()))
                cur_ns.append((stmt.lineno, Bytecode.JUMP_TAG_IF_FALSE, (stmt_tags[2],)))
                cur_ns.append((stmt.lineno, Bytecode.JUMP_TAG, (stmt_tags[0],)))
                self.cur_inst_n += 2
                self.cur_tags.append(self.cur_inst_n)
            elif isinstance(stmt, LoopForStart):
                loops_for_indexes.append(i)
                loops_for.append((stmt.target, stmt.from_expr, stmt.to_expr, stmt.step))
                cur_ns.extend(self._expr_bc(stmt.lineno, stmt.from_expr))
                cur_ns.append((stmt.lineno, Bytecode.STORE, ('цел', (stmt.target,))))
                cur_ns.append((stmt.lineno, Bytecode.LOAD_NAME, (stmt.target,)))
                cur_ns.extend(self._expr_bc(stmt.lineno, stmt.to_expr))
                cur_ns.append((stmt.lineno, Bytecode.BIN_OP, ('<=',)))
                cur_ns.append((stmt.lineno, Bytecode.JUMP_TAG_IF_FALSE, (tags[i][2],)))
                self.cur_inst_n += 4
                self.cur_tags.append(self.cur_inst_n)
            elif isinstance(stmt, LoopForEnd):
                stmt_tags = tags[loops_for_indexes[-1]]
                loop = loops_for.pop()
                self.cur_tags.append(self.cur_inst_n)
                cur_ns.extend(self._expr_bc(stmt.lineno, loop[1]))
                cur_ns.extend(self._loop_for_cond(stmt.lineno, loop[0], loop[2], loop[3]))
                cur_ns.append((stmt.lineno, Bytecode.JUMP_TAG_IF_FALSE, (stmt_tags[2],)))
                cur_ns.append((stmt.lineno, Bytecode.JUMP_TAG, (stmt_tags[0],)))
                self.cur_inst_n += 2
                self.cur_tags.append(self.cur_inst_n)

            last_line = stmt.lineno

        if main_alg is not None:
            self.bytecode.append((last_line, Bytecode.CALL, (main_alg,)))

        return self.bytecode, self.algs

    def _loop_with_count_cond(self, lineno: int, loop_name: str) -> list[BytecodeType]:
        res = [
            (lineno, Bytecode.LOAD_NAME, (loop_name,)),
            (lineno, Bytecode.LOAD_CONST, (Value('цел', 1),)),
            (lineno, Bytecode.BIN_OP, ('-',)),
            (lineno, Bytecode.STORE, (None, (loop_name,))),
            (lineno, Bytecode.LOAD_NAME, (loop_name,)),
            (lineno, Bytecode.LOAD_CONST, (Value('цел', -1),)),
            (lineno, Bytecode.BIN_OP, ('>',))
        ]
        self.cur_inst_n += 7
        return res

    def _loop_for_cond(self, lineno: int, target: str, to_expr: Expr, step: Expr) -> list[Bytecode]:
        res = [
            (lineno, Bytecode.LOAD_NAME, (target,)),
            *self._expr_bc(lineno, step),
            (lineno, Bytecode.BIN_OP, ('+',)),
            (lineno, Bytecode.STORE, (None, (target,))),
            (lineno, Bytecode.LOAD_NAME, (target,)),
            *self._expr_bc(lineno, to_expr),
            (lineno, Bytecode.BIN_OP, ('<=',))
        ]
        self.cur_inst_n += 5
        return res

    def _expr_bc(self, lineno: int, expr: list[Value | Op]) -> list[BytecodeType]:
        """
        Превращает обратную польскую запись вида `(2, 3, Op(op='+'))`
        в набор команд байт-кода вида `LOAD 2, LOAD 3, BIN_OP +`.
        """
        res: list[BytecodeType] = []
        for v in expr:
            if isinstance(v, Op):
                res.append((lineno, Bytecode.BIN_OP, (v.op,)))
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

    for i, stmt in enumerate(parsed):
        if isinstance(stmt, IfStart):
            ifs.append(i)
            res[i] = []
        elif isinstance(stmt, (LoopWithCountStart, LoopWhileStart, LoopForStart)):
            loops.append(i)
            res[i] = [cur_tag_n]
            cur_tag_n += 1

        elif isinstance(stmt, ElseStart):
            res[ifs[-1]].append(cur_tag_n)
            cur_tag_n += 1
        elif isinstance(stmt, IfEnd):
            res[ifs.pop()].append(cur_tag_n)
            cur_tag_n += 1
        elif isinstance(stmt, (LoopWithCountEnd, LoopWhileEnd, LoopForEnd)):
            res[loops.pop()].extend((cur_tag_n, cur_tag_n+1))
            cur_tag_n += 2

    return res
