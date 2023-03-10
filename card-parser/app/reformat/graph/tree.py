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
from graph_el import *

from multiple_matcher import *


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
