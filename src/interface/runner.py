from datetime import datetime

from interpreter import code2bc, SyntaxException, RuntimeException, VM

from .console import Console


class Runner:
    def __init__(
        self,
        console: Console,
        work_dir: str | None = None,
        cur_dir: str | None = None,
        cur_file: str | None = None,
    ):
        self.console = console

        self.work_dir = work_dir
        self.cur_dir = cur_dir
        self.cur_file = cur_file

    def _output(self, s: str):
        self.console.output.emit(s)

    def _input(self) -> str:
        return self.console.input()

    def run(self, code: str):
        self.console.output_sys.emit(
            f'>> {datetime.now().strftime("%H:%M:%S")} - Новая программа - Начало выполнения\n'
        )
        try:
            bc = code2bc(code)
        except SyntaxException as e:
            print(e.args)
        else:
            vm = VM(
                bytecode=bc[0],
                output_f=self._output,
                input_f=self._input,
                algs=bc[1],
                work_dir=self.work_dir,
                cur_dir=self.cur_dir,
                cur_file=self.cur_file,
            )
            try:
                vm.execute()
            except RuntimeException as e:
                print(e.args)
        self.console.output_sys.emit(
            f'\n>> {datetime.now().strftime("%H:%M:%S")} - Новая программа - Выполнение завершено\n'
        )
