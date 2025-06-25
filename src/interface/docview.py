import os
import re
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QSplitter, QGridLayout,
                             QTreeWidget, QTreeWidgetItem, QTextBrowser)

from .lexer import CSS, highlight_text_without_css


class DocView(QWidget):
    PRETTY_NAMES = {
        'algs.md': 'Алгоритмы',
        'branching.md': 'Команды ветвления',
        'commands.md': 'Команды',
        'comments.md': 'Комментарии',
        'exprs.md': 'Вычисления',
        'io.md': 'Ввод/вывод',
        'loops.md': 'Циклы',
        'prog_struct.md': 'Структура программы',
        'README.md': 'Содержание',
        'vars.md': 'Переменные'
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        self.resize(815, 500)

        self.view = QTextBrowser(self)
        self.view.setLineWrapMode(QTextBrowser.LineWrapMode.WidgetWidth)

        self.base_dir = Path(__file__).parent.parent.parent
        with open(os.path.join(self.base_dir, 'docs', 'lang', 'README.md'), encoding='utf-8') as f:
            self.view.setHtml(_prepare(f.read(), self.base_dir))

        self.view.anchorClicked.connect(self.update_selected_item)

        self.tree = QTreeWidget(self)
        for f in _get_all_files(os.path.join(self.base_dir, 'docs', 'lang')):
            item = QTreeWidgetItem(self.tree)
            item.setText(0, self.PRETTY_NAMES[f])
            item.setData(1, 0, os.path.join(self.base_dir, 'docs', 'lang', f))
            self.tree.addTopLevelItem(item)
            if item.data(1, 0) == os.path.join(self.base_dir, 'docs',
                                                            'lang', 'README.md'):
                self.tree.setCurrentItem(item)
        self.tree.selectionModel().selectionChanged.connect(self.on_selection_changed)

        self.tree_and_doc = QSplitter(Qt.Orientation.Horizontal, self)
        self.tree_and_doc.addWidget(self.tree)
        self.tree_and_doc.addWidget(self.view)

        self.view.resize(800, 400)
        self.view.setMinimumSize(400, 300)
        self.tree.setMinimumSize(150, 300)

        self.grid = QGridLayout(self)
        self.grid.addWidget(self.tree_and_doc, 0, 0, 0, 0)

        self.setMinimumSize(700, 400)

        self.setLayout(self.grid)

    def on_selection_changed(self):
        with open(
                os.path.join(self.base_dir, 'docs', 'lang',
                             self.tree.selectedItems()[0].data(1, 0)),
                encoding='utf-8'
        ) as f:
            self.view.setHtml(_prepare(f.read(), self.base_dir))

    def update_selected_item(self, new_file):
        new_file_path = new_file.path()
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item.data(1, 0) == new_file_path:
                self.tree.setCurrentItem(item)
                break


def _get_all_files(root: str) -> list[str]:
    result = []
    for item in os.listdir(root):
        if not os.path.isdir(os.path.join(root, item)):
            result.append(item)
        else:
            result += _get_all_files(os.path.join(root, item))

    return result


def _prepare(text: str, base_dir: Path) -> str:
    text = CSS + '\n' + re.sub(r'```kumir\n(?P<code>[^`]+)```', _highlight, text.strip())
    text = re.sub(r'```\n(?P<code>[^`]+)```', r'<code><pre>\g<code></pre></code>', text)
    return _links_from_relative_to_absolute(text, base_dir)


def _highlight(m: re.Match[str]) -> str:
    return highlight_text_without_css(m.group(1))


def _links_from_relative_to_absolute(text: str, base_dir: Path) -> str:
    res = []
    for line in text.split('\n'):
        if line.strip().startswith('<li><a href='):
            start, filename, end = line.split('"')
            full_filename = os.path.join(base_dir, "docs", "lang", filename)
            res.append(f'{start}"file://{"" if full_filename.startswith("/") else "/"}'
                       f'{full_filename}"{end}')
        else:
            res.append(line)
    return '\n'.join(res)
