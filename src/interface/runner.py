from datetime import datetime

from PyQt6.QtCore import pyqtSignal
from interpreter import code2bc, KumirException, SyntaxException, RuntimeException, VM

from .console import Console


class Runner:
    def __init__(
        self,
        console: Console,
        on_error: pyqtSignal(KumirException),
        work_dir: str | None = None,
        cur_dir: str | None = None,
        cur_file: str | None = None,
    ):
        self.console = console

        self.on_error = on_error

        self.work_dir = work_dir
        self.cur_dir = cur_dir
        self.cur_file = cur_file

    def _output(self, s: str):
        self.console.output.emit(s)

    def _input(self) -> str:
        return self.console.input()

    def run(self, code: str):
        self.console.output_sys.emit(
            f'>> {datetime.now().strftime("%H:%M:%S")} - '
            f'{self.cur_file if self.cur_file is not None else "Новая программа"} - Начало выполнения\n'
        )
        try:
            bc = code2bc(code)
        except KumirException as e:
            self.on_error.emit(e)
        else:
            if self.work_dir is not None:
                kwargs = {'work_dir': self.work_dir}
            else:
                kwargs = {}
            vm = VM(
                bytecode=bc[0],
                output_f=self._output,
                input_f=self._input,
                algs=bc[1],
                **kwargs,
                cur_dir=self.cur_dir,
                cur_file=self.cur_file,
            )
            try:
                vm.execute()
            except KumirException as e:
                self.on_error.emit(e)
        self.console.output_sys.emit(
            f'\n>> {datetime.now().strftime("%H:%M:%S")} - Новая программа - Выполнение завершено\n'
        )
