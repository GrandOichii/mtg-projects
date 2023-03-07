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

NODE_NAME_SYMS = 'abcdefghijklmnopqrstuvwqyz'
NODE_NAME_SYMS += NODE_NAME_SYMS.upper()
NODE_NAME_SYMS += '0123456789'

def random_node_name():
    result = ''
    for i in range(random.randint(2, 4)):
        result += NODE_NAME_SYMS[random.randint(0, len(NODE_NAME_SYMS)-1)]
    return result

# TODO doesn't work
def random_node(depth: int=3) -> Node:
    if depth == 0:
        return None
    # num_c = random.randint(0, depth)
    num_c = depth
    print(depth, num_c)
    children = []
    for _ in range(num_c):
        c = random_node(depth-1)
        if c is None: continue
        children += [c]
    return Node(random_node_name(), children)

data = \
Node('1', [
    Node('amogus', [
    ]),
    Node('8', [
        Node('3', [
            Node('AA'),
            Node('NN')
        ]),
        Node('4', [
            Node('6'),
            Node('7')
        ]),
        Node('5'),
    ]),
])
# data = random_node()

# data = Node('root', [])

# TODO !!! NODES ARE LAYERED ON TOP OF EACH OTHER !!!

class TreeNode:
    def __init__(self, area: 'GraphArea', node: Node, parent: 'TreeNode'=None) -> None:
        self.box = ProgressTextBox(area, node.name, random.randint(0, 100), filled_color='red')

        self.parent: TreeNode = parent

        def press(ev: QMouseEvent):
            mpos = ev.pos()
            mx, my = mpos.x(), mpos.y()
            w, h = self.box.width(), self.box.height()
            # print(mx, my)
            if not (self.x < mx < self.x + w and self.y < my < self.y + h): return
            self.box.selected = True
            self.area.draw()
            # print('mg')

        def release(ev: QMouseEvent):
            # mpos = ev.pos()
            if self.box.selected: 
                print('no')
                self.box.selected = False
            self.area.draw()
            # self.area.update()

        def move(ev: QMouseEvent):
            if not self.box.selected: return

            pos = ev.pos()
            diff_x = pos.x() - self.x
            diff_y = pos.y() - self.y

            def move(node: TreeNode):
                node.x += diff_x
                node.y += diff_y
                for child in node.children:
                    move(child)
            move(self)

            # self.x = pos.x()
            # self.y = pos.y()
            self.area.draw()

        area.press.connect(press)
        area.release.connect(release)
        area.move.connect(move)

        self.x: int = None
        self.y: int = None
        
        # TODO the layout is drawn, new child in incorrect location, then is drawn again (when releasing the button), and the child fits to the position
        # possible solutions
        # add last_clicked to box -- is kinda clunky
        # add deferred actions to tree after drawing -- also kinda clunky
        # add stop_draw fuse to new child -- will try out
        # remake the boxes to be inferited from QWidget -- will take a long time to reformat

        # def f():
        #     n = Node(random_node_name())
        #     # tn = TreeNode()
        #     self.children += [TreeNode(area, n, self)]
            # WARN drawing triggers recursion loop, don't do that
            # self.area.draw()
            # self.area.update()

        # self.box.clicked = f

        self.area = area

        # TODO save the original node?
        # self.info = node
        self.children: list[TreeNode] = []
        for child in node.children:
            self.children += [TreeNode(area, child, self)]

    def update_state(self):
        # do something

        for child in self.children:
            child.update_state()

    def children_width(self, between_x: int=0):
        result = 0
        for child in self.children:
            result += child.children_width(between_x) + between_x
        result -= between_x
        if not self.children:
            result = self.box.width()
        return result
        return max(self.box.width(), result)

    def draw(self, painter: QPainter):
        # draw self
        self.box.draw(painter, self.x, self.y)

        # draw connection
        if self.parent:
            regular = painter.pen()
            pen = QPen()
            # pen.setWidth(10)

            # TODO set color dynamically
            pen.setColor(QColor('magenta'))

            parent = self.parent
            b = self.box

            x_start = self.x + b.width() // 2
            y_start = self.y

            x_end = parent.x + parent.box.width() // 2
            y_end = parent.y + parent.box.height()

            painter.setPen(pen)
            painter.drawLine(x_start, y_start, x_end, y_end)
            # painter.drawPoint(x_start, y_start)
            # painter.drawPoint(x_end, y_end)
            painter.setPen(regular)

        # draw children
        for child in self.children:
            child.draw(painter)    

    def draw1(self, painter: QPainter, x: int, y: int, between: tuple[int, int], parent_t: tuple['TreeNode', int]=None, layer_offsets:list[int]=None, layer:int=0)->int:
        # if not layer_offsets:
        #     layer_offsets = []
        # if layer >= len(layer_offsets):
        #     layer_offsets += [0 for i in range(layer+1)]

        # cwidth = self.children_width(between[0])
        # my_x = x
        # # TODO fix inconsistent width when adding to amogus 
        # # if cwidth > self.box.width():
        # my_x += (cwidth - self.box.width()) // 2
        # # x -= (cwidth-self.box.width())//2

        # cwidth = max(self.box.width(), cwidth)

        # my_x += (cwidth-self.box.width()) // 2
        # if parent_t:
        #     p = parent_t[0]

        # my_x += (self.box.width()) // 2
        # my_x += (cwidth) // 2

        # my_x = x


        # draw children
        for child in self.children:
            new_y = y + between[1] + self.box.height()
            cx, cy = child.x, child.y
            if not child.x:
                cx = x
                cy = new_y
            w = child.draw(painter, cx, cy, between, (self, my_x), layer_offsets, layer+1) + between[0]
            x += w

        # draw self
        self.box.draw(painter, self.x, self.y)
        # layer_offsets[layer] += self.box.width() + between[0]

        # draw connection
        if parent_t:
            regular = painter.pen()
            pen = QPen()
            # pen.setWidth(10)

            # TODO change color (or set it dynamically)
            pen.setColor(QColor('magenta'))

            parent = parent_t[0]
            b = self.box

            x_start = my_x + b.width() // 2
            y_start = y

            x_end = parent_t[1] + parent.box.width() // 2
            y_end = y - between[1]

            painter.setPen(pen)
            painter.drawLine(x_start, y_start, x_end, y_end)
            # painter.drawPoint(x_start, y_start)
            # painter.drawPoint(x_end, y_end)
            painter.setPen(regular)

        # TODO remove
        # draw width line
        pen = painter.pen()
        tpen = QPen()
        tpen.setColor(Qt.yellow)
        tpen.setWidth(3)
        painter.setPen(tpen)

        lx = my_x - (cwidth - self.box.width()) // 2
        # lx = my_x
        ly = y + self.box.height()
        rx = lx + cwidth
        ry = y+self.box.height()

        painter.drawLine(lx, ly, rx, ry)
        tpen.setWidth(5)
        tpen.setColor(Qt.blue)
        painter.setPen(tpen)
        painter.drawPoint(lx, ly)
        painter.drawPoint(rx, ry)
        painter.setPen(pen)

        return cwidth
        # return max(self.box.width(), cwidth)

    def set_initial_loc(self, x: int, y: int, between: tuple[int, int]) -> int:
        cwidth = self.children_width(between[0])
        my_x = x
        # TODO fix inconsistent width when adding to amogus 
        # if cwidth > self.box.width():
        my_x += (cwidth - self.box.width()) // 2
        # x -= (cwidth-self.box.width())//2

        cwidth = max(self.box.width(), cwidth)

        # set locs for children
        for child in self.children:
            new_y = y + between[1] + self.box.height()
            w = child.set_initial_loc(x, new_y, between) + between[0]
            x += w

        # set locs for self
        self.x = my_x
        self.y = y
        return cwidth
        # self.box.draw(painter, my_x, y)


