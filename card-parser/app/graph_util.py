from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from graph import *
# def average_mid()

def center_pos(x: int, y: int, width: int, height: int, inner_width: int, inner_height: int):
    return x + (width - inner_width) // 2, y + (height - inner_height) // 2

class TextBox:
    fill_color = Qt.green

    HOR_PADDING = 10
    VER_PADDING = 5


    # TODO why can't detect? (sometimes)
    def __init__(self, parent: 'GraphArea', label:str=None) -> None:
        if not label: label = ''

        # def press(ev: QMouseEvent):
        #     mpos = ev.pos()
        #     mx, my = mpos.x(), mpos.y()
        #     w, h = self.width(), self.height()
        #     h = self.height()
        #     if not (self.x < mx < self.x + w and self.y < my < self.y + h): return
        #     self.selected = True

        # def release(ev: QMouseEvent):
        #     # mpos = ev.pos()
        #     if self.selected: self.selected = False

        self.selected: bool = False
        # parent.press.connect(press)
        # parent.release.connect(release)
        
        # parent.parent_w.
        # print(par)

        self.clicked = None

        self.parent: GraphArea = parent
        
        self.label: QStaticText = QStaticText()

        self.set_text(label)

    def set_text(self, text: str):
        self.label.setText(text)
        ts = self.label.size()
        self.text_width, self.text_height = int(ts.width()), int(ts.height())

    def draw_mid_text(self, painter: QPainter, x: int, y: int, text: str):
        t = QStaticText(text)
        # c_pos = center_pos(x, y, self.width(), self.height(), self.text_width, self.text_height)
        painter.drawStaticText(x + TextBox.HOR_PADDING, y + TextBox.VER_PADDING, t)

    # override this
    def draw(self, painter: QPainter, x: int, y: int):
        o_pen = painter.pen()
        pen = QPen()

        # mx, my = -1, -1
        # m: ModMouseEvent = None
        # if self.parent.last_mouse_state:
        #     # sp = self.parent.screen().pos
        #     m = self.parent.last_mouse_state
        #     # mp = m.e.pos() + self.parent.pos()
        #     mp = m.e.pos()
        #     mx, my = mp.x(), mp.y()
        
        w = self.width()
        h = self.height()
        # # fill background
        # # print(x)
        # inside = x < mx < x + w and y < my < y + h
        # c = Qt.red if inside else TextBox.fill_color
        c = Qt.red if self.selected else TextBox.fill_color
        painter.fillRect(x, y, w, h, c)
        # # outline
        # if m is not None and inside and m.clicked:
        #     if self.clicked: self.clicked()
        #     pen.setColor(Qt.blue)
        #     pen.setWidth(3)
        painter.setPen(pen)
        painter.drawRect(x, y, w, h)
        painter.setPen(o_pen)
        self.draw_mid_text(painter, x, y, self.label)

    def height(self):
        return self.text_height + 2 * TextBox.VER_PADDING
    
    def width(self):
        return self.text_width + 2 * TextBox.HOR_PADDING

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