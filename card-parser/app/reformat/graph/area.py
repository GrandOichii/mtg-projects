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

# from ..graph.area import *

# from pyqtgraph.parametertree import *
# import pyqtgraph as pb/

# from main import *
# from elements import *
# from graph_util import *

# from multiple_matcher import *

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
        
        # self.label.mouse.connect(self.mouse_action)
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

        def do(node: MTGObject, parent: MTGTreeNode=None) -> MTGTreeNode:
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

