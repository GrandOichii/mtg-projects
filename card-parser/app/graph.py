import math
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


class TreeNode:
    def __init__(self, area: 'GraphArea', tree: 'Tree', node: Node, parent: 'TreeNode'=None) -> None:
        self.box = ProgressTextBox(area, node.name, random.randint(0, 100), filled_color='red')

        self.tree: Tree = tree
        self.parent: TreeNode = parent
        self.mouse_pos: QPoint = None

        def get_mpos(ev: QMouseEvent):
            return ev.pos() - self.area.label.pos()

        def in_mouse(node: TreeNode, ev) -> bool:
            mpos = get_mpos(ev)
            mx, my = mpos.x(), mpos.y()
            w, h = node.box.width(), node.box.height()
            return node.x < mx < node.x + w and node.y < my < node.y + h
            
        def press(ev: QMouseEvent):
            if ev.button() != Qt.MouseButton.LeftButton: return

            if not in_mouse(self, ev): return

            if ev.modifiers() == Qt.ControlModifier:
                if not self.parent: return
                self.parent.children.remove(self)
                self.parent = None

                self.tree.roots += [self]
                return
            
            if ev.modifiers() == Qt.AltModifier:
                self.mouse_pos = get_mpos(ev)
                # self.draw_mouse_connection = True
                # self.area.connect_node = self
                return
            
            self.box.is_moving = True
            self.area.draw()

        def double_press(ev: QMouseEvent):
            if not in_mouse(self, ev): return
            n = Node(random_node_name())
            nd = TreeNode(self.area, self.tree, n, self)
            nd.x = self.x
            nd.y = self.y + self.box.height() + Tree.BETWEEN_Y
            self.children += [nd]

        def release(ev: QMouseEvent):
            # mpos = ev.pos()
            if self.box.is_moving: self.box.is_moving = False
            if self.mouse_pos:
                parents = []
                n = self
                while n:
                    parents += [n]
                    n = n.parent
                for n in self.tree.roots:
                    if not in_mouse(n, ev): continue
                    if n in parents: break
                    n.parent = self
                    self.children += [n]
                    break

                self.mouse_pos = None
            self.area.draw()
            # self.area.update()

        # TODO if multiple elements are on top of each other, all are moved
        def move(ev: QMouseEvent):
            if self.mouse_pos:
                # self.mouse_pos = ev.pos()
                self.mouse_pos = get_mpos(ev)
                self.area.draw()
                return
            if not self.box.is_moving: return
            pos =  get_mpos(ev)
            diff_x = pos.x() - self.x
            diff_y = pos.y() - self.y

            def move(node: TreeNode):
                node.x += diff_x
                node.y += diff_y
                for child in node.children:
                    move(child)
            move(self)

            self.area.draw()

        area.press.connect(press)
        area.double_press.connect(double_press)
        area.release.connect(release)
        area.move.connect(move)

        self.x: int = None
        self.y: int = None
        
        self.area = area

        # TODO save the original node?
        # self.info = node
        self.children: list[TreeNode] = []
        for child in node.children:
            self.children += [TreeNode(area, tree, child, self)]

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

        # draw mouse connection
        if self.mouse_pos:
            start_x = self.x + self.box.width() // 2
            start_y = self.y + self.box.height()
            painter.drawLine(QPoint(start_x, start_y), self.mouse_pos)

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

    def __init__(self, area: 'GraphArea', data) -> None:
        self.roots = [TreeNode(area, self, data)]

        self.area = area
        self.roots[0].set_initial_loc(200, 10, (Tree.BETWEEN_X, Tree.BETWEEN_Y))

        self.move: bool = False
        self.last: QPoint = None

        def get_mpos(ev: QMouseEvent):
            return ev.pos() - self.area.label.pos()

        def enable_move(ev: QMouseEvent):
            if ev.button() != Qt.MouseButton.RightButton: return
            self.move = True
            self.last = get_mpos(ev)

        def disable_move(ev: QMouseEvent):
            if ev.button() != Qt.MouseButton.RightButton: return
            self.move = False

        def move(ev: QMouseEvent):
            pos = get_mpos(ev)
            if not self.last:
                self.last = pos
            diff = pos - self.last
            diff_x, diff_y = diff.x(), diff.y()
            self.last = pos

            if not self.move: return
            def do(node: TreeNode):
                node.x += diff_x
                node.y += diff_y
                for child in node.children:
                    do(child)
            for n in self.roots:
                do(n)
            # do(self.root)
            self.area.draw()

        self.area.press.connect(enable_move)
        self.area.release.connect(disable_move)
        self.area.move.connect(move)

    # def update_state(self):
    #     self.root.update_state()

    def draw(self):
        p = self.area.label.pixmap()
        p.fill(Qt.cyan)

        painter = QPainter(p)

        regular = QPen()
        painter.setPen(regular)

        pen = QPen()
        pen.setColor(QColor(random.randint(0, 2000)))
                
        for n in self.roots:
            n.draw(painter)

        painter.end()


