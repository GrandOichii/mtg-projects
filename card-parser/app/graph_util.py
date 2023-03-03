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
    def __init__(self, parent: 'GraphArea', label:str=None) -> None:
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
        o_pen = painter.pen()
        pen = QPen()

        mx, my = -1, -1
        m: ModMouseEvent = None
        if self.parent.last_mouse_state:
            # sp = self.parent.screen().pos
            m = self.parent.last_mouse_state
            # mp = m.e.pos() + self.parent.pos()
            mp = m.e.pos()
            mx, my = mp.x(), mp.y()
        
        w = self.width()
        h = self.height()
        # fill background
        inside = x < mx < x + w and y < my < y + h
        c = Qt.red if inside else TextBox.fill_color
        painter.fillRect(x, y, w, h, c)
        # outline
        if m is not None and inside and m.clicked:
            self.clicked()
            pen.setColor(Qt.blue)
            pen.setWidth(3)
        painter.setPen(pen)
        painter.drawRect(x, y, w, h)
        painter.setPen(o_pen)
        self.draw_mid_text(painter, x, y, self.label)

    def height(self):
        return self.text_height + 2 * VER_PADDING
    
    def width(self):
        return self.text_width + 2 * HOR_PADDING

    def clicked(self):
        # TODO
        print(self.label.text())

class ProgressTextBox(TextBox):
    def __init__(self, parent: 'GraphArea', label: str=None, value: int=0, max_value: int=100, filled_color: str='green', blank_color: str='gray') -> None:
        super().__init__(parent, label)

        self.filled_c = QColor(filled_color)
        self.blank_c = QColor(blank_color)

        self.value = value
        self.max_value = max_value

    def bar_height(self):
        return super().height() // 4

    def height(self):
        return super().height() + self.bar_height()
    
    def draw(self, painter: QPainter, x: int, y: int):
        super().draw(painter, x, y)

        # draw progress bar
        bh = self.bar_height()
        sy = y + super().height()
        w = self.width()
        # draw blank
        painter.fillRect(x, sy, w, bh, self.blank_c)
        # draw filled
        painter.fillRect(x, sy, w * self.value // self.max_value, bh, self.filled_c)
        # draw border
        painter.drawRect(x, sy, w, bh)