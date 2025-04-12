from typing import NamedTuple

from .ast_classes import StoreVar


class Bytecode(NamedTuple):
    start_line: int
    command: str
    args: dict


def build_bytecode(ast_tree) -> list[Bytecode]:
    bytecode: list[Bytecode] = []
    for sub_tree in ast_tree.iter_subtrees_topdown():
        if sub_tree.data.value == 'statement':
            stmt = sub_tree.children[0]
            if isinstance(stmt, StoreVar):
                bytecode.append(
                    Bytecode(
                        stmt.meta.line,
                        'store',
                        {
                            'type': stmt.typename,
                            'names': stmt.names,
                            'value': stmt.value.expr if stmt.value else None
                        }
                    )
                )
    return bytecode


if __name__ == '__main__':
    from build_ast import build_ast

    code = """цел а := 5"""
    print(build_bytecode(build_ast(code)))
