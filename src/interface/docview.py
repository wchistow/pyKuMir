import os
from re import match, sub
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QSplitter, QGridLayout,
                             QTreeWidget, QTreeWidgetItem, QTextBrowser)


class DocView(QWidget):
    PRETTY_NAMES = {
        'lang/algs.md': 'Алгоритмы',
        'lang/branching.md': 'Команды ветвления',
        'lang/commands.md': 'Команды',
        'lang/comments.md': 'Комментарии',
        'lang/exprs.md': 'Вычисления',
        'lang/io.md': 'Ввод/вывод',
        'lang/loops.md': 'Циклы',
        'lang/prog_struct.md': 'Структура программы',
        'lang/README.md': 'Содержание',
        'lang/vars.md': 'Переменные'
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        self.resize(600, 500)

        self.view = QTextBrowser(self)
        self.view.setLineWrapMode(QTextBrowser.LineWrapMode.WidgetWidth)

        self.base_dir = Path(__file__).parent.parent.parent
        with open(os.path.join(self.base_dir, 'docs', 'lang', 'README.md')) as f:
            self.view.setMarkdown(_links_from_relative_to_absolute(f.read(), self.base_dir))

        self.view.anchorClicked.connect(self.update_selected_item)

        self.tree = QTreeWidget(self)
        for f in _get_all_files(os.path.join(self.base_dir, 'docs', 'lang')):
            item = QTreeWidgetItem(self.tree)
            item.setText(0, self.PRETTY_NAMES[f])
            item.setData(1, 0, os.path.join(self.base_dir, 'docs', f))
            self.tree.addTopLevelItem(item)
            if item.data(1, 0) == os.path.join(self.base_dir, 'docs',
                                                            'lang', 'README.md'):
                self.tree.setCurrentItem(item)
        self.tree.selectionModel().selectionChanged.connect(self.on_selection_changed)

        self.tree_and_doc = QSplitter(Qt.Orientation.Horizontal, self)
        self.tree_and_doc.addWidget(self.tree)
        self.tree_and_doc.addWidget(self.view)

        self.grid = QGridLayout(self)
        self.grid.addWidget(self.tree_and_doc, 0, 0, 0, 0)

        self.setMinimumSize(500, 400)

        self.setLayout(self.grid)

    def on_selection_changed(self):
        with open(
                os.path.join(self.base_dir, 'docs',
                             self.tree.selectedItems()[0].data(1, 0))
        ) as f:
            self.view.setMarkdown(_links_from_relative_to_absolute(f.read(), self.base_dir))

    def update_selected_item(self, new_file):
        new_file_path = new_file.path()
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item.data(1, 0) == new_file_path:
                self.tree.setCurrentItem(item)
                break


def _get_all_files(root: str) -> list[str]:
    result = []
    regex = os.path.join('.*', 'docs', '(.*)')
    for item in os.listdir(root):
        if not os.path.isdir(os.path.join(root, item)):
            result.append(match(regex, os.path.join(root, item)).groups()[0])
        else:
            result += _get_all_files(os.path.join(root, item))

    return result


def _links_from_relative_to_absolute(text: str, base_dir: Path) -> str:
    return sub(r'\./(?P<filename>[a-z_]+\.md)',
               rf'file://{os.path.join(base_dir, "docs", "lang")}'
               rf'{os.path.sep}\g<filename>', text)
