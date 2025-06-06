import os
from re import match
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextDocument
from PyQt6.QtWidgets import (QWidget, QTextEdit, QSplitter, QGridLayout,
                             QTreeWidget, QTreeWidgetItem)


class DocView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.resize(600, 500)

        self.view = QTextDocument()

        self.base_dir = Path(__file__).parent.parent.parent
        with open(os.path.join(self.base_dir, 'docs', 'lang', 'README.md')) as f:
            text = f.read()

        self.view.setMarkdown(text)

        self.tree = QTreeWidget(self)
        for f in _get_all_files(os.path.join(self.base_dir, 'docs')):
            item = QTreeWidgetItem(self.tree)
            item.setText(0, f)
            self.tree.addTopLevelItem(item)
            if item.text(0) == os.path.join('lang', 'README.md'):
                self.tree.setCurrentItem(item)
        self.tree.selectionModel().selectionChanged.connect(self.on_selection_changed)

        self.textview = QTextEdit(self)
        self.textview.setReadOnly(True)
        self.textview.resize(500, 600)
        self.textview.setDocument(self.view)

        self.tree_and_doc = QSplitter(Qt.Orientation.Horizontal, self)
        self.tree_and_doc.addWidget(self.tree)
        self.tree_and_doc.addWidget(self.textview)

        self.grid = QGridLayout(self)
        self.grid.addWidget(self.tree_and_doc, 0, 0, 0, 0)

        self.setMinimumSize(500, 400)

        self.setLayout(self.grid)

    def on_selection_changed(self):
        with open(os.path.join(self.base_dir, 'docs', self.tree.selectedIndexes()[0].data())) as f:
            text = f.read()

        self.view.setMarkdown(text)


def _get_all_files(root: str) -> list[str]:
    result = []
    regex = os.path.join('.*', 'docs', '(.*)')
    for item in os.listdir(root):
        if not os.path.isdir(os.path.join(root, item)):
            result.append(match(regex, os.path.join(root, item)).groups()[0])
        else:
            result += _get_all_files(os.path.join(root, item))

    return result