class Tree:

    BETWEEN_X = 20
    BETWEEN_Y = 20

    def __init__(self, parent: 'GraphArea', data) -> None:
        self.root = TreeNode(parent, data)

        self.area = parent
        self.root.set_initial_loc(200, 10, (Tree.BETWEEN_X, Tree.BETWEEN_Y))

    def update_state(self):
        self.root.update_state()
        # print(random.randint(0, 10))

    def draw(self, x: int, y: int):
        p = self.area.label.pixmap()
        p.fill(Qt.cyan)

        painter = QPainter(p)

        regular = QPen()
        painter.setPen(regular)

        pen = QPen()
        pen.setColor(QColor(random.randint(0, 2000)))
        
        # widths
        widths = {}
        def get_width(node: TreeNode, widths: dict) -> int:
            result = 0
            for child in node.children:
                result += get_width(child, widths) + Tree.BETWEEN_X
            result -= Tree.BETWEEN_X
            if not node.children:
                result = node.box.width()
            widths[node] = result
            return result
        
        get_width(self.root, widths)

        # x_locs = {}
        # def cals_xloc_for_children(node: TreeNode, x_locs: dict, parent: TreeNode=None):
        #     pass
        # cals_xloc_for_children(self.root, x_locs)

        # print(self.area.width())
        # for key, value in widths.items():
        #     print(key.box.label.text(), value)
        # pre-construct layer offsets
        layers = []
        # layer_c = []
        # def f(node: TreeNode, layer: int, layers: list[int], layer_c: list[int]):
        #     if layer >= len(layers):
        #         layers += [0 for i in range(layer+1)]
        #         layer_c += [0 for i in range(layer+1)]
        #     layers[layer] += node.box.width() + Tree.BETWEEN_X
        #     layer_c[layer] += 1
        #     for child in node.children:
        #         f(child, layer+1, layers, layer_c)

        # f(self.root, 0, layers, layer_c)

        # for i in range(len(layers)):
        #     if layer_c[i] == 0: continue
        #     layers[i] = (self.area.w - layers[i] + Tree.BETWEEN_X) // 2

        layers += [(self.area.w - widths[self.root]) // 2]

        # draw nodes
        # self.root.draw(painter, (self.area.w - self.root.children_width()) // 2, Tree.BETWEEN_Y, (Tree.BETWEEN_X, Tree.BETWEEN_Y), None, layers)
        x = 200
        # self.root.draw(painter, x, y, (Tree.BETWEEN_X, Tree.BETWEEN_Y), None, layers)
        self.root.draw(painter)

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

    press = pyqtSignal(QMouseEvent)
    release = pyqtSignal(QMouseEvent)
    move = pyqtSignal(QMouseEvent)

    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)

        self.installEventFilter(self)

        # self.a = 100

    # def mousePressEvent(self, ev: QMouseEvent) -> None:
    #     self.mouse.emit(ModMouseEvent(ev, True))

    #     self.press.emit(ev)

    # def mouseReleaseEvent(self, ev: QMouseEvent) -> None:
    #     self.mouse.emit(ModMouseEvent(ev, False))

    #     self.press.emit(ev)

    # def mouseMoveEvent(self, ev: QMouseEvent) -> None:
    #     self.mouse.emit(ModMouseEvent(ev, False))

    #     self.press.emit(ev)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        # TODO fix resizing issue

        # if self.a < 0: return
        # self.a -= 1
        # pixmap = self.pixmap()
        # pixmap=pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        # pixmap = QPixmap(self.size())
        # self.setPixmap(pixmap)
        # print(pixmap.size())
        # print(self.size())
        # self.setPixmap(QPixmap(self.size()))
        # print('mogus')
        return super().resizeEvent(a0)


