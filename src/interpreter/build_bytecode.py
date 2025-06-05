from .ast_classes import (StoreVar, Output, Op, AlgStart, AlgEnd, Call,
                          Input, IfStart, IfEnd, ElseStart, LoopWithCountStart, LoopWithCountEnd)
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
        self.cur_tag_n = 0
        self.cur_inst_n = 0

    def build(self, parsed_code: list) -> tuple[list[BytecodeType], dict]:
        main_alg: str | None = None
        last_line = 0

        cur_loop_name = None

        if_indent = 0

        for stmt in parsed_code:
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
                if if_indent:
                    self.cur_tags.append(self.cur_inst_n)
                cur_ns.extend(self._expr_bc(stmt.lineno, stmt.cond))
                cur_ns.append((stmt.lineno, Bytecode.JUMP_TAG_IF_FALSE, (self.cur_tag_n,)))
                self.cur_inst_n += 1
                self.cur_tag_n += 1
                if_indent += 1
            elif isinstance(stmt, ElseStart):
                cur_ns.append((stmt.lineno, Bytecode.JUMP_TAG, (self.cur_tag_n,)))
                self.cur_inst_n += 1
                self.cur_tag_n += 1
                self.cur_tags.append(self.cur_inst_n)
            elif isinstance(stmt, IfEnd):
                self.cur_tags.append(self.cur_inst_n)
                if_indent -= 1
            elif isinstance(stmt, LoopWithCountStart):
                cur_loop_name = str(self.cur_tag_n)
                cur_ns.extend(self._expr_bc(stmt.lineno, stmt.count))
                cur_ns.append((stmt.lineno, Bytecode.STORE, ('цел', (cur_loop_name,))))
                cur_ns.extend(self._loop_with_count_cond(stmt.lineno, cur_loop_name))
                cur_ns.append((stmt.lineno, Bytecode.JUMP_TAG_IF_FALSE, (self.cur_tag_n+2,)))
                self.cur_inst_n += 2
                self.cur_tags.append(self.cur_inst_n)
                self.cur_tag_n += 1
            elif isinstance(stmt, LoopWithCountEnd):
                self.cur_tags.append(self.cur_inst_n)
                cur_ns.extend(self._loop_with_count_cond(stmt.lineno, cur_loop_name))
                cur_ns.append((stmt.lineno, Bytecode.JUMP_TAG_IF_FALSE, (self.cur_tag_n+1,)))
                cur_ns.append((stmt.lineno, Bytecode.JUMP_TAG, (self.cur_tag_n-1,)))
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

    def _expr_bc(self, lineno: int, expr: list[Value | Op]) -> list[BytecodeType]:
        """
        Превращает обратную польскую запись вида `(2, 3, Op(op='+'))` в набор команд байт-кода, например:
        ```
        LOAD 2
        LOAD 3
        BIN_OP +
        ```
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
