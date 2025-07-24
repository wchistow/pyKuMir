import os
import shutil

from .base import Actor, KumirFunc, KumirValue, KumirRuntimeException


class Files(Actor):
    encodings = {
        ('cp-1251', 'cp1251', 'windows-1251', 'windows1251', 'windows'): 'cp1251',
        ('cp-866', 'cp866', 'ibm-866', 'ibm866', 'dos'): 'cp866',
        ('koi8-r', 'koi8r', 'koi8', 'кои8', 'кои8-р', 'кои8-р'): 'koi8_r',
        ('utf-8', 'utf8', 'utf', 'linux'): 'utf-8',
    }
    encoding = 'utf-8'

    @staticmethod
    def _open_file_to_kumir_value(filename: str, mode: str) -> KumirValue:
        try:
            file = open(filename, mode, encoding=Files.encoding)
        except FileNotFoundError:
            raise KumirRuntimeException(-1, f'файл не существует: {filename}')
        except (PermissionError, IsADirectoryError):
            raise KumirRuntimeException(-1, f'невозможно открыть файл: {filename}')
        else:
            return KumirValue('файл', file)

    @staticmethod
    def _close(args: list[KumirValue]) -> None:
        args[0].value.close()

    @staticmethod
    def _has_data(args: list[KumirValue]) -> KumirValue:
        b = Files._is_end(args).value
        return KumirValue('лог', 'нет' if b == 'да' else 'да')

    @staticmethod
    def _start_reading(args: list[KumirValue]) -> None:
        args[0].value.seek(0, 0)

    @staticmethod
    def _is_end(args: list[KumirValue]) -> KumirValue:
        f = args[0].value
        return KumirValue('лог', 'да' if f.tell() == os.fstat(f.fileno()).st_size else 'нет')

    @staticmethod
    def _can_read(args: list[KumirValue]) -> KumirValue:
        f = args[0].value
        return KumirValue('лог', 'да' if os.path.exists(f) and os.access(f, os.R_OK) else 'нет')

    @staticmethod
    def _can_write(args: list[KumirValue]) -> KumirValue:
        f = args[0].value
        return KumirValue('лог', 'да' if os.path.exists(f) and os.access(f, os.W_OK) else 'нет')

    @staticmethod
    def _exists(args: list[KumirValue]) -> KumirValue:
        return KumirValue('лог', 'да' if os.path.exists(args[0].value) else 'нет')

    @staticmethod
    def _mkdir(args: list[KumirValue], work_dir: str) -> KumirValue:
        path = args[0].value
        try:
            if os.path.isabs(path):
                os.mkdir(path)
            else:
                os.mkdir(os.path.join(work_dir, path))
        except (PermissionError, FileExistsError, FileNotFoundError):
            return KumirValue('лог', 'нет')
        else:
            return KumirValue('лог', 'да')

    @staticmethod
    def _is_dir(args: list[KumirValue]) -> KumirValue:
        return KumirValue('лог', 'да' if os.path.isdir(args[0].value) else 'нет')

    @staticmethod
    def _open_for_adding(args: list[KumirValue]) -> KumirValue:
        return Files._open_file_to_kumir_value(args[0].value, 'a')

    @staticmethod
    def _open_for_writing(args: list[KumirValue]) -> KumirValue:
        return Files._open_file_to_kumir_value(args[0].value, 'w')

    @staticmethod
    def _open_for_reading(args: list[KumirValue]) -> KumirValue:
        return Files._open_file_to_kumir_value(args[0].value, 'r')

    @staticmethod
    def _full_path(args: list[KumirValue], work_dir: str) -> KumirValue:
        return KumirValue('лит', os.path.join(work_dir, args[0].value))

    @staticmethod
    def _rm_file(args: list[KumirValue]) -> KumirValue:
        try:
            os.remove(args[0].value)
        except (PermissionError, OSError, FileNotFoundError):
            return KumirValue('лог', 'нет')
        else:
            return KumirValue('лог', 'да')

    @staticmethod
    def _rm_dir(args: list[KumirValue]) -> KumirValue:
        try:
            shutil.rmtree(args[0].value)
        except (PermissionError, OSError, FileNotFoundError):
            return KumirValue('лог', 'нет')
        else:
            return KumirValue('лог', 'да')

    @staticmethod
    def _set_encoding(args: list[KumirValue]) -> None:
        name = args[0].value
        for k, v in Files.encodings.items():
            if name in k:
                Files.encoding = name
                break
        else:
            raise KumirRuntimeException(-1, 'неизвестная кодировка')

    @staticmethod
    def _work_dir(_: list[KumirValue], work_dir: str) -> KumirValue:
        return KumirValue('лит', work_dir)

    @staticmethod
    def _prog_dir(_: list[KumirValue], prog_dir: str | None) -> KumirValue:
        return KumirValue('лит', prog_dir or './')

    funcs = {
        'закрыть': KumirFunc(_close, '', [('арг', 'файл', 'имя файла')]),
        'есть данные': KumirFunc(_has_data, 'лог', [('арг', 'файл', 'имя файла')]),
        'начать чтение': KumirFunc(_start_reading, '', [('арг', 'файл', 'имя файла')]),
        'конец файла': KumirFunc(_is_end, 'лог', [('арг', 'файл', 'имя файла')]),
        'можно открыть на чтение': KumirFunc(_can_read, 'лог', [('арг', 'лит', 'имя файла')]),
        'можно открыть на запись': KumirFunc(_can_write, 'лог', [('арг', 'лит', 'имя файла')]),
        'существует': KumirFunc(_exists, 'лог', [('арг', 'лит', 'имя')]),
        'создать каталог': KumirFunc(_mkdir, 'лог', [('арг', 'лит', 'имя каталога')]),
        'является каталогом': KumirFunc(_is_dir, 'лог', [('арг', 'лит', 'имя')]),
        'открыть на добавление': KumirFunc(_open_for_adding, 'файл', [('арг', 'лит', 'имя файла')]),
        'открыть на запись': KumirFunc(_open_for_writing, 'файл', [('арг', 'лит', 'имя файла')]),
        'открыть на чтение': KumirFunc(_open_for_reading, 'файл', [('арг', 'лит', 'имя файла')]),
        'полный путь': KumirFunc(_full_path, 'лит', [('арг', 'лит', 'имя')]),
        'удалить_файл': KumirFunc(_rm_file, 'лог', [('арг', 'лит', 'имя файла')]),
        'удалить_каталог': KumirFunc(_rm_dir, 'лог', [('арг', 'лит', 'имя каталога')]),
        'установить кодировку': KumirFunc(_set_encoding, '', [('арг', 'файл', 'имя файла')]),
        'РАБОЧИЙ КАТАЛОГ': KumirFunc(_work_dir, 'лит', []),
        'КАТАЛОГ ПРОГРАММЫ': KumirFunc(_prog_dir, 'лит', []),
    }
