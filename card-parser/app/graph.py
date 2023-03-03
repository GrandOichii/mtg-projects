import random
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

class Node:
    def __init__(self, name: str, children: list['Node']=[]) -> None:
        self.name = name
        self.children = children

data = \
Node('1', [
    Node('amogus', [
    ]),
    Node('8', [
        Node('3'),
        Node('4', [
            Node('6'),
            Node('7')
        ]),
        Node('5'),
    ]),
])

class TreeNode:
    def __init__(self, parent: 'GraphArea', node: Node) -> None:
        # super().__init__(parent, node.name)
        self.box = ProgressTextBox(parent, node.name, random.randint(0, 100), filled_color='red')

        self.area = parent

        # TODO need the original node?
        # self.info = node
        self.children: list[TreeNode] = []
        for child in node.children:
            self.children += [TreeNode(parent, child)]

    def draw(self, painter: QPainter, x: int, y: int, between: tuple[int, int], parent_t: tuple['TreeNode', int]=None):
        # draw self
        self.box.draw(painter, x, y)
        my_x = x

        if parent_t:
            regular = painter.pen()
            pen = QPen()
            # pen.setWidth(10)

            # TODO change color (or set it dynamically)
            pen.setColor(QColor('magenta'))

            parent = parent_t[0]
            b = self.box

            x_start = x + b.width() // 2
            y_start = y

            x_end = parent_t[1] + parent.box.width() // 2
            y_end = y - between[1]

            painter.setPen(pen)
            painter.drawLine(x_start, y_start, x_end, y_end)
            # painter.drawPoint(x_start, y_start)
            # painter.drawPoint(x_end, y_end)
            painter.setPen(regular)

        # TODO move to different method, cache the result?
        x = 0
        for child in self.children:
            x += child.box.width() + between[0]
        x -= between[0]
        x = (self.area.w - x) // 2


        # draw children
        for child in self.children:
            new_y = y + between[1] + self.box.height()
            child.draw(painter, x, new_y, between, (self, my_x))

            x += child.box.width() + between[0]
            

class Tree:
    def __init__(self, parent: 'GraphArea', data) -> None:
        self.root = TreeNode(parent, data)

        self.area = parent

    def draw(self):
        between = 10
        p = self.area.label.pixmap()
        p.fill(Qt.white)

        painter = QPainter(p)

        regular = QPen()
        painter.setPen(regular)

        pen = QPen()
        pen.setColor(QColor(random.randint(0, 2000)))

        self.root.draw(painter, (self.area.w - self.root.box.width()) // 2, between, (between, between*2))
        # def draw_layer(layer: list[tuple[tuple[TextBox, int], Amogus]], layer_offset=10):
            
        #     for parent_t, item in layer:
        #         b.draw(painter, x, layer_offset)
        #         if parent_t:
        #             parent = parent_t[0]

        #             x_start = x + b.width() // 2
        #             y_start = layer_offset

        #             x_end = parent_t[1] + parent.width() // 2
        #             y_end = layer_offset - layer_diff

        #             painter.setPen(pen)
        #             painter.drawLine(x_start, y_start, x_end, y_end)
        #             painter.drawPoint(x_start, y_start)
        #             painter.drawPoint(x_end, y_end)
        #             painter.setPen(regular)
        #         for child in item.children: next_layer += [((b, x), child)]
        #         x += b.width() + between
        #         # next_layer += (b, item.children)
        #     if not next_layer: return
        #     layer_offset += layer_diff + b.height()
        #     draw_layer(next_layer, layer_offset)
        # draw_layer([(None, data)])
        painter.end()


# data = \
# Amogus('1', [
#     Amogus('2', [
#         Amogus('3'),
#         Amogus('4', [
#             Amogus('6'),
#             Amogus('7')
#         ]),
#         Amogus('5'),
#     ]),
#     Amogus('8'),
# ])

class ModMouseEvent:
    def __init__(self, e: QMouseEvent, clicked: bool) -> None:
        self.e = e
        self.clicked = clicked

class CLabel(QLabel):
    mouse = pyqtSignal(ModMouseEvent)

    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)

        self.installEventFilter(self)

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        self.mouse.emit(ModMouseEvent(ev, True))

    def mouseReleaseEvent(self, ev: QMouseEvent) -> None:
        self.mouse.emit(ModMouseEvent(ev, False))

    def mouseMoveEvent(self, ev: QMouseEvent) -> None:
        self.mouse.emit(ModMouseEvent(ev, False))

    def resizeEvent(self, a0) -> None:
        # pixmap = self.pixmap()
        # pixmap=pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        # self.setPixmap(pixmap)
        # print(pixmap.size())
        # print(self.size())
        # self.setPixmap(QPixmap(self.size()))
        # print('mogus')
        return super().resizeEvent(a0)

    # def eventFilter(self, object, event):
    #     if event.type() == QEvent.Enter:
    #         print("Mouse is over the label")
    #         print(event)
    #         return True
    #     if event.type() == QEvent.Leave:
    #         print("Mouse is not over the label")
    #         print(event)
    #     if event.type() == QEvent.MouseMove:
    #         print('mogus')
        # return False


class GraphArea(QWidget):
    def __init__(self, parent: 'GraphWidget', data) -> None:
        super().__init__()

        self.parent_w = parent
        self.main = parent.main

        self.last_mouse_state: QMouseEvent = None

        self.w = 400
        self.h = 600

        self.init_tree(data)
        self.init_ui()


        # self.setFixedSize(self.w, self.h)

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = CLabel()
        # self.label.setScaledContents(True)
        # self.label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        # self.label.resizeEvent.connect(lambda: self.label.setPixmap(self.label.pixmap().scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)))

        self.label.mouse.connect(self.mouse_action)
        # self.label.setsi
        # self.canvas = QPixmap()
        self.canvas = QPixmap(self.w, self.h)
        # self.canvas = QPixmap(self.w, self.h).scaled(self.label.width(), self.label.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.canvas.fill(Qt.cyan)
        self.label.setPixmap(self.canvas)
        self.label.update()
        layout.addWidget(self.label)

        self.draw()
        # self.data_line = 

        self.setLayout(layout)

    def init_tree(self, data):
        self.tree = Tree(self, data)

    def draw(self):
        self.tree.draw()
        return
        
        

    def mouse_action(self, ev: QMouseEvent):
        self.last_mouse_state = ev
        self.canvas.fill(Qt.white)
        # painter = QPainter(self.label.pixmap())
        
        # pen = QPen()
        # pen.setColor(Qt.magenta)
        # pen.setWidth(4)
        # painter.setPen(pen)
        # pos = ev.localPos() - self.label.pos()
        # pos = ev.localPos()
        # pos_diff = QPoint(self.label.geometry().getCoords()[0], self.label.geometry().getCoords()[1]) 
        # pos_diff = QPoint(0, 0)
        # print(pos)
        # print(pos_diff)
        # pos += pos_diff
        # print(pos)
        # x = int(pos.x())
        # y = int(pos.y())
        # painter.drawPoint(x, y)
        # painter.end()

        self.draw()
        self.update()


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

        self.graph_area = GraphArea(self, data)
        self.selector_editor_area = SelectorWidget(self)

        layout.addWidget(self.graph_area, 2)
        layout.addWidget(self.selector_editor_area, 1)

        self.setLayout(layout)

    