class ModMouseEvent:
    def __init__(self, e: QMouseEvent, clicked: bool) -> None:
        self.e = e
        self.clicked = clicked


class CLabel(QLabel):
    mouse = pyqtSignal(ModMouseEvent)

    press = pyqtSignal(QMouseEvent)
    release = pyqtSignal(QMouseEvent)
    move = pyqtSignal(QMouseEvent)

    def __init__(self, parent: 'GraphArea'):
        super().__init__()
        self._parent = parent

        self.setMouseTracking(True)

        self.installEventFilter(self)

    def resizeEvent(self, ev: QResizeEvent) -> None:
        # TODO fix resizing issue

        # if self.a < 0: return
        # self.a -= 1
        pixmap = self.pixmap()
        pixmap=pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        # # pixmap = QPixmap(self.size())
        self.setPixmap(pixmap)
        self._parent.draw()


class GraphArea(QWidget):
    press = pyqtSignal(QMouseEvent)
    double_press = pyqtSignal(QMouseEvent)
    release = pyqtSignal(QMouseEvent)
    move = pyqtSignal(QMouseEvent)

    def __init__(self, parent: 'GraphWidget', data) -> None:
        super().__init__()

        self.parent_w = parent
        self.main = parent.main

        self.last_mouse_state: QMouseEvent = None

        # self.w = 800
        # self.h = 600

        self.init_tree(data)
        self.init_ui()


        # self.setFixedSize(self.w, self.h)

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        self.label = CLabel(self)
        # self.label.setStyleSheet("border: 1px solid black;")
        # self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.label.setScaledContents(True)
        
        self.label.mouse.connect(self.mouse_action)
        layout.addWidget(self.label)

        self.setLayout(layout)


        self.canvas = QPixmap(self.label.size())
        self.canvas.fill(Qt.cyan)
        self.label.setPixmap(self.canvas)
        self.draw()
        self.label.update()

    def init_tree(self, data):
        self.tree = Tree(self, data)

    def draw(self):
        self.tree.draw()
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
        # x = int(pos.x())
        # y = int(pos.y())
        # painter.drawPoint(x, y)
        # painter.end()

        # TODO implement
        # self.tree.update_state()
        self.draw()
        self.update()
    
    # events
    def mousePressEvent(self, ev: QMouseEvent) -> None:
        # self.mouse.emit(ModMouseEvent(ev, True))

        self.press.emit(ev)

    def mouseDoubleClickEvent(self, ev: QMouseEvent) -> None:
        self.double_press.emit(ev)
        # return super().mouseDoubleClickEvent(a0)

    def mouseReleaseEvent(self, ev: QMouseEvent) -> None:
        # self.mouse.emit(ModMouseEvent(ev, False))

        self.release.emit(ev)

    def mouseMoveEvent(self, ev: QMouseEvent) -> None:
        # self.mouse.emit(ModMouseEvent(ev, False))
        self.move.emit(ev)

    def wheelEvent(self, ev: QWheelEvent) -> None:
        return
        direction = ev.angleDelta().y()

        v = 1
        if direction < 0: v = -v

        # TextBox.VER_PADDING += v * TextBox.HOR_PADDING // TextBox.VER_PADDING
        wheel = 1 if direction < 0 else -1

        zoom = math.exp(wheel)
        TextBox.HOR_PADDING *= wheel
        TextBox.VER_PADDING *= wheel
        pos = ev.pos()
        mx, my = pos.x(), pos.y()

        def sqrt(v):
            d = math.sqrt(abs(v))
            if v < 0:
                d = -d
            return int(d)
        
        scale = 2
        def do(node: TreeNode, diff: int):
            
            # context.translate(originx, originy)
        
            # node.x += int(mx/(zoom*scale) - mx)
            # node.y += int(my/(zoom*scale) - my)
            
            # # context.scale(zoom, zoom)
            # # context.translate(-originx, -originy)

            # # scale *= zoom
            # # zoom = math.exp(dir)
            

            # for child in node.children:
            #     do(child, diff)

            # return
            # diff *= 2
            diff_x = mx - node.x + node.box.width()
            diff_y = my - node.y + node.box.height()
            if direction < 0:
                diff_x = -diff_x
                diff_y = -diff_y
            # node.x -= diff_x
            node.x -= sqrt(direction)
            # node.y -= diff_y
            node.y -= sqrt(direction)
            # node.x -= diff
            # node.y -= diff
            for child in node.children:
                do(child, diff)
        for n in self.tree.roots:
            do(n, v)
        # do(self.tree.root, v)
        self.draw()
        # return super().wheelEvent(ev)


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

    