import sys

from interpreter import build_bytecode, improve, Parser, VM
from interpreter.build_bytecode import pretty_print_bc
from metadata import VERSION

HELP = '''Использование:
python cli.py [ОПЦИИ] файл.kum

Опции:
  --debug       - запустить программу в режиме отладки
  --help, -h    - распечатать это сообщение
  --version, -V - распечатать версию
'''


def main(argv):
    debug = False

    argv = argv[1:]
    if not argv or '--help' in argv or '-h' in argv:
        print_help()
        return
    elif '--version' in argv or '-V' in argv:
        print(f'pyKuMir v{VERSION}')
        return
    elif len(argv) == 2 and '--debug' in argv:
        debug = True
        argv = argv[1:]

    for file in argv:
        if file.endswith('.kum'):
            with open(file) as f:
                run_program(f.read(), debug)


def run_program(code: str, debug: bool):
    parser = Parser(code, debug)
    parsed = improve(parser.parse())
    bc = build_bytecode(parsed)
    if debug:
        print(parsed)
        print('-'*40)
        pretty_print_bc(bc[0])
        for name, alg in bc[1].items():
            print(f'{name!r}:')
            pretty_print_bc(alg, indent=4)
        print('-' * 40)
    vm = VM(bc[0], output_f=lambda s: print(s, end=''), algs=bc[1])
    vm.execute()


def print_help():
    print(HELP)


if __name__ == '__main__':
    main(sys.argv)