class GraphArea(QWidget):
    press = pyqtSignal(QMouseEvent)
    release = pyqtSignal(QMouseEvent)
    move = pyqtSignal(QMouseEvent)

    def __init__(self, parent: 'GraphWidget', data) -> None:
        super().__init__()

        self.parent_w = parent
        self.main = parent.main

        self.last_mouse_state: QMouseEvent = None

        self.w = 800
        self.h = 600

        self.tree_x = 0
        self.tree_y = 0

        self.init_tree(data)
        self.init_ui()


        # self.setFixedSize(self.w, self.h)

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        self.label = CLabel()
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.label.setScaledContents(True)
        # self.label.setresi
        
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
        self.tree.draw(self.tree_x, self.tree_y)
        self.update()
        
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

        # TODO implement
        self.tree.update_state()
        self.draw()
        self.update()
    
    # events
    def mousePressEvent(self, ev: QMouseEvent) -> None:
        # self.mouse.emit(ModMouseEvent(ev, True))

        self.press.emit(ev)

    def mouseReleaseEvent(self, ev: QMouseEvent) -> None:
        # self.mouse.emit(ModMouseEvent(ev, False))

        self.release.emit(ev)

    def mouseMoveEvent(self, ev: QMouseEvent) -> None:
        # self.mouse.emit(ModMouseEvent(ev, False))

        self.move.emit(ev)


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

    