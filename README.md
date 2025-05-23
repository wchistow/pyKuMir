# pyKuMir

Клон КуМир (**К**омплекс **у**чебных **мир**ов), написанный на Python.

> **ВАЖНО:** проект находиться в разработке и пока не предназначен для повседневного использования.\
> Тестирование разрабатываемой версии программы и нахождение ошибок приветствуются.\
> Сообщить об ошибке или предложить новую функциональность вы можете по ссылке: <https://gitflic.ru/project/wchistow/pykumir/issue/create>.

## Способы использования:

### GUI (графический интерфейс)

```sh
python src/main.py
```

### CLI (интерфейс командной строки)

```sh
python src/cli.py файл.kum
```

## Установка

### Зависимости:

 + Python>=3.10
   ```
   Pygments>=2.2
   PyQt6
   ```
 + Qt6

### Установка зависимостей:

#### Python-библиотеки

```sh
pip install Pygments>=2.2 PyQt6
```

#### Qt6

Debian и основанные на нём (Ubuntu, Linux Mint, Kali Linux, ...):
```sh
sudo apt install qt6-base-dev
```
RHEL и основанные на нём (Fedora Linux, CentOS, РЕД ОС, ROSA Linux, Alt Linux, ...):
```sh
sudo dnf install qt6-qtbase-devel
```
Arch и основанные на нём (Manjaro Linux, EndeavourOS, Garuda Linux, CachyOS, ...):
```sh
sudo pacman -S qt6-base
```

*Для справки: версии основных дистрибутивов с доступным qt6 в стандартных репозиториях:*

 + Debian 11+
 + Ubuntu 22.04+

## Текущие возможности языка:

 + Переменные и вычисления
 + Ключевые слова `вывод` и `ввод`
 + Процедуры и вызовы
 + Условный оператор `если`-`иначе`

*Ведётся активная разработка*
