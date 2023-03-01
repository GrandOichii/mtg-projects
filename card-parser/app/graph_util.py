from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from graph import *
# def average_mid()

HOR_PADDING = 10
VER_PADDING = 5

def center_pos(x: int, y: int, width: int, height: int, inner_width: int, inner_height: int):
    return x + (width - inner_width) // 2, y + (height - inner_height) // 2

class TextBox:
    fill_color = Qt.green

    # TODO why can't detect?
    def __init__(self, parent: 'GraphArea', label=None) -> None:
        if not label: label = ''

        self.parent: GraphArea = parent
        
        self.label: QStaticText = None
        self.set_text(label)

    def set_text(self, text: str):
        self.label = QStaticText(text)
        ts = self.label.size()
        self.text_width, self.text_height = int(ts.width()), int(ts.height())

    def draw_mid_text(self, painter: QPainter, x: int, y: int, text: str):
        t = QStaticText(text)
        # c_pos = center_pos(x, y, self.width(), self.height(), self.text_width, self.text_height)
        painter.drawStaticText(x + HOR_PADDING, y + VER_PADDING, t)

    # override this
    def draw(self, painter: QPainter, x: int, y: int):
        mx, my = -1, -1
        if self.parent.last_mouse_state:
            m: QMouseEvent = self.parent.last_mouse_state
            mp = m.pos() + self.parent.pos()
            mx, my = mp.x(), mp.y()
        
        w = self.width()
        h = self.height()
        c = Qt.red if x < mx < x + w and y < my < y + h else TextBox.fill_color
        painter.fillRect(x, y, w, h, c)
        # painter.drawRect(x, y, w, h)
        # self.draw_mid_text(painter, x, y, self.label)

    def height(self):
        return self.text_height + 2 * VER_PADDING
    
    def width(self):
        return self.text_width + 2 * HOR_PADDING
