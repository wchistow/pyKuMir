import sys

from interpreter import build_bytecode, Parser, VM, pretty_print_bc
from metadata import VERSION

HELP = '''Использование:
pykumir [ОПЦИИ] файл.kum

Опции:
  --debug       - запустить программу в режиме отладки
  --help, -h    - распечатать это сообщение
  --version, -V - распечатать версию
'''


def main(argv):
    debug = False

    argv = argv[1:]
    if '--help' in argv or '-h' in argv:
        print(HELP)
        return
    elif '--version' in argv or '-V' in argv:
        print(f'pyKuMir v{VERSION}')
        return
    elif len(argv) == 2 and '--debug' in argv:
        debug = True
        argv = argv[1:]

    for file in argv:
        if file.endswith('.kum'):
            with open(file, encoding='utf-8') as f:
                run_program(f.read(), debug)


def run_program(code: str, debug: bool):
    parser = Parser(code, debug)
    parsed = parser.parse()
    if debug:
        print(parsed)
        print('-'*40)
    bc = build_bytecode(parsed)
    if debug:
        pretty_print_bc(*bc)
        print('-' * 40)
    vm = VM(bc[0], output_f=lambda s: print(s, end=''), input_f=input, algs=bc[1])
    vm.execute()


if __name__ == '__main__':
    main(sys.argv)
