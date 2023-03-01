from termcolor import colored
import os.path as path
import re
import sys
import json

from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

# from pyqtgraph.parametertree import *
# import pyqtgraph as pb/

from main import *
from graph_util import *

class Amogus:
    def __init__(self, name: str, children: list['Amogus']=[]) -> None:
        self.name = name
        self.children = children

data = \
Amogus('1', [
    Amogus('2', [
        Amogus('3'),
        Amogus('4', [
            Amogus('6'),
            Amogus('7')
        ]),
        Amogus('5'),
    ]),
    Amogus('8'),
])

class GraphArea(QWidget):
    def __init__(self, parent: 'GraphWidget') -> None:
        super().__init__()

        self.parent_w = parent
        self.main = parent.main

        self.init_ui()

        # self.setFixedSize(600, 400)

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel()
        canvas = QPixmap(400, 600)
        canvas.fill(Qt.cyan)
        self.label.setPixmap(canvas)
        self.label.update()
        layout.addWidget(self.label)

        self.draw_smt()
        # self.data_line = 

        self.setLayout(layout)

    def draw_smt(self):
        p = self.label.pixmap()

        layer_diff = 20
        painter = QPainter(p)

        regular = QPen()
        painter.setPen(regular)

        pen = QPen()
        pen.setColor(Qt.red)
        # pen.setWidth(10)
        def draw_layer(layer: list[tuple[tuple[Box, int], Amogus]], layer_offset=0):
            x = 0
            next_layer = []
            for parent_t, item in layer:
                b = Box(p, (100, 20), label=item.name)
                b.draw(painter, x, layer_offset)
                if parent_t:
                    parent = parent_t[0]

                    x_start = x + b.width // 2
                    y_start = layer_offset

                    x_end = parent_t[1] + parent.width // 2
                    y_end = layer_offset - layer_diff

                    painter.setPen(pen)
                    painter.drawLine(x_start, y_start, x_end, y_end)
                    painter.drawPoint(x_start, y_start)
                    painter.drawPoint(x_end, y_end)
                    painter.setPen(regular)
                for child in item.children: next_layer += [((b, x), child)]
                x += b.width + 10
                # next_layer += (b, item.children)
            if not next_layer: return
            layer_offset += layer_diff + b.height
            draw_layer(next_layer, layer_offset)
        draw_layer([(None, data)])
        painter.end()

        # painter = QPainter(self.label.pixmap())
        # painter.drawLine(10, 10, 20, 30)
        # painter.end()

class SelectorWidget(QWidget):
    def __init__(self, parent: 'GraphWidget') -> None:
        super().__init__()

        self.parent_w = parent
        self.main = parent.main

        self.init_ui()
        self.known_clicked()

    def init_ui(self):
        self.init_type_widgets()

        # TODO unfinished
        layout = QVBoxLayout()

        form = QFormLayout()

        self.name_edit = QLineEdit()
        self.selector_edit = QLineEdit()
        self.type_combo_box = QComboBox()
        self.type_combo_box.addItems(list(self.type_dict.keys()))
        self.type_combo_box.currentTextChanged.connect(self.type_changed_action)

        self.type_widget = QStackedWidget()
        for w in self.type_dict.values():
            self.type_widget.addWidget(w)

        form.addRow('Name:', self.name_edit)
        form.addRow('Selector:', self.selector_edit)

        layout.addLayout(form)
        layout.addWidget(self.type_combo_box)
        layout.addWidget(self.type_widget)

        self.setLayout(layout)

    def init_type_widgets(self):
        self.type_dict = {}

        self.init_single_type_widget()
        self.init_multiple_type_widget()

    def init_single_type_widget(self):
        wid = QWidget()

        layout = QVBoxLayout()

        known_layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        self.known_radio_box = QRadioButton()
        # self.known_radio_box.setAlignment(Qt.AlignTop)
        self.known_radio_box.clicked.connect(self.known_clicked)

        self.known_selectors_combo_box = QComboBox()
        self.known_selectors_combo_box.addItems(['Selector1', 'Selector2', 'Selector3'])
        # TODO add items

        known_layout.addWidget(QLabel('Implemented selector'))
        known_layout.addWidget(self.known_radio_box)

        layout.addLayout(known_layout)
        layout.addWidget(self.known_selectors_combo_box)

        wid.setLayout(layout)

        self.type_dict['Single'] = wid

    def init_multiple_type_widget(self):
        wid = QWidget()

        self.type_dict['Multiple'] = wid

    # actions
    def type_changed_action(self):
        self.type_widget.setCurrentWidget(self.type_dict[self.type_combo_box.currentText()])
        # TODO

    def known_clicked(self):
        self.known_selectors_combo_box.setEnabled(self.known_radio_box.isChecked())
        # TODO

class GraphWidget(QWidget):
    def __init__(self, parent: MainWindow) -> None:
        super().__init__()

        self.main = parent

        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()

        self.graph_area = GraphArea(self)
        self.selector_editor_area = SelectorWidget(self)

        layout.addWidget(self.graph_area, 2)
        layout.addWidget(self.selector_editor_area, 1)

        self.setLayout(layout)

    