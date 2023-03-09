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
from elements import *
from graph_util import *

from multiple_matcher import *


# class Node:
#     def __init__(self, name: str, children: list['Node']=[]) -> None:
#         self.name = name
#         self.children = children


NODE_NAME_SYMS = 'abcdefghijklmnopqrstuvwqyz'
NODE_NAME_SYMS += NODE_NAME_SYMS.upper()
NODE_NAME_SYMS += '0123456789'


def random_node_name():
    result = ''
    for i in range(random.randint(2, 4)):
        result += NODE_NAME_SYMS[random.randint(0, len(NODE_NAME_SYMS)-1)]
    return result


# data = \
# Node('1', [
#     Node('amogus', [
#     ]),
#     Node('8', [
#         Node('3', [
#             Node('AA'),
#             Node('NN')
#         ]),
#         Node('4', [
#             Node('6'),
#             Node('7')
#         ]),
#         Node('5'),
#     ]),
# ])


# data = Node('root')


data = MultipleMatcher('(.*)')


class TreeNode:
    def __init__(self, area: 'GraphArea', tree: 'Tree', text: str='', parent: 'TreeNode'=None, 
                 interactable:bool = True,
                 movable: bool=True,
                 disconnectable: bool=True) -> None:
        # self.box = ProgressTextBox(area, text, random.randint(0, 100), filled_color='red')
        self.box: MovableBox = MovableBox()

        self.tree: Tree = tree

        self.interactable = interactable
        self.movable = movable
        self.disconnectable = disconnectable

        self.children: list[TreeNode] = []
        self.parent: TreeNode = parent
        
        self.mouse_pos: QPoint = None
        
        self.on_click = None
        self.on_double_click = None

        def get_mpos(ev: QMouseEvent):
            return ev.pos() - self.area.label.pos()

        def in_mouse(node: TreeNode, ev) -> bool:
            if not node.interactable: return False

            mpos = get_mpos(ev)
            mx, my = mpos.x(), mpos.y()
            w, h = node.box.width(), node.box.height()
            return node.x < mx < node.x + w and node.y < my < node.y + h
            
        def press(ev: QMouseEvent):
            if ev.button() != Qt.MouseButton.LeftButton: return

            if not in_mouse(self, ev): return

            if ev.modifiers() == Qt.ControlModifier:
                if not self.parent: return
                if not self.disconnectable: return
                self.parent.children.remove(self)
                self.parent = None

                self.tree.roots += [self]
                return
            
            if ev.modifiers() == Qt.AltModifier:
                self.mouse_pos = get_mpos(ev)
                # self.draw_mouse_connection = True
                # self.area.connect_node = self
                return
            
            if self.on_click: self.on_click()
            self.box.is_moving = True
            self.area.draw()

        def double_press(ev: QMouseEvent):
            if not self.interactable: return

            if not in_mouse(self, ev): return
            if self.on_double_click(): self.on_double_click()

        def release(ev: QMouseEvent):
            if not self.interactable: return

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
                    self.tree.roots.remove(n)
                    self.children += [n]
                    break

                self.mouse_pos = None
            self.area.draw()
            # self.area.update()

        # TODO if multiple elements are on top of each other, all are moved
        def move(ev: QMouseEvent):
            if not self.movable: return

            if self.mouse_pos:
                # self.mouse_pos = ev.pos()
                self.mouse_pos = get_mpos(ev)
                self.area.draw()
                return
            if not self.box.is_moving: return
            pos =  get_mpos(ev)
            diff_x = pos.x() - self.x - self.box.width() // 2
            diff_y = pos.y() - self.y - self.box.height() // 2

            self.move(diff_x, diff_y)

            self.area.draw()

        area.press.connect(press)
        area.double_press.connect(double_press)
        area.release.connect(release)
        area.move.connect(move)

        self.x: int = None
        self.y: int = None
        
        self.area = area

    def set_text(self, text: str):
        self.box.set_text(text)

    def children_width(self, between_x: int=0):
        result = 0
        for child in self.children:
            result += child.children_width(between_x) + between_x
        result -= between_x
        if not self.children:
            result = self.box.width()
        return result

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

    def set_initial_loc(self, x: int, y: int, between: tuple[int, int], correct_self_loc: bool = True) -> int:
        cwidth = self.children_width(between[0])
        my_x = x
        # TODO fix inconsistent width when adding to amogus 
        # if cwidth > self.box.width():
        if correct_self_loc:
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

    def move(self, xdiff: int, ydiff: int):
        self.x += xdiff 
        self.y += ydiff
        for child in self.children:
            child.move(xdiff, ydiff)

BETWEEN_X = 20
BETWEEN_Y = 20


class Tree:


    def __init__(self, area: 'GraphArea') -> None:
        self.roots: list[TreeNode] = []

        self.area = area

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

        pixmap = self.pixmap()
        pixmap=pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(pixmap)
        self._parent.draw()


class MTGTree(Tree):
    def __init__(self, area: 'GraphArea') -> None:
        super().__init__(area)

    def get_pipeline(self):
        # TODO
        result = None

        return result


