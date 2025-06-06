from datetime import datetime

from interpreter import code2bc, SyntaxException, RuntimeException, VM

from .console import Console


class Runner:
    def __init__(self, console: Console):
        self.console = console

    def _output(self, s: str):
        self.console.output(s)

    def _input(self) -> str:
        return self.console.input()

    def run(self, code: str):
        self.console.output_sys(
            f'>> {datetime.now().strftime("%H:%M:%S")} - Новая программа - Начало выполнения\n'
        )
        try:
            bc = code2bc(code)
        except SyntaxException as e:
            print(e.args)
        else:
            vm = VM(bytecode=bc[0],
                    output_f=self._output,
                    input_f=self._input,
                    algs=bc[1])
            try:
                vm.execute()
            except RuntimeException as e:
                print(e.args)
        self.console.output_sys(
            f'\n>> {datetime.now().strftime("%H:%M:%S")} - Новая программа - Выполнение завершено\n'
        )