class MTGTreeNode(TreeNode):
    def __init__(self, area: 'GraphArea', tree: 'MTGTree', text: str = '', parent: 'TreeNode' = None, 
                 interactable: bool=True,
                 movable: bool=True,
                 disconnectable: bool=True) -> None:
        super().__init__(area, tree, text, parent, interactable, movable, disconnectable)

        self.box = TextBox(area, text)
        # self.box = MultiTextBox(area)
        # for i in range(random.randint(1, 4)):
        #     self.box.sub_boxes += [TextBox(area, random_node_name())]
        # self.box = ProgressWraper(TextBox(area, text), random.randint(0, 100), filled_color='red')
        # self.box = ProgressTextBox(area, text, random.randint(0, 100), filled_color='red')

    
        def dc():
            nd = MTGTreeNode(self.area, self.tree, random_node_name(), self)
            nd.x = self.x
            nd.y = self.y + self.box.height() + BETWEEN_Y
            self.children += [nd]

        self.on_double_click = dc

        self.on_click = lambda: self.area.parent_w.set_current_node(self)


class MTGTreeMultNode(MTGTreeNode):
    def __init__(self, area: 'GraphArea', tree: 'MTGTree', text: str = '', parent: 'TreeNode' = None, sub_nodes: list[MTGTreeNode] = None) -> None:
        super().__init__(area, tree, text, parent)
        if not sub_nodes: sub_nodes = []

        self.box = MultiTextBox(area, text)

        self.sub_nodes: list[MTGTreeNode] = []

        for node in sub_nodes:
            self.add_node(node)

        # self.sub_nodes: list[MTGTreeNode] = sub_nodes

    def add_node(self, node: MTGTreeNode):
        self.sub_nodes += [node]
        # node.x = 110/
        # node.y = 110

        # self.box.add_sub_box(node.box)
        self.box.sub_boxes += [node.box]

    def set_initial_loc(self, x: int, y: int, between: tuple[int, int]) -> int:
        super().set_initial_loc(x, y, between)

        y += self.box.height() - TextBox.height(self.box)

        for child in self.sub_nodes:
            child.set_initial_loc(x, y, between, False)
            x += child.box.width()

    def draw(self, painter: QPainter):
        super().draw(painter)

        for child in self.sub_nodes:
            child.draw(painter)

    def move(self, xdiff: int, ydiff: int):
        super().move(xdiff, ydiff)
        for child in self.sub_nodes:
            child.move(xdiff, ydiff)

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
        # double click action
        self.tree = MTGTree(self)

        def do(node: MTGObject, parent: TreeNode=None) -> MTGTreeNode:
            n = MTGTreeNode(self, self.tree, node.name)
            for child in n.children:
                c = do(child, n, parent)
                n.children += [c]
            return n
        
        # root = do(data)
        sub_nodes = []

        ssnode1 = MTGTreeNode(self, self.tree, 'T1', interactable=False)
        ssnode1.children += [MTGTreeNode(self, self.tree, 'Child of T1', ssnode1, disconnectable=False)]
        sub_nodes += [ssnode1]

        ssnode2 = MTGTreeNode(self, self.tree, 'T2', interactable=False)
        ssnode2.children += [MTGTreeNode(self, self.tree, 'Child of T2 1', ssnode2, disconnectable=False)]
        ssnode2.children += [MTGTreeNode(self, self.tree, 'Child of T2 2', ssnode2, disconnectable=False)]
        sub_nodes += [ssnode2]

        root = MTGTreeMultNode(self, self.tree, 'root', sub_nodes=sub_nodes)
        root.set_initial_loc(200, 10, (BETWEEN_X, BETWEEN_Y))
        self.tree.roots += [root]


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

        self.current_node: MTGTreeNode = None

        self.main = parent

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        top_layout = QHBoxLayout()

        self.graph_area = GraphArea(self, data)

        # self.selector_editor_area = SelectorWidget(self)
        self.right = QFormLayout()
        self.right.setEnabled(False)
        self.node_name_edit = QLineEdit()
        self.node_name_edit.textChanged.connect(self.text_changed)
        self.right.addRow('Label:', self.node_name_edit)

        top_layout.addWidget(self.graph_area, 2)
        top_layout.addLayout(self.right, 1)
        # top_layout.addWidget(self.selector_editor_area, 1)

        card_name_line = QHBoxLayout()
        parse_button = QPushButton('Parse')
        parse_button.clicked.connect(self.parse_action)
        self.card_name_edit = CardNameLine(list(self.main.name_dict.keys()))
        self.card_name_edit.textChanged.connect(self.card_name_text_changed)
        card_name_line.addWidget(self.card_name_edit)
        card_name_line.addWidget(parse_button)

        texts_line = QHBoxLayout()
        self.original_text = QTextEdit()
        self.parsed_text = QTextEdit()
        self.parsed_text.setReadOnly(True)
        texts_line.addWidget(self.original_text)
        texts_line.addWidget(self.parsed_text)

        layout.addLayout(top_layout)
        layout.addLayout(card_name_line)
        layout.addLayout(texts_line)
        self.setLayout(layout)

    def set_current_node(self, node: MTGTreeNode):
        self.right.setEnabled(True)
        self.current_node = node
        self.node_name_edit.setText(node.box.label.text())

    def text_changed(self):
        text = self.node_name_edit.text()
        self.current_node.set_text(text)
        self.graph_area.draw()

    def card_name_text_changed(self):
        cname = self.card_name_edit.text()
        if not cname in self.main.name_dict: return

        card = self.main.name_dict[cname]
        if not 'oracle_text' in card: return
        self.original_text.setText(card['oracle_text'])

    def parse_action(self):
        original_text = self.original_text.toPlainText()
        result = ''

        self.parsed_text.setText(result